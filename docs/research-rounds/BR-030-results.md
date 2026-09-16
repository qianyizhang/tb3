# BR-030 — a real coronary gap, tracing, rotated CPR and a mesh

The larger workflow is implemented and tested on a real coronary segmentation
error. Terra/high repaired the mask, traced the requested vessel and produced a
valid mesh, but failed the distance-axis consistency check in its CPR archive.
Correcting **one metadata array** makes the same package pass. Both fixed author
baselines also pass, including the variant that removes image evidence from
repair and tracing. This is a useful geometry workflow and a narrow software
consistency miss; it does **not** establish difficult anatomical discrimination.

[Interactive reference view](../../runs/br030-vessel-geometry/viewer/index.html) ·
[Image-guided baseline](../../runs/br030-vessel-geometry/viewer-image-baseline/index.html) ·
[Terra plus axis correction](../../runs/br030-vessel-geometry/viewer-terra-arc-correction/index.html) ·
[Frozen task](../../runs/br030-vessel-geometry/tasks/coronary-cpr/instruction.md) ·
[Results receipt](../evidence/br030-results.json)

## The concrete task

Given a CTA crop, an unedited predicted binary mask, an 8 mm review sphere and
two route landmarks, return:

1. A locally corrected mask, with every voxel outside the sphere preserved.
2. An ordered centerline from the RCA ostium to the distal right posterior
   descending artery (R-PDA), in RAS millimeters.
3. Eight rotated CPR planes, their original HU values, source coordinates for
   every pixel and a consistent distance axis.
4. A closed world-space surface mesh containing both coronary trees.

The viewer links CPR angle, vessel position, orthogonal cross-section and mesh.
It also shows the central lumen cross-sectional area, with no disease-grade
claim. Numerical arrays, full-resolution meshes and corrected masks are
downloadable from each view. Simplification affects only the interactive mesh
preview. The HTML embeds its previews and needs no external JavaScript service.

The clinical motivation is vessel-following review of the contrast-filled
lumen. A wrong branch, unsupported connection, left/right coordinate error or
incorrect distance axis can corrupt that workflow. No lesion-specific stenosis,
plaque or flow ground truth was supplied, so the task does not grade those
diagnoses or claim that the mesh is ready for a hemodynamic simulation.

## Ground truth and real-error curation

**ImageCAS-X** provides coronary masks, named centerlines, surfaces and split
metadata for 800 ImageCAS CTAs. Its final centerlines and surfaces derive from
corrected masks; they are related references, not independent anatomical votes.
The paper describes a second-analyst comparison, but the downloaded archive
inventory contains one reference mask per case, with no separate second-rater
directory located. [Paper](https://arxiv.org/abs/2608.30404),
[release](https://zenodo.org/records/21887809).

The CTA was obtained from the original
[ImageCAS release](https://www.kaggle.com/datasets/xiaoweixumedicalai/imagecas).
Case 1 has matching native image/mask grids, excellent image quality and right
dominance. It belongs to the **training split**. This is a development fixture,
not a held-out estimate of CAS-Net accuracy. Published source code and weight
hashes, archive CRC checks, selected-member hashes and license declarations are
retained in the [source receipt](../evidence/br030-sources.json).

The author ran the released ImageCAS-X CAS-Net checkpoint on the **full CTA**,
using the published resampling, clipping, patch inference, Gaussian blending,
X/Y mirroring and component filtering. Batch size was one; MPS used CPU fallback
for an unsupported pooling operation. The output was never cut or bridged by
the author. The task contains an unchanged spatial crop of it.
[Implementation](https://github.com/kitbransby/ImageCAS-X).

| Screen | Observation | Disposition |
| --- | --- | --- |
| Four TopCoW MRA cases, single CLAIM fold | Full skeleton coverage of the seven present communicating-artery labels inspected | No local natural gap admitted; this does not imply the entire masks are error-free |
| Coronary LM → LAD | Continuous across the released route | Preservation context |
| Coronary LM → LCx | Approximately 4.5 mm missing at the distal endpoint | Not selected: terminal extent disagreement is less decisive |
| Coronary RCA → R-PDA | Approximately 5 mm **internal** gap, separating an existing distal component | Selected |
| Coronary RCA → R-PLA | Continuous across the released route | Nearby branch preservation context |

The selected prediction has **94.14% global Dice**. Ten consecutive samples at
approximately 0.5 mm spacing miss the lumen between arc positions 131.10 and
136.08 mm. Their first-to-last span is 4.49 mm; the sampling-based gap estimate
is 4.98 mm. The existing segments on either side belong to different connected
components. Source CTA intensity at those reference centerline samples has
median **162.9 HU**, compared with **−66 HU** in the review-region background.
This local evidence supports an annotation-backed repair, with no new clinical
expert adjudication claimed.

Reference-assisted replacement inside the review sphere adds 205 voxels and
removes 17, restores the intended connection and changes the mask from three
components to two. It changes nothing outside the sphere. The reference route
is approximately 161.5 mm long. Those author outputs establish an oracle and
working viewer; they are not the blind model result.

## Frozen diagnostic and controls

The task was frozen before the model attempt. Oracle and no-op ran through
Harbor 0.18; Terra/high used Harbor 0.14 with one attempt, public network access,
the ordinary 1,800-second agent allowance and a separate verifier. All three
runs have the same task checksum and completed without exceptions. No retry
or model escalation was performed. The Terra agent phase took **484.14 s**
(8 min 4 s), with 19,648 output tokens. The entire job took about 8 min 48 s.

| Condition | Repair | Trace | CPR | Mesh | Overall |
| --- | --- | --- | --- | --- | --- |
| Docker oracle | Pass | Pass | Pass | Pass | Pass |
| Docker no-op | Fail | Fail | Fail | Fail | Fail |
| Fixed image-guided author method | Pass | Pass | Pass | Pass | Pass |
| Matched geometry-only repair/trace method | Pass | Pass | Pass | Pass | Pass |
| **Terra/high, original output** | **Pass** | **Pass** | **Fail** | **Pass** | **Fail** |
| Post-outcome correction of `arc_mm` only | Pass | Pass | Pass | Pass | Pass |

Author baselines were designed after source review. Their execution reads only
the delivered inputs, but they are not blinded discoveries. The image-guided
method uses a fixed HU threshold, physical shortest-path costs, mediality and
a small repair envelope; it runs in 6.46 s locally. Its matched contrast ignores
intensity only during repair/tracing, while still sampling the real CTA for CPR.
Both pass. Image evidence improves local Dice from 0.900 to 0.951 and reduces
edits from 250 to 125 voxels, but is not necessary for passing this fixture.

Terra adds **103 voxels**, with zero changes outside the review sphere and no
far additions. Local Dice is **0.9448**; centerline 95th-percentile distance is
**0.4996 mm**, with **100% reference coverage** at 0.8 mm. The mesh is closed and
passes global and local surface checks. The retained trajectory includes image
inspection and quantitative HU checks, with no external source-answer retrieval
observed. The runtime context reports Terra/high. Artifact replay reproduces
the frozen checks; no provider-side identity attestation is inferred.

### The failure is specifically the distance axis

Terra calculates a 184.809 mm arc grid on its original voxel skeleton, then
interpolates a new centerline on that grid. Interpolation cuts polyline corners:
the saved line's cumulative Euclidean length is **175.918 mm**. It saves the old
grid as `arc_mm`, overstating the final length by **8.891 mm**.

The CPR source-coordinate error is only **0.00000853 mm**, and the 99th-percentile
HU error is **0.00162 HU**. Its sampled curved planes are correct for its saved
line. The frozen check named `cpr_coordinates` combines coordinate and distance
axis checks; here **only the distance axis fails**. This is not a branch-selection
error, failed segmentation repair or invented anatomy.

The post-outcome intervention replaces only `arc_mm` with cumulative Euclidean
distances along the saved centerline. Mask, centerline, source-coordinate arrays,
HU values and mesh remain identical. The unmodified verifier then passes all
stages. This is an author diagnostic repair, not a second model success. The
original output and frozen score remain intact.

## Validation and limits

Six analytic checks cover oblique/reflected physical transforms, exact sampling
of a known linear field, quarter-turn CPR directions, stable curved frames and
closed mesh orientation. Six wrong-output controls exercise unrepaired masks,
reversed routes, fabricated HU values, mirrored meshes, unrepaired meshes and
collateral edits. All fail the intended overall test. Two additional graph
checks confirm that a route follows line connectivity despite scrambled point
IDs and never mistakes the ostium for its own distal endpoint.
[Validation](../evidence/br030-validation.json).

Browser checks exercised CPR rotation, route position, cross-section updates,
mesh dragging and responsive rendering. Numerical arrays are checked separately;
visual inspection is not their oracle. The simplified mesh preview is not used
for grading. No deployment, external publication or submission change occurred.

The frozen tolerances admit some centerline roughness and boundary variation.
One successful repair cannot certify general anatomical reasoning; one
distance-axis failure cannot establish broad difficulty. Retain this as a
reproducible workflow/calibration task and a narrow coordinate-consistency case.
A stronger anatomy benchmark still needs independently reviewed difficult
predictions plus matched intact, absent-branch and genuine-variant controls.
Do not tighten this case's gates after observing its outcomes.

## The earlier MRA disagreement

The BR-026 output's 244 added voxels contact only L-ACA. A rigid comparison of
16 paired CTA/MRA boundary/bifurcation landmarks gives median residual
**0.711 mm**, 95th percentile **1.220 mm** and maximum **1.362 mm**. At that
resolution, paired-image inspection cannot decide whether the marked signal
is a true unlabeled vessel, a scope difference or a false connection.

TopCoW's label scope is the Circle of Willis within its ROI, rather than every
visible artery. The source describes expert review for uncertain annotations;
no new neuroradiologist review was available here. The supplementary appendix
request returned a browser-verification page, so no inaccessible protocol detail
was assumed. [Source](https://pmc.ncbi.nlm.nih.gov/articles/PMC13496301/).

The original preservation failure stays recorded, but the case remains excluded
from confirmed anatomical-failure claims. The
[review packet](../evidence/br030-adjudication.json) and
[paired image panel](../../runs/br030-vessel-geometry/adjudication/paired-review.png)
give an expert the exact marker, native sources, transform and question.
No external clinician was contacted. BR-026 task and freeze bytes are unchanged.

## Reproduction and evidence

[Predeclared scope](BR-030-vessel-diagnostic-geometry.md) ·
[Frozen hashes](../evidence/br030-freeze.json) ·
[Source and inference provenance](../evidence/br030-sources.json) ·
[Implementation and commands](../../probes/vessel-geometry/README.md).

Current artifacts are local research outputs. Source images, models, archives,
native trajectories and environments remain under ignored runtime paths.
Concise source, validation, model and adjudication receipts are retained in
`docs/evidence/br030-*`.
