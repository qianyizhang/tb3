# Segment dental anatomy — Original contract

Segment dental anatomy — Original contract.

## Value

Tests semantic dental segmentation, including small structures and tooth identity.

## Given

### Original data

Native dental CBCT; exact F002/F018 source and geometry remain in the experiment.

### Supplied helpers

CT plus the complete semantic taxonomy; no example masks.

### Callable tools

Each linked protocol specifies the permitted tools and execution environment.

### Reference-only material

References and permitted access follow each frozen contract. A reader-facing source or illustration is not automatically solver-visible.

## Task specification

Produce native-grid semantic masks for the specified dental structures and tooth identities. Follow each protocol's coordinate, identifier and access contract.

## Expected output

Produce native-grid semantic masks for the specified dental structures and tooth identities.

## Evaluation

Frozen voxel-label scores retain laterality, restoration-subtype and reference-convention limitations; no clinical correctness is inferred from overlap.

## Difficulty

Fine pulp/canal structure, source geometry and annotation conventions complicate voxel overlap. An annotated example supplies a labeling convention as well as visual assistance.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [Dental CBCT segmentation from CT alone — Astra medium](../../experiments/dental-ct-only-astra-medium/protocol.md)
- [Dental F018 CT-only segmentation — Astra xhigh](../../experiments/dental-f018-astra-xhigh/protocol.md)
- [Dental F002 CT-only segmentation — Astra medium](../../experiments/dental-f002-astra-medium/protocol.md)
