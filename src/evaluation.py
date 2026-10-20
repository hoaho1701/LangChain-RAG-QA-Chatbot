# src/evaluation.py
"""Retrieval + generation evaluation harness for RAGPipeline.

Measures two things a running chatbot can't tell you on its own:
  - Retrieval quality: does the retriever + reranker surface the chunk that
    actually contains the answer (Recall@k, MRR)?
  - Generation quality: is the LLM's answer correct vs. a reference answer,
    and faithful to the retrieved context (LLM-as-judge, yes/no)?

Each case also carries a `language` tag — English questions target the
English document, Vietnamese questions target the Vietnamese document — so
metrics can be broken down per language to compare how well the pipeline
performs end-to-end in one language vs. the other.
"""

import json
import re
from typing import List, TypedDict

from src.config import OLLAMA_BASE_URL
from src.prompts import CORRECTNESS_JUDGE_PROMPT, FAITHFULNESS_JUDGE_PROMPT


class EvalCase(TypedDict):
    question: str
    language: str
    expected_answer: str
    expected_source: str
    expected_page: int
    expected_chunk_index: int


def load_dataset(path: str) -> List[EvalCase]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def make_judge(model: str):
    """Build the grading LLM: deterministic, short replies, thinking off (thinking models burn the token budget)."""
    from langchain_ollama import ChatOllama  # lazy: only needed when a separate judge grades

    ollama_kwargs = {"base_url": OLLAMA_BASE_URL} if OLLAMA_BASE_URL else {}
    return ChatOllama(model=model, temperature=0, num_predict=32, reasoning=False, **ollama_kwargs)


def _judge_yes(llm, prompt, **kwargs) -> bool:
    messages = prompt.format_messages(**kwargs)
    reply = llm.invoke(messages).content.strip().lower()
    return re.sub(r"^[^a-z]+", "", reply).startswith("yes")  # tolerate leading markdown such as "**Yes**"


def _mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _grouped_mean(per_case: List[dict], value_key: str) -> dict:
    """Average `value_key` per distinct `language`, e.g. {"en": 0.8, "vi": 0.5}."""
    groups: dict = {}
    for c in per_case:
        groups.setdefault(c["language"], []).append(c[value_key])
    return {lang: _mean(vals) for lang, vals in groups.items()}


def evaluate_retrieval(pipeline, dataset: List[EvalCase]) -> dict:
    """Recall@k and MRR of the retriever+reranker against ground-truth chunks."""
    per_case = []

    for case in dataset:
        candidates = pipeline._retriever.invoke(case["question"])
        reranked = pipeline._rerank(case["question"], candidates)

        rank = None
        for i, doc in enumerate(reranked, start=1):
            # start_index resets per source Document (e.g. per PDF page), so it's only
            # unique in combination with (source, page).
            if (
                doc.metadata.get("source") == case["expected_source"]
                and doc.metadata.get("page") == case["expected_page"]
                and doc.metadata.get("start_index") == case["expected_chunk_index"]
            ):
                rank = i
                break

        per_case.append(
            {
                "question": case["question"],
                "language": case["language"],
                "hit": rank is not None,
                "rank": rank,
                "reciprocal_rank": 1 / rank if rank else 0,
            }
        )

    return {
        "recall_at_k": _mean([1 if c["hit"] else 0 for c in per_case]),
        "mrr": _mean([c["reciprocal_rank"] for c in per_case]),
        "recall_at_k_by_language": _grouped_mean(per_case, "hit"),
        "mrr_by_language": _grouped_mean(per_case, "reciprocal_rank"),
        "per_case": per_case,
    }


def evaluate_generation(pipeline, dataset: List[EvalCase], judge=None) -> dict:
    """LLM-as-judge correctness + faithfulness of the full chat() pipeline; the judge defaults to pipeline.llm."""
    judge = judge or pipeline.llm
    per_case = []

    for case in dataset:
        docs = []
        answer = ""
        for chunk in pipeline.chat(case["question"], []):
            if "context" in chunk:
                docs = chunk["context"]
            if "answer" in chunk:
                answer += chunk["answer"]

        context_text = pipeline._format_docs(docs)

        is_correct = _judge_yes(
            judge,
            CORRECTNESS_JUDGE_PROMPT,
            question=case["question"],
            reference=case["expected_answer"],
            answer=answer,
        )
        is_faithful = _judge_yes(
            judge,
            FAITHFULNESS_JUDGE_PROMPT,
            context=context_text,
            answer=answer,
        )

        per_case.append(
            {
                "question": case["question"],
                "language": case["language"],
                "answer": answer,
                "correct": is_correct,
                "faithful": is_faithful,
            }
        )

    return {
        "correctness": _mean([1 if c["correct"] else 0 for c in per_case]),
        "faithfulness": _mean([1 if c["faithful"] else 0 for c in per_case]),
        "correctness_by_language": _grouped_mean(per_case, "correct"),
        "faithfulness_by_language": _grouped_mean(per_case, "faithful"),
        "per_case": per_case,
    }


def run_evaluation(pipeline, dataset_path: str, judge=None) -> dict:
    """Run both retrieval and generation evaluation and return a combined report."""
    dataset = load_dataset(dataset_path)
    return {
        "n_cases": len(dataset),
        "judge_model": getattr(judge or pipeline.llm, "model", "unknown"),
        "retrieval": evaluate_retrieval(pipeline, dataset),
        "generation": evaluate_generation(pipeline, dataset, judge),
    }
