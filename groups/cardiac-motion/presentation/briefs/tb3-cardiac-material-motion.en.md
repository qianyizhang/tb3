# Recover cardiac material motion and compute mechanics

Recover cardiac material motion and compute mechanics.

## Value

Tests reusable reconstruction and deformation calculations under explicit observation levels.

## Given

### Original data

Synthetic calibrated ultrasound views or full volumes, depending on stage.

### Supplied helpers

Initial material mesh/axes; stage 0 also supplies reference motion and tests calculations rather than motion inference.

### Callable tools

Each linked protocol specifies the permitted tools and execution environment.

### Reference-only material

References and permitted access follow each frozen contract. A reader-facing source or illustration is not automatically solver-visible.

## Task specification

Produce reusable motion reconstruction and finite-deformation fields with physical consistency. Follow each protocol's coordinate, identifier and access contract.

## Expected output

Produce reusable motion reconstruction and finite-deformation fields with physical consistency.

## Evaluation

Separate calculations, observed/withheld images, geometry and material-motion/strain error; input stages are not equivalent.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Stage 0: calculations | Initial mesh, reference motion and anatomical axes | Compute consistent finite-deformation fields; no motion inference |
| Stage 1: sparse views | Calibrated ultrasound videos, initial mesh and axes | Recover subsequent material motion and compute fields |
| Stage 1V: source volume | Initial mesh and full native ultrasound cycle | Use volumetric observations to recover material motion |

Only documented executed stages constitute agent evidence.

## Difficulty

Correct finite-strain calculations do not prove recovered tissue motion. Sparse and volumetric observations constrain different parts of the inverse problem.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [BR-031 — cardiac agent capability ladder](../../experiments/br031/protocol.md)
