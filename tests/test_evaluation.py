"""Tests for src/evaluation.py with fake pipeline and judges: no Ollama, no models."""

import json
import sys

import pytest

from src import config
from src.evaluation import _judge_yes, evaluate_generation, make_judge, run_evaluation
from src.prompts import FAITHFULNESS_JUDGE_PROMPT, FAITHFULNESS_SYSTEM_PROMPT


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


@pytest.mark.parametrize("reply", ["yes", "Yes.", "**Yes**", "- yes", '"yes"', "\n yes, it is"])
def test_a_yes_is_recognised_even_with_leading_markdown(reply):
    """Judges often wrap the verdict in markdown or punctuation."""
    assert _judge_yes(FakeLLM(reply), FAITHFULNESS_JUDGE_PROMPT, context="c", answer="a")


@pytest.mark.parametrize("reply", ["no", "**No**", "Based on the context", "", "not yes"])
def test_anything_that_does_not_start_with_yes_counts_as_no(reply):
    """Stripping the prefix must not turn a 'no' or an unclear reply into a 'yes'."""
    assert not _judge_yes(FakeLLM(reply), FAITHFULNESS_JUDGE_PROMPT, context="c", answer="a")


def test_make_judge_builds_a_deterministic_non_thinking_model(monkeypatch):
    """A thinking model would spend its token budget before answering; temperature 0 keeps runs repeatable."""

    class FakeChatOllama:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    fake_module = type(sys)("langchain_ollama")
    fake_module.ChatOllama = FakeChatOllama
    monkeypatch.setitem(sys.modules, "langchain_ollama", fake_module)

    judge = make_judge("some-model")

    assert judge.kwargs["model"] == "some-model"
    assert judge.kwargs["temperature"] == 0
    assert judge.kwargs["reasoning"] is False


@pytest.mark.parametrize("base_url, expected", [("", {}), ("http://host:11434", {"base_url": "http://host:11434"})])
def test_make_judge_passes_base_url_only_when_one_is_configured(monkeypatch, base_url, expected):
    """An empty base_url must not be sent, or the client would not fall back to its default server."""

    class FakeChatOllama:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    fake_module = type(sys)("langchain_ollama")
    fake_module.ChatOllama = FakeChatOllama
    monkeypatch.setitem(sys.modules, "langchain_ollama", fake_module)
    monkeypatch.setattr("src.evaluation.OLLAMA_BASE_URL", base_url)

    judge = make_judge("some-model")

    assert {k: v for k, v in judge.kwargs.items() if k == "base_url"} == expected


def test_the_judge_is_not_the_answering_model():
    """A model grading its own answers is the bias the separate judge exists to avoid."""
    assert config.JUDGE_MODEL != config.LLM_MODEL


def test_the_faithfulness_prompt_tells_the_judge_that_a_refusal_is_faithful():
    """Without this line every judge marked correct refusals as unfaithful."""
    assert "cannot be found" in FAITHFULNESS_SYSTEM_PROMPT


def test_the_faithfulness_prompt_still_ends_with_its_own_line_asking_for_yes_or_no():
    """The added sentence must end with a newline, otherwise it fuses with the last instruction."""
    assert FAITHFULNESS_SYSTEM_PROMPT.endswith('\nOutput only "yes" or "no", nothing else.')
