#!/usr/bin/env python3
"""Compare generated source choice with the sign of the CLL margin.

The expected result layout is:

    ROOT/<benchmark>/{image_degradation,text_degradation}/<model>/*.cll.jsonl

Only trials whose generated answer is attributable to exactly one source
(``follows`` is ``image`` or ``text``) and whose finite margin is nonzero enter
the analysis. The combined summary counts the shared clean L0 context once
rather than once per degradation arm.
"""

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np


ARMS = ("image_degradation", "text_degradation")


def wilson_interval(successes, total, z=1.959963984540054):
    if total == 0:
        return float("nan"), float("nan")
    proportion = successes / total
    denominator = 1 + z * z / total
    center = (proportion + z * z / (2 * total)) / denominator
    radius = (
        z
        * math.sqrt(
            proportion * (1 - proportion) / total
            + z * z / (4 * total * total)
        )
        / denominator
    )
    return center - radius, center + radius


def iter_rows(root):
    for benchmark_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        benchmark = benchmark_dir.name
        for arm in ARMS:
            arm_dir = benchmark_dir / arm
            if not arm_dir.is_dir():
                continue
            for model_dir in sorted(path for path in arm_dir.iterdir() if path.is_dir()):
                model = model_dir.name
                for path in sorted(model_dir.glob("level_*.cll.jsonl")):
                    with path.open(encoding="utf-8") as handle:
                        for line in handle:
                            row = json.loads(line)
                            follows = row.get("follows")
                            margin = (row.get("margin") or {}).get("margin_mean")
                            if follows not in {"image", "text"}:
                                continue
                            if margin is None or not math.isfinite(float(margin)):
                                continue
                            margin = float(margin)
                            if margin == 0:
                                continue
                            level = int(row["level"])
                            item = int(row["i"])
                            predicted = "text" if margin > 0 else "image"
                            yield {
                                "benchmark": benchmark,
                                "arm": arm,
                                "model": model,
                                "level": level,
                                "item": item,
                                "agree": predicted == follows,
                            }


def summarize(rows):
    successes = sum(row["agree"] for row in rows)
    total = len(rows)
    lo, hi = wilson_interval(successes, total)
    return successes, total, successes / total if total else float("nan"), lo, hi


def print_row(scope, rows):
    successes, total, agreement, lo, hi = summarize(rows)
    print(
        f"{scope}\t{successes}\t{total}\t{agreement:.4f}\t"
        f"[{lo:.4f},{hi:.4f}]"
    )


def clustered_bootstrap_interval(rows, resamples, seed):
    """Bootstrap benchmark items, retaining all model/level observations."""
    grouped = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for row in rows:
        cell = grouped[row["benchmark"]][row["item"]]
        cell[0] += int(row["agree"])
        cell[1] += 1

    rng = np.random.default_rng(seed)
    estimates = np.empty(resamples, dtype=float)
    for replicate in range(resamples):
        successes = 0
        total = 0
        for benchmark in sorted(grouped):
            clusters = np.asarray(list(grouped[benchmark].values()), dtype=int)
            sampled = clusters[rng.integers(0, len(clusters), size=len(clusters))]
            successes += int(sampled[:, 0].sum())
            total += int(sampled[:, 1].sum())
        estimates[replicate] = successes / total
    return tuple(np.quantile(estimates, (0.025, 0.975)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("results/main_arithmetic"),
        help="Root containing benchmark/arm/model CLL result trees.",
    )
    parser.add_argument("--resamples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260721)
    args = parser.parse_args()

    rows = list(iter_rows(args.root))
    if not rows:
        raise SystemExit(f"No attributable CLL rows found under {args.root}")

    print("scope\tagree\tn\trate\tWilson 95% CI")

    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["benchmark"], row["model"], row["arm"])].append(row)
    for key in sorted(grouped):
        print_row("/".join(key), grouped[key])

    models = sorted({row["model"] for row in rows})
    for model in models:
        for arm in ARMS:
            print_row(
                f"MODEL_POOLED/{model}/{arm}",
                [
                    row for row in rows
                    if row["model"] == model and row["arm"] == arm
                ],
            )

    for arm in ARMS:
        print_row(f"POOLED/{arm}", [row for row in rows if row["arm"] == arm])

    # Both arms share the exact same clean context. Count each model-item L0
    # observation once, but retain every degraded observation because the
    # degraded source and stimulus differ by arm.
    unique = {}
    shared_l0_disagreements = 0
    for row in rows:
        if row["level"] == 0:
            key = (row["benchmark"], row["model"], 0, row["item"])
        else:
            key = (
                row["benchmark"],
                row["model"],
                row["arm"],
                row["level"],
                row["item"],
            )
        previous = unique.get(key)
        if row["level"] == 0 and previous is not None:
            if previous["agree"] != row["agree"]:
                shared_l0_disagreements += 1
            # Use the image-arm L0 record as the canonical copy. Although the
            # prompt and stimulus are shared, separately generated answer rows
            # can occasionally differ between runs.
            if previous["arm"] == "image_degradation":
                continue
        unique[key] = row
    print_row("POOLED/both_arms_L0_deduplicated", list(unique.values()))
    for label, selected in (
        ("image_degradation", [row for row in rows
                               if row["arm"] == "image_degradation"]),
        ("text_degradation", [row for row in rows
                              if row["arm"] == "text_degradation"]),
        ("both_arms_L0_deduplicated", list(unique.values())),
    ):
        lo, hi = clustered_bootstrap_interval(
            selected, args.resamples, args.seed
        )
        print(
            f"CLUSTER_BOOTSTRAP/{label}\tNA\tNA\tNA\t"
            f"[{lo:.4f},{hi:.4f}]"
        )
    print(
        "NOTE/shared_L0_generation_disagreements"
        f"\t{shared_l0_disagreements}\tNA\tNA\tNA"
    )


if __name__ == "__main__":
    main()
