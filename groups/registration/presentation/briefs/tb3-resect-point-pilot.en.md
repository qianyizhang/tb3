# Correct two MRI-to-ultrasound point correspondences

Correct two MRI-to-ultrasound point correspondences.

## Value

Tests local correspondence correction while preserving an already-close initialization.

## Given

### Original data

Two full FLAIR / pre-resection ultrasound pairs and an MRI query point for each.

### Supplied helpers

Initial US candidate copies the MRI world coordinate; generic orthogonal viewer. No tumor masks in this pilot.

### Callable tools

Each linked protocol specifies the permitted tools and execution environment.

### Reference-only material

References and permitted access follow each frozen contract. A reader-facing source or illustration is not automatically solver-visible.

## Task specification

Return a retained or corrected US voxel point with confidence and image evidence for each query. Follow each protocol's coordinate, identifier and access contract.

## Expected output

Return a retained or corrected US voxel point with confidence and image evidence for each query.

## Evaluation

TRE in mm and improvement relative to the copied-coordinate no-op; retain harmful overcorrections. Two selected queries are not population validation.

## Difficulty

MRI and ultrasound appearance differ. Copying the shared coordinate can already be strong, so unnecessary movement can make an answer worse.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [RESECT standard/challenge point audit — Astra medium](../../experiments/resect-point-audit-astra-medium/protocol.md)
