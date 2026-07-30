# Reported experiment metadata

`configs/paper_experiments.yaml` is the canonical compact configuration for
the matched-degradation experiments reported in the paper. The older
development-wide configuration is intentionally not included because it
contains settings for experiments outside the submitted paper.

## Checkpoints

The reported open-weight models were loaded from the six Hugging Face
repository identifiers recorded in the configuration, without quantization.
Exact Hub commit hashes were not persisted in the original run metadata; the
artifact therefore does not invent revisions after the fact. The runs used the
repository defaults available at execution time with Transformers 4.49.0.
This limitation should also be disclosed in the paper's reproducibility
statement.

## Generation and scoring

- Open-model arithmetic generation: greedy decoding, 256 new-token limit.
- Open-model ChartQA generation: greedy decoding, 128 new-token limit.
- Candidate CLL: teacher-forced continuation scoring under the same
  multimodal context, reported as mean log probability per answer token.
- Main endpoint: paired L0-to-L5 item contrast.
- Uncertainty: 10,000 paired bootstrap resamples.
- Tests: two-sided Wilcoxon signed-rank and 10,000 random sign flips.

Prompt construction, chat-template handling, candidate token boundaries, and
normalization are implemented in `src/models.py`, `scripts/run_legibility.py`,
and `scripts/run_chartqa_conflict.py`.

## Hardware and software

Runs used one NVIDIA L40S 48 GB GPU per open-model job. Exact library versions
are recorded in `configs/paper_experiments.yaml` and the top-level README.
