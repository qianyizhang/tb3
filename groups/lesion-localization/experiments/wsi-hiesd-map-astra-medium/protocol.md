# HiESD gastric strip map — Astra medium

Can `openai/gpt-6-astra` at medium produce a coarse six-class map from one gastric ESD WSI? This is a selected public slide with two tissue strips, not an invasion-depth, margin or exact-gland-boundary task.

The solver sees a neutral native SVS, GT-free 64x overview, physical scale and crop helper. It returns a 623 × 448 single-channel PNG with codes 1–6 for the six released classes and 0 for unknown. The private evaluator rasterizes the source coarse-grid XML. It scores coverage and class correctness only on annotated pixels, and accuracy among the pixels the agent chooses to label. Unannotated tissue is not normal reference. The released category PNG's interpolated colors are not used as separate classes.

Use `openai/gpt-6-astra` medium, one 3600-second attempt, no automatic retry, Docker 4 CPUs/12 GiB/0 GPUs, and existing restricted transport. Preview and run oracle/no-op controls before dispatch. Review coarse XML mapping and visual overlays before interpreting a result. Stop on source mismatch, leakage, invalid controls or infrastructure failure. Apply the one-time quota preflight in `docs/workflow.md`; a lower-cost condition or shorter timeout requires user acceptance before launch.

## Question and method

## Inputs and reference

## Findings and limits

### Diagnostic observation — 2026-09-23

`attempt-97fa20fa8e884676` completed with `gpt-6-astra` medium in Harbor, no terminal exception, unchanged frozen task bytes, and a valid 623 × 448 single-channel output (`reward=1` for the artifact contract). The private result `observation-c0a0bd2dc1595143f6cc62e2` scored 10,088 labeled pixels of 11,290 annotated XML-grid pixels (coverage 0.894), of which 3,222 had the correct class. That is 0.285 of all annotated pixels and 0.319 of labeled annotated pixels. The crop helper logged 19 calls; the inspected 8 shell commands showed no explicit access to private `tests/` or `solution/` paths.

Post-hoc inspection of the saved map and private coarse reference shows the output used only classes 1, 2, 3 and 6; it never emitted codes 4 (normal glands) or 5 (well differentiated adenocarcinoma). Within annotated pixels, class 1 (chronic gastritis) was correct on 1,252/6,911; class 2 on 1,106/1,796; class 3 on 71/100; class 4 on 0/121; class 5 on 0/361; class 6 on 793/2,001. This is a diagnostic description of one slide, not a class-level population estimate. The map also labels unannotated tissue, which the reference does not establish as normal or abnormal. The [source/reference/result figure](../../findings/figures/wsi-hiesd-astra-coarse-map.jpg) uses the same 623 × 448 grid and categorical colors; the reference overlay is evaluator-only and was made after the run. Coarse XML boundaries and unannotated tissue prevent fine gland, margin or invasion-depth claims.
