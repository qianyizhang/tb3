# Recover a galaxy behind a gravitational lens

Implement a computational method to recover a galaxy behind a gravitational lens.

## Value

This is an astronomy inverse problem: infer inaccessible structure from indirect light measurements.

## Given

### Original data

A noisy, blurred image of a gravitationally lensed galaxy.

### Supplied helpers

A lens model, point-spread function and shapelet basis setup. The assistance level can add an approach and software design.

### Callable tools

Python and the task’s numerical/model dependencies. End-to-end, function-level and planning modes assess different work.

### Reference-only material

Reference arrays or published outputs, when listed by the README, support evaluation. Some tasks package ground truth alongside raw data; solver-visible staging has not been audited.

## Task specification

Implement the linked README’s forward/inverse problem with its array conventions and units. The expected artifact below describes the scientific result; the selected harness mode owns exact filenames and callable signatures.

## Expected output

The inferred unlensed source-brightness distribution.

## Evaluation

End-to-end mode compares numerical outputs where a reference exists; the project uses metrics including correlation and normalized error. Function tests and plan judgments are separate. Task-specific metric availability has not been replayed.

## Visual explanation

### Workflow

- A noisy, blurred image of a gravitationally lensed galaxy
- Recover a galaxy behind a gravitational lens
- The inferred unlensed source-brightness distribution

### Input

**Contract view; native sample not yet illustrated.** A noisy, blurred image of a gravitationally lensed galaxy.

### Supplied helpers

**Given material, not an answer reveal.** A lens model, point-spread function and shapelet basis setup. The assistance level can add an approach and software design.

### Reference or output

**Expected artifact, not an actual prediction.** The inferred unlensed source-brightness distribution.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Difficulty

Lens mapping and blur mix source structure; errors in the supplied lens model can masquerade as source features.

## Sources

- [Pinned task README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/shapelet_source_reconstruction/README.md)
- [Evaluation modes and assistance](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/README.md)

## Coverage

One scientific task definition across L1/L2/L3 assistance. This collection includes non-medical astronomy, optics and Earth-science tasks as well as medical imaging.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.
