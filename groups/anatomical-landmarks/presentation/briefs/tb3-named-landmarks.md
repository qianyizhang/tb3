# Locate named anatomy and detect unavailable targets

Locate named anatomy and detect unavailable targets.

## Value

Measures spatial anatomical knowledge and appropriate abstention outside the acquired field of view.

## Given

### Original data

Native CT or MRI volumes; named landmark targets.

### Supplied helpers

Target names are supplied. Field of view, target inventory and atlas assistance vary by condition.

### Callable tools

Each linked protocol specifies the permitted tools and execution environment.

### Reference-only material

References and permitted access follow each frozen contract. A reader-facing source or illustration is not automatically solver-visible.

## Task specification

Return landmark locations in the specified native/world coordinates, or the required unavailable-target response. Follow each protocol's coordinate, identifier and access contract.

## Expected output

Return landmark locations in the specified native/world coordinates, or the required unavailable-target response.

## Evaluation

Physical localization and availability endpoints stay separate; use the full specified target denominator.

## Difficulty

Naming the target does not give its position. Coordinate errors, localization errors and unavailable-target hallucination require separate endpoints.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [BR-036 — semantic landmark localization on CT and MRI](../../experiments/br036/protocol.md)
- [BR-038 — coordinate audit and remaining localization errors](../../experiments/br038/protocol.md)
- [BR-039 — Expanded CT landmarks and unavailable-target hallucination](../../experiments/br039/protocol.md)
- [BR-040 — Sol/xhigh CT and MRI landmark comparison](../../experiments/br040/protocol.md)
