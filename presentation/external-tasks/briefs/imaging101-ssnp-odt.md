# Recover 3D refractive index from complex optical fields

Implement a computational method to recover 3D refractive index from complex optical fields.

## Value

This imaging problem tests the computational step between acquired measurements and an interpretable image or physical-property map.

## Given

### Original data

Multi-angle measurements containing both amplitude and phase.

### Supplied helpers

Optical geometry and a split-step nonparaxial propagation model. The assistance level can add an approach and software design.

### Callable tools

Python and the task’s numerical/model dependencies. End-to-end, function-level and planning modes assess different work.

### Reference-only material

Reference arrays or published outputs, when listed by the README, support evaluation. Some tasks package ground truth alongside raw data; solver-visible staging has not been audited.

## Task specification

Implement the linked README’s forward/inverse problem with its array conventions and units. The expected artifact below describes the scientific result; the selected harness mode owns exact filenames and callable signatures.

## Expected output

A reconstructed 3D refractive-index volume.

## Evaluation

End-to-end mode compares numerical outputs where a reference exists; the project uses metrics including correlation and normalized error. Function tests and plan judgments are separate. Task-specific metric availability has not been replayed.

## Visual explanation

### Workflow

- Multi-angle measurements containing both amplitude and phase
- Recover 3D refractive index from complex optical fields
- A reconstructed 3D refractive-index volume

### Input

**Contract view; native sample not yet illustrated.** Multi-angle measurements containing both amplitude and phase.

### Supplied helpers

**Given material, not an answer reveal.** Optical geometry and a split-step nonparaxial propagation model. The assistance level can add an approach and software design.

### Reference or output

**Expected artifact, not an actual prediction.** A reconstructed 3D refractive-index volume.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Difficulty

Measured phase reduces one ambiguity, but multiple scattering and limited angles still constrain depth recovery.

## Sources

- [Pinned task README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/ssnp_odt/README.md)
- [Evaluation modes and assistance](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/README.md)

## Coverage

One scientific task definition across L1/L2/L3 assistance. This collection includes non-medical astronomy, optics and Earth-science tasks as well as medical imaging.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.
