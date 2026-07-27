#!/usr/bin/env python3
"""Per-model CLL reallocation slopes calibrated by unimodal accuracy loss.

For each model and degradation arm, this analysis regresses the median CLL
shift toward the clean source on proportional unimodal accuracy loss.  The line
is constrained through the origin because both quantities are zero at L0 by
construction.  Confidence intervals for the text-minus-image slope difference
bootstrap the common matched conflict items while conditioning on the observed
unimodal accuracy losses.
"""

import argparse
import json
from pathlib import Path

import numpy as np

from cll_replication_table import DISPLAY, _load_by_id, result_dir


ROOT = Path(__file__).resolve().parent.parent
LEVELS = (0, 2, 4, 5)
LEVEL_FILE = {
    "image": {
        0: "level_0_clean.cll.jsonl",
        2: "level_2_blur_light.cll.jsonl",
        4: "level_4_blur_noise.cll.jsonl",
        5: "level_5_heavy_degradation.cll.jsonl",
    },
    "text": {
        0: "level_0_clean.cll.jsonl",
        2: "level_2_light_corruption.cll.jsonl",
        4: "level_4_medium_corruption.cll.jsonl",
        5: "level_5_heavy_corruption.cll.jsonl",
    },
}


def load_accuracy(benchmark, model):
    if benchmark == "chartqa":
        accuracy = {"image": {}, "text": {}}
        root = (
            ROOT
            / "results/phase_control/chartqa_decodability_full230_hf_v1/evidence"
        )
        for channel in ("image", "text"):
            model_dir = root / channel / model
            for level in LEVELS:
                pattern = (
                    f"level_{level}_*.decodability.jsonl"
                )
                matches = sorted(model_dir.glob(pattern))
                if len(matches) != 1:
                    raise RuntimeError(
                        f"Expected one ChartQA {channel} accuracy file for "
                        f"{model} L{level}; found {len(matches)}"
                    )
                correct = []
                with matches[0].open(encoding="utf-8") as handle:
                    for line in handle:
                        row = json.loads(line)
                        if int(row["i"]) != 45:
                            correct.append(bool(row.get("correct")))
                if not correct:
                    raise RuntimeError(
                        f"No audited ChartQA accuracy rows for {model} "
                        f"{channel} L{level}"
                    )
                accuracy[channel][level] = float(np.mean(correct))
        return accuracy

    decodability_path = (
        ROOT
        / "results/phase_control/decodability"
        / benchmark
        / "decodability_all.json"
    )
    with decodability_path.open(encoding="utf-8") as handle:
        decodability = json.load(handle)
    row = decodability[model]
    accuracy = {
        channel: {int(level): float(value) for level, value in row[channel].items()}
        for channel in ("image", "text")
    }

    # The GSM8K decodability jobs measured the text channel; the matching
    # canonical-image unimodal runs are the Phase 4 per-level results.
    if benchmark == "gsm8k" and not accuracy["image"]:
        phase4 = ROOT / "results/phase4" / model
        for level in LEVELS:
            matches = sorted(phase4.glob(f"level_{level}_*.json"))
            if len(matches) != 1:
                raise RuntimeError(
                    f"Expected one GSM8K image-accuracy file for {model} L{level}; "
                    f"found {len(matches)}"
                )
            with matches[0].open(encoding="utf-8") as handle:
                accuracy["image"][level] = float(json.load(handle)["accuracy"])

    for channel in ("image", "text"):
        missing = sorted(set(LEVELS) - set(accuracy[channel]))
        if missing:
            raise RuntimeError(
                f"Missing {benchmark} {channel} accuracies for {model}: {missing}"
            )
        if accuracy[channel][0] <= 0:
            raise RuntimeError(
                f"Cannot normalize zero L0 accuracy for {benchmark} {model} {channel}"
            )
    return accuracy


def accuracy_losses(accuracy, channel):
    baseline = accuracy[channel][0]
    return np.asarray(
        [(baseline - accuracy[channel][level]) / baseline for level in LEVELS[1:]],
        dtype=float,
    )


def load_common_changes(benchmark, model):
    margins = {}
    common_ids = None
    for channel in ("image", "text"):
        model_dir = (
            ROOT
            / "results/phase_control/chartqa_conflict_full230_hf_v1/evidence"
            / channel
            / model
            if benchmark == "chartqa"
            else result_dir(model, benchmark, channel, "neutral")
        )
        margins[channel] = {}
        for level in LEVELS:
            rows = _load_by_id(model_dir / LEVEL_FILE[channel][level])
            if not rows:
                raise RuntimeError(
                    f"No neutral CLL rows for {benchmark} {model} {channel} L{level}"
                )
            margins[channel][level] = rows
            ids = set(rows)
            if benchmark == "chartqa":
                ids.discard(45)
            common_ids = ids if common_ids is None else common_ids & ids

    ids = sorted(common_ids or ())
    if not ids:
        raise RuntimeError(f"No common matched CLL items for {benchmark} {model}")

    changes = {}
    for channel in ("image", "text"):
        baseline = margins[channel][0]
        per_level = []
        for level in LEVELS[1:]:
            raw = np.asarray(
                [margins[channel][level][item] - baseline[item] for item in ids],
                dtype=float,
            )
            # Image degradation: positive raw change is toward clean text.
            # Text degradation: negative raw change is toward the clean image.
            per_level.append(raw if channel == "image" else -raw)
        changes[channel] = np.stack(per_level)
    return ids, changes


def origin_slope(x, y):
    denominator = float(np.dot(x, x))
    if denominator <= 0:
        raise RuntimeError("All measured accuracy losses are zero.")
    return float(np.dot(x, y) / denominator)


def analyze_model(benchmark, model, resamples, seed, min_l0_accuracy):
    accuracy = load_accuracy(benchmark, model)
    low_headroom = {
        channel: accuracy[channel][0]
        for channel in ("image", "text")
        if accuracy[channel][0] < min_l0_accuracy
    }
    if low_headroom:
        return {
            "status": "excluded_low_l0_accuracy",
            "minimum_l0_accuracy": min_l0_accuracy,
            "accuracy": accuracy,
            "excluded_channels": low_headroom,
        }
    losses = {
        channel: accuracy_losses(accuracy, channel)
        for channel in ("image", "text")
    }
    ids, changes = load_common_changes(benchmark, model)
    medians = {
        channel: np.median(changes[channel], axis=1)
        for channel in ("image", "text")
    }
    slopes = {
        channel: origin_slope(losses[channel], medians[channel])
        for channel in ("image", "text")
    }
    difference = slopes["text"] - slopes["image"]

    rng = np.random.default_rng(seed)
    bootstrap = np.empty(resamples, dtype=float)
    batch_size = 250
    n = len(ids)
    for start in range(0, resamples, batch_size):
        size = min(batch_size, resamples - start)
        indices = rng.integers(0, n, size=(size, n))
        sampled_medians = {
            channel: np.stack(
                [
                    np.median(changes[channel][level][indices], axis=1)
                    for level in range(len(LEVELS) - 1)
                ],
                axis=1,
            )
            for channel in ("image", "text")
        }
        sampled_slopes = {}
        for channel in ("image", "text"):
            x = losses[channel]
            sampled_slopes[channel] = sampled_medians[channel] @ x / np.dot(x, x)
        bootstrap[start : start + size] = (
            sampled_slopes["text"] - sampled_slopes["image"]
        )
    lo, hi = np.quantile(bootstrap, (0.025, 0.975))
    return {
        "n": n,
        "accuracy": accuracy,
        "loss": {channel: losses[channel].tolist() for channel in losses},
        "median_shift": {channel: medians[channel].tolist() for channel in medians},
        "image_slope": slopes["image"],
        "text_slope": slopes["text"],
        "difference": difference,
        "bootstrap_ci": [float(lo), float(hi)],
        "bootstrap_resamples": resamples,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--benchmark",
        choices=("gsm8k", "svamp", "chartqa", "all"),
        default="all",
    )
    parser.add_argument("--resamples", type=int, default=10_000)
    parser.add_argument(
        "--min-l0-accuracy",
        type=float,
        default=0.10,
        help="Exclude a model if either unimodal L0 accuracy is below this floor.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results/phase_control/calibrated_slopes.json",
    )
    args = parser.parse_args()
    benchmarks = (
        ("gsm8k", "svamp", "chartqa")
        if args.benchmark == "all"
        else (args.benchmark,)
    )

    results = {}
    print("benchmark\tmodel\tn\tb_image\tb_text\tdifference\t95% CI")
    for benchmark_index, benchmark in enumerate(benchmarks):
        results[benchmark] = {}
        for model_index, model in enumerate(DISPLAY):
            result = analyze_model(
                benchmark,
                model,
                args.resamples,
                seed=20260726 + 100 * benchmark_index + model_index,
                min_l0_accuracy=args.min_l0_accuracy,
            )
            results[benchmark][model] = result
            if result.get("status") == "excluded_low_l0_accuracy":
                excluded = ", ".join(
                    f"{channel}={value:.4f}"
                    for channel, value in result["excluded_channels"].items()
                )
                print(
                    f"{benchmark}\t{DISPLAY[model]}\tEXCLUDED "
                    f"(L0 accuracy below {args.min_l0_accuracy:.2f}: {excluded})"
                )
                continue
            lo, hi = result["bootstrap_ci"]
            print(
                f"{benchmark}\t{DISPLAY[model]}\t{result['n']}\t"
                f"{result['image_slope']:+.4f}\t{result['text_slope']:+.4f}\t"
                f"{result['difference']:+.4f}\t[{lo:+.4f},{hi:+.4f}]"
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
    print(f"\nSaved {args.output}")


if __name__ == "__main__":
    main()
