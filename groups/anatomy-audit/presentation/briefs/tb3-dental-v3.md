# Segment dental anatomy — F018 contract v3

Segment dental anatomy — F018 contract v3.

## Value

Tests semantic dental segmentation, including small structures and tooth identity.

## Given

### Original data

Full native F018 dental CBCT; source hashes and geometry remain in the linked protocols.

### Supplied helpers

Further operational label boundaries in v3; example and no-example conditions remain separate.

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
| No annotated example | F018 CT and v3 label boundaries | Infer target anatomy under the explicit boundaries |
| F008 example | F018 target and v3 contract plus F008 CT/annotation | Apply the demonstrated convention to the new target |

## Difficulty

Fine pulp/canal structure, source geometry and annotation conventions complicate voxel overlap. An annotated example supplies a labeling convention as well as visual assistance.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [Dental F018 contract v3 — Astra medium without example](../../experiments/dental-f018-contract-v3-astra-medium/protocol.md)
- [Dental F018 contract v3 — Astra medium with F008 example](../../experiments/dental-f018-reference-v3-astra-medium/protocol.md)
