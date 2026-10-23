"""Compare two evaluation runs question by question.

Usage:
    python -m eval.compare before.json after.json [--out comparison.md]

Both files come from `python -m eval.evaluate --per-case-json`. The questions are paired by id, so the comparison
only counts a question that both runs answered. For every metric it shows the mean in each run, the difference, a 95%
interval for that difference (paired bootstrap) and how many questions got better or worse. When the interval
contains 0 the two runs cannot be told apart on this many questions.
"""

import argparse
import json
import random
import sys
from typing import Dict, List, Optional, Tuple

METRICS = ("correctness", "faithfulness", "recall_at_k", "mrr")
RESAMPLES = 2000


def load_run(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        run = json.load(f)
    return {**run, "cases": {c["id"]: c for c in run["cases"]}}


def metric_value(case: dict, metric: str) -> Optional[float]:
    """The case's value for `metric`, or None when the case has no such metric (e.g. no retrieval for out_of_doc)."""
    if metric == "correctness":
        return 1.0 if case["correct"] else 0.0
    if metric == "faithfulness":
        return 1.0 if case["faithful"] else 0.0
    if case["hit"] is None:
        return None
    if metric == "recall_at_k":
        return 1.0 if case["hit"] else 0.0
    return 1 / case["rank"] if case["rank"] else 0.0


def paired_values(before: dict, after: dict, metric: str) -> List[Tuple[float, float]]:
    """(before, after) for every question that is in both runs and has the metric in both."""
    pairs = []
    for case_id in sorted(before["cases"].keys() & after["cases"].keys()):
        a = metric_value(before["cases"][case_id], metric)
        b = metric_value(after["cases"][case_id], metric)
        if a is not None and b is not None:
            pairs.append((a, b))
    return pairs


def bootstrap_interval(diffs: List[float], resamples: int = RESAMPLES, seed: int = 0) -> Tuple[float, float]:
    """95% interval of the mean of `diffs`: resample the questions with replacement and look at the middle 95%."""
    rng = random.Random(seed)
    means = sorted(sum(rng.choices(diffs, k=len(diffs))) / len(diffs) for _ in range(resamples))
    return means[int(0.025 * resamples)], means[int(0.975 * resamples) - 1]


def compare_runs(before: dict, after: dict) -> Dict[str, dict]:
    """For every metric in METRICS that has pairs: n, before, after, diff, low, high, better, worse, verdict."""
    results = {}
    for metric in METRICS:
        pairs = paired_values(before, after, metric)
        if not pairs:
            continue
        diffs = [b - a for a, b in pairs]
        low, high = bootstrap_interval(diffs)
        results[metric] = {
            "n": len(pairs),
            "before": sum(a for a, _ in pairs) / len(pairs),
            "after": sum(b for _, b in pairs) / len(pairs),
            "diff": sum(diffs) / len(diffs),
            "low": low,
            "high": high,
            "better": sum(d > 0 for d in diffs),
            "worse": sum(d < 0 for d in diffs),
            "verdict": "better" if low > 0 else "worse" if high < 0 else "no clear difference",
        }
    return results


def warnings(before: dict, after: dict) -> List[str]:
    """Reasons why the two runs may not be comparable."""
    found = []
    for key in ("judge_model", "split"):
        if before.get(key) != after.get(key):
            found.append(f"The runs differ in {key}: {before.get(key)} vs {after.get(key)}.")
    only = before["cases"].keys() ^ after["cases"].keys()
    if only:
        found.append(f"{len(only)} questions are in only one of the runs and were left out.")
    return found


def render(results: Dict[str, dict], notes: List[str]) -> str:
    lines = [
        "# Comparison of two evaluation runs",
        "",
        *[f"> {note}" for note in notes],
        *([""] if notes else []),
        "| Metric | Questions | Before | After | Change | 95% interval | Better | Worse | Verdict |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for metric, r in results.items():
        lines.append(
            f"| {metric} | {r['n']} | {r['before']:.3f} | {r['after']:.3f} | {r['diff']:+.3f} "
            f"| [{r['low']:+.3f}, {r['high']:+.3f}] | {r['better']} | {r['worse']} | {r['verdict']} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Compare two runs of eval.evaluate --per-case-json.")
    parser.add_argument("before", help="Per-case JSON of the run to compare against (the baseline).")
    parser.add_argument("after", help="Per-case JSON of the new run.")
    parser.add_argument("--out", help="Also write the comparison to this Markdown file.")
    args = parser.parse_args(argv)

    before, after = load_run(args.before), load_run(args.after)
    rendered = render(compare_runs(before, after), warnings(before, after))
    print(rendered)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(rendered)


if __name__ == "__main__":
    main(sys.argv[1:])
