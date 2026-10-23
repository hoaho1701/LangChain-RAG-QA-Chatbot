# eval/evaluate.py
"""CLI: run the RAG evaluation harness against a Q&A dataset and print a report.

Usage:
    python -m eval.evaluate [--dataset eval/dataset.json] [--report eval/last_report.md] [--mlflow] [--judge-model NAME]
                       [--split dev|test|all] [--per-case-json PATH]
"""

import os

# Must be set before any ML library is imported.
os.environ["TOKENIZERS_PARALLELISM"] = "false"
# 4 threads make the reranker about 1.5x faster than 1; more than the CPU has would only compete with each other.
os.environ["OMP_NUM_THREADS"] = str(min(4, os.cpu_count() or 1))

from dotenv import load_dotenv

load_dotenv()

import argparse
import json
from typing import List

from src.config import JUDGE_MODEL, RERANKER_TOP_N
from src.rag_pipeline import RAGPipeline
from src.evaluation import GROUPS, load_dataset, make_judge, missing_evidence, run_evaluation, per_case_results


def _breakdown(group: str, r: dict, g: dict) -> List[str]:
    """One table of metrics per value of `group` (language, type or split)."""
    # Names come from the generation metrics: a value such as type "out_of_doc" has no retrieval metric and is missing
    # from the retrieval dicts, so its Recall@k and MRR cells show "-".
    lines = [
        "",
        f"## By {group}",
        "",
        f"| {group.capitalize()} | Recall@k | MRR | Correctness | Faithfulness |",
        "|---|---|---|---|---|",
    ]
    recall = r[f"recall_at_k_by_{group}"]
    mrr = r[f"mrr_by_{group}"]
    for name in sorted(g[f"correctness_by_{group}"]):
        has_retrieval = name in recall
        recall_cell = f"{recall[name]:.0%}" if has_retrieval else "-"
        mrr_cell = f"{mrr[name]:.2f}" if has_retrieval else "-"
        correctness = g[f"correctness_by_{group}"][name]
        faithfulness = g[f"faithfulness_by_{group}"][name]
        lines.append(f"| {name} | {recall_cell} | {mrr_cell} | {correctness:.0%} | {faithfulness:.0%} |")

    return lines


def render_report(report: dict) -> str:
    r, g = report["retrieval"], report["generation"]
    lines = [
        f"# Evaluation report ({report['n_cases']} questions, {report['split']} split)",
        "",
        f"- Retrieval — Recall@{RERANKER_TOP_N}: **{r['recall_at_k']:.0%}**, MRR: **{r['mrr']:.2f}** "
        f"({len(r['per_case'])} questions that have evidence)",
        f"- Generation — Correctness: **{g['correctness']:.0%}**, Faithfulness: **{g['faithfulness']:.0%}**, "
        f"median {g['median_seconds']:.0f} s per answer",
        "",
    ]
    for group in GROUPS:
        lines += _breakdown(group, r, g)
    lines += [
        "",
        "English questions are asked against the English document, Vietnamese questions against the Vietnamese",
        "document (independent question sets, not translations of each other).",
        "",
        "| # | Id | Question | Retrieved | Rank | Correct | Faithful | Seconds |",
        "|---|---|---|---|---|---|---|---|",
    ]
    # hit is None when the question has no retrieval record (out-of-document): show "-", not "no".
    for i, c in enumerate(per_case_results(report), start=1):
        retrieved = "-" if c["hit"] is None else ("yes" if c["hit"] else "no")
        lines.append(
            f"| {i} | {c['id']} | {c['question']} | {retrieved} | {c['rank'] or '-'} "
            f"| {'yes' if c['correct'] else 'no'} | {'yes' if c['faithful'] else 'no'} | {c['seconds']} |"
        )
    return "\n".join(lines) + "\n"


def main():
    """Run the evaluation, write the Markdown report, and optionally log the run to MLflow."""
    parser = argparse.ArgumentParser(description="Evaluate the RAG pipeline against a Q&A dataset.")
    parser.add_argument("--dataset", default="eval/dataset.json", help="Path to the eval dataset JSON file.")
    parser.add_argument("--report", default="eval/last_report.md", help="Path to write the Markdown report to.")
    parser.add_argument("--mlflow", action="store_true", help="Log params, metrics and the report to MLflow.")
    parser.add_argument(
        "--judge-model",
        default=JUDGE_MODEL,
        help="Ollama model that grades the answers (default: JUDGE_MODEL; empty = the answering model).",
    )
    parser.add_argument(
        "--split",
        choices=["dev", "test", "all"],
        default="dev",
        help="Questions to run: dev to iterate on (default), test to confirm once, all for the final report.",
    )
    parser.add_argument(
        "--per-case-json", help="Also write one JSON record per question, to compare two runs case by case."
    )
    args = parser.parse_args()

    pipeline = RAGPipeline()
    if not pipeline.load_existing_index():
        raise SystemExit("No indexed documents found in the vector database. Upload documents via the app first.")

    # Stop before the slow grading if the dataset does not match the index: a snippet found in no chunk would be
    # scored as a retrieval miss and blamed on the retriever.
    missing = missing_evidence(load_dataset(args.dataset), pipeline.vector_store.get()["documents"])
    if missing:
        raise SystemExit(
            "These evidence snippets are in no indexed chunk, so the dataset does not match the index:\n"
            + "\n".join(missing)
        )
    judge = make_judge(args.judge_model) if args.judge_model else None  # empty value: the answering model grades itself

    print(f"Running evaluation on {args.dataset} ({args.split} split)...")
    report = run_evaluation(pipeline, args.dataset, judge, args.split)

    rendered = render_report(report)
    print("\n" + rendered)

    with open(args.report, "w", encoding="utf-8") as f:
        f.write(rendered)
    print(f"Report saved to {args.report}")

    if args.per_case_json:
        with open(args.per_case_json, "w", encoding="utf-8") as f:
            json.dump(
                {"judge_model": report["judge_model"], "split": report["split"], "cases": per_case_results(report)},
                f,
                ensure_ascii=False,
                indent=2,
            )
        print(f"Per-question results saved to {args.per_case_json}")

    if args.mlflow:
        from src.tracking import log_evaluation  # lazy: mlflow is only needed with --mlflow

        run_id = log_evaluation(report, rendered, args.dataset)
        print(f"Logged to MLflow, run id: {run_id}")


if __name__ == "__main__":
    main()
