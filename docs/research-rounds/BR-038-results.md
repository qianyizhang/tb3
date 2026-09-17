# BR-038 — full-volume voxel-landmark retest

[Setup and coordinate audit](BR-038-volume-landmarks.md) · [Measured results](../evidence/br038-results.json) · [Interpretation](BR-038-traces.md) · [Voxel-axis overlays](../../runs/br038-volume-landmarks/review/index.html)

Complete native volumes were supplied. Outputs are tagged zero-based [i,j,k] array indices; the verifier converts differences to millimetres. No crop or screenshot-coordinate output is involved.

| Task | Accepted | Mean / max error | Duration | Coordinate check / supplied viewer |
| --- | ---: | --- | ---: | --- |
| ct-full | 2/4 | 18.094 / 35.146 mm | 488 s | True / True |
| mri32-full | 3/32 | 9.402 / 28.235 mm | 265 s | True / True |

## ct-full

Normal completion: True; reward: 0.0; contract valid: True.

| Landmark | Error mm | Within tolerance |
| --- | ---: | --- |
| chin | 2.724 | True |
| mand_r | 32.072 | False |
| mand_l | 35.146 | False |
| odont_proc | 2.436 | True |

## mri32-full

Normal completion: True; reward: 0.0; contract valid: True.

| Landmark | Error mm | Within tolerance |
| --- | ---: | --- |
| 1 | 0.716 | True |
| 2 | 4.769 | False |
| 3 | 5.541 | False |
| 4 | 4.417 | False |
| 5 | 8.260 | False |
| 6 | 8.592 | False |
| 7 | 7.496 | False |
| 8 | 7.764 | False |
| 9 | 5.953 | False |
| 10 | 4.294 | False |
| 11 | 4.908 | False |
| 12 | 5.345 | False |
| 13 | 5.325 | False |
| 14 | 7.366 | False |
| 15 | 16.680 | False |
| 16 | 17.268 | False |
| 17 | 11.658 | False |
| 18 | 12.839 | False |
| 19 | 23.866 | False |
| 20 | 1.555 | True |
| 21 | 2.616 | True |
| 22 | 5.939 | False |
| 23 | 5.757 | False |
| 24 | 3.912 | False |
| 25 | 11.261 | False |
| 26 | 12.322 | False |
| 27 | 8.481 | False |
| 28 | 10.270 | False |
| 29 | 28.235 | False |
| 30 | 27.412 | False |
| 31 | 10.041 | False |
| 32 | 10.015 | False |

The fixed limits are 5 mm for CT and 3 mm for MRI. These are reference-agreement thresholds, not clinical standards. An all-target reward requires every queried point to pass. Public reference use and coordinate-helper usage are audited in the receipt.

These new runs change output representation and display scaffolding. The MRI also changes query set/FOV relative to earlier conditions. One attempt per condition cannot isolate causality or establish population accuracy.
