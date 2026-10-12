# BR-026 vessel repair: a small gap in a connected network

The retained V01 Terra/high attempt added **198 voxels**, all inside the
**200-voxel authored deletion**, restored the tested right-Pcom connection, and
made no other edits. Current reconstruction reproduces nine logged threshold
sizes, both contact-patch counts, the saved mask, and all 12 frozen verifier
checks. This is calibration using real MRA and a synthetic mask defect.

## Task and reference boundary

- **Input:** TopCoW 2024 MRA case 007, a native 187 × 132 × 53 crop, proposed
  binary mask, editable region, and NIfTI geometry. Source intensities were unchanged.
- **Return:** repair a supported defect or return an acceptable mask unchanged.
  Preserve the native grid, affine and surrounding mask. Symmetry is not required.
- **Private reference:** source mask, branch labels, local corridors, anchors and
  mask-derived centerlines. These are engineering references, not independent
  clinical adjudication, and were excluded from the agent image.
- **Condition:** a 1.8 mm-radius authored deletion removes 200 right-Pcom mask
  voxels. This is a mask corruption, not a vessel injury or natural model error.

The [retained results](../../../docs/research-rounds/BR-026-results.md),
[freeze](../../../docs/evidence/br026-freeze.json) and
[trace review](../../../docs/evidence/br026-trace-review.json) establish controls,
source/reference fitness, and the companion unchanged-case dispute. This analysis
reads the actual arrays, trajectory, saved output and scorer.

## Observable process

Attempt `vessel-v01__c6dKGRX` is under
`runs/br026-vessel-v01-terra-high-v1-20260916/`. It contains 32 trace steps and
300.813302 seconds of recorded agent time. Terra/high matches the requested and
trace-recorded setting; this is not independent provider attestation.

| Stage | Trace evidence | Supported interpretation |
| --- | --- | --- |
| Inspect | Steps 7–15 inspect metadata, projections and native montages. | Volumetric image context was available and viewed. |
| Find candidates | Steps 17–20 measure bright unmasked components and review six selected groups. | Brightness produces multiple candidates; the largest is not automatically the gap. |
| Review locally | Steps 21–27 show details and check orientation. | Signal and mask ends are discernible in selected delivered views. |
| Scan thresholds | Step 28 tests nine thresholds at seed `(66,76,15)`. | The selected component expands from 89 voxels at 250 to 198 at 165. |
| Test contacts | Step 29 checks candidate voxels adjacent to the mask. | At 165, two distinct patches contain 32 and 33 voxels. |
| Save | Step 31 unions the 198-voxel component with the input and reloads the file. | Binary values, outside-editable preservation, shape and affine are checked. |
| Evaluate | Frozen verifier and current read-only saved-output replay. | Local connection, coverage, overlap and preservation pass. |

Only tool calls and observations are exposed. Reconstructed components are not a
continuous screen recording or an account of hidden cognition.

## Exact measures

| Measure | Result | Evidence role |
| --- | --- | --- |
| Initial whole-mask Dice | 0.9984509813033443 | Current diagnostic on preserved input/reference |
| Initial global foreground components | 1 | Current 26-connectivity diagnostic |
| Initial right-Pcom local route | Broken | Retained scorer on original input |
| Threshold → component voxels | 150→247; 160→212; 165→198; 170→186; 180→178; 190→170; 200→155; 220→122; 250→89 | All reconstructed counts match step 28 |
| Contact patches at 165 | 32 + 33 voxels | Reconstruction matches step 29 |
| Authored deletion recovered | 198 / 200 voxels | Saved output versus private reference |
| Unrelated additions / deletions | 0 / 0 voxels | Saved output versus input/reference |
| Local Dice | 0.9973333333333333 | Frozen result reproduced exactly |
| Right-Pcom centerline coverage | 100% within 0.45 mm | Frozen physically weighted coverage |
| Frozen checks | 12 / 12 pass | Full metric dictionary reproduces exactly |

The step-31 component union is voxel-identical to the saved answer. The recipe
calls only the reviewed scorer's pure array function; its main entry point is
guarded. No model, optimizer, historical preparation script or answer writer runs.

## Visual inspection

The local viewer is `.local/anatomy-pose/vessel/index.html`; the
[source recipe](../presentation/anatomy-repair/prepare.py) and
[design/build notes](../presentation/anatomy-repair/design.md) define derivations.

- **Source views inspected:** retained `terra-gap-result.png`, delivered step-19
  candidate image 5 (three-axis view), and delivered step-27 image 3 (axial
  k=12,14,16,18). Bright unmasked signal lies between mask-covered structures.
  This establishes discernibility in selected views, not attention or clinical truth.
- **Whole-to-local context:** original mask exposed voxel faces use the full
  oblique NIfTI RAS affine. Local focus clips around the logged seed; cut edges
  are labeled as display boundaries rather than anatomical endings.
- **Matched slices:** native samples, nearest-neighbor display and physical aspect
  ratio. Display window is 70–650 source units; thresholds use original scaled
  intensities. Native planes are slightly oblique to patient axes.
- **Roles:** blue-gray outlines/surfaces = input mask; teal fill = reconstructed
  candidate or saved additions; amber = contact voxels; magenta = missed reference
  voxels, revealed only at the final phase.
- **Reader controls:** orbit, slices, before/after and focus are teaching controls.
  The detail crop `[49:83,59:94,7:25]` is centered near the logged seed. Threshold
  alternatives are deterministic reconstructions of the nine recorded values.

Desktop stages, native image panels, 390 px layout and no-WebGL fallback were
inspected. Browser checks cover phase/reference visibility, thresholds, contacts,
full affine mapping, slice bounds, keyboard controls and no external requests.

## Interpretation and alternatives

This observed run supports image-based component selection, local attachment
checking and a bounded union repair. Global overlap and global connectedness do
not express the particular route requirement. Observed image use does not prove
necessity: no image-ablation experiment was run.

Non-identical boundaries were explicitly permitted; the two remaining reference
voxels do not violate the thresholds. No new instruction/scorer defect was
observed. The companion unchanged-mask case retains its failed preservation score
and unresolved annotation disagreement. It is a different patient, not a matched
control for image necessity or model behavior. A simple image-guided baseline
also passed V01. There is no general success-rate, clinical or hard-task claim.

## Provenance

- [Workbench manifest](evidence/br026-gap-trace.json).
- [Source hashes and derivation receipt](evidence/br026-gap-visuals.json).
- [Original results](../../../docs/evidence/br026-results.json) and
  [trace audit](../../../docs/evidence/br026-trace-audit.json).
- [TopCoW source](https://zenodo.org/records/15692630), Yang et al., University
  Hospital Zurich. Attribution required; commercial use needs owner permission.
