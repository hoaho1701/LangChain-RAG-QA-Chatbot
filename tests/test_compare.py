import json

from eval.compare import (
    bootstrap_interval,
    compare_runs,
    load_run,
    main,
    metric_value,
    paired_values,
    warnings,
)


def make_case(id="a", correct=True, faithful=True, hit=True, rank=1):
    return {"id": id, "correct": correct, "faithful": faithful, "hit": hit, "rank": rank}


def make_run(*cases, judge_model="judge", split="dev"):
    return {"judge_model": judge_model, "split": split, "cases": {c["id"]: c for c in cases}}


def test_metric_value_is_none_for_a_question_without_retrieval():
    case = make_case(hit=None, rank=None)

    assert metric_value(case, "recall_at_k") is None
    assert metric_value(case, "mrr") is None
    assert metric_value(case, "correctness") == 1.0


def test_metric_value_turns_the_rank_into_a_reciprocal_rank():
    assert metric_value(make_case(rank=4), "mrr") == 0.25
    assert metric_value(make_case(hit=False, rank=None), "mrr") == 0.0


def test_paired_values_keep_only_questions_that_are_in_both_runs_and_have_the_metric():
    before = make_run(make_case("a", correct=False), make_case("b"), make_case("c", hit=None, rank=None))
    after = make_run(make_case("a", correct=True), make_case("c", hit=None, rank=None), make_case("d"))

    assert paired_values(before, after, "correctness") == [(0.0, 1.0), (1.0, 1.0)]
    assert paired_values(before, after, "recall_at_k") == [(1.0, 1.0)]


def test_bootstrap_interval_is_repeatable_and_contains_the_mean():
    diffs = [1.0, 0.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0]

    low, high = bootstrap_interval(diffs)

    assert (low, high) == bootstrap_interval(diffs)
    assert low <= sum(diffs) / len(diffs) <= high


def test_no_change_gives_an_interval_of_zero_and_no_clear_difference():
    run = make_run(make_case("a"), make_case("b", correct=False))

    result = compare_runs(run, run)["correctness"]

    assert (result["diff"], result["low"], result["high"]) == (0.0, 0.0, 0.0)
    assert result["verdict"] == "no clear difference"


def test_a_clear_gain_is_called_better_and_counts_the_questions_that_changed():
    before = make_run(*[make_case(str(i), correct=False) for i in range(30)])
    after = make_run(*[make_case(str(i), correct=True) for i in range(30)])

    result = compare_runs(before, after)["correctness"]

    assert result["verdict"] == "better"
    assert (result["better"], result["worse"]) == (30, 0)
    assert result["low"] > 0


def test_a_small_mixed_change_is_not_called_better():
    before = make_run(make_case("a", correct=False), make_case("b"), make_case("c"), make_case("d"))
    after = make_run(make_case("a"), make_case("b", correct=False), make_case("c"), make_case("d"))

    result = compare_runs(before, after)["correctness"]

    assert (result["better"], result["worse"]) == (1, 1)
    assert result["verdict"] == "no clear difference"


def test_warnings_name_a_different_judge_split_or_question_set():
    before = make_run(make_case("a"), make_case("b"), judge_model="gemma4:12b", split="dev")
    after = make_run(make_case("a"), judge_model="phi4:14b", split="test")

    found = warnings(before, after)

    assert any("judge_model" in w for w in found)
    assert any("split" in w for w in found)
    assert any("1 questions" in w for w in found)


def test_main_reads_two_files_and_writes_the_comparison(tmp_path):
    def write(name, correct):
        path = tmp_path / name
        cases = [make_case(str(i), correct=correct) for i in range(10)]
        path.write_text(json.dumps({"judge_model": "j", "split": "dev", "cases": cases}))
        return str(path)

    out = tmp_path / "out.md"

    main([write("a.json", False), write("b.json", True), "--out", str(out)])

    text = out.read_text()
    assert "| correctness | 10 |" in text
    assert "better" in text
    assert load_run(write("c.json", True))["cases"]["0"]["correct"] is True
