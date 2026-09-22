# Construct deforming meshes from supplied masks

Construct deforming meshes from supplied masks.

## Value

Separates mesh construction from material-motion inference after segmentation is provided.

## Given

### Original data

Full-cycle binary masks; paired condition adds registered ultrasound.

### Supplied helpers

All-phase segmentation is supplied, but persistent material coordinates and the reference mesh are withheld.

### Callable tools

Each linked protocol specifies the permitted tools and execution environment.

### Reference-only material

References and permitted access follow each frozen contract. A reader-facing source or illustration is not automatically solver-visible.

## Task specification

Build a shared tetrahedral mesh across phases and compute F, Green–Lagrange E and J. Follow each protocol's coordinate, identifier and access contract.

## Expected output

Build a shared tetrahedral mesh across phases and compute F, Green–Lagrange E and J.

## Evaluation

Construction and independent field recomputation are separate from material-motion/strain accuracy. Clinical cavity replay does not validate myocardial strain.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Masks only | All-phase binary masks | Build shared material geometry and estimate correspondence |
| Masks and images | Identical masks plus registered ultrasound | Use appearance to constrain material motion |

## Difficulty

Different material maps can fit the same moving boundary. Accurate masks and algebraically correct deformation fields can coexist with incorrect tissue motion.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [BR-035 — Segmentation supplied, geometry and mechanics separated](../../experiments/br035/protocol.md)
