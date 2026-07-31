#!/usr/bin/env python3
"""Reproduce the two main tables and every appendix-table analysis."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reproduced"
MODELS = [
    "Qwen2-VL-2B-Instruct",
    "Qwen2.5-VL-7B-Instruct",
    "Idefics3-8B-Llama3",
    "llava-onevision-qwen2-7b-ov-hf",
    "llava-v1.6-mistral-7b-hf",
    "Phi-3.5-vision-instruct",
]


def run(name, arguments):
    print(f"\n===== {name} =====", flush=True)
    result = subprocess.run(
        [sys.executable, *arguments],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = result.stdout
    print(output, end="")
    (OUT / f"{name}.txt").write_text(output, encoding="utf-8")
    if result.returncode:
        raise SystemExit(f"{name} failed with exit code {result.returncode}")


def main():
    OUT.mkdir(exist_ok=True)
    run("artifact_verification", ["scripts/verify_artifact.py"])
    run(
        "table_1_main_arithmetic",
        [
            "scripts/cll_replication_table.py",
            "--prompt-role", "neutral",
            "--resamples", "10000",
        ],
    )
    run(
        "table_2_main_chartqa",
        [
            "scripts/analyze_chartqa_conflict.py",
            "--root", "results/main_chartqa_conflict",
            "--models", *MODELS,
            "--exclude-ids", "45",
            "--resamples", "10000",
        ],
    )
    run(
        "appendix_chartqa_chart_vs_table",
        [
            "scripts/analyze_chartqa_representation.py",
            "--chart-root", "results/main_chartqa_conflict",
            "--table-root", "results/ablation_chartqa_table",
            "--models", *MODELS,
            "--resamples", "10000",
            "--seed", "20260731",
        ],
    )
    run(
        "main_asymmetry_forest",
        [
            "scripts/plot_asymmetry_forest.py",
            "--resamples", "10000",
            "--output-prefix", "reproduced/asymmetry_forest",
        ],
    )
    run(
        "appendix_tables",
        ["scripts/reproduce_appendix_tables.py"],
    )
    print(f"\nReproduction complete: {OUT}")


if __name__ == "__main__":
    main()
