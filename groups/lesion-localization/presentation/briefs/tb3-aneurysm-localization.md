# Search for aneurysms and preserve negative cases

Search for aneurysms and preserve negative cases.

## Value

Tests abnormality search with explicit negative-case handling.

## Given

### Original data

Full angiographic imaging in the frozen lesion-localization packets.

### Supplied helpers

Image and source-assistance boundaries differ by condition; a negative answer can be source-assisted.

### Callable tools

Each linked protocol specifies the permitted tools and execution environment.

### Reference-only material

References and permitted access follow each frozen contract. A reader-facing source or illustration is not automatically solver-visible.

## Task specification

Return the requested aneurysm presence/localization findings, including supported negative results. Follow each protocol's coordinate, identifier and access contract.

## Expected output

Return the requested aneurysm presence/localization findings, including supported negative results.

## Evaluation

Weak source regions support bounded localization checks; preserve v1/v2 reference changes and negative controls.

## Difficulty

The agent must decide whether a target exists before locating it. Source hints and weak reference regions constrain what a result can establish.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [BR-016 — Aneurysm localization pilot](../../experiments/br016/protocol.md)
