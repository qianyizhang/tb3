# Trace a named coronary artery

Trace a named coronary artery.

## Value

Tests recovering one specified artery course directly from CTA.

## Given

### Original data

Full native coronary CTA.

### Supplied helpers

Named target; no supplied centerline or segmentation.

### Callable tools

Each linked protocol specifies the permitted tools and execution environment.

### Reference-only material

References and permitted access follow each frozen contract. A reader-facing source or illustration is not automatically solver-visible.

## Task specification

Return the requested artery centerline in patient coordinates. Follow each protocol's coordinate, identifier and access contract.

## Expected output

Return the requested artery centerline in patient coordinates.

## Evaluation

Path geometry and target identity; naming the target removes branch-inventory discovery.

## Difficulty

The target name supplies inventory information but not its route. Geometry and identity still need separate checks.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [BR-041 — Named coronary centerline from CTA alone](../../experiments/br041/protocol.md)
