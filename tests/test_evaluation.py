"""Tests for src/evaluation.py with fake pipeline and judges: no Ollama, no models."""

import json

import pytest

from src.evaluation import evaluate_generation, run_evaluation


class Reply:
    def __init__(self, content):
        self.content = content


class FakeLLM:
    """Records every prompt it receives and always answers `reply`."""

    def __init__(self, reply, model="fake"):
        self.reply = reply
        self.model = model
        self.calls = 0

    def invoke(self, messages):
        self.calls += 1
        return Reply(self.reply)


class FakePipeline:
    def __init__(self, llm):
        self.llm = llm
        self._retriever = type("R", (), {"invoke": staticmethod(lambda q: [])})()

    def _rerank(self, question, docs):
        return []

    def _format_docs(self, docs):
        return ""

    def chat(self, question, history):
        yield {"context": []}
        yield {"answer": "some answer"}


CASE = {
    "question": "q",
    "language": "en",
    "expected_answer": "a",
    "expected_source": "s",
    "expected_page": 0,
    "expected_chunk_index": 0,
}


@pytest.fixture
def dataset_path(tmp_path):
    path = tmp_path / "cases.json"
    path.write_text(json.dumps([CASE]))
    return str(path)


def test_a_separate_judge_grades_instead_of_the_pipeline_llm():
    answering, judge = FakeLLM("no", "answering"), FakeLLM("yes", "judge")

    result = evaluate_generation(FakePipeline(answering), [CASE], judge)

    assert (judge.calls, answering.calls) == (2, 0)
    assert result["correctness"] == 1.0 and result["faithfulness"] == 1.0


def test_the_pipeline_llm_judges_when_no_judge_is_given():
    answering = FakeLLM("yes", "answering")

    evaluate_generation(FakePipeline(answering), [CASE])

    assert answering.calls == 2


def test_the_report_names_the_judge_model(dataset_path):
    pipeline = FakePipeline(FakeLLM("yes", "answering"))

    assert run_evaluation(pipeline, dataset_path)["judge_model"] == "answering"
    assert run_evaluation(pipeline, dataset_path, FakeLLM("yes", "judge"))["judge_model"] == "judge"
