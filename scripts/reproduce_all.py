#!/usr/bin/env python3
"""Reproduce all principal paper statistics into a fresh output directory."""

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
    run(
        "main_arithmetic",
        ["scripts/cll_replication_table.py", "--prompt-role", "neutral"],
    )
    run(
        "main_chartqa",
        [
            "scripts/analyze_chartqa_conflict.py",
            "--root", "results/main_chartqa_conflict",
            "--models", *MODELS,
            "--exclude-ids", "45",
        ],
    )
    run(
        "calibrated_slopes",
        [
            "scripts/analyze_calibrated_slopes.py",
            "--benchmark", "all",
            "--output", "reproduced/calibrated_slopes.json",
        ],
    )
    run(
        "prompt_framing",
        ["scripts/analyze_role_control.py", "--models", *MODELS],
    )
    run(
        "length_normalization",
        ["scripts/analyze_cll_normalization.py", "--models", *MODELS],
    )
    print(f"\nReproduction complete: {OUT}")


if __name__ == "__main__":
    main()
