# A repaired importer preserves the retained acquisition associations

The retained Terra/high attempt passed **36/36 private fixtures from 12 acquisitions**. The three encodings per acquisition are correlated. This completed calibration does not support the proposed frame-association failure hypothesis; the user parked the study.

| Same frozen task checksum | Ordered/shared | Shuffled/shared | Shuffled/per-frame | Original reward |
| --- | --- | --- | --- | --- |
| Terra/high, one attempt | 12/12 | 12/12 | 12/12 | 1 |
| Oracle control | 12/12 | 12/12 | 12/12 | 1 |
| Starter / no-op | 12/12 | 0/12 | 0/12 | 0 |

## Contract and reference fitness

- **Input:** decoded pydicom Dataset; frame pixels remain paired with their functional-group metadata. Four public encodings from two additional acquisitions include expected outputs.
- **Output:** exact samples in `[time,echo,slice,row,column]`, sorted actual temporal indices and echo times, plus an affine mapping `[column,row,slice,1]` into LPS mm. Singleton time/echo axes remain present.
- **Geometry:** slices sort by position dotted with the cross product of the two orientation vectors. DICOM PixelSpacing is `[row,column]`; the first orientation vector advances a column. The origin is the first sorted slice’s first pixel centre.
- **Private truth:** canonical arrays were generated before serialization. The read-only audit independently reproduces the pinned recipe in memory, checks all 40 public/private encodings and **16,749 sample values**, verifies raw little-endian samples against pydicom decoding, and checks every frame’s unique metadata association and ordinal mapping. It never executes the old authoring module or writes a frozen fixture.
- **Scorer:** exact shape, sample values and temporal labels; echo error ≤10⁻⁹ ms; eight physical corner errors ≤10⁻⁵ mm; finite affine and exact homogeneous row. This is numerical importer correctness, not anatomical or clinical accuracy.

The task explicitly states that dimension ordinals may differ from actual values and their sort order. The [DICOM dimension definition](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.17.html) also distinguishes logical indices from the referenced attribute values. The frozen task, rather than an evolving standard, defines this pilot’s narrower required behavior.

## Observable repair and intermediate check

The [saved answer](../../../runs/mr-terra-high-v1-20260914/mr-frame-association__5L3qSjg/artifacts/app/answer/solution.py) looks up shared or per-frame geometry, sorts actual acquisition labels and slice projections, routes each intact sample tile to its canonical slot, and constructs the affine with correctly assigned spacings. It does not need to use dimension descriptors.

- **Trace step 13:** all four public examples pass.
- **Step 15:** the repair tightens its slice-grouping tolerance.
- **Step 16:** moving public geometry from shared to per-frame groups produces an exact dictionary-equality assertion failure; all four numerical public checks still pass.
- **Step 17:** inspection finds zero sample/label differences and a maximum affine-entry difference of **2.948752353404416×10⁻¹³**. Local replay reproduces that exact difference and a maximum physical corner error of **2.9827988255067856×10⁻¹³ mm**, well within the frozen bound.

The [observable trajectory](../../../runs/mr-terra-high-v1-20260914/mr-frame-association__5L3qSjg/agent/trajectory.json) and original verifier report retain the intermediate failure and later 36/36 pass. Normal agent execution took 150.284386 seconds; this is one retained execution, not a new timing measurement.

## Controls and interpretation

The read-only audit replays the three saved answers against all 36 frozen private cases and reproduces their reports exactly. It uses existing NumPy 2.2.6 and pydicom 3.0.2; the original image pinned pydicom 3.0.1. This confirms current local numerical replay, not identical runtime recovery.

The starter’s shuffled/shared variants have eight shape failures and four sample-value failures. All twelve per-frame variants fail at the shared-only geometry lookup. These are distinct importer failures under the supplied profile. Post-hoc output controls isolate spacing and labels: swapped row/column spacing passes only the three encodings of the isotropic control; logical echo ordinals pass 0/36. Neither diagnostic is a model trial.

## Limits and disposition

The profile has one stack, constant orthonormal orientation, equally spaced parallel slices, a complete Cartesian acquisition and uncompressed signed samples without rescaling. Full clinical Enhanced MR conformance, missing/duplicate slices, single-frame inputs, multiple stacks and broader robustness remain untested. The original source benchmark’s withheld failures are not this pilot’s test cases.

The [idea and accepted parking decision](../ideas/idea-mr-frame-association.md) remain authoritative. This assistant-authored result explanation preserves the original outcome; it does not promote the task or reopen research.

## Inspectable sources

- [Frozen task](../../../probes/mr-frame-association/instruction.md), [original freeze](../../../docs/evidence/mr-pilot-freeze.json) and [original trial summary](../../../docs/evidence/mr-trial-summary.json).
- [Source audit](../presentation/sources/mri-importer-audit.json), [read-only audit utility](../../../scripts/audit_mri_importer_evidence.py), [record evidence manifest](evidence/mri-importer-calibration.json).
- [Teaching source pack](../../../presentation/task-explorer/mri-importer/NOTICE.md) and [canonical story](../presentation/stories/mri-importer.story.md). Pixel tiles are exact synthetic source samples, not patient MRI. Association highlighting is a teaching traversal, not a solver trajectory.
