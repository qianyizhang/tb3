# Segment dental anatomy — F002 contract v2

Segment dental anatomy — F002 contract v2.

## Value

Tests semantic dental segmentation, including small structures and tooth identity.

## Given

### Original data

Full native F002 dental CBCT; source hashes and geometry remain in the linked protocols.

### Supplied helpers

Explicit revised label/convention contract; the paired assistance condition supplies an annotated F008 example.

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

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| No annotated example | F002 CT and v2 label contract | Infer boundaries and apply the contract |
| F008 example | F002 target plus F008 CT and annotation | Transfer the convention without copying target anatomy |

## Difficulty

Fine pulp/canal structure, source geometry and annotation conventions complicate voxel overlap. An annotated example supplies a labeling convention as well as visual assistance.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [Dental F002 v2 contract — Astra medium without example](../../experiments/dental-f002-contract-v2-astra-medium/protocol.md)
- [Dental F002 v2 contract — Astra medium with annotated example](../../experiments/dental-f002-reference-v2-astra-medium/protocol.md)
