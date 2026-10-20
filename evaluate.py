# evaluate.py
"""CLI: run the RAG evaluation harness against a Q&A dataset and print a report.

Usage:
    python evaluate.py [--dataset eval/dataset.json] [--report eval/last_report.md] [--mlflow] [--judge-model NAME]
"""

import os

# Must be set before any ML library is imported.
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

from dotenv import load_dotenv

load_dotenv()

import argparse

from src.config import JUDGE_MODEL, RERANKER_TOP_N
from src.rag_pipeline import RAGPipeline
from src.evaluation import make_judge, run_evaluation


def render_report(report: dict) -> str:
    r, g = report["retrieval"], report["generation"]
    lines = [
        f"# Evaluation report ({report['n_cases']} questions)",
        "",
        f"- Retrieval — Recall@{RERANKER_TOP_N}: **{r['recall_at_k']:.0%}**, MRR: **{r['mrr']:.2f}**",
        f"- Generation — Correctness: **{g['correctness']:.0%}**, Faithfulness: **{g['faithfulness']:.0%}**",
        "",
        "## Breakdown by language",
        "",
        "English questions are asked against the English document, Vietnamese questions against "
        "the Vietnamese document (independent question sets, not translations of each other) — "
        "this compares how well the pipeline performs end-to-end when working entirely in one "
        "language vs. the other.",
        "",
        "| Language | Recall@k | MRR | Correctness | Faithfulness |",
        "|---|---|---|---|---|",
    ]
    languages = sorted(r["recall_at_k_by_language"])
    for lang in languages:
        lines.append(
            f"| {lang} | {r['recall_at_k_by_language'][lang]:.0%} | {r['mrr_by_language'][lang]:.2f} "
            f"| {g['correctness_by_language'][lang]:.0%} | {g['faithfulness_by_language'][lang]:.0%} |"
        )
    lines += [
        "",
        "| # | Language | Question | Retrieved | Rank | Correct | Faithful |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, (rc, gc) in enumerate(zip(r["per_case"], g["per_case"]), start=1):
        lines.append(
            f"| {i} | {rc['language']} | {rc['question']} | {'yes' if rc['hit'] else 'no'} | {rc['rank'] or '-'} "
            f"| {'yes' if gc['correct'] else 'no'} | {'yes' if gc['faithful'] else 'no'} |"
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
    args = parser.parse_args()

    pipeline = RAGPipeline()
    if not pipeline.load_existing_index():
        raise SystemExit("No indexed documents found in vector_db/. Upload documents via the app first.")

    judge = make_judge(args.judge_model) if args.judge_model else None  # empty value: the answering model grades itself

    print(f"Running evaluation on {args.dataset}...")
    report = run_evaluation(pipeline, args.dataset, judge)

    rendered = render_report(report)
    print("\n" + rendered)

    with open(args.report, "w", encoding="utf-8") as f:
        f.write(rendered)
    print(f"Report saved to {args.report}")

    if args.mlflow:
        from src.tracking import log_evaluation  # lazy: mlflow is only needed with --mlflow

        run_id = log_evaluation(report, rendered, args.dataset)
        print(f"Logged to MLflow, run id: {run_id}")


if __name__ == "__main__":
    main()
