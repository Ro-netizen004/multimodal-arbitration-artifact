#!/usr/bin/env python3
"""Plot the primary paired asymmetry contrasts across all three settings."""

import argparse
import csv
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analyze_chartqa_conflict import changes as chartqa_changes
from analyze_chartqa_conflict import paired_stats as chartqa_paired_stats
from cll_replication_table import paired_differences_by_id, paired_stats


ROOT = Path(__file__).resolve().parents[1]
MODELS = [
    ("Qwen2-VL-2B-Instruct", "Qwen2-VL-2B"),
    ("Qwen2.5-VL-7B-Instruct", "Qwen2.5-VL-7B"),
    ("Idefics3-8B-Llama3", "Idefics3-8B"),
    ("llava-onevision-qwen2-7b-ov-hf", "LLaVA-OneVision-7B"),
    ("llava-v1.6-mistral-7b-hf", "LLaVA-1.6-7B"),
    ("Phi-3.5-vision-instruct", "Phi-3.5-Vision"),
]
SETTINGS = [
    ("GSM8K", "#0072B2", "o", 0.22),
    ("SVAMP", "#E69F00", "s", 0.00),
    ("ChartQA-Conflict", "#009E73", "D", -0.22),
]


def arithmetic_row(benchmark: str, model: str, resamples: int) -> dict:
    image = paired_differences_by_id(model, benchmark, "image", "neutral")
    text = paired_differences_by_id(model, benchmark, "text", "neutral")
    ids = sorted(image.keys() & text.keys())
    contrast = np.asarray([-text[item] - image[item] for item in ids], dtype=float)
    result = paired_stats(contrast, seed=20260721, n_resamples=resamples)
    lo, hi = result["bootstrap_ci"]
    return {
        "setting": "GSM8K" if benchmark == "gsm8k" else "SVAMP",
        "model": model,
        "n": result["n"],
        "asymmetry": result["median_paired_change"],
        "ci_low": lo,
        "ci_high": hi,
    }


def chartqa_row(model: str, model_index: int, resamples: int) -> dict:
    root = ROOT / "results" / "main_chartqa_conflict"
    image = chartqa_changes(root, model, "image", "cll")
    text = chartqa_changes(root, model, "text", "cll")
    ids = sorted((image.keys() & text.keys()) - {45})
    contrast = np.asarray([-text[item] - image[item] for item in ids], dtype=float)
    estimate, lo, hi, _, _ = chartqa_paired_stats(
        contrast,
        seed=20260721 + model_index,
        resamples=resamples,
        statistic="median",
    )
    return {
        "setting": "ChartQA-Conflict",
        "model": model,
        "n": len(ids),
        "asymmetry": estimate,
        "ci_low": lo,
        "ci_high": hi,
    }


def collect_rows(resamples: int) -> list[dict]:
    rows = []
    for model_index, (model, _) in enumerate(MODELS):
        rows.append(arithmetic_row("gsm8k", model, resamples))
        rows.append(arithmetic_row("svamp", model, resamples))
        rows.append(chartqa_row(model, model_index, resamples))
    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("setting", "model", "n", "asymmetry", "ci_low", "ci_high"),
        )
        writer.writeheader()
        writer.writerows(rows)


def plot(rows: list[dict], output_prefix: Path) -> None:
    display = dict(MODELS)
    row_lookup = {(row["setting"], row["model"]): row for row in rows}
    y_base = np.arange(len(MODELS), dtype=float)

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 9,
            "legend.fontsize": 8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    fig, ax = plt.subplots(figsize=(7.2, 4.0))

    for y in y_base:
        if int(y) % 2 == 0:
            ax.axhspan(y - 0.43, y + 0.43, color="#F2F2F2", zorder=0)

    for setting, color, marker, offset in SETTINGS:
        estimates, lows, highs = [], [], []
        for model, _ in MODELS:
            row = row_lookup[(setting, model)]
            estimates.append(row["asymmetry"])
            lows.append(row["ci_low"])
            highs.append(row["ci_high"])
        estimates = np.asarray(estimates)
        errors = np.vstack((estimates - np.asarray(lows), np.asarray(highs) - estimates))
        ax.errorbar(
            estimates,
            y_base + offset,
            xerr=errors,
            fmt=marker,
            markersize=5.2,
            markerfacecolor=color,
            markeredgecolor="white",
            markeredgewidth=0.6,
            ecolor=color,
            elinewidth=1.25,
            capsize=2.2,
            capthick=1.0,
            linestyle="none",
            label=setting,
            zorder=3,
        )

    ax.axvline(0, color="#444444", linewidth=1.0, linestyle=(0, (3, 2)), zorder=1)
    ax.set_yticks(y_base)
    ax.set_yticklabels([display[model] for model, _ in MODELS])
    ax.invert_yaxis()
    ax.set_xlabel(r"Paired asymmetry $A=R_T-R_I$ (nats/token)")
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.6, zorder=0)
    ax.grid(axis="y", visible=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, 1.01),
        ncol=3,
        frameon=False,
        handletextpad=0.5,
        columnspacing=1.4,
    )
    ax.text(
        0.0,
        -0.18,
        "Stronger response to image/chart degradation",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8,
        color="#444444",
    )
    ax.text(
        1.0,
        -0.18,
        "Stronger response to text/report degradation",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=8,
        color="#444444",
    )

    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_prefix.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output_prefix.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resamples", type=int, default=10_000)
    parser.add_argument(
        "--output-prefix",
        type=Path,
        default=ROOT / "reproduced" / "asymmetry_forest",
    )
    args = parser.parse_args()
    rows = collect_rows(args.resamples)
    write_csv(rows, args.output_prefix.with_suffix(".csv"))
    plot(rows, args.output_prefix)
    print(f"Saved {args.output_prefix.with_suffix('.pdf')}")
    print(f"Saved {args.output_prefix.with_suffix('.png')}")
    print(f"Saved {args.output_prefix.with_suffix('.csv')}")


if __name__ == "__main__":
    main()
