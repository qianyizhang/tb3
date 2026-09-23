# TIGER tissue-conditioned cell count — Astra medium

Can `openai/gpt-6-astra` at medium find the merged lymphocyte/plasma-cell class in three fixed `114S` ROIs and assign each cell to tissue? Run two independent conditions: image-only and official tissue-mask supplied. These are ROI tasks, not whole-slide hotspot search or clinical sTIL scoring.

The solver receives exactly three paired ROI PNGs. The supplied-mask case also receives their tissue masks; the image-only case does not. COCO cell boxes and evaluator tissue masks stay private. Output is cell centers in ROI-local pixels with compartment codes. One-to-one matching accepts a center within 20 pixels of a source box center; report cell recall/precision, signed count error and compartment accuracy among matched cells for each ROI. The same public case underlies both conditions, so their difference is diagnostic rather than a population effect.

Use `openai/gpt-6-astra` medium, one 3600-second attempt per condition, no automatic retry, Docker 4 CPUs/12 GiB/0 GPUs, and existing restricted transport. Pin source and runtime identities. Preview both cases and pass oracle/no-op controls before model dispatch. Review cell-box validity and any mask-code ambiguity before interpreting misses. Stop on source mismatch, leakage, invalid controls or infrastructure failure. Apply the one-time quota preflight in `docs/workflow.md`; a lower-cost condition or shorter timeout requires user acceptance before launch.

## Question and method

## Inputs and reference

## Findings and limits

### Paired diagnostic observations — 2026-09-23

Both Astra medium conditions completed in Harbor with no exception, valid answer artifacts (`reward=1`), unchanged frozen task bytes and private-score observations. The image-only attempt is `attempt-582f254a1a1a43e3` / `observation-8f8d8a9d38f610159e0f8fbb`; tissue-supplied is `attempt-7cb2fd0dca184603` / `observation-a87accfd5e23b8e90fbb0f31`. The inspected command traces showed no explicit access to private `tests/` or `solution/` paths.

| ROI (reference cells) | Image-only matched / predicted | Image-only matched compartment accuracy | Tissue-supplied matched / predicted | Tissue-supplied matched compartment accuracy |
| --- | ---: | ---: | ---: | ---: |
| roi1 (20) | 9 / 16 | 0% | 7 / 10 | 100% |
| roi2 (175) | 136 / 154 | 12.5% | 141 / 176 | 100% |
| roi3 (323) | 250 / 278 | 64% | 232 / 255 | 99.1% |

Matching uses one-to-one cell centers within 20 ROI-local pixels. The supplied tissue masks directly encode the compartment reference, so their near-perfect matched-cell attribution checks use of that assistance rather than independent tissue inference. Cell matching changes in different directions across ROIs; one stochastic attempt per condition on the same three public ROIs cannot establish a causal improvement or generalization. ROI1 has only 20 reference cells. No full-slide hotspot or clinical sTIL claim follows from these fixed ROIs.
