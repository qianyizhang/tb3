# HiESD gastric strip map — Sol 6 xhigh

Can `openai/gpt-6-sol` at xhigh produce a coarse six-class map from one gastric ESD WSI? This is a selected public slide with two tissue strips, not an invasion-depth, margin or exact-gland-boundary task.

The solver sees a neutral native SVS, GT-free 64x overview, physical scale and crop helper. It returns a 623 × 448 single-channel PNG with codes 1–6 for the six released classes and 0 for unknown. The private evaluator rasterizes the source coarse-grid XML. It scores coverage and class correctness only on annotated pixels, and accuracy among the pixels the agent chooses to label. Unannotated tissue is not normal reference. The released category PNG's interpolated colors are not used as separate classes.

Use `openai/gpt-6-sol` xhigh, one 3600-second attempt, no automatic retry, Docker 4 CPUs/12 GiB/0 GPUs, and existing restricted transport. Preview and run oracle/no-op controls before dispatch. Review coarse XML mapping and visual overlays before interpreting a result. Stop on source mismatch, leakage, invalid controls or infrastructure failure. Apply the one-time quota preflight in `docs/workflow.md`; a lower-cost condition or shorter timeout requires user acceptance before launch.

## Question and method

## Inputs and reference

## Findings and limits
