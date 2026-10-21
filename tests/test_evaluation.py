"""Tests for src/evaluation.py with fake pipeline and judges: no Ollama, no models."""

import json
import sys

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from src import config
from src.evaluation import (
    _judge_yes,
    evaluate_generation,
    evaluate_retrieval,
    load_dataset,
    make_judge,
    missing_evidence,
    per_case_results,
    run_evaluation,
)
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


class Doc:
    def __init__(self, text):
        self.page_content = text


class FakeRetriever:
    def __init__(self, pipeline):
        self.pipeline = pipeline

    def invoke(self, question):
        self.pipeline.searched_for.append(question)
        return self.pipeline.docs


class FakePipeline:
    """Retrieves the same `chunks` for every question and answers "some answer"."""

    def __init__(self, llm, chunks=()):
        self.llm = llm
        self.docs = [Doc(t) for t in chunks]
        self.searched_for = []
        self.histories = []
        self._retriever = FakeRetriever(self)

    def _contextualize_fn(self, inputs):
        return f"standalone: {inputs['input']}" if inputs["chat_history"] else inputs["input"]

    def _rerank(self, question, docs):
        return docs

    def _format_docs(self, docs):
        return "\n\n".join(d.page_content for d in docs)

    def chat(self, question, history):
        self.histories.append(history)
        yield {"context": self.docs}
        yield {"answer": "some answer"}


CASE = {
    "id": "c1",
    "type": "factoid",
    "language": "en",
    "split": "dev",
    "question": "q",
    "history": [],
    "expected_answer": "a",
    "evidence": ["the evidence"],
}


def make_case(**changes):
    return {**CASE, **changes}


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


def test_load_dataset_keeps_only_the_requested_split(tmp_path):
    path = tmp_path / "cases.json"
    path.write_text(json.dumps([make_case(id="a", split="dev"), make_case(id="b", split="test")]))

    assert [c["id"] for c in load_dataset(str(path), "dev")] == ["a"]
    assert [c["id"] for c in load_dataset(str(path), "test")] == ["b"]
    assert [c["id"] for c in load_dataset(str(path), "all")] == ["a", "b"]


def test_missing_evidence_names_the_snippets_that_are_in_no_chunk():
    dataset = [make_case(id="a", evidence=["found"]), make_case(id="b", evidence=["lost"])]

    assert missing_evidence(dataset, ["some text that was found here"]) == ["b: lost"]


def test_evidence_matches_across_line_breaks_and_pdf_hyphens():
    dataset = [make_case(evidence=["Pre-trained models learn", "a split sentence"])]

    assert missing_evidence(dataset, ["Pre\u2010trained models\nlearn from a split\n sentence"]) == []


def test_retrieval_is_a_hit_only_when_every_evidence_snippet_is_retrieved():
    case = make_case(evidence=["first fact", "second fact"])

    partial = evaluate_retrieval(FakePipeline(FakeLLM("x"), ["the first fact"]), [case])["per_case"][0]
    full = evaluate_retrieval(FakePipeline(FakeLLM("x"), ["the first fact", "the second fact"]), [case])["per_case"][0]

    assert (partial["hit"], partial["rank"]) == (False, 1)
    assert (full["hit"], full["rank"]) == (True, 1)


def test_retrieval_rank_is_the_best_chunk_that_holds_the_evidence():
    result = evaluate_retrieval(FakePipeline(FakeLLM("x"), ["noise", "noise", "the evidence"]), [CASE])

    assert result["per_case"][0]["rank"] == 3
    assert result["mrr"] == pytest.approx(1 / 3)


def test_retrieval_skips_questions_without_evidence():
    result = evaluate_retrieval(FakePipeline(FakeLLM("x"), ["anything"]), [make_case(type="out_of_doc", evidence=[])])

    assert result["per_case"] == []


def test_retrieval_searches_with_the_standalone_version_of_a_follow_up():
    pipeline = FakePipeline(FakeLLM("x"), ["the evidence"])
    follow_up = make_case(history=[["human", "first"], ["ai", "reply"]], question="and then?")

    evaluate_retrieval(pipeline, [follow_up])

    assert pipeline.searched_for == ["standalone: and then?"]


def test_the_history_reaches_the_pipeline_as_chat_messages():
    pipeline = FakePipeline(FakeLLM("yes"))
    follow_up = make_case(history=[["human", "first"], ["ai", "reply"]])

    evaluate_generation(pipeline, [follow_up])

    assert pipeline.histories == [[HumanMessage("first"), AIMessage("reply")]]


def test_every_generation_result_names_its_case_and_how_long_the_answer_took():
    result = evaluate_generation(FakePipeline(FakeLLM("yes")), [CASE])["per_case"][0]

    assert (result["id"], result["type"], result["split"]) == ("c1", "factoid", "dev")
    assert result["seconds"] >= 0


def test_metrics_are_broken_down_by_language_type_and_split():
    cases = [
        make_case(id="a", type="factoid", language="en", split="dev"),
        make_case(id="b", type="hard", language="vi", split="test"),
    ]
    pipeline = FakePipeline(FakeLLM("yes"), ["the evidence"])

    retrieval, generation = evaluate_retrieval(pipeline, cases), evaluate_generation(pipeline, cases)

    assert set(retrieval["recall_at_k_by_type"]) == {"factoid", "hard"}
    assert set(retrieval["mrr_by_split"]) == {"dev", "test"}
    assert set(generation["correctness_by_language"]) == {"en", "vi"}
    assert set(generation["faithfulness_by_type"]) == {"factoid", "hard"}


def test_per_case_results_put_retrieval_and_generation_side_by_side():
    cases = [make_case(id="a"), make_case(id="b", type="out_of_doc", evidence=[])]
    report = {
        "retrieval": evaluate_retrieval(FakePipeline(FakeLLM("yes"), ["the evidence"]), cases),
        "generation": evaluate_generation(FakePipeline(FakeLLM("yes"), ["the evidence"]), cases),
    }

    results = {r["id"]: r for r in per_case_results(report)}

    assert (results["a"]["hit"], results["a"]["rank"]) == (True, 1)
    assert (results["b"]["hit"], results["b"]["rank"]) == (None, None)
    assert results["b"]["correct"] is True


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
