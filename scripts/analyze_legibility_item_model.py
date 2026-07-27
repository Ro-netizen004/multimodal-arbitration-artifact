#!/usr/bin/env python3
"""Item-level legibility-adjusted CLL analysis for the role-neutral experiment.

The response is the item-level CLL shift toward the source that remains clean.
Legibility loss is measured at the model x channel x level cell using unimodal
task accuracy. The script reports:

1. a linear mixed model with a random item intercept and model fixed effects;
2. the same fixed-effects specification with standard errors clustered by the
   model x channel x level cell, guarding against pseudoreplication because the
   legibility-loss predictor is constant within each such cell.
"""

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


LEVELS = (2, 4, 5)
CLL_RE = re.compile(r"^level_(\d+)_.*\.cll\.jsonl$")
DECOD_RE = re.compile(r"^level_(\d+)_.*\.decodability\.jsonl$")


def load_json(path):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def load_margins(model_dir, excluded=frozenset()):
    per_level = {}
    for path in Path(model_dir).glob("level_*.cll.jsonl"):
        match = CLL_RE.match(path.name)
        if not match:
            continue
        rows = {}
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                value = (row.get("margin") or {}).get("margin_mean")
                item = int(row["i"])
                if value is not None and item not in excluded:
                    rows[item] = float(value)
        per_level[int(match.group(1))] = rows
    return per_level


def phase4_image_accuracy(root, model):
    values = {}
    if not root:
        return values
    model_dir = Path(root) / model
    for level in (0, *LEVELS):
        matches = sorted(model_dir.glob(f"level_{level}_*.json"))
        if len(matches) != 1:
            continue
        row = load_json(matches[0])
        if row.get("accuracy") is not None:
            values[level] = float(row["accuracy"])
    return values


def int_keys(raw):
    return {int(key): float(value) for key, value in (raw or {}).items()}


def accuracy_by_channel(decodability, model, phase4_root):
    row = decodability.get(model, {})
    image = int_keys(row.get("image"))
    text = int_keys(row.get("text"))
    fallback = phase4_image_accuracy(phase4_root, model)
    for level, value in fallback.items():
        image.setdefault(level, value)
    return {"image": image, "text": text}


def chartqa_accuracies(root, excluded):
    root = Path(root)
    output = {}
    for channel in ("image", "text"):
        channel_root = root / channel
        if not channel_root.is_dir():
            continue
        for model_dir in channel_root.iterdir():
            if not model_dir.is_dir():
                continue
            values = {}
            for path in model_dir.glob("level_*.decodability.jsonl"):
                match = DECOD_RE.match(path.name)
                if not match:
                    continue
                correct = []
                with path.open(encoding="utf-8") as handle:
                    for line in handle:
                        row = json.loads(line)
                        if int(row["i"]) not in excluded:
                            correct.append(bool(row.get("correct")))
                if correct:
                    values[int(match.group(1))] = float(np.mean(correct))
            output.setdefault(model_dir.name, {"image": {}, "text": {}})
            output[model_dir.name][channel] = values
    return output


def build_frame(args):
    excluded = set(args.exclude_ids)
    decodability = (
        chartqa_accuracies(args.chartqa_decodability_root, excluded)
        if args.chartqa_decodability_root
        else load_json(args.decodability)
    )
    rows = []
    for model in sorted(decodability):
        image = load_margins(Path(args.image_root) / model, excluded)
        text = load_margins(Path(args.text_root) / model, excluded)
        accuracies = accuracy_by_channel(decodability, model, args.phase4_image_root)
        for channel, margins in (("image", image), ("text", text)):
            accuracy = accuracies[channel]
            if 0 not in accuracy or accuracy[0] <= 0:
                continue
            if accuracy[0] < args.min_headroom:
                continue
            if 0 not in margins:
                continue
            for level in LEVELS:
                if level not in accuracy or level not in margins:
                    continue
                loss = (accuracy[0] - accuracy[level]) / accuracy[0]
                ids = sorted(
                    (margins[0].keys() & margins[level].keys()) - excluded
                )
                for item in ids:
                    raw_change = margins[level][item] - margins[0][item]
                    shift = raw_change if channel == "image" else -raw_change
                    rows.append(
                        {
                            "item": str(item),
                            "model": model,
                            "channel": channel,
                            "text_channel": int(channel == "text"),
                            "level": level,
                            "leg_loss": loss,
                            "shift": shift,
                            "cell": f"{model}|{channel}|L{level}",
                        }
                    )
    return pd.DataFrame(rows)


def coefficient_line(result, name):
    estimate = float(result.params[name])
    se = float(result.bse[name])
    p = float(result.pvalues[name])
    lo, hi = map(float, result.conf_int().loc[name])
    return estimate, se, lo, hi, p


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--decodability")
    source.add_argument(
        "--chartqa-decodability-root",
        help="Root containing evidence/{image,text}/MODEL decodability JSONLs.",
    )
    parser.add_argument("--image-root", required=True)
    parser.add_argument("--text-root", required=True)
    parser.add_argument("--phase4-image-root")
    parser.add_argument("--exclude-ids", nargs="*", type=int, default=[])
    parser.add_argument("--min-headroom", type=float, default=0.0)
    parser.add_argument(
        "--winsorize",
        type=float,
        default=0.0,
        help="Optional proportion clipped from each tail of the item-level shift.",
    )
    parser.add_argument("--output")
    args = parser.parse_args()

    frame = build_frame(args)
    if frame.empty:
        raise SystemExit("No matched item-level observations were assembled.")
    if not 0.0 <= args.winsorize < 0.5:
        raise SystemExit("--winsorize must be in [0, 0.5).")
    if args.winsorize:
        lower, upper = frame["shift"].quantile(
            [args.winsorize, 1.0 - args.winsorize]
        )
        frame["shift"] = frame["shift"].clip(lower, upper)

    formula = "shift ~ leg_loss * text_channel + C(model)"
    mixed_result = None
    mixed_error = None
    try:
        mixed = smf.mixedlm(formula, frame, groups=frame["item"])
        mixed_result = mixed.fit(reml=False, method="lbfgs", maxiter=1000)
    except (ValueError, np.linalg.LinAlgError) as error:
        mixed_error = repr(error)

    clustered = smf.ols(formula, frame).fit(
        cov_type="cluster",
        cov_kwds={"groups": frame["cell"], "use_correction": True},
    )
    model_clustered = smf.ols(formula, frame).fit(
        cov_type="cluster",
        cov_kwds={
            "groups": frame["model"],
            "use_correction": True,
            "df_correction": True,
        },
        use_t=True,
    )
    cell_frame = (
        frame.groupby(
            ["cell", "model", "channel", "text_channel", "level", "leg_loss"],
            as_index=False,
        )["shift"]
        .median()
    )
    cell_median = smf.ols(
        "shift ~ leg_loss * text_channel", cell_frame
    ).fit()

    interaction = "leg_loss:text_channel"
    mixed_stats = (
        coefficient_line(mixed_result, interaction)
        if mixed_result is not None
        else None
    )
    cluster_stats = coefficient_line(clustered, interaction)
    model_cluster_stats = coefficient_line(model_clustered, interaction)
    cell_median_stats = coefficient_line(cell_median, interaction)
    lines = [
        f"benchmark={args.benchmark}",
        f"rows={len(frame)} items={frame['item'].nunique()} "
        f"models={frame['model'].nunique()} cells={frame['cell'].nunique()}",
        f"winsorize_each_tail={args.winsorize}",
        "formula: shift ~ leg_loss * text_channel + C(model) + (1|item)",
        "",
        "interaction beta3 (text slope - image slope)",
        "method\testimate\tSE\t95% CI\tp",
        (
            f"mixed_item_intercept\t{mixed_stats[0]:+.6f}\t{mixed_stats[1]:.6f}\t"
            f"[{mixed_stats[2]:+.6f},{mixed_stats[3]:+.6f}]\t{mixed_stats[4]:.6g}"
            if mixed_stats is not None
            else f"mixed_item_intercept\tUNAVAILABLE ({mixed_error})"
        ),
        (
            f"OLS_clustered_by_cell\t{cluster_stats[0]:+.6f}\t{cluster_stats[1]:.6f}\t"
            f"[{cluster_stats[2]:+.6f},{cluster_stats[3]:+.6f}]\t{cluster_stats[4]:.6g}"
        ),
        (
            f"OLS_clustered_by_model\t{model_cluster_stats[0]:+.6f}\t"
            f"{model_cluster_stats[1]:.6f}\t"
            f"[{model_cluster_stats[2]:+.6f},{model_cluster_stats[3]:+.6f}]\t"
            f"{model_cluster_stats[4]:.6g}"
        ),
        (
            f"OLS_cell_medians\t{cell_median_stats[0]:+.6f}\t"
            f"{cell_median_stats[1]:.6f}\t"
            f"[{cell_median_stats[2]:+.6f},{cell_median_stats[3]:+.6f}]\t"
            f"{cell_median_stats[4]:.6g}"
        ),
        "",
        "Cell clustering guards against pseudoreplication because legibility loss is",
        "constant within model x channel x level cells. Model clustering is the",
        "generalization check, but it has only six clusters and should be interpreted",
        "cautiously.",
    ]
    output = "\n".join(lines)
    print(output)
    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
