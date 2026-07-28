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

There are two supported reproducibility paths:

1. **Analysis reproduction (CPU-only):** rerun the paired tests, bootstrap
   intervals, tables, and figures from the included item-level outputs.
2. **Inference reproduction (GPU/API):** regenerate those item-level outputs
   using the canonical model wrapper, prompts, corruptions, and runners.

The first path is complete and immediately runnable from this repository. The
second additionally requires the relevant model weights and upstream benchmark
access. Proprietary-model checks also require the reviewer's own API keys.

## Repository map

```text
.
|-- src/                         canonical model and stimulus implementation
|-- scripts/                     inference, scoring, and analysis entry points
|-- configs/                     model and benchmark configuration
|-- data/chartqa_conflict/       229 reviewed chart-report conflicts
|-- results/main_arithmetic/     GSM8K and SVAMP item-level outputs
|-- results/main_chartqa_conflict/
|-- results/calibration/         unimodal-accuracy calibration outputs
|-- results/supplementary/       prompt and survival checks
|-- paper/figures/               generated paper figures
|-- DATA_ACCESS.md               included and external data dependencies
`-- MANIFEST.json                file sizes and SHA-256 checksums
```

## Canonical inference path

The artifact also includes the canonical code used to produce the item-level
outputs:

- `src/models.py`: model loading, multimodal generation, and candidate CLL;
- `src/benchmarks.py`: benchmark and frozen-render loading;
- `src/rendering.py`, `src/noise.py`, and `src/text_noise.py`: stimulus creation;
- `scripts/run_legibility.py`: matched GSM8K/SVAMP degradation experiments;
- `scripts/run_chartqa_conflict.py`: ChartQA-Conflict inference;
- `scripts/prepare_chartqa_evidence.py`: reviewed ChartQA manifest compilation.

Rerunning inference is not required to verify the reported statistics. It
additionally requires model weights, upstream benchmark access, suitable GPU
hardware, and—only for optional proprietary-model checks—provider API keys.
No model weights, caches, credentials, or private cluster paths are included.

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

## CPU-only setup

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

Model inference requires substantially more storage and compute than the
CPU-only analysis commands below.

## Reproduce the principal results

From the artifact root:

```bash
python scripts/cll_replication_table.py --prompt-role neutral

python scripts/analyze_chartqa_conflict.py   --root results/main_chartqa_conflict   --models Qwen2-VL-2B-Instruct Qwen2.5-VL-7B-Instruct     Idefics3-8B-Llama3 llava-onevision-qwen2-7b-ov-hf     llava-v1.6-mistral-7b-hf Phi-3.5-vision-instruct   --exclude-ids 45

python scripts/analyze_calibrated_slopes.py   --benchmark all
```

The ChartQA generated-answer analysis reports Phi-3.5-Vision as incomplete;
this is expected and is not silently imputed. Its primary CLL analysis is
complete for all 229 retained items in both degradation arms.

## Inspect ChartQA-Conflict

Each row in `data/chartqa_conflict/items.jsonl` links the shared question,
chart-supported answer, report-supported answer, evidence-bearing report,
source-label assignment, and local chart image. The corresponding images are
under `data/chartqa_conflict/images/`. See
`data/chartqa_conflict/README.md` and `DATA_ACCESS.md` for provenance and
redistribution details.

## Integrity and exclusions

The `MANIFEST.json` file records every included file's size and SHA-256 digest.
Compiled ChartQA item 45 is excluded from the reported 229-item analysis and
is recorded in both the manifest and the analysis commands. Model weights,
credentials, caches, development logs, and the private working repository are
intentionally not included.
