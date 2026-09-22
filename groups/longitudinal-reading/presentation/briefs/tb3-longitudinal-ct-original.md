# Track CT lesions — Original image-only contract

Track CT lesions — Original image-only contract.

## Value

Tests discovery, segmentation and identity tracking without supplied lesion locations.

## Given

### Original data

Two full native CT volumes at different visits.

### Supplied helpers

Only full CTs and generic schema; no lesion locations, masks or clinical context.

### Callable tools

Each linked protocol specifies the permitted tools and execution environment.

### Reference-only material

References and permitted access follow each frozen contract. A reader-facing source or illustration is not automatically solver-visible.

## Task specification

Produce per-visit instance masks, longitudinal identities/events and a report. Follow each protocol's coordinate, identifier and access contract.

## Expected output

Produce per-visit instance masks, longitudinal identities/events and a report.

## Evaluation

Score detection, overlap, instance association and events separately. Preserve all reference instances and unchanged scientific endpoints; contract revisions do not establish matched causal comparisons.

## Difficulty

Foreground overlap can hide missed instances. Lesion inclusion, instance partition and cross-visit identity are distinct decisions.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [Image-only longitudinal CT — Astra medium](../../experiments/longitudinal-ct-image-only-astra-medium/protocol.md)
- [Image-only longitudinal CT — Sol xhigh](../../experiments/longitudinal-ct-image-only-sol-xhigh/protocol.md)
