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
4. Phi-3.5-Vision generated-answer ChartQA analysis is reported as incomplete;
   its CLL analysis is complete and is never imputed.
5. The calibrated-slope output covers GSM8K, SVAMP, and ChartQA-Conflict and
   records any low-clean-accuracy exclusions explicitly.

For exact table values, compare the generated logs with
`results/main_arithmetic/analysis/neutral_cll_paired_statistics.txt` and
`results/calibration/derived/calibrated_slopes.json`. Fixed resampling seeds
make the statistical outputs deterministic.
