# Infer only clinical context supported by CT

Infer only clinical context supported by CT.

## Value

Tests which contextual claims an agent can support from deidentified images alone.

## Given

### Original data

Two deidentified full CT volumes and retained headers.

### Supplied helpers

No supplied clinical diagnosis, dates, locations or prior output; explicit permission to answer unknown.

### Callable tools

Each linked protocol specifies the permitted tools and execution environment.

### Reference-only material

References and permitted access follow each frozen contract. A reader-facing source or illustration is not automatically solver-visible.

## Task specification

Return broad/specific context claims with evidence, confidence, alternatives and unknowns. Follow each protocol's coordinate, identifier and access contract.

## Expected output

Return broad/specific context claims with evidence, confidence, alternatives and unknowns.

## Evaluation

The evaluator checks schema/report presence only; diagnostic correctness is not established by the reward.

## Difficulty

Specific diagnoses or treatment history may be unknowable. Coincidental agreement with source metadata is not evidence of valid image inference.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [CT-only clinical context inference — Astra medium](../../experiments/longitudinal-ct-context-inference-astra-medium/protocol.md)
