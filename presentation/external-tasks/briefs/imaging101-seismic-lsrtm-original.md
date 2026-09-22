# Recover subsurface reflectivity

Implement a computational method to recover subsurface reflectivity.

## Value

This is an Earth-science inference problem: recover a physical field from incomplete observations.

## Given

### Original data

Scattered seismic waveforms.

### Supplied helpers

A background velocity model, source/receiver geometry and a migration operator. The assistance level can add an approach and software design.

### Callable tools

Python and the task’s numerical/model dependencies. End-to-end, function-level and planning modes assess different work.

### Reference-only material

Reference arrays or published outputs, when listed by the README, support evaluation. Some tasks package ground truth alongside raw data; solver-visible staging has not been audited.

## Task specification

Implement the linked README’s forward/inverse problem with its array conventions and units. The expected artifact below describes the scientific result; the selected harness mode owns exact filenames and callable signatures.

## Expected output

A 2D reflectivity image.

## Evaluation

End-to-end mode compares numerical outputs where a reference exists; the project uses metrics including correlation and normalized error. Function tests and plan judgments are separate. Task-specific metric availability has not been replayed.

## Visual explanation

### Workflow

- Scattered seismic waveforms
- Recover subsurface reflectivity
- A 2D reflectivity image

### Input

**Contract view; native sample not yet illustrated.** Scattered seismic waveforms.

### Supplied helpers

**Given material, not an answer reveal.** A background velocity model, source/receiver geometry and a migration operator. The assistance level can add an approach and software design.

### Reference or output

**Expected artifact, not an actual prediction.** A 2D reflectivity image.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Difficulty

Separate weak reflected events from acquisition effects while relying on the supplied background model.

## Sources

- [Pinned task README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/seismic_lsrtm_original/README.md)
- [Evaluation modes and assistance](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/README.md)

## Coverage

One scientific task definition across L1/L2/L3 assistance. This collection includes non-medical astronomy, optics and Earth-science tasks as well as medical imaging.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.
