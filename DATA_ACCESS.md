# Data access and reproducibility boundary

## Available directly in this artifact

- Item-level conditional-log-likelihood margins for every reported model,
  benchmark, degradation arm, and level.
- Generated-answer source-attribution outputs used in the behavioral analyses.
- Unimodal decodability measurements used by the calibration analyses.
- Machine-readable derived summaries and figure inputs.
- Scripts for paired tests, bootstrap intervals, calibrated slopes, tables, and
  figures.
- Experiment configurations, degradation implementations, prompts, answer
  normalization, and model-loading code.

These files are sufficient to reproduce all reported aggregate numbers without
model weights, GPUs, or access to the original benchmark images.

## Not redistributed in this artifact

- Model weights.
- Upstream GSM8K, SVAMP, or ChartQA data.
- The 230 ChartQA-Conflict chart images and reports.
- Large token-by-token generation traces, caches, and cluster logs.

The ChartQA-Conflict manifest is frozen by SHA-256 in `MANIFEST.json`, and the
saved result configurations retain its revision and design version. The
dataset location is anonymized during double-blind review. With authorized
dataset access, `scripts/run_chartqa_conflict.py` can rerun inference; without
it, all downstream statistical analyses remain reproducible from the included
outputs.

After the anonymity period, the final archival release should replace the
placeholder dataset namespace with the public dataset URL and pinned revision.
