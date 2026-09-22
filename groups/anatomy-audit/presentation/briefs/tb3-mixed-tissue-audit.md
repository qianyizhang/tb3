# Find foreign tissue inside a named mask

Find foreign tissue inside a named mask.

## Value

Tests whether an agent notices tissue assigned inside the wrong named structure.

## Given

### Original data

Native abdominal CT and named organ masks.

### Supplied helpers

Proposed masks and neighboring anatomy; whole absorption, partial absorption and unchanged controls supply different cues.

### Callable tools

Each linked protocol specifies the permitted tools and execution environment.

### Reference-only material

References and permitted access follow each frozen contract. A reader-facing source or illustration is not automatically solver-visible.

## Task specification

Return host object, included anatomical class and a physical LPS witness point. Follow each protocol's coordinate, identifier and access contract.

## Expected output

Return host object, included anatomical class and a physical LPS witness point.

## Evaluation

Foreign-tissue identity and spatial witness; no contour reconstruction is required.

## Difficulty

Pure-organ recognition is insufficient: the agent must inspect mixed ownership within one mask. Whole-organ absence and partial transfer provide different cues.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [BR-017 — Substantial anatomy absorbed into an adjacent label](../../experiments/br017/protocol.md)
