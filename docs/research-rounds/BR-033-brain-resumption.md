# BR-033 — resumed TopBrain experiment

Resumed 2026-09-16 after the user asked what happened to the first-choice
brain-vessel task and approved proceeding. This continues the original BR-033
plan; it does not replace the frozen airway trial or its scope correction.

**Completed: model acquisition and five-scan development screen. No clean hard
case was admitted, and no brain coding-agent trial was run.** A geometry-only
calibration supplies an actual parent-to-target repair, centerline, eight rotated
CPRs and a connected mesh, with its remaining reference disagreement explicit.

[Evidence](../evidence/br033-brain-resumption.json) ·
[Local brain viewer](../../runs/br033-brain-routing/viewer-brain/index.html) ·
[Static preview](../../runs/br033-brain-routing/review/brain-calibration-summary.png)

## Question and admission criteria

Can an agent repair a natural vessel-label or connectivity error, identify the
named target artery, and trace a route from its correctly identified parent?
The reconstruction must preserve nearby vessels and supported variants.
CPR and mesh exports make the result inspectable; exporting them does not by
itself establish anatomical difficulty.

Start with the three already verified public MRA images (004, 007, 012), the
TA36 reference labels, and the official released TA36 checkpoints. Preserve
unmodified predictions and record the exact checkpoint, software, orientation,
inference settings, and any departure from the official ensemble. These are
development scans with training exposure, not an unseen test set.

Before any coding-agent trial:

1. Screen actual predictions for a reference-supported class or connection
   error. Exclude disputed reference areas and crop-boundary artifacts.
2. Keep enough proximal context to verify the requested parent-to-target route.
   A pair of anchors inside a detached fragment is not an intact control.
3. Compare unchanged predictions and ordinary geometric/label baselines with
   an input-legal repair. Do not call an easy reconnect difficult because a
   deliberately unsuitable baseline failed.
4. Admit preservation controls only after checking both the local branch and
   its parent attachment. Do not equate reference absence with genuine
   anatomical absence; unresolved absence cases are excluded.
5. Freeze the task and independent verifier before a fresh model trial. Score
   branch identity, parent connectivity, route agreement, spurious joins and
   unintended edits separately from CPR coordinates and intensity sampling.

If no clean error/control set survives this audit, report that curation result
instead of manufacturing a difficult case or running a misleading trial.

## Acquisition

The [official model archive](https://zenodo.org/records/21959166) is reachable
again: a bounded request returned HTTP 206 with the requested 64 KiB range.
The retained downloader now resumes the 763,634,344-byte source/model OCI layer
via the API endpoint. Its published OCI SHA-256 must match before model use.
The original partial files and historical failure record are retained.

Runtime evidence remains under `runs/br033-brain-routing/`.

The resumed download completed in 356 seconds and the full OCI layer SHA-256
matched. All 314 extracted source/model files are inventoried and individually
hashed. A first inference screen uses the released ResEncM fold-4 component
on each full native LPS MRA, with the released preprocessing and sliding-window
predictor, Gaussian weighting, 0.5 tile step, and the checkpoint's disabled
mirroring. It uses Apple MPS rather than CUDA, without reference-derived cropping,
synthetic defects, ensemble fusion, or component-pruning postprocessing. This
is a real released checkpoint's output, not a reproduction of the official
three-model ensemble's challenge result. The complete run settings and hashes
are saved with each prediction.

The reference-only parent-chain screen already flags incomplete left MCA
attachment in MRA 007 (approximately 13% of its M2 label is outside the main
parent component). Such regions require further review and cannot automatically
be scored as prediction errors. Most other major chains in the three scans are
fully attached in the reference under 26-neighbor connectivity; that numerical
check does not by itself establish anatomical correctness.

## Completed screen

The initial scans 004, 007 and 012 did not produce a convincing named-branch
identity error. The screen was extended to 006 and 011 because the retained
reference inventory identifies third-A2/third-A3 anatomy in those scans.
Their images were acquired from the original TopCoW record 15692630, and both
compressed NIfTI sizes and CRCs match the retained TopBrain archive metadata.
This is targeted, reference-assisted development selection.

| MRA | Mean Dice across labels present in either mask | Third-A2 Dice | Third-A3 Dice |
| --- | ---: | ---: | ---: |
| 004 | 0.9388 | — | — |
| 006 | 0.9161 | 0.9544 | 0.9369 |
| 007 | 0.9440 | — | — |
| 011 | 0.9422 | 0.9431 | 0.9250 |
| 012 | 0.9447 | — | — |

These are development segmentation measurements, not coding-agent scores or
held-out clinical accuracy. Both annotated third-artery variants are present
and fully attached to the carotid parent through the selected ACA label chain,
in prediction and reference. They are potential preservation controls, not
evidence of a hard repair. Neither is treated as a clinically adjudicated
absent-branch case.

Three new PCA–SCA face adjacencies were screened (004 left, 007 right, 011 left).
All three reference masks already touch under 26-neighbor connectivity, with
8, 1 and 13 contact voxels respectively. They therefore do not provide an
unambiguous binary-topology oracle. The MRA 004 contact is visualized in the
retained review image; none was admitted as a false-connection task.

Interior-label disagreements were small and concentrated around anatomical
label transitions (for example M2/M3). The screen's 0.5 mm interior threshold
does not establish absence of errors in thinner vessels. There was no clinical
expert adjudication or exhaustive manual review of every branch.

## Real repair retained as calibration

MRA 004 has a 247-voxel distal right SCA fragment whose nearest voxel center is
0.939 mm from the main same-label component. An input-legal nearest-point
geometric bridge restores its attachment to the basilar parent. The final
native-grid implementation adds **two voxels**, one annotated as R-SCA and one
as background. It makes no other full-volume edits. This is a connectivity
repair with a residual mask disagreement, not an exact reference reconstruction.

The source-only solver traces an **85.57 mm** route from a basilar anchor to
the distal R-SCA target. Against an independently traced reference route,
the nearest-centerline distance is **0.298 mm at p95** and **0.449 mm maximum**.
The shown target-chain mesh changes from disconnected to one connected,
watertight surface. Other vessels are retained in the full labeled output;
the viewer explicitly limits its surface and repair claim to BA plus R-SCA.

Exports include a full labeled NIfTI, centerline, eight CPR rotations with
source RAS coordinates and MRA signal values, and PLY mesh. The 140,352 numeric
CPR samples were independently checked against trilinear interpolation of the
full original MRA. Maximum intensity difference was 0.000102, within the
float32 comparison tolerance. Arc distances, radial offsets, parent attachment,
unchanged voxels, mesh connectivity, prediction hashes, all 17 image-atlas
dimensions and JavaScript syntax passed. Browser interaction was not retested:
the earlier local-file navigation policy block was not bypassed.

Authoring checks caught insufficient CPR image padding and crop-dependent
half-voxel rounding. The final export samples actual source pixels and rounds
the bridge on the original voxel lattice. Earlier three-voxel exports remain
in `gap-calibration-v1` and `gap-calibration-v2`; the final two-voxel version is
`gap-calibration`. This was pretrial authoring, and no frozen task or model
prediction was changed to improve an agent result.

## Decision

The checkpoint-download problem is resolved. The bounded five-scan screen did
not establish a clean, difficult branch-identity or topology repair. The small
gap is a useful calibration, the contacts have a reference-convention problem,
and the selected variants are already preserved. Following the predeclared
admission rule, no new task was frozen and no coding-agent trial was launched.

The original hypothesis remains untested. A further attempt needs a substantial,
reference-supported branch error and valid parent-connected controls. These
results do not show that brain-vessel tasks are intrinsically harder or that
TopBrain cannot supply a suitable case.
