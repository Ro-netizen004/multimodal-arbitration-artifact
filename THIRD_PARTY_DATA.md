# Third-party data and licensing

## ChartQA-derived material

The chart images and original questions/answers in `data/chartqa_conflict/`
are derived from ChartQA. The upstream ChartQA repository distributes the
dataset under GPL-3.0 and requests citation of Masry et al. (2022). The
counterfactual reports and curation metadata are new derivative annotations.
The paired chart/table representation release is available during anonymous
review at https://anonymous-hf.com/a/p1nzaf47bbqu/. Its chart images and official
table facts remain ChartQA-derived material under the upstream terms; the rendered
plain-table images and new ablation metadata are project-created derivatives.

## GSM8K and SVAMP

The upstream GSM8K and SVAMP datasets and their complete rendered-image
collections are not redistributed here. Saved item-level outputs are included
to reproduce the reported analyses. Users rerunning inference are responsible
for obtaining and complying with the upstream datasets' terms.

The rendered conflict stimuli are distributed separately through the anonymous
stimulus mirror documented in `DATA_ACCESS.md`; their upstream problem content
remains governed by the GSM8K and SVAMP licenses.

The official GSM8K and SVAMP repositories distribute their respective datasets
under the MIT License.

## Repository license

Repository code is licensed under the MIT License; see `LICENSE`. Newly created
annotations, degradation metadata, conflict-pair mappings, exclusion records,
and saved model outputs are licensed under CC BY 4.0; see `DATA_LICENSE.md`.
These licenses cover only material created for this project. Included
third-party material remains subject to its upstream terms, and this notice
does not replace those licenses.
