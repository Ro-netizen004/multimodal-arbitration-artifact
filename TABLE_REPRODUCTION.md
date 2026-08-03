# Paper table reproduction map

The numbering below follows `Which Source Wins?` (submission PDF, 12 tables).
Run all commands from the repository root after completing the CPU-only setup.

The one-command route is:

```bash
python scripts/reproduce_all.py
```

It verifies the frozen inputs first and writes human-readable outputs under
`reproduced/`. The following map identifies the source command and output for
every paper table.

| Paper table | Contents | Reproduction output |
|---|---|---|
| 1 | CLL arm contrasts for GSM8K, SVAMP, and ChartQA-Conflict | `reproduced/table_1_main_arithmetic.txt` (GSM8K/SVAMP) and the `cll` rows of `reproduced/table_2_main_chartqa.txt` (ChartQA) |
| 2 | Hugging Face checkpoints and pinned revisions | `reproduced/table_2_checkpoint_revisions.txt` |
| 3 | Frontier-model ChartQA endpoint contrasts | `reproduced/frontier_chartqa_contrast_luna.txt` and `reproduced/frontier_chartqa_contrast_gemini.txt` |
| 4 | Frontier-model ChartQA trajectories | `reproduced/frontier_chartqa_trajectories.txt` |
| 5 | Generated-choice/CLL-sign agreement | `reproduced/appendix/cll_generation_agreement.txt` |
| 6 | Pooled accuracy-adjusted interactions | `reproduced/appendix/pooled_accuracy_regression_{gsm8k,svamp}.txt`, `..._winsor01.txt`, and the `task_acc` blocks of `reproduced/appendix/calibration_axes_{gsm8k,svamp}.txt` |
| 7 | Arithmetic per-model calibrated slopes | GSM8K and SVAMP rows in `reproduced/appendix/calibrated_slopes.txt` |
| 8 | ChartQA per-model calibrated slopes | ChartQA rows in `reproduced/appendix/calibrated_slopes.txt` |
| 9 | Chart-versus-table representation control | `reproduced/appendix_chartqa_chart_vs_table.txt` (paired representation change) and the `cll` rows of `reproduced/appendix_chartqa_table_endpoint.txt` (standalone table-condition CIs) |
| 10 | Candidate-length-normalization sensitivity | Neutral GSM8K rows in `reproduced/appendix/length_normalization.txt` |
| 11 | Open-model generated-answer ChartQA contrasts | `generation` rows in `reproduced/appendix/chartqa_generated_answers.txt` |
| 12 | Prompt-framing sensitivity | `reproduced/appendix/prompt_framing.txt` |

Table 1 is typeset as one table in the paper but deliberately comes from the
two benchmark-specific analyzers: the arithmetic script and the ChartQA script.
This avoids maintaining a second implementation of either statistic.

Table 6 combines three estimators. The raw and winsorized item-level rows come
from `analyze_legibility_item_model.py`; the coarser cell-median row and the
character/OCR-survival sensitivity coefficients come from
`analyze_legibility_control.py`. For GSM8K, both commands explicitly load
`results/calibration/gsm8k_image_unimodal/` because the compact
`decodability_all.json` stores the text curves while the legacy Phase-4 files
store the image curves.

To reproduce only appendix tables, run:

```bash
python scripts/reproduce_appendix_tables.py
```

No command in either wrapper performs model inference or contacts an API.

After reproduction, verify the complete 12-table contract directly:

```bash
python scripts/verify_paper_table_outputs.py
```

This check fails if an expected output is missing or no longer contains the
submitted paper's stable point estimates and sample identifiers.
