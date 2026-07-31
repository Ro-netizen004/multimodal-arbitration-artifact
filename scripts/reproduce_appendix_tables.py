#!/usr/bin/env python3
"""Regenerate every appendix-table analysis from the frozen artifact results."""

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reproduced" / "appendix"
CLL_MODELS = [
    "Qwen2-VL-2B-Instruct",
    "Qwen2.5-VL-7B-Instruct",
    "Idefics3-8B-Llama3",
    "llava-onevision-qwen2-7b-ov-hf",
    "llava-v1.6-mistral-7b-hf",
    "Phi-3.5-vision-instruct",
]
FRAMING_MODELS = [
    "Qwen2-VL-2B-Instruct",
    "Qwen2.5-VL-7B-Instruct",
    "Idefics3-8B-Llama3",
    "llava-onevision-qwen2-7b-ov-hf",
    "Phi-3.5-vision-instruct",
]
CHARTQA_BEHAVIOR_MODELS = [*CLL_MODELS, "InternVL2-8B"]


def run(name: str, arguments: list[str]) -> None:
    print(f"\n===== appendix/{name} =====", flush=True)
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
        raise SystemExit(f"appendix/{name} failed with exit code {result.returncode}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    run(
        "cll_generation_agreement",
        [
            "scripts/analyze_cll_generation_agreement.py",
            "--root", "results/main_arithmetic",
            "--resamples", "10000",
            "--seed", "20260721",
        ],
    )
    run(
        "calibrated_slopes",
        [
            "scripts/analyze_calibrated_slopes.py",
            "--benchmark", "all",
            "--resamples", "10000",
            "--seed", "20260726",
            "--output", "reproduced/appendix/calibrated_slopes.json",
        ],
    )
    run(
        "chartqa_generated_answers",
        [
            "scripts/analyze_chartqa_conflict.py",
            "--root", "results/main_chartqa_conflict",
            "--models", *CHARTQA_BEHAVIOR_MODELS,
            "--exclude-ids", "45",
            "--resamples", "10000",
        ],
    )
    run(
        "length_normalization",
        [
            "scripts/analyze_cll_normalization.py",
            "--models", *CLL_MODELS,
            "--resamples", "10000",
        ],
    )
    run(
        "prompt_framing",
        [
            "scripts/analyze_role_control.py",
            "--models", *FRAMING_MODELS,
            "--resamples", "10000",
        ],
    )

    print(f"\nAppendix-table reproduction complete: {OUT}")


if __name__ == "__main__":
    main()
