# Reconstruct canonical MRI frame associations

Repair an importer so equivalent encodings preserve every sample and its acquisition/physical coordinate. One retained Terra/high repair passes the bounded synthetic task.

## Value

Makes equivalent frame ordering and functional-group placement yield the same canonical acquisition.

## Given

### Original data

A decoded pydicom Dataset with signed int16 pixels paired with per-frame metadata. One stack, constant orthonormal orientation, equally spaced parallel slices and a complete time × echo × slice acquisition; no rescaling or compression.

### Supplied helpers

The exact reconstruction metadata profile, editable starter, unchanged JSON adapter and four public examples with expected outputs. Public examples represent two acquisitions. Time and echo each have 1–3 values, slices 2–5, rows 3–7 and columns 4–8. Geometry may be oblique with unequal row/column spacing.

### Callable tools

Python 3.12, NumPy 2.2.6, pydicom 3.0.1 and NiBabel 5.3.2 in the original environment. Other legitimate methods are allowed; added dependencies must be self-contained under the transferred answer directory. Online solutions or hints specific to the task are forbidden. Original agent limit: 1800 seconds.

### Reference-only material

Thirty-six private fixtures from twelve acquisitions, each serialized three ways, with original canonical arrays generated before serialization. Public expected outputs are solver-visible; private test arrays and the verifier are separate. Reader HTML is not a solver packet.

## Task specification

Repair `reconstruct(ds)` in `/app/answer/solution.py`. Sort actual TemporalPositionIndex and EffectiveEchoTime values; dimension descriptor ordinals do not necessarily equal actual values or their numerical order. Sort slices by increasing position projected onto the orientation normal. Preserve the pairing of each pixel frame and its metadata. Support shared or per-frame geometry according to the documented profile.

## Expected output

Return exact `pixels[time,echo,slice,row,column]`, ascending actual `temporal_indices` and `echo_ms`, and `affine_lps[4,4]` mapping `[column,row,slice,1]` to LPS mm. The first orientation vector advances columns and PixelSpacing is `[row,column]`. Origin is the first sorted slice’s first pixel centre. Singleton time/echo axes stay present.

## Evaluation

Exact pixel/temporal shapes and values; echo error ≤10⁻⁹ ms; eight corner landmark errors ≤10⁻⁵ mm; finite outputs and exact affine homogeneous row. The 36-input batch has 90 seconds on two CPUs and receives reward 1 only when every case passes. Retained Terra/high and oracle pass 36/36; starter passes 12/36. This is importer correctness, not clinical accuracy.

## Difficulty

Storage order, descriptor order, logical ordinals and actual acquisition labels are separate. Correct sample association must coexist with physical geometry and permitted macro placement. There is no remaining model-failure claim for this completed calibration.

## Coverage

Twelve private acquisitions have three correlated encodings each; four public inputs cover two further acquisitions. One completed Terra/high attempt supports a bounded pass. Full Enhanced MR IOD conformance, missing/duplicate slices, multiple stacks and clinical robustness are outside scope. The user parked the study.

## Sources

- [MRI frame association](../../experiments/mr-frame-association/protocol.md).
- [Frozen instructions](../../../../probes/mr-frame-association/instruction.md).
- [Retained result and read-only audit](../../findings/mri-importer-calibration.md).
