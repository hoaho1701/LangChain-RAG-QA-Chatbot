"""Log evaluation runs to MLflow."""

import hashlib
import os

from src import config
from src.prompts import CORRECTNESS_SYSTEM_PROMPT, FAITHFULNESS_SYSTEM_PROMPT, QA_SYSTEM_PROMPT


def log_evaluation(report: dict, report_md: str, dataset_path: str, experiment: str = "rag-eval") -> str:
    """Log one evaluation run (params, metrics, report) to MLflow and return its run id."""
    import mlflow  # lazy: evaluate.py must still work without --mlflow

    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "./mlruns"))
    mlflow.set_experiment(experiment)

    # Runs on different questions must not be compared: the hash tells two versions of the dataset file apart.
    with open(dataset_path, "rb") as f:
        dataset_hash = hashlib.sha256(f.read()).hexdigest()[:12]
    r, g = report["retrieval"], report["generation"]
    # Logged like the QA prompt: runs graded with different judge wording must be told apart.
    judge_prompts = CORRECTNESS_SYSTEM_PROMPT + "\n\n" + FAITHFULNESS_SYSTEM_PROMPT
    with mlflow.start_run() as run:
        mlflow.log_params(
            {
                "llm_model": config.LLM_MODEL,
                "embedding_model": config.EMBEDDING_MODEL,
                "reranker_model": config.RERANKER_MODEL,
                "chunk_size": config.CHUNK_SIZE,
                "chunk_overlap": config.CHUNK_OVERLAP,
                "retriever_top_k": config.RETRIEVER_TOP_K,
                "reranker_top_n": config.RERANKER_TOP_N,
                "n_cases": report["n_cases"],
                "eval_split": report.get("split", "all"),
                "dataset_hash": dataset_hash,
                "judge_model": report.get("judge_model", config.LLM_MODEL),
                "qa_prompt_hash": hashlib.sha256(QA_SYSTEM_PROMPT.encode()).hexdigest()[:12],
                "judge_prompt_hash": hashlib.sha256(judge_prompts.encode()).hexdigest()[:12],
            }
        )
        mlflow.log_metrics(
            {
                "recall_at_k": r["recall_at_k"],
                "mrr": r["mrr"],
                "correctness": g["correctness"],
                "faithfulness": g["faithfulness"],
            }
        )

        # One metric per language, e.g. recall_at_k_en.
        by_language = {
            "recall_at_k": r["recall_at_k_by_language"],
            "mrr": r["mrr_by_language"],
            "correctness": g["correctness_by_language"],
            "faithfulness": g["faithfulness_by_language"],
        }
        for name, values in by_language.items():
            for lang, value in values.items():
                mlflow.log_metric(f"{name}_{lang}", value)

        mlflow.log_text(report_md, "report.md")
        mlflow.log_text(QA_SYSTEM_PROMPT, "qa_prompt.txt")
        mlflow.log_text(judge_prompts, "judge_prompts.txt")
        mlflow.log_artifact(dataset_path)
        return run.info.run_id
