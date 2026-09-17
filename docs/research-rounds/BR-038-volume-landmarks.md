# BR-038 — full-volume 3D landmarks with an explicit voxel-coordinate contract

Completed: [results](BR-038-results.md) and [interpretation](BR-038-traces.md).

The user questioned BR-036's unexpectedly poor predictions and asked whether
input was a volume or image patch, then explicitly requested volume -> 3D
landmarks without coordinate-system confusion. This new user-requested audit and
retest was fixed on 2026-09-17. Exact message IDs are unavailable.

## Audit of the original setup

The original inputs were full native NIfTI volumes for the first two tasks and
inferiorly truncated **3D volumes** for the two follow-ups. No 2D image patches
were supplied as task inputs. Agents generated their own slice images and
montages from the arrays. The original output was **physical RAS millimetres**,
not screenshot pixels and not native voxel indices.

| BR-036 input | Array shape [i,j,k] | Positive voxel axes | Slice spacing |
| --- | --- | --- | --- |
| Full CT | 512 x 512 x 107 | L, P, S | 3 mm |
| Full MRI | 224 x 342 x 342 | R, A, S | 0.702 mm |
| Cropped CT | 512 x 512 x 39 | L, P, S | 3 mm |
| Cropped MRI | 224 x 342 x 197 | R, A, S | 0.702 mm |

[Independent audit](../evidence/br038-original-audit.json) verifies all old task
hashes, exact source-to-task voxel intensities, crop offsets, qform/sform,
nibabel RAS and SimpleITK LPS conversions, and independent physical-distance
rescoring. Maximum coordinate differences are below 1e-12; no index-order,
RAS/LPS, crop-affine or distance-scoring defect was found. This confirms technical
alignment, not independent clinical correctness of the source manual annotations.

Raw Codex session records also contain 7–9 structured `input_image` payloads
per original attempt ([receipt](../evidence/br038-original-image-payloads.json)).
Images were not merely represented by filenames in those records. The coding
agent had programmatic access to the whole volume and visually inspected its
rendered 2D views; this is not a native 3D medical-image encoder taking a volume
tensor as one visual input.

The cropped MRI attempt's public AC-PC-alignment assertion was inconsistent with
the native subject frame. Its AC=[0,0,0] was its own output, not a supplied anchor.
A RAS coordinate orientation does not imply MNI or AC-PC registration. The old
runs remain frozen; no result has been rewritten as the new condition.

## New input and output

Two separate tasks use the same **complete source volumes**, without spatial
cropping, downsampling or reorientation. CT has the same four queried landmarks;
MRI has all 32 AFIDs. Every queried reference is contained in its complete volume.

- `volume.npy`: raw native array, accessed exactly as `volume[i,j,k]`.
- `volume.nii.gz`: identical array with source spatial geometry.
- `geometry.json`: shape, spacing, positive-axis directions, affine and two
  arbitrary non-anatomical coordinate examples.
- `landmarks.json`: source anatomical definitions, without reference positions.
- `volume_tools.py`: array/NIfTI equivalence check, optional conversion, and
  three-plane display with original voxel axes and physical aspect ratio.

Output has a mandatory coordinate tag:

```json
{"space":"voxel_ijk_zero_based","landmarks":{"landmark_name":[i,j,k]}}
```

Indices are zero-based and may be fractional. They are neither image-display
pixels nor physical coordinates. No anatomical meaning is assigned to voxel or
world origin. Output axes are never implicitly permuted or flipped. The model
must inspect the volume; a nominal atlas coordinate is not a subject localization.
The instructions explicitly explain these distinctions and direct the model to
run the coordinate self-check. Tool use and additional image views remain free.

The verifier computes physical error as `norm(A[:3,:3] @ (pred_ijk - gt_ijk))`.
Reference indices are obtained independently with SimpleITK from the original
manual physical coordinates and cross-checked against nibabel. Tolerances remain
5 mm CT and 3 mm MRI. The evaluator rejects a wrong space tag, physical coordinates
submitted as voxels, missing names, nonfinite values and out-of-bounds points.

## Pretrial checks and frozen trials

The renderer's transpose and pixel-to-voxel mapping were checked at every pixel
of all three planes of an asymmetric 7 x 11 x 13 ramp array. Each source array
matches the independent SimpleITK read. The public helper check passes in both
prepared environments; a rendered MRI view was visually inspected. One-voxel
perturbations score exactly the corresponding physical spacing on every axis.
Oracle coordinates pass; empty, wrong-space and swapped-axis controls fail.

[Validation](../evidence/br038-validation.json) · [Freeze](../evidence/br038-freeze.json).
Matched Docker oracle/nop controls precede one fresh Terra/high attempt per task,
3,600 seconds, 2 CPUs, 4 GiB, zero retries. No prior output, reference coordinate,
review overlay or trial critique enters the image. The generic coordinate warning
and viewer scaffold are deliberate changes requested by the user.

This is not a one-factor ablation: output representation and viewer scaffolding
change, and full MRI has 32 queries rather than the earlier full-volume eight.
Report overlap descriptively, not as a causal estimate. Public-source training
exposure cannot be ruled out; subject-specific answer retrieval remains excluded.
No independent clinical adjudication or blind author solution is claimed.

## Ownership and reproduction

New sources: `probes/semantic-landmarks/authoring/br038/`.
Local arrays, task snapshots and raw jobs: `runs/br038-volume-landmarks/` and
`runs/br038-*-v1-20260917/`. Retained concise evidence: `docs/evidence/br038-*`.
The existing BR-036 freezes and unrelated BR-018/BR-037 work are preserved.
No publication or sibling submission changes are authorized by this retest.
