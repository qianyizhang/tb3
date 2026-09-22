# Reconstruct an image from sparse CT projections

Recover a 256 × 256 synthetic phantom from noisy measurements at 30 projection angles.

## Value

Sparse acquisition illustrates the tradeoff between fewer measurements and reconstruction artifacts. This example uses a mathematical phantom, not patient anatomy.

## Given

### Original data

A sparse sinogram of 256 detectors × 30 angles, plus projection angles and acquisition metadata.

### Supplied helpers

README method hints at L1; an approach document at L2; approach and software design at L3.

### Callable tools

A coding environment with task dependencies. Function mode and planning mode assess different capabilities.

### Reference-only material

Reference-image metrics require ground truth. The README lists full projections and ground truth among task assets; solver-visible staging remains unverified.

## Task specification

For end-to-end evaluation, implement the reconstruction pipeline and produce output/reconstruction.npy.

## Expected output

A reconstructed image array. Input and reference data have explicit dimensions in the task README.

## Evaluation

End-to-end quality uses reference-image metrics such as NCC/NRMSE. Function tests and plan judgments are separate evaluation modes.

## Visual explanation

### Workflow

- 30 noisy projection angles
- Implement inverse reconstruction
- 256 × 256 image

### Input

![Actual 30-angle CT sinogram](../../../presentation/tours/data/task-briefs/imaging101-input.png)

Downloaded measurements, not a schematic. Each column records attenuation from one angle; the task turns these projections into an image.

### Supplied helpers

Assistance is textual: README at L1, approach at L2, and software design at L3. These levels do not add an image overlay.

### Reference or output

![Phantom and published reconstructions](../../../presentation/tours/data/task-briefs/imaging101-reference.png)

Left: ground truth. Middle: published filtered backprojection (FBP). Right: published total-variation (TV) reconstruction. Common 0–1 display scale exposes streak artifacts. Upstream reference arrays, not new agent results. All four downloaded assets match published SHA-256 checksums; asset license: MIT.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| L1 · README | Task description + data + requirements | Design the algorithm and software, then implement. |
| L2 · + approach | A proposed algorithmic approach | Design the software and implement the approach. |
| L3 · + design | Approach + software design | Implement the supplied design. |

## Difficulty

Only 30 of 180 angular samples are used in the stated problem. Supplied plans reduce algorithm-design work; they do not add measurement angles.

## Sources

- [Preview image notices](../../../presentation/task-explorer/assets/NOTICES.md)
- [Preview image manifest](../../../presentation/task-explorer/assets/manifest.json)

- [Sparse-view CT task](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/ct_sparse_view/README.md)
- [Evaluation modes and assistance](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/README.md)
- [Assistance staging code](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/evaluation_harness/runner.py)

- [Pinned task assets](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/ct_sparse_view)
- [Published checksums](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/assets_manifest.json)
- [Sample download and rendering receipt](../samples.json)

## Coverage

Also: MRI reconstruction and parameter mapping, PET, ultrasound and other scientific inverse problems. The inspected tree has 58 task directories; not all are medical.

## Gaps

The two Imaging-101 PNGs remain optional local previews. The pinned asset manifest declares MIT, but its full copyright and permission notice has not been recovered; these two files are not retained in Git.

The README lists full projections and ground truth among task assets. Solver-visible staging still needs checking before asserting what is withheld.
