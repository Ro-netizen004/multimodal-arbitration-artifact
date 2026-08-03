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
6. Chart-versus-plain-table representation ablation on matched ChartQA conflicts.

Every numbered table in the submission PDF is mapped to its generating command
and output in [`TABLE_REPRODUCTION.md`](TABLE_REPRODUCTION.md). The complete map
is executed by `python scripts/reproduce_all.py`.

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

## Licensing

Evaluation code is released under the MIT License (`LICENSE`). Newly created
annotations, degradation metadata, conflict mappings, exclusion records, and
saved model outputs are released under CC BY 4.0 (`DATA_LICENSE.md`). Upstream
GSM8K and SVAMP material is MIT-licensed; ChartQA-derived charts and source data
remain under GPL-3.0. See `THIRD_PARTY_DATA.md` for the component-level notice.

## Repository map

```text
.
|-- src/                         canonical model and stimulus implementation
|-- scripts/                     inference, scoring, and analysis entry points
|-- configs/                     model and benchmark configuration
|-- data/chartqa_conflict/       229 reviewed chart-report conflicts
|-- results/main_arithmetic/     GSM8K and SVAMP item-level outputs
|-- results/main_chartqa_conflict/
|-- results/ablation_chartqa_table/  chart-to-table representation ablation
|-- results/calibration/         unimodal-accuracy calibration outputs
|-- results/supplementary/       prompt and survival checks
|-- paper/figures/               generated paper figures
|-- EXPECTED_RESULTS.md          reviewer-facing output checks
|-- TABLE_REPRODUCTION.md        commands and outputs for paper Tables 1--12
|-- EXPERIMENT_METADATA.md       reported-run settings and limitations
|-- THIRD_PARTY_DATA.md          dataset provenance and licensing
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
- `scripts/analyze_chartqa_representation.py`: paired chart-versus-table contrast.

Rerunning inference is not required to verify the reported statistics. Exact
end-to-end inference is not self-contained during anonymous review: it
requires model weights, upstream benchmark access, and the frozen derivative
dataset identifier that will be restored after the anonymity period. Optional
proprietary-model checks also require provider API keys. No model weights,
caches, credentials, or private cluster paths are included.

The artifact includes an inspection-ready release of the 229 ChartQA-Conflict
items used in the reported analyses: each native chart, shared question,
chart-supported answer, conflicting evidence-bearing report, and
report-supported answer. The original GSM8K, SVAMP, and complete upstream
ChartQA datasets are not redistributed. The included inference scripts and
frozen configuration metadata provide the pipeline for rerunning the reported
ChartQA-Conflict condition.

The sanitized 230-item derivative dataset, **ChartQA-Conflict v2**, is also
available through the
[anonymous ChartQA-Conflict mirror](https://anonymous-hf.com/a/l6ys5y01rlpw/).
It omits
reviewer identities and free-form review notes; the artifact records the single
post-run exclusion that yields the 229-item analysis set.

The rendered GSM8K and SVAMP conflict stimuli are available through a separate
[anonymous stimulus mirror](https://anonymous-hf.com/a/4qcemes98r9t/). Their
upstream problem content remains subject to the GSM8K and SVAMP MIT licenses.

The paired ChartQA chart-versus-table release, containing both `chart_image` and
`table_image` for the 229 analyzed conflicts, is available through the
[anonymous chart/table mirror](https://anonymous-hf.com/a/p1nzaf47bbqu/).

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
use pandas and statsmodels. Inference dependencies are kept separate so that
reviewers do not need to install the GPU stack.

## Run model inference (optional, GPU)

Inference is optional: all paper statistics can be reproduced from the included
item-level outputs without downloading model weights. To regenerate those raw
outputs, use Python 3.10, a CUDA-capable GPU, and the separately pinned inference
environment:

```bash
python -m venv .venv-inference
source .venv-inference/bin/activate       # Windows: .venv-inference\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-inference.txt
```

The examples below run one open checkpoint at a time. Replace `MODEL` with a key
accepted by `src/models.py`, for example `Qwen2.5-VL-7B-Instruct`. Generation must
finish before CLL scoring because the latter joins its scores to the saved
generation rows. Use a fresh output directory; the runners intentionally refuse
incompatible resumes.

### Role-counterbalanced GSM8K or SVAMP

The paper uses levels L0, L2, L4, and L5. Run both degradation arms in generation
mode, followed by the corresponding CLL jobs:

```bash
MODEL=Qwen2.5-VL-7B-Instruct
OUT=outputs/inference_arithmetic
BENCHMARK=gsm8k                 # use svamp for the 300-item SVAMP run
N=1319                          # use 300 for SVAMP

# Use the load_dataset repository ID displayed by the anonymous arithmetic
# mirror. The combined dataset supports both GSM8K and SVAMP; the runner
# extracts its clean L0 rows and deterministically recreates the requested arm.
DATASET_REPO="COPY_DATASET_ID_FROM_ANONYMOUS_MIRROR"

python scripts/run_legibility.py \
  --dataset-repo "$DATASET_REPO" \
  --benchmark "$BENCHMARK" --num-problems "$N" \
  --prompt-role neutral --noise-levels 0 2 4 5 \
  --channel image --models "$MODEL" --output-dir "$OUT"
python scripts/run_legibility.py \
  --dataset-repo "$DATASET_REPO" \
  --benchmark "$BENCHMARK" --num-problems "$N" \
  --prompt-role neutral --noise-levels 0 2 4 5 \
  --channel image --models "$MODEL" --output-dir "$OUT" --score-cll

python scripts/run_legibility.py \
  --dataset-repo "$DATASET_REPO" \
  --benchmark "$BENCHMARK" --num-problems "$N" \
  --prompt-role neutral --noise-levels 0 2 4 5 \
  --channel text --models "$MODEL" --output-dir "$OUT"
python scripts/run_legibility.py \
  --dataset-repo "$DATASET_REPO" \
  --benchmark "$BENCHMARK" --num-problems "$N" \
  --prompt-role neutral --noise-levels 0 2 4 5 \
  --channel text --models "$MODEL" --output-dir "$OUT" --score-cll
```

The arithmetic runner downloads the benchmark and canonical rendered stimuli from
Hugging Face. Model weights are downloaded from the checkpoint identifiers listed
in `EXPERIMENT_METADATA.md`.

### ChartQA-Conflict and chart-versus-table ablation

The paired representation release contains both `chart_image` and `table_image`
and is available from the
[anonymous chart/table mirror](https://anonymous-hf.com/a/p1nzaf47bbqu/).
Open that page and copy the anonymous Hugging Face dataset identifier shown in its
loading instructions into `TABLE_DATASET_REPO`. The reported table-ablation release
is pinned to revision
`4c5d377d37e0b8854f230a37f757b0fc08a31379` and contains 229 rows.

Run once with `REP=chart` for the genuine-chart condition and once with
`REP=plain_table` for the table-image condition:

```bash
MODEL=Qwen2.5-VL-7B-Instruct
TABLE_DATASET_REPO="COPY_DATASET_ID_FROM_ANONYMOUS_MIRROR"
TABLE_DATASET_REVISION=4c5d377d37e0b8854f230a37f757b0fc08a31379
REP=plain_table                    # or: chart
OUT=outputs/inference_chartqa_${REP}

for ARM in image text; do
  python scripts/run_chartqa_conflict.py \
    --models "$MODEL" --arm "$ARM" --mode generation \
    --levels 0 2 4 5 --num-problems 229 \
    --visual-representation "$REP" \
    --dataset-repo "$TABLE_DATASET_REPO" \
    --dataset-revision "$TABLE_DATASET_REVISION" \
    --output-dir "$OUT"

  python scripts/run_chartqa_conflict.py \
    --models "$MODEL" --arm "$ARM" --mode cll \
    --levels 0 2 4 5 --num-problems 229 \
    --visual-representation "$REP" \
    --dataset-repo "$TABLE_DATASET_REPO" \
    --dataset-revision "$TABLE_DATASET_REVISION" \
    --output-dir "$OUT"
done
```

For a cheap pre-flight check, change `--num-problems 229` to `12` and use a new
output directory. Confirm that each requested level contains 12 generation rows and
12 CLL rows before launching the full run. CLL is available only for checkpoints
whose local wrapper exposes continuation scoring; InternVL2 and proprietary API
models are evaluated behaviorally instead.

After the complete chart and table runs, compare them with:

```bash
python scripts/analyze_chartqa_representation.py \
  --chart-root outputs/inference_chartqa_chart \
  --table-root outputs/inference_chartqa_plain_table \
  --resamples 10000 --seed 20260731
```

These are portable shell examples. On a scheduler, submit generation and CLL as
separate jobs and make each CLL job depend on successful completion of its matching
generation job.

## CPU-only setup

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
python -m pip install -r requirements-analysis.txt
```

Model inference requires substantially more storage and compute than the
CPU-only analysis commands below.

## Reproduce the principal results

From the artifact root:

```bash
python scripts/verify_artifact.py
python scripts/reproduce_all.py
```

The wrapper verifies the artifact, reproduces main-text Tables 1 and 2, and
then runs every appendix-table analysis. It writes fresh logs and derived JSON
under `reproduced/` without modifying the supplied results. To reproduce the
two primary paper tables directly, run:

```bash
# Table 1: role-neutral arithmetic contrasts (GSM8K and SVAMP)
python scripts/cll_replication_table.py \
  --prompt-role neutral \
  --resamples 10000

# Table 2: ChartQA-Conflict contrasts
python scripts/analyze_chartqa_conflict.py \
  --root results/main_chartqa_conflict \
  --models Qwen2-VL-2B-Instruct Qwen2.5-VL-7B-Instruct \
    Idefics3-8B-Llama3 llava-onevision-qwen2-7b-ov-hf \
    llava-v1.6-mistral-7b-hf Phi-3.5-vision-instruct \
  --exclude-ids 45 \
  --resamples 10000
```

For Table 1, use the `PAIRED ARM CONTRAST` block. For Table 2, use the six
rows whose `mode` is `cll`; the preceding `generation` rows are the
supplementary behavioral analysis. The explicit resample count matches the
paper and `configs/paper_experiments.yaml`.

The main-text asymmetry forest plot is regenerated directly from those frozen
item-level results with:

```bash
python scripts/plot_asymmetry_forest.py \
  --resamples 10000 \
  --output-prefix reproduced/asymmetry_forest
```

This writes PDF, PNG, and CSV versions of the plotted estimates.
The pre-rendered submission figure and its plotted values are also included
under `figures/asymmetry_forest.{pdf,png,csv}`.

The supporting chart-versus-table representation ablation is reproduced with:

```bash
python scripts/analyze_chartqa_representation.py \
  --chart-root results/main_chartqa_conflict \
  --table-root results/ablation_chartqa_table \
  --resamples 10000 \
  --seed 20260731
```

The script reports each representation's median item-level asymmetry and the
median paired change `A_table,i - A_chart,i`. All six table-condition CLL
asymmetries remain negative; representation changes have no common direction.
To regenerate only the appendix-table analyses, run:

```bash
python scripts/reproduce_appendix_tables.py
```

Its outputs are written to `reproduced/appendix/` and cover generated-choice/
CLL agreement, accuracy-calibrated slopes for all three benchmarks,
ChartQA generated-answer contrasts (including InternVL2), candidate-length
normalization, and prompt-framing sensitivity.

To reproduce the complete generated-answer ChartQA-Conflict appendix table,
including InternVL2, run:

```bash
python scripts/analyze_chartqa_conflict.py \
  --root results/main_chartqa_conflict \
  --models Qwen2-VL-2B-Instruct Qwen2.5-VL-7B-Instruct \
    Idefics3-8B-Llama3 llava-onevision-qwen2-7b-ov-hf \
    llava-v1.6-mistral-7b-hf Phi-3.5-vision-instruct InternVL2-8B \
  --exclude-ids 45 \
  --resamples 10000
```

Use the rows whose `mode` is `generation`. Phi-3.5-Vision is expected to be
reported as `INCOMPLETE`, while InternVL2 has generated-answer results but no
CLL result.

The calibrated-slope appendix tables can be reproduced separately:

```bash
python scripts/analyze_calibrated_slopes.py \
  --benchmark all \
  --resamples 10000 \
  --seed 20260726 \
  --output reproduced/calibrated_slopes.json
```

The generated-choice/CLL agreement validation is reproduced with:

```bash
python scripts/analyze_cll_generation_agreement.py \
  --root results/main_arithmetic \
  --resamples 10000 \
  --seed 20260721
```

The primary combined summary is
`POOLED/both_arms_L0_deduplicated`; its item-clustered interval is printed as
`CLUSTER_BOOTSTRAP/both_arms_L0_deduplicated`.

The appendix wrapper also regenerates the pooled task-accuracy regressions
(Table 6) and the character/OCR-survival interactions in Appendix F. The latter
uses the frozen survival measurements in `results/supplementary/`; rerunning OCR
measurement itself is not required to reproduce the reported coefficients.

Table 7, the candidate-length-normalization sensitivity analysis, is
reproduced with:

```bash
python scripts/analyze_cll_normalization.py \
  --models Qwen2-VL-2B-Instruct Qwen2.5-VL-7B-Instruct \
    Idefics3-8B-Llama3 llava-onevision-qwen2-7b-ov-hf \
    llava-v1.6-mistral-7b-hf Phi-3.5-vision-instruct \
  --benchmarks gsm8k svamp chartqa \
  --resamples 10000
```

The role-neutral GSM8K and SVAMP rows and the audited 229-item ChartQA rows test
the same exponents, \(\alpha\in\{0,0.5,1\}\). ChartQA conflict ID 45 is excluded
by default, matching the primary analysis.

Use the six rows whose `framing` value is `neutral`; the `original` rows are
the prompt-framing control. The reported columns for Table 7 are the
`asymmetry` values at \(\alpha=0\), \(0.5\), and \(1\).

The matched GSM8K prompt-framing sensitivity table is reproduced with:

```bash
python scripts/analyze_role_control.py \
  --models Qwen2-VL-2B-Instruct Qwen2.5-VL-7B-Instruct \
    Idefics3-8B-Llama3 llava-onevision-qwen2-7b-ov-hf \
    Phi-3.5-vision-instruct \
  --resamples 10000
```

The output reports the original-prompt asymmetry, role-neutral asymmetry,
their within-item paired contrast, its bootstrap confidence interval, and
the two-sided Wilcoxon signed-rank \(p\)-value.

See `EXPECTED_RESULTS.md` for high-level checks and
`EXPERIMENT_METADATA.md` for the reported-run configuration.

Phi-3.5-Vision often returned its direct answer on the first line without the
requested delimiter. The released ChartQA files use a uniform, conservative
no-inference rescore: an undelimited first line is accepted only when the whole
line normalizes to one answer. This changes Phi's audited clean chart-only
accuracy from the delimiter-only 2/229 (0.009) to 166/229 (0.725), ruling out a
loading or image-processing failure. Its generated endpoint contrast still has
only nine complete cases and is not emphasized; its primary CLL analysis is
complete for all 229 retained items in both arms.

## Reproduce the frontier-model appendix

Saved API generations are included, so these analyses require no API keys and
perform no inference. First rescore the raw ChartQA outputs with the same strict
numeric matcher used in the paper; compatible unit labels are accepted, while
conflicting scales, currencies, and units remain invalid:

```bash
python scripts/rescore_chartqa_generation.py \
  --root results/frontier_models/chartqa_conflict_raw \
  --output-root reproduced/frontier_chartqa_rescored \
  --manifest data/chartqa_conflict/items.jsonl \
  --models GPT-5.6-Luna Gemini-3.5-Flash

python scripts/analyze_chartqa_conflict.py \
  --root reproduced/frontier_chartqa_rescored/evidence \
  --models GPT-5.6-Luna \
  --resamples 10000

python scripts/analyze_chartqa_conflict.py \
  --root reproduced/frontier_chartqa_rescored/evidence \
  --models Gemini-3.5-Flash \
  --resamples 10000
```

The four-level behavioral trajectories used by the frontier trajectory table are
emitted explicitly with:

```powershell
python scripts\analyze_frontier_chartqa_trajectories.py `
  --root reproduced\frontier_chartqa_rescored\evidence `
  --models GPT-5.6-Luna Gemini-3.5-Flash
```

The paired
endpoint analysis reproduces GPT-5.6-Luna \(A=-0.9249\) and
Gemini-3.5-Flash \(A=-0.7719\).

Reproduce the 300-item GPT-5.6-Luna GSM8K contrast and both shared-clean
baseline sensitivity checks with:

```bash
python scripts/analyze_frontier_gsm8k.py \
  --root results/frontier_models/gsm8k_role_neutral_300 \
  --model GPT-5.6-Luna \
  --resamples 10000
```

This reports \(A=+0.2910\), its paired-bootstrap interval, and the positive
shared-baseline sensitivity range. These commands are also part of
`python scripts/reproduce_all.py`.

## Inspect ChartQA-Conflict

Each row in `data/chartqa_conflict/items.jsonl` links the shared question,
chart-supported answer, report-supported answer, evidence-bearing report,
source-label assignment, and local chart image. The corresponding images are
under `data/chartqa_conflict/images/`. See
`data/chartqa_conflict/README.md` and `DATA_ACCESS.md` for provenance and
redistribution details.

## Integrity and exclusions

The `MANIFEST.json` file records every included file's size and SHA-256 digest.
Run `python scripts/verify_artifact.py` to check those records and scan the
review copy for accidental identity-bearing paths or credentials.
Compiled ChartQA item 45 is excluded from the reported 229-item analysis and
is recorded in both the manifest and the analysis commands. Model weights,
credentials, caches, development logs, and the private working repository are
intentionally not included.
