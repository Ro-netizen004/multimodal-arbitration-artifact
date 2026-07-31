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
- `ablation_chartqa_table/`: the matched ChartQA representation ablation in
  which each original chart is replaced by a plain table image containing the
  same source facts. It contains generation and CLL outputs for both
  degradation arms and all six CLL-capable models.

Regenerate the matched GSM8K prompt-framing comparison from the artifact root:

```bash
python scripts/analyze_role_control.py \
  --models Qwen2-VL-2B-Instruct Qwen2.5-VL-7B-Instruct \
    Idefics3-8B-Llama3 llava-onevision-qwen2-7b-ov-hf \
    Phi-3.5-vision-instruct \
  --resamples 10000
```

The role-neutral arithmetic runs were originally stored under a directory
named `role_counterbalance`. That historical name is intentionally absent from
this reviewer-facing artifact because the neutral condition is the paper's
primary analysis.
