# ChartQA answer-extraction audit

Phi-3.5-Vision frequently returned a bare answer on its first output line
without the requested `####` delimiter. Under delimiter-only parsing, its clean
chart-only score was 2/229 (0.009). Manual inspection showed that this was an
answer-formatting failure rather than a model-loading, image-processing, or
visual-input failure.

We therefore applied the same conservative, no-inference rescore to every
ChartQA generation and unimodal output. An explicit `####` answer remains
preferred. When it is absent, the first nonempty line is accepted only if that
entire line normalizes to one valid answer; numbers embedded in explanations or
reasoning traces are not mined. No model inference was rerun.

After excluding audited conflict item 45, Phi-3.5-Vision's corrected clean
chart-only accuracy is 166/229 (0.725). The corrected files in this directory
are the inputs used by `scripts/analyze_calibrated_slopes.py`.
