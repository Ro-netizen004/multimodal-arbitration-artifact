#!/usr/bin/env python3
"""Paired chart-versus-table comparison of ChartQA CLL asymmetry."""

import argparse
import json
from pathlib import Path

import numpy as np
from scipy import stats


DEFAULT_MODELS = [
    "Qwen2-VL-2B-Instruct",
    "Qwen2.5-VL-7B-Instruct",
    "Idefics3-8B-Llama3",
    "llava-onevision-qwen2-7b-ov-hf",
    "llava-v1.6-mistral-7b-hf",
    "Phi-3.5-vision-instruct",
]


def load_margin(path: Path) -> dict[int, float]:
    rows = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            value = (row.get("margin") or {}).get("margin_mean")
            if value is not None:
                rows[int(row["i"])] = float(value)
    return rows


def item_asymmetry(root: Path, model: str) -> dict[int, float]:
    image_l0 = load_margin(root / "image" / model / "level_0_clean.cll.jsonl")
    image_l5 = load_margin(
        root / "image" / model / "level_5_heavy_degradation.cll.jsonl"
    )
    text_l0 = load_margin(root / "text" / model / "level_0_clean.cll.jsonl")
    text_l5 = load_margin(
        root / "text" / model / "level_5_heavy_corruption.cll.jsonl"
    )
    ids = image_l0.keys() & image_l5.keys() & text_l0.keys() & text_l5.keys()
    return {
        item: (text_l0[item] - text_l5[item]) - (image_l5[item] - image_l0[item])
        for item in ids
    }


def paired_stats(values, seed, resamples):
    values = np.asarray(values, dtype=float)
    observed = float(np.median(values))
    rng = np.random.default_rng(seed)
    boot = np.empty(resamples)
    extreme = 0
    for start in range(0, resamples, 1000):
        size = min(1000, resamples - start)
        indices = rng.integers(0, len(values), size=(size, len(values)))
        boot[start:start + size] = np.median(values[indices], axis=1)
        signs = rng.choice((-1.0, 1.0), size=(size, len(values)))
        permuted = np.abs(np.median(signs * values, axis=1))
        extreme += int(np.count_nonzero(permuted >= abs(observed)))
    lo, hi = np.quantile(boot, (0.025, 0.975))
    try:
        wilcoxon = float(stats.wilcoxon(values, zero_method="wilcox").pvalue)
    except ValueError:
        wilcoxon = 1.0
    permutation = (extreme + 1) / (resamples + 1)
    return observed, float(lo), float(hi), wilcoxon, permutation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chart-root", type=Path, required=True)
    parser.add_argument("--table-root", type=Path, required=True)
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    parser.add_argument("--resamples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260731)
    args = parser.parse_args()

    print(
        "model\tn\tA_chart\tA_table\ttable-minus-chart\t95% CI\t"
        "Wilcoxon p\tpermutation p"
    )
    for model_index, model in enumerate(args.models):
        chart = item_asymmetry(args.chart_root, model)
        table = item_asymmetry(args.table_root, model)
        ids = sorted(chart.keys() & table.keys())
        chart_values = np.asarray([chart[item] for item in ids])
        table_values = np.asarray([table[item] for item in ids])
        delta = table_values - chart_values
        estimate, lo, hi, p_w, p_perm = paired_stats(
            delta, args.seed + model_index, args.resamples
        )
        print(
            f"{model}\t{len(ids)}\t{np.median(chart_values):+.4f}\t"
            f"{np.median(table_values):+.4f}\t{estimate:+.4f}\t"
            f"[{lo:+.4f},{hi:+.4f}]\t{p_w:.3g}\t{p_perm:.3g}"
        )


if __name__ == "__main__":
    main()
