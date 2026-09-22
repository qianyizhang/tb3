# Recover the pose of an oblique CT section

Recover the pose of an oblique CT section.

## Value

Recovers where a section belongs in a three-dimensional acquisition.

## Given

### Original data

An oblique CT section and a target CT volume.

### Supplied helpers

Known pixel spacing and coordinate convention; full/cropped views and reconstruction kernels vary.

### Callable tools

Each linked protocol specifies the permitted tools and execution environment.

### Reference-only material

References and permitted access follow each frozen contract. A reader-facing source or illustration is not automatically solver-visible.

## Task specification

Return the rigid pixel-to-patient 4×4 transform. Follow each protocol's coordinate, identifier and access contract.

## Expected output

Return the rigid pixel-to-patient 4×4 transform.

## Evaluation

Physical grid-point error, matrix validity and orientation; not image similarity alone.

## Difficulty

The section origin and in-plane orientation matter as well as its normal. A plausible visual match can still produce the wrong physical transform.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [BR-019 — Recover an oblique CT slice pose](../../experiments/br019/protocol.md)
- [BR-020 — registration across CT reconstructions](../../experiments/br020/protocol.md)
