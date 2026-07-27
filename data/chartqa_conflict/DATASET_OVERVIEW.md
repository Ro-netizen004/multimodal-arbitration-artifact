# ChartQA-Conflict dataset overview

ChartQA-Conflict is a curated same-question conflict benchmark derived from the
ChartQA test set. Each item contains one genuine chart and one
evidence-bearing textual report. Both sources answer the same question but
support different answers:

- `chart_answer` is supported by the original chart.
- `report_answer` is supported by the accompanying counterfactual report.

The reports preserve the question's answer type and unit. Counterfactual
values were assigned using a unit-preserving permutation so that the two
candidate answers remain distinguishable during strict source attribution.
Other facts in a report are retained only when they remain internally
consistent with the counterfactual answer.

## Size and audit

- Frozen construction: 230 reviewed items.
- Primary analyzed set: 229 items.
- Excluded compiled item: `conflict_id=45`.
- Exclusion reason: the final audit found that its report did not sufficiently
  entail the report-supported answer.
- Frozen construction manifest SHA-256:
  `388bce0572487024f5ac12261621cbab8931ec3032d8bf0c65a258c134d20842`.
- Design version: `chartqa-same-question-conflict-v4`.

## Item fields

| Field | Meaning |
|---|---|
| `conflict_id` | Stable index in the curated conflict set |
| `chartqa_test_index` | Index of the source item in the ChartQA test split |
| `question` | Shared question answered from either source |
| `chart_answer` | Answer supported by the chart |
| `report_answer` | Conflicting answer supported by the report |
| `text_report` | Evidence-bearing counterfactual report |
| `answer_type` | Numeric, date, Boolean, or other answer class |
| `unit_class` | Preserved unit, such as percent, count, or currency scale |
| `counterfactual_strategy` | Recorded construction operation |
| `chart_source_label` | Counterbalanced source label used for the chart |
| `report_source_label` | Counterbalanced source label used for the report |
| `source_table` | ChartQA table provenance |
| `image_file` | Relative chart-image path in the inspection release |

## Evaluation

Generated answers are classified by strict normalized matching as `chart`,
`report`, `neither`, `ambiguous`, or `invalid`. Fuzzy matching and the
arithmetic reasoning-trace rescore are not used. The chart and report are
degraded independently at L0, L2, L4, and L5; degraded variants are generated
deterministically at evaluation time rather than stored as separate dataset
rows.

The saved item-level experimental outputs in this repository are sufficient to
reproduce all reported ChartQA-Conflict statistics. The chart files and
reports are distributed separately during anonymous review when permitted;
their public archival location will be restored after the anonymity period.

## Source and licensing

Charts and original questions/answers come from ChartQA. The original ChartQA
repository distributes the dataset publicly under GPL-3.0 and requests
citation of Masry et al. (2022). The counterfactual reports and annotations are
new derivative metadata. Users remain responsible for the upstream dataset
terms and for citing ChartQA.
