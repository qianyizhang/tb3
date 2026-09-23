# Audit supplied anatomical labels

Audit supplied anatomical labels.

## Value

Tests whether an agent can identify erroneous labels without raising false alarms on clean anatomy.

## Given

### Original data

Patient DICOM / CT and supplied named spatial labels.

### Supplied helpers

Existing annotations and focus lists; clean and altered cases remain separate.

### Callable tools

Each linked protocol specifies the permitted tools and execution environment.

### Reference-only material

References and permitted access follow each frozen contract. A reader-facing source or illustration is not automatically solver-visible.

## Task specification

Return affected label identities and spatial witnesses; allow an empty finding list for a clean case. Follow each protocol's coordinate, identifier and access contract.

## Expected output

Return affected label identities and spatial witnesses; allow an empty finding list for a clean case.

## Evaluation

Exact label and witness checks; preserve clean-control semantics and case-specific references.

## Difficulty

Supplied labels can anchor judgment. Spatial witnesses must support the reported defect, and unchanged cases require restraint.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [BR-004 — DICOM annotation difficulty revisit](../../experiments/br004/protocol.md)
