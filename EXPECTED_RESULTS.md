# Expected reproduction checks

Run:

```bash
python scripts/verify_artifact.py
python scripts/reproduce_all.py
```

The fresh outputs are written under `reproduced/`. A successful reproduction
should satisfy these high-level checks:

1. GSM8K and SVAMP each contain paired CLL arm contrasts for six open-weight
   models.
2. Five of six models have positive median `R_text - R_image` on each
   arithmetic benchmark; Qwen2.5-VL-7B is the exception on SVAMP and has only
   a small positive GSM8K endpoint contrast.
3. ChartQA-Conflict contains 229 analyzed CLL items per model after excluding
   compiled item 45, and all six CLL contrasts have the opposite direction
   from the majority arithmetic pattern.
4. Phi-3.5-Vision's corrected clean chart-only accuracy is 166/229 (0.725).
   The earlier 2/229 (0.009) value counted only outputs containing the requested
   delimiter; a uniform no-inference rescore also accepts an answer-only first
   line when that complete line normalizes to a single answer. Phi's endpoint
   generated-answer contrast remains based on only nine complete cases and is
   therefore not emphasized; its CLL analysis is complete for all 229 items.
5. The calibrated-slope output covers GSM8K, SVAMP, and ChartQA-Conflict. All
   six CLL models enter the corrected ChartQA calibration and have negative
   chart-versus-report slope differences.
6. `reproduce_appendix_tables.py` completes the generated-choice/CLL agreement,
   per-model calibrated slopes, ChartQA generated answers, candidate-length
   normalization, prompt-framing sensitivity, raw and 1%-winsorized pooled
   accuracy regressions, and task-accuracy/character-survival calibration axes.
7. The chart-versus-table ablation contains 229 paired CLL items per model. All
   six plain-table asymmetries remain negative. The paired table-minus-chart
   change is not uniformly directed across models.
8. `verify_paper_table_outputs.py` reports `PASS` for Tables 1--12.
For the complete command/output map, see `TABLE_REPRODUCTION.md`. Fixed
resampling seeds make the statistical outputs deterministic.
