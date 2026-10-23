# src/evaluation.py
"""Retrieval + generation evaluation harness for RAGPipeline.

Measures two things a running chatbot can't tell you on its own:
  - Retrieval quality: does the retriever + reranker surface the chunk that
    actually contains the answer (Recall@k, MRR)?
  - Generation quality: is the LLM's answer correct vs. a reference answer,
    and faithful to the retrieved context (LLM-as-judge, yes/no)?

Each case carries:
  - `evidence`: verbatim snippets of the source text that a retrieved chunk must
    contain (empty for out-of-document questions). Matching is on text, not on
    chunk positions, so re-chunking the documents does not invalidate the dataset.
  - `history`: earlier chat turns for follow-up questions, empty otherwise.
  - `language`, `type`, `split` tags: English questions target the English
    document, Vietnamese questions the Vietnamese one; `type` is the kind of
    question; `split` is "dev" (used to iterate) or "test" (confirm once). Metrics
    can be broken down by these tags.
"""

import json
import re
import statistics
import time
from typing import List, TypedDict

from langchain_core.messages import AIMessage, HumanMessage

from src.config import OLLAMA_BASE_URL
from src.prompts import CORRECTNESS_JUDGE_PROMPT, FAITHFULNESS_JUDGE_PROMPT

# The tags a metric is broken down by in the report.
GROUPS = ("language", "type", "split", "doc")
# PDF text marks a hyphenated line break with U+2010 (hyphen) or U+00AD (soft hyphen). Code points, not the characters
# themselves, because U+00AD is invisible and `ruff format` rewrites escapes into the literal character.
PDF_HYPHENS: dict = {0x2010: "-", 0x00AD: None}


class EvalCase(TypedDict):
    id: str
    type: str
    language: str
    split: str
    doc: str  # which document the question is about; an older dataset without it reports "unknown"
    question: str
    history: List[List[str]]
    expected_answer: str
    evidence: List[str]


def load_dataset(path: str, split: str = "all") -> List[EvalCase]:
    with open(path, "r", encoding="utf-8") as f:
        return [EvalCase(**c) for c in json.load(f) if split == "all" or c.get("split") == split]


def _normalize(text: str) -> str:
    """Collapse whitespace and the hyphenation marks of PDF line breaks so a snippet matches across lines."""
    return re.sub(r"\s+", " ", text.translate(PDF_HYPHENS)).strip()


def missing_evidence(dataset: List[EvalCase], chunk_texts: List[str]) -> List[str]:
    """Evidence snippets found in no indexed chunk, i.e. where the dataset no longer matches the index."""
    # Normalise each chunk once, not once per snippet.
    norm_chunks = [_normalize(chunk) for chunk in chunk_texts]
    return [
        f"{case['id']}: {snippet}"
        for case in dataset
        for snippet in case["evidence"]
        if not any(_normalize(snippet) in chunk for chunk in norm_chunks)
    ]


def _history_messages(case: EvalCase) -> list:
    messages = []
    for role, text in case["history"]:
        if role == "human":
            messages.append(HumanMessage(content=text))
        elif role == "ai":
            messages.append(AIMessage(content=text))
    return messages


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


def _grouped_mean(per_case: List[dict], value_key: str, group_key: str = "language") -> dict:
    """Average `value_key` per distinct `group_key`, e.g. {"en": 0.8, "vi": 0.5}."""
    groups: dict = {}
    for c in per_case:
        groups.setdefault(c[group_key], []).append(c[value_key])
    return {name: _mean(vals) for name, vals in groups.items()}


def _breakdowns(per_case: List[dict], metrics: dict) -> dict:
    """{"<metric>_by_<group>": {...}} for every metric and every group in GROUPS.

    `metrics` maps a metric name to the per-case key holding its value, e.g. {"mrr": "reciprocal_rank"}.
    """
    return {
        f"{metric_name}_by_{group}": _grouped_mean(per_case, metric_key, group)
        for metric_name, metric_key in metrics.items()
        for group in GROUPS
    }


def evaluate_retrieval(pipeline, dataset: List[EvalCase]) -> dict:
    """Recall@k and MRR of the retriever+reranker against the evidence snippets."""
    # A snippet is a text, not a chunk position: it counts as retrieved if a normalised retrieved chunk contains it.
    # A follow-up is searched as the standalone question chat() would build; questions without evidence are skipped.
    per_case = []

    for case in dataset:
        if not case["evidence"]:
            continue

        question = pipeline._contextualize_fn({"input": case["question"], "chat_history": _history_messages(case)})
        candidates = pipeline._retriever.invoke(question)
        reranked = pipeline._rerank(question, candidates)
        texts = [_normalize(doc.page_content) for doc in reranked]

        ranks = [
            next((i for i, t in enumerate(texts, start=1) if _normalize(snippet) in t), None)
            for snippet in case["evidence"]
        ]

        hit = all(r is not None for r in ranks)
        found = [r for r in ranks if r is not None]
        rank = min(found) if found else None

        per_case.append(
            {
                "id": case["id"],
                "type": case["type"],
                "split": case["split"],
                "doc": case.get("doc", "unknown"),
                "question": case["question"],
                "language": case["language"],
                "hit": hit,
                "rank": rank,
                "reciprocal_rank": 1 / rank if rank else 0,
            }
        )

    return {
        "recall_at_k": _mean([1 if c["hit"] else 0 for c in per_case]),
        "mrr": _mean([c["reciprocal_rank"] for c in per_case]),
        **_breakdowns(per_case, {"recall_at_k": "hit", "mrr": "reciprocal_rank"}),
        "per_case": per_case,
    }


def evaluate_generation(pipeline, dataset: List[EvalCase], judge=None) -> dict:
    """LLM-as-judge correctness + faithfulness of the full chat() pipeline; the judge defaults to pipeline.llm."""
    judge = judge or pipeline.llm
    per_case = []

    for case in dataset:
        # Time the pipeline only: the grading below is not part of how long the chatbot takes to answer.
        start_time = time.perf_counter()
        docs = []
        answer = ""
        for chunk in pipeline.chat(case["question"], _history_messages(case)):
            if "context" in chunk:
                docs = chunk["context"]
            if "answer" in chunk:
                answer += chunk["answer"]
        elapsed_seconds = time.perf_counter() - start_time

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
                "id": case["id"],
                "type": case["type"],
                "split": case["split"],
                "doc": case.get("doc", "unknown"),
                "question": case["question"],
                "language": case["language"],
                "answer": answer,
                "correct": is_correct,
                "faithful": is_faithful,
                "seconds": round(elapsed_seconds, 1),
            }
        )

    return {
        "correctness": _mean([1 if c["correct"] else 0 for c in per_case]),
        "faithfulness": _mean([1 if c["faithful"] else 0 for c in per_case]),
        **_breakdowns(per_case, {"correctness": "correct", "faithfulness": "faithful"}),
        "median_seconds": statistics.median([c["seconds"] for c in per_case]) if per_case else 0.0,
        "per_case": per_case,
    }


def run_evaluation(pipeline, dataset_path: str, judge=None, split: str = "all") -> dict:
    """Run both retrieval and generation evaluation and return a combined report."""
    dataset = load_dataset(dataset_path, split)
    return {
        "n_cases": len(dataset),
        "split": split,
        "judge_model": getattr(judge or pipeline.llm, "model", "unknown"),
        "retrieval": evaluate_retrieval(pipeline, dataset),
        "generation": evaluate_generation(pipeline, dataset, judge),
    }


def per_case_results(report: dict) -> List[dict]:
    """One record per question with its retrieval and generation results side by side, for paired comparisons."""
    # Out-of-document questions have no retrieval record: their hit and rank are None, not False, so a table can
    # tell "nothing to retrieve" from "retrieved nothing".
    retrieval_cases = {c["id"]: c for c in report.get("retrieval", {}).get("per_case", [])}

    results = []
    for g in report.get("generation", {}).get("per_case", []):
        case_id = g["id"]
        ret_case = retrieval_cases.get(case_id)

        hit = ret_case["hit"] if ret_case else None
        rank = ret_case["rank"] if ret_case else None

        results.append(
            {
                **g,
                "hit": hit,
                "rank": rank,
            }
        )

    return results
