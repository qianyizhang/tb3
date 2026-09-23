# TIGER tissue-conditioned cell count — Sol 6 xhigh

Can `openai/gpt-6-sol` at xhigh find the merged lymphocyte/plasma-cell class in three fixed `114S` ROIs and assign each cell to tissue? Run two independent conditions: image-only and official tissue-mask supplied. These are ROI tasks, not whole-slide hotspot search or clinical sTIL scoring.

The solver receives exactly three paired ROI PNGs. The supplied-mask case also receives their tissue masks; the image-only case does not. COCO cell boxes and evaluator tissue masks stay private. Output is cell centers in ROI-local pixels with compartment codes. One-to-one matching accepts a center within 20 pixels of a source box center; report cell recall/precision, signed count error and compartment accuracy among matched cells for each ROI. The same public case underlies both conditions, so their difference is diagnostic rather than a population effect.

Use `openai/gpt-6-sol` xhigh, one 3600-second attempt per condition, no automatic retry, Docker 4 CPUs/12 GiB/0 GPUs, and existing restricted transport. Pin source and runtime identities. Preview both cases and pass oracle/no-op controls before model dispatch. Review cell-box validity and any mask-code ambiguity before interpreting misses. Stop on source mismatch, leakage, invalid controls, infrastructure failure or weekly Codex usage below a 20% reserve.

## Question and method

## Inputs and reference

## Findings and limits
