#!/usr/bin/env python3
"""Paired behavioral endpoint analysis for frontier GSM8K results."""

import argparse
import csv
from pathlib import Path

import numpy as np
from scipy import stats


FILES = {
    "image_l0": Path("role_neutral") / "{model}" / "level_0_clean.csv",
    "image_l5": Path("role_neutral") / "{model}" / "level_5_heavy_degradation.csv",
    "text_l0": Path("text_legibility") / "role_neutral" / "{model}" / "level_0_clean.csv",
    "text_l5": Path("text_legibility") / "role_neutral" / "{model}" / "level_5_heavy_corruption.csv",
}


def load(path):
    values = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            follows = row.get("follows")
            if follows in {"image", "text"}:
                values[int(row["problem_id"])] = 1.0 if follows == "text" else 0.0
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--model", default="GPT-5.6-Luna")
    parser.add_argument("--resamples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260721)
    args = parser.parse_args()

    values = {
        name: load(args.root / Path(str(relative).format(model=args.model)))
        for name, relative in FILES.items()
    }
    ids = sorted(set.intersection(*(set(item) for item in values.values())))
    r_image = np.asarray([
        values["image_l5"][item] - values["image_l0"][item] for item in ids
    ])
    r_text = np.asarray([
        values["text_l0"][item] - values["text_l5"][item] for item in ids
    ])
    contrast = r_text - r_image
    rng = np.random.default_rng(args.seed)
    observed = abs(float(np.mean(contrast)))
    indices = rng.integers(
        0, len(contrast), size=(args.resamples, len(contrast))
    )
    bootstrap = np.mean(contrast[indices], axis=1)
    signs = rng.choice((-1.0, 1.0), size=(args.resamples, len(contrast)))
    permutation_extreme = int(np.count_nonzero(
        np.abs(np.mean(signs * contrast, axis=1)) >= observed
    ))
    lo, hi = np.quantile(bootstrap, (0.025, 0.975))
    permutation_p = (permutation_extreme + 1) / (args.resamples + 1)
    wilcoxon_p = stats.wilcoxon(contrast, zero_method="wilcox").pvalue

    print("model\tn\tR_image\tR_text\tasymmetry\t95% CI\tWilcoxon p\tpermutation p")
    print(f"{args.model}\t{len(ids)}\t{np.mean(r_image):+.4f}\t"
          f"{np.mean(r_text):+.4f}\t{np.mean(contrast):+.4f}\t"
          f"[{lo:+.4f},{hi:+.4f}]\t{wilcoxon_p:.3g}\t{permutation_p:.3g}")

    preferences = {name: float(np.mean(list(item.values())))
                   for name, item in values.items()}
    print("\nchanging-denominator text preference")
    for name, preference in preferences.items():
        print(f"{name}\tn={len(values[name])}\t{preference:.4f}")
    for label, baseline in (("image_l0", preferences["image_l0"]),
                            ("text_l0", preferences["text_l0"])):
        shared_r_image = preferences["image_l5"] - baseline
        shared_r_text = baseline - preferences["text_l5"]
        print(f"shared_baseline={label}\tR_image={shared_r_image:+.4f}\t"
              f"R_text={shared_r_text:+.4f}\t"
              f"A={shared_r_text - shared_r_image:+.4f}")


if __name__ == "__main__":
    main()
