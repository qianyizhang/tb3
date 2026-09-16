# BR-033 — execution record

Completed airway pilot, 2026-09-16. **Terra/high passes the frozen task.**
Three patients were screened; one real airway omission and two internal-fragment
preservation controls were admitted. **User review exposed a control-selection
flaw: A02 and A03 still have obvious parent gaps.** The tested geometric shortcuts fail, while both an
image-guided development baseline and Terra succeed. This improves the test
of image use over BR-030, but does not establish a hard coding-agent task or
validate a clinical workflow. The initial TopBrain checkpoint download was
blocked; the subsequent [brain resumption](BR-033-brain-resumption.md) recovered
the model, completed five MRA predictions and retained a geometry calibration.
It did not admit a clean hard case or run a brain coding-agent trial.

[Results and checks](../evidence/br033-results.json) ·
[Pretrial freeze](../evidence/br033-freeze.json) ·
[Source audit](../evidence/br033-source-audit.json) ·
[Local Terra viewer](../../runs/br033-airway-routing/viewer-terra/index.html) ·
[Local baseline viewer](../../runs/br033-airway-routing/viewer/index.html)

## Correction after user review: A02 and A03 remain disconnected

The user's browser comments correctly identified the unrepaired parent gaps.
In both A02 and A03, the two requested anchors lie inside a detached fragment.
**A03 has exactly the same input CT, mask and affine as A01**; its request
chooses anchors below the gap and a different editable region.
Their short internal route is connected, but the fragment is not connected to
the larger airway. Both output masks are exactly unchanged. Calling these
“intact controls” and labeling their full surfaces “repaired airway” obscured
that distinction. These are inadequate negative controls for deciding whether
an airway connection should be restored. They are neither fully intact airway
trees nor genuine absent-branch examples.

[Direct connectivity audit](../evidence/br033-scope-audit.json):

| Case | Requested anchors before → after | Parent connection after | Added voxels |
| --- | --- | --- | --- |
| A01 | Separate components → same largest component | Requested connection restored | 578 |
| A02 | Same 89-voxel fragment → same fragment | Still disconnected from the 2,715-voxel largest component | 0 |
| A03 | Same 348-voxel fragment → same fragment | Still disconnected from the 6,018-voxel largest component | 0 |

This is a task-design and reporting problem, not an agent failure under the
frozen instructions. The original pass and output bytes remain unchanged.
The viewer now highlights A01's actual additions, switches the 3D surface with
Input/Output, marks the requested anchors, and explicitly warns that A02/A03
remain detached. Earlier viewer bytes are retained locally.

The user's other point also holds: noticing that these fragments should be
connected is relatively obvious from their structure. Failed geometric
shortcuts test where and how to draw a connection; they do not show that the
decision to reconnect is difficult. This pilot does not test the original
repair-versus-real-anatomical-variant hypothesis. Any successor needs independent
upstream-to-distal reachability checks and genuinely intact or adjudicated
absent/obstructed controls, rather than choosing both anchors within an island.

## Frozen task and measured result

Inputs are three small CT/prediction crops with ordered route anchors and
editable regions. Outputs are repaired masks, physical centerlines and eight
rotated CPRs. A01 contains an unchanged real model omission from AeroPath
patient 1. A03 uses an internally connected fragment of that same crop, and A02
an internally connected fragment from patient 10. Both fragments remain detached
from their parents. A03 is correlated with A01; these are not three patients.
Patient 11 was screened but supplied no admitted case.

| Method | A01 anatomy | A02/A03 preservation and routing | CPR | Interpretation |
| --- | --- | --- | --- | --- |
| Reference-assisted oracle | Pass | Pass | Pass | Verifier positive control |
| Unchanged mask with oracle geometry | Fail | Pass | Pass | Fails the missing lumen and connection |
| Mask-only path/repair baseline | Fail | Pass | Pass | Wrong branch connection and added tissue |
| Image-guided development baseline v2 | Pass | Pass | Pass | Public inputs at execution; tuned by author before trial |
| Nearest-component bridge | Fail | Pass | Pass | Additional post-freeze geometric check |
| Straight-anchor tube | Fail | Pass | Pass | Additional post-freeze geometric check |
| **Terra/high, one normal completion** | **Pass** | **Pass** | **Pass** | **Frozen reward 1.0** |

The Docker oracle returned 1 and Docker no-op returned 0 before the model trial.
All three runs used task checksum
`9cb3f8b3c92d688b59bea64d6debac631859eda7834f947d80137dfe772e7c00`.
Frozen files were checked before and after each run. There were no retries,
timeouts or provider errors. Local rescoring of saved artifacts agrees with the
separate Docker verifier. Agent execution took approximately 330 seconds.

Terra added 578 voxels to A01, removed none, and made no edits outside its review
region. Scored lumen-core coverage was **87.47%**, route error **0.449 mm at the
95th percentile**, and reference-route coverage **100% within 1.2 mm**. Newly
added volume farther than 0.8 mm from the reference airway was **0 mm³**. A02
and A03 masks were preserved exactly. All CPR coordinate, sampled-intensity and
arc-distance checks passed. This core-coverage metric is not whole-airway Dice.

The recorded trace contains 14 completed shell commands. It uses input CT
intensities and connectivity to isolate the missing lumen, preserves the two
already connected requests, and constructs the required geometry. No command
retrieving external truth or reading private verifier/solution paths was
observed. Public-data pretraining exposure remains unknown.

## Why the screen did not become a harder benchmark

On patient 1, the fixed route screen chooses a 53.3 mm mask-only detour versus
a 29.8 mm CT-guided route. The geometric route crosses tissue; all added samples
of the image-guided route are inside the released reference. Several patient-10
gaps also show image benefit; patient 11 does not show the same contrast.
This is evidence against these particular geometric shortcuts, not proof that
every mask-only method must fail.

Mask reconstruction required additional care beyond a thin path. The first
baseline underfilled the missing lumen. Before freezing, v2 increased the
repair radius to 2 mm and its fill threshold to -400 HU; both parameters and
all intermediate outputs are retained. A01 passes comfortably with that
input-legal solver. A second proposed error, A04, remained sensitive to the
reference boundary and repair width; it was excluded before the coding-agent
trial. The oracle, image baseline, six deliberately incorrect outputs and
mask-only contrast were checked before trial dispatch. The nearest-component
and straight-anchor checks were added afterward without changing the freeze.

The intended six-case mix was not achieved. No genuine absent branch, true
obstruction, false connection, or named-bronchus identity control is admitted.
The retained task tests a local lumen omission and internal-fragment preservation. Its
intensity cue is strong enough for a simple algorithm and for Terra. Retire it
as a passed calibration fixture, while retaining the usable reconstruction.

## Inspectable outputs

The Terra viewer combines original CT slices, mask overlays, route navigation,
eight CPR rotations, perpendicular cross-sections and a rotatable mesh. Masks,
centerlines and CPR files are unchanged trial artifacts. The author derived
PLY meshes afterward from those masks; mesh generation was not a scored agent
deliverable. All meshes have consistent winding and closed surfaces.

Numerical geometry, source sampling, atlas dimensions, downloadable files and
JavaScript syntax were checked. The browser's file-URL policy blocked automated
page rendering; no alternate browser route was used. The source-derived CPR
preview was inspected separately. The UI itself has not had an interactive
browser test.

## Brain data acquired; checkpoint unavailable

The current [TopBrain data release](https://zenodo.org/records/21972006) contains
50 scans, original modality-specific labels, and updated TA36 labels. All 100
reference masks, label maps and license files were extracted and verified by
ZIP CRC. Three matching MRA images (004, 007, 012) were reused only after their
compressed file sizes and CRCs matched the new release exactly. Their grids
match both corresponding reference masks.

The [official model release](https://zenodo.org/records/21959166) could not be
fully downloaded. Repeated direct, proxy, API and file-endpoint requests returned
504 errors or timed out. Partial bytes and manifests are retained locally;
there is no complete checkpoint and no new brain prediction. This is a source
availability problem, not a model failure. The current data terms permit
noncommercial research; commercial use requires the owner's permission.

The 244 additions disputed in BR-026 were also mapped into the updated brain
labels. All remain background. This confirms the disagreement survives that
release; it does not resolve whether the source annotations missed a vessel.
The original result remains unchanged and no clinical adjudication is claimed.

## Airway source and inference

Use [AeroPath](https://github.com/raidionics/AeroPath), with files from an author's
[pinned mirror](https://huggingface.co/datasets/andreped/AeroPath/tree/6d0f831ca22bf57918aba3980ae475c94d45b997).
All selected files are checked against their published LFS SHA-256 digests.
The included `license.md` is CC BY 4.0, while the mirror card says MIT; retain
both declarations and do not silently infer redistribution rights from the
code repository's MIT license.

Run the official lung and airway ONNX models from
[Raidionics release 1.2.0](https://github.com/raidionics/Raidionics-models/releases/tag/1.2.0)
using `raidionicsseg==1.5.2`, CPU ONNX Runtime 1.22.1 and the released
preprocessing configurations. Lung cropping uses a predicted lung mask;
neither reference mask is supplied to inference. Model bytes are unchanged.
The backend needs two compatibility adjustments: a fold subdirectory layout,
and removal of a retained singleton batch axis for the full-volume lung model.
The failed unadjusted run is retained. These adjustments do not alter model
probabilities, thresholds or spatial interpolation. This released single
patch model is not asserted to reproduce the paper's full-volume/patch ensemble.

Case 10 was selected first for inexpensive acquisition and pipeline validation.
Cases 1 and 11 were selected as two additional patients before reviewing their
predictions. This three-patient convenience sample is not a prevalence estimate.

The [AeroPath paper](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0311416)
describes reference refinement under pulmonologist supervision and also warns
that valid distal branches can be absent from annotations. Therefore the screen
uses internal gaps bounded by retained predictions and excludes unresolved
terminal disagreements. Dataset pathology does not establish a particular
diagnosis for any selected crop.

## Curation and trial gate

The initial route comparison fixes costs before applying them to the two later
patients: inverse predicted-mask radius inside the mask; cost 8 outside it;
the matched image condition permits additions only below -500 HU. Both receive
the same source image, prediction and endpoints. The mask-only condition does
not use image values in route selection. Endpoints and review regions are
reference-assisted author choices, not blinded discoveries. Masks remain the
unchanged released-model predictions, with no injected defects.

The pretrial admission rule required a supported connection that the geometry baseline
misroutes, an input-legal successful image solution, and preservation controls.
Route scoring and clinical utility are different claims. An engineering route
does not establish lesion identity, disease severity or bronchoscope reachability.
The coding-agent trial followed frozen inputs, criteria, oracle and no-op
validation. The completed trial and exports are described above.

Local runtime evidence: `runs/br033-brain-routing/` and
`runs/br033-airway-routing/`. Reusable authoring scripts:
`probes/brain-routing/authoring/` and `probes/airway-routing/authoring/`.
