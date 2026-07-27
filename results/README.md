# Results directory guide

The result tree is organized by each experiment's role in the paper rather
than by the historical phase names used while the project was developed.

## Primary experiments

- `main_arithmetic/`: the primary role-neutral matched-degradation experiment
  on GSM8K and SVAMP. Each benchmark contains separate `image_degradation/`
  and `text_degradation/` arms.
- `main_chartqa_conflict/`: the primary natural-visual ChartQA-Conflict
  experiment, again separated into image and text degradation arms.

## Calibration and controls

- `calibration/`: unimodal accuracy measurements and derived calibrated-slope
  summaries. These quantify how much task-relevant information each
  degradation removes.
- `prompt_framing_control/`: the earlier text-designating prompt runs and the
  direct original-versus-neutral comparison. These are controls, not the
  primary arithmetic results.
- `supplementary/`: character/OCR-survival checks and other supporting outputs.

The role-neutral arithmetic runs were originally stored under a directory
named `role_counterbalance`. That historical name is intentionally absent from
this reviewer-facing artifact because the neutral condition is the paper's
primary analysis.
