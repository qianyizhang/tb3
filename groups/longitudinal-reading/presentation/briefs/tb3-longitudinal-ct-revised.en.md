# Track CT lesions — Revised inclusion and instance contract

Track CT lesions — Revised inclusion and instance contract.

## Value

Tests lesion tracking under explicit generic inclusion and touching-instance rules.

## Given

### Original data

Two full native CT volumes at different visits.

### Supplied helpers

Revised touching-lesion and inclusion rules; the supplied-context condition adds broad clinical prior information.

### Callable tools

Each linked protocol specifies the permitted tools and execution environment.

### Reference-only material

References and permitted access follow each frozen contract. A reader-facing source or illustration is not automatically solver-visible.

## Task specification

Produce per-visit instance masks, correspondences/events and uncertain-candidate decisions. Follow each protocol's coordinate, identifier and access contract.

## Expected output

Produce per-visit instance masks, correspondences/events and uncertain-candidate decisions.

## Evaluation

Score detection, overlap, instance association and events separately. Preserve all reference instances and unchanged scientific endpoints; contract revisions do not establish matched causal comparisons.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Image only | Full CT pair and revised generic instructions | Discover lesions and infer inclusion, instances and events |
| Broad context supplied | Same second-patient CT pair plus released broad clinical context | Use context without supplied locations or instance identities |

## Difficulty

Revised wording does not supply locations. Added broad clinical context changes priors, and changing the patient changes the case.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [Revised image-only CT instructions — Astra medium](../../experiments/longitudinal-ct-v2-astra-medium/protocol.md)
- [Second image-only CT case: persistent and new lesions — Astra medium](../../experiments/longitudinal-ct-case02-astra-medium/protocol.md)
- [Paired CT lesions with verified broad clinical context — Astra medium](../../experiments/longitudinal-ct-context-supplied-astra-medium/protocol.md)
