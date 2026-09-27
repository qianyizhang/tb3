# Repair an airway route while preserving supplied fragments

Repair the requested connection in a cropped airway mask, then return a centerline
and eight curved planar reconstructions (CPRs). Preserve routes already connected
between their supplied anchors. **This tests local routes, not whole-tree repair.**

## Value

Connect image-supported local mask repair with inspectable path geometry and CT
sampling. A local connection can support later navigation work; clinical utility
and named-bronchus identity were not evaluated.

## Given

### Original data

AeroPath CT in HU. Three requests, A01–A03, come from **two patients**; A01 and A03
share exactly the same CT and prediction crop. The author selected crops using
source references. These are natural omissions in the retained released-model
prediction, with no injected defect.

### Supplied helpers

Binary proposed mask, editable region, public review centre/radius and two ordered
anchors in **NIfTI RAS+ mm**. This removes whole-volume localization. A02/A03 anchors
lie within detached fragments: their requested local routes are connected, while
the larger parent mask remains disconnected.

### Callable tools

The frozen Python environment supplies scientific imaging libraries; ordinary
shell/code tools and network access were allowed. The retained attempt inspected
CT montages and used local threshold/connectivity and path calculations. No new
execution is implied by this explanation.

### Reference-only material

Private evaluator CT copies, GT, core, route tube and reference centerline remain
outside the solver packet. Reader reveals expose selected core/path geometry and
original metrics separately. Portable teaching HTML embeds those reference assets.

## Task specification

Add lumen supported by CT between the requested anchors; preserve existing
foreground and all voxels outside the editable region. Already connected requested
routes must remain **exactly unchanged**. Unrelated defects are outside scope.

## Expected output

Per request: same-grid binary `corrected_mask.nii.gz`, ordered `centerline.npy`
(N×3 RAS+ mm; 0.05–0.75 mm steps), and `cpr.npz`. CPR HU has shape **8×N×65**, with
source coordinates, angles, offsets −8…+8 mm at 0.25 mm, and cumulative arc length.
The frozen contract specifies parallel-transport frames and trilinear CT sampling.
Optional posttrial PLYs are author views, not required outputs.

## Evaluation

Frozen gates check preservation, requested route connectivity, ≥80% reference-core
coverage, false additions, route geometry/containment and CPR coordinates/HU/arc.
The [result and scope audit](../../findings/airway-local-route-scope.md) retains
**reward 1** for one Terra/high attempt: A01 adds **578 voxels**, while A02/A03 each
change **zero**. A01 covers **433/495 core voxels (87.47%)**; this is not global Dice.

## Difficulty

An unchanged-mask control fails A01; a tuned image baseline passes. Selected
geometric shortcuts fail, which does not rule out every mask-only method.
Preserving detached fragments is weaker than establishing an intact parent tree.
The original pass is consistent with its narrow instructions.

## Coverage

Three screened patients yielded three admitted requests from two patients. A04
was excluded before the trial for boundary-sensitive scoring. No true-absence,
false-connection or clinically intact parent-tree control was admitted. Public
source exposure and reference completeness remain limits.

## Sources

- [Airway protocol within mixed BR-033](../../experiments/br033/protocol.md)
- [Result, trace and parent-gap interpretation](../../findings/airway-local-route-scope.md)
- [Source-derived teaching provenance](../../../../presentation/task-explorer/airway-repair/NOTICE.md)
- [AeroPath source and attribution](https://github.com/raidionics/AeroPath)
- [Annotation workflow and reference limitations](https://doi.org/10.1371/journal.pone.0311416)
