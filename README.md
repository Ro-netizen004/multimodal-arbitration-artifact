# Anonymous multimodal-arbitration artifact

This artifact contains the code and item-level outputs needed to reproduce the
paper's reported statistical analyses. It excludes model weights, upstream
benchmark data, token-by-token log-probability traces, cluster logs, caches,
curation workbooks, and Git history.

## Included analyses

1. Role-neutral paired CLL contrasts on GSM8K and SVAMP.
2. Original-versus-neutral prompt-framing comparison.
3. ChartQA-Conflict paired CLL and generated-answer contrasts.
4. Per-model reallocation slopes calibrated by unimodal accuracy loss.
5. Candidate-length-normalization sensitivity analyses.

## Reproducibility scope

The artifact is self-contained for reproducing the paper's analyses, metrics,
confidence intervals, statistical tests, tables, and figures from the saved
item-level outputs. Reviewers do not need to download a benchmark or rerun a
vision-language model for those checks.

The artifact includes an inspection-ready release of the 229 ChartQA-Conflict
items used in the reported analyses: each native chart, shared question,
chart-supported answer, conflicting evidence-bearing report, and
report-supported answer. The original GSM8K, SVAMP, and complete upstream
ChartQA datasets are not redistributed. The included inference scripts and
frozen configuration metadata provide the pipeline for rerunning the reported
ChartQA-Conflict condition.

## Environment used for inference

- Python 3.10.20
- PyTorch 2.5.1+cu121
- CUDA 12.1; cuDNN 9.1
- Transformers 4.49.0
- Torchvision 0.20.1+cu121
- Pillow 12.2.0
- Accelerate 1.14.0
- NVIDIA L40S 48 GB, one GPU per job

CPU-only analysis requires NumPy and SciPy; calibrated analyses additionally
use pandas and statsmodels.

## Quick verification

From the artifact root:

```bash
python scripts/cll_replication_table.py --prompt-role neutral

python scripts/analyze_chartqa_conflict.py   --root results/main_chartqa_conflict   --models Qwen2-VL-2B-Instruct Qwen2.5-VL-7B-Instruct     Idefics3-8B-Llama3 llava-onevision-qwen2-7b-ov-hf     llava-v1.6-mistral-7b-hf Phi-3.5-vision-instruct   --exclude-ids 45

python scripts/analyze_calibrated_slopes.py   --benchmark all
```

The `MANIFEST.json` file records every included file's size and SHA-256 digest.
The working repository is intentionally not included.
