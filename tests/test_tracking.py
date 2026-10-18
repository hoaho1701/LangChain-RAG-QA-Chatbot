"""Tests for src/tracking.py: log a fake report to a temporary MLflow store, then read the run back."""

import json

import mlflow
import pytest

from src import config
from src.tracking import log_evaluation


@pytest.fixture(autouse=True)
def tracking_store(tmp_path, monkeypatch):
    """Point MLflow at a throwaway folder so tests never touch ./mlruns."""
    monkeypatch.setenv("MLFLOW_TRACKING_URI", str(tmp_path / "mlruns"))


@pytest.fixture
def report():
    """A report shaped like run_evaluation() output, with values that differ per metric."""
    return {
        "n_cases": 20,
        "retrieval": {
            "recall_at_k": 0.95,
            "mrr": 0.9,
            "recall_at_k_by_language": {"en": 1.0, "vi": 0.9},
            "mrr_by_language": {"en": 0.95, "vi": 0.85},
        },
        "generation": {
            "correctness": 0.8,
            "faithfulness": 0.75,
            "correctness_by_language": {"en": 0.7, "vi": 0.9},
            "faithfulness_by_language": {"en": 0.6, "vi": 0.9},
        },
    }


@pytest.fixture
def dataset_file(tmp_path):
    """A dataset file whose name is NOT dataset.json, to catch a hardcoded path."""
    path = tmp_path / "other.json"
    path.write_text(json.dumps([]))
    return str(path)


def test_logs_config_and_case_count_as_params(report, dataset_file):
    """All 9 params are logged; MLflow reads params back as strings."""
    run = mlflow.get_run(log_evaluation(report, "# md", dataset_file))

    params = run.data.params
    assert len(params) == 9
    assert params["n_cases"] == "20"
    assert params["chunk_size"] == str(config.CHUNK_SIZE)
    assert params["embedding_model"] == config.EMBEDDING_MODEL


def test_logs_overall_and_per_language_metrics(report, dataset_file):
    """4 overall + 8 per-language metrics are logged with the values from the right dicts."""
    run = mlflow.get_run(log_evaluation(report, "# md", dataset_file))

    metrics = run.data.metrics
    assert len(metrics) == 12
    assert metrics["recall_at_k"] == 0.95
    assert metrics["recall_at_k_vi"] == 0.9
    assert metrics["faithfulness_en"] == 0.6
    assert metrics["mrr_vi"] == 0.85


def test_logs_report_and_the_dataset_that_was_passed(report, dataset_file):
    """Both artifacts land in the returned run, and the dataset keeps the name of the file passed in."""
    run_id = log_evaluation(report, "# md", dataset_file)

    names = {a.path for a in mlflow.MlflowClient().list_artifacts(run_id)}
    assert names == {"report.md", "qa_prompt.txt", "other.json"}


def test_logs_a_hash_of_the_qa_prompt_and_its_text(report, dataset_file, monkeypatch):
    """Runs can be compared by prompt: the hash changes with the prompt and the full text is an artifact."""
    first = mlflow.get_run(log_evaluation(report, "# md", dataset_file))
    monkeypatch.setattr("src.tracking.QA_SYSTEM_PROMPT", "a different prompt")
    second_id = log_evaluation(report, "# md", dataset_file)
    second = mlflow.get_run(second_id)

    assert first.data.params["qa_prompt_hash"] != second.data.params["qa_prompt_hash"]
    assert mlflow.artifacts.load_text(f"runs:/{second_id}/qa_prompt.txt") == "a different prompt"
