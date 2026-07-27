# ChartQA-Conflict review data

This directory contains the 229 items used in the reported
ChartQA-Conflict analyses. Each JSONL row links a native ChartQA chart to the
shared question, chart-supported answer, report-supported answer, and
evidence-bearing report. The charts are stored under `images/`.

The original frozen construction contained 230 rows. One compiled
item was excluded after a post-run entailment audit; its identifier and
exclusion reason are recorded in `excluded_items.json`.

Frozen construction manifest SHA-256:

`388bce0572487024f5ac12261621cbab8931ec3032d8bf0c65a258c134d20842`

Reviewer identities, internal workbook comments, local paths, and curation
history are not included. The source charts, questions, and original answers
come from ChartQA. Users remain responsible for the upstream dataset's terms
and citation requirements.
