# Calibrate promptable segmenters on CT slices

Calibrate promptable segmenters on CT slices.

## Value

Establishes bounded tool behavior and runtime costs before selecting a segmenter for an agent.

## Given

### Original data

One known public CT; six organs and 18 reference-selected organ/slice pairs.

### Supplied helpers

GT-derived slices and boxes expanded by 2 or 10 pixels; direct local SAM2/LiteMedSAM inference.

### Callable tools

Each linked protocol specifies the permitted tools and execution environment.

### Reference-only material

Reference access follows the author-study protocol and can include privileged inputs.

## Task specification

Compare slice masks and synchronized inference timings. Follow each protocol's coordinate, identifier and access contract.

## Expected output

Compare slice masks and synchronized inference timings.

## Evaluation

2D overlap, boundary distance and latency. This is privileged tool calibration, not a whole-volume agent segmentation task.

## Difficulty

Reference-derived boxes and slices already provide localization. Correlated slices from one known CT do not measure autonomous discovery or generalization.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [SAM 2.1 Small versus LiteMedSAM: narrow Mac slice calibration](../../experiments/sam-litemedsam-slice-calibration/protocol.md)
