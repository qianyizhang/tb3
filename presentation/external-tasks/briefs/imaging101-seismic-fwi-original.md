# Infer subsurface velocity from waveforms

Implement a computational method to infer subsurface velocity from waveforms.

## Value

This is an Earth-science inference problem: recover a physical field from incomplete observations.

## Given

### Original data

Seismic traces recorded for known source/receiver pairs.

### Supplied helpers

Source waveform, survey geometry and an initial acoustic model. The assistance level can add an approach and software design.

### Callable tools

Python and the task’s numerical/model dependencies. End-to-end, function-level and planning modes assess different work.

### Reference-only material

Reference arrays or published outputs, when listed by the README, support evaluation. Some tasks package ground truth alongside raw data; solver-visible staging has not been audited.

## Task specification

Implement the linked README’s forward/inverse problem with its array conventions and units. The expected artifact below describes the scientific result; the selected harness mode owns exact filenames and callable signatures.

## Expected output

A subsurface P-wave velocity model.

## Evaluation

End-to-end mode compares numerical outputs where a reference exists; the project uses metrics including correlation and normalized error. Function tests and plan judgments are separate. Task-specific metric availability has not been replayed.

## Visual explanation

### Workflow

- Seismic traces recorded for known source/receiver pairs
- Infer subsurface velocity from waveforms
- A subsurface P-wave velocity model

### Input

**Contract view; native sample not yet illustrated.** Seismic traces recorded for known source/receiver pairs.

### Supplied helpers

**Given material, not an answer reveal.** Source waveform, survey geometry and an initial acoustic model. The assistance level can add an approach and software design.

### Reference or output

**Expected artifact, not an actual prediction.** A subsurface P-wave velocity model.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Difficulty

Waveform mismatch is highly nonconvex; a poor starting model can converge to the wrong geology.

## Sources

- [Pinned task README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/seismic_FWI_original/README.md)
- [Evaluation modes and assistance](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/README.md)

## Coverage

One scientific task definition across L1/L2/L3 assistance. This collection includes non-medical astronomy, optics and Earth-science tasks as well as medical imaging.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.
