# Data access and reproducibility boundary

## Available directly in this artifact

- Item-level conditional-log-likelihood margins for every reported model,
  benchmark, degradation arm, and level.
- Generated-answer source-attribution outputs used in the behavioral analyses.
- Unimodal decodability measurements used by the calibration analyses.
- The 229 analyzed ChartQA-Conflict charts and evidence-bearing reports, with
  source-supported answers, provenance fields, and the documented post-run
  exclusion.
- Machine-readable derived summaries and figure inputs.
- Scripts for paired tests, bootstrap intervals, calibrated slopes, tables, and
  figures.
- Experiment configurations, degradation implementations, prompts, answer
  normalization, and model-loading code.

These files are sufficient to reproduce all reported aggregate numbers without
model weights, GPUs, or access to the original benchmark images.

The sanitized 230-item derivative dataset, **ChartQA-Conflict v2**, used to
construct the analyzed ChartQA-Conflict release is available during anonymous review at
https://anonymous-hf.com/a/4qcemes98r9t/. The anonymous release excludes
reviewer identities and free-form review notes while preserving the frozen
experimental fields, chart images, and manifest hash.

## Not redistributed in this artifact

- Model weights.
- Upstream GSM8K, SVAMP, or ChartQA data.
- Large token-by-token generation traces, caches, and cluster logs.

The original ChartQA-Conflict construction contained 230 reviewed items and is
frozen by SHA-256 in `MANIFEST.json`. One item was removed by a post-run
entailment audit; `data/chartqa_conflict/` contains the 229 analyzed items and
records the exclusion. Saved result configurations retain the frozen revision
and design version.

After the anonymity period, the final archival release should replace the
anonymous URL and placeholder namespace with the public v2 dataset URL and
pinned revision.
