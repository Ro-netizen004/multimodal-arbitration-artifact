# ChartQA counterfactual protocol

This protocol defines the evidence-bearing main condition used by
`scripts/run_chartqa_conflict.py`. The current automatic sampler admits only numeric and
yes/no ChartQA answers. Other answer types require a separately reviewed extension to the
parser and classifier; do not silently mix them into this experiment.

## Construction priority

For every item, keep the original question and chart unchanged. Let the chart-supported
gold answer be A. Construct a textual report containing counterfactual facts that entail a
distinct answer B to the same question. Choose B using the first feasible rule below and
record the rule in `counterfactual_strategy`:

1. `chart_value`: another plausible value actually present in the chart.
2. `nearby_category_value`: the value of an adjacent or otherwise clearly defined category.
3. `rank_swap`: a deterministic swap of the relevant ranked categories or series.
4. `arithmetic_alternative`: a plausible result from counterfactual operands stated in the
   report (for example, 100 to 120 entails a 20% increase).
5. `unit_preserving_perturbation`: a controlled perturbation with unchanged units and
   precision; use only when no chart-grounded alternative is feasible.
6. `boolean_flip`: flip yes/no and state facts that coherently entail the flipped answer.

The generic numeric perturbation in the assertion draft is a placeholder for preparing the
review sheet. It is not accepted as the evidence-bearing main condition unless a reviewer
reconstructs it as a feasible, unit-preserving counterfactual and records that strategy.

## Required checks

The curator must fill `text_answer`, `counterfactual_strategy`, `unit_class`, `text_report`,
`entailed=yes`, `counterfactual_valid=yes`, and `reviewer`. The report should state the facts
needed to answer the question and should not state “the answer is B.” Before marking the row
valid, verify all of the following:

- A and B remain different after case, punctuation, comma, decimal, percentage, and ordinary
  rounding normalization.
- B is possible under the question and is uniquely entailed by the report.
- Neither normalized answer is a substring of the other.
- Counts, percentages, currency, durations, dates/years, and other units are not mixed.
- Decimal precision and rounding match the question and the counterfactual facts.
- Dates and years retain their original representation and temporal meaning.
- Category, series, legend, and rank references remain coherent after any swap.
- For derived answers, recomputing from the report gives B.
- For yes/no items, the report contains sufficient facts for the flipped truth value.

`compile` enforces the structural and readily machine-checkable subset. The reviewer flag is
the auditable certification for semantic validity; ambiguous items should be excluded rather
than forced into the sample. Preserve the final TSV with the released manifest.

## Generated-answer attribution

Generation is classified using only the answer following the requested `####` marker. A
single terse answer-only response is accepted as a fallback; numbers are never mined from a
reasoning trace. The hierarchy is exact normalized match to A, exact normalized match to B,
ambiguous when A and B have the same canonical form, neither for another parseable answer,
and invalid for a missing or unparseable final answer. Normalization handles comma grouping,
currency symbols and names, explicit percentages, signs, decimal precision, exact fractions,
recorded units, and a fixed set of yes/no synonyms. It does not use numeric tolerances,
edit-distance matching, substring matching, or nearest-candidate assignment.

Do not apply the GSM8K lexical reasoning-trace rescore to these results. Chart explanations
can legitimately mention values from both sources, so lexical overlap is not an attribution
measure here. Report `neither` and `invalid` rates separately and compute source preference
only on exact A/B matches.
