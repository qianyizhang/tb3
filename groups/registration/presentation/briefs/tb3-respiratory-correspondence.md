# Transfer landmarks across respiratory deformation

Transfer landmarks across respiratory deformation.

## Value

Tests whether anatomical correspondences remain recoverable across real deformation.

## Given

### Original data

Paired respiratory CT observations, supplied as a section or full source volume.

### Supplied helpers

Query landmarks and image calibration; source depth, field of view and fixed component interventions vary.

### Callable tools

Each linked protocol specifies the permitted tools and execution environment.

### Reference-only material

References and permitted access follow each frozen contract. A reader-facing source or illustration is not automatically solver-visible.

## Task specification

Return corresponding anatomical points in target patient coordinates. Follow each protocol's coordinate, identifier and access contract.

## Expected output

Return corresponding anatomical points in target patient coordinates.

## Evaluation

Physical target-point error; frozen references and transforms remain authoritative, without asserting a validated dense field.

## Difficulty

A rigid pose cannot explain general respiratory deformation. A section and a full source volume expose different amounts of contextual information.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [BR-021 — anatomical deformation in registration](../../experiments/br021/protocol.md)
- [BR-023 — fixed component interventions](../../experiments/br023/protocol.md)
- [BR-024 — harder real-deformation cases for Sol](../../experiments/br024/protocol.md)
- [BR-028 — add source depth to the failing registration case](../../experiments/br028/protocol.md)
