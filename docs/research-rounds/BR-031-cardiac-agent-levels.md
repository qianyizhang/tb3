# BR-031 — cardiac agent capability ladder

New user request, 2026-09-16: experimentally assess progressively less supplied
cardiac anatomy/motion, and independently score observed images, withheld views,
geometry, material motion and mechanics. The source message proposed levels
0–8. This explicitly authorizes fresh trials after the earlier author-only
BR-029 work. No other task, historical freeze or interview publication is owned
by this round.

## Refined hierarchy

Input difficulty and output claims form two axes. Levels 0–4 remove evidence;
levels 5–8 add quantities requiring different references. Passing one does not
automatically establish the others.

| Input stage | Supplied | Target |
| --- | --- | --- |
| 0 | Initial material mesh, complete reference motion and anatomical axes | Correct finite-deformation calculations and reusable implementation |
| 1 | Four calibrated synthetic ultrasound videos, initial material mesh and axes | Recover subsequent 3D material motion |
| 1V | Initial mesh plus native 3D ultrasound cycle | Matched observation-depth diagnostic if sparse-view recovery fails |
| 2 | Calibrated videos and explicitly specified contour anchors | Joint initial geometry and material deformation |
| 3 | Raw multiview videos plus obtainable acquisition metadata | Segmentation, calibration/phase estimation and geometry/motion; absolute scale needs calibration evidence |
| 4 | Sparse/single-view observations | Conditional reconstruction with uncertainty and declared prior assumptions |

| Output track | Reference required |
| --- | --- |
| 5: regional strain | Known material correspondence and reference anatomical directions; scored at stage 1 already |
| 6: cavity volumes/EF | Audited endocardial surfaces and valve-plane closure; myocardial volume is insufficient |
| 7: flow/hemodynamics | Doppler or measured/simulated flow and pressure, boundary conditions, valve information |
| 8: pathology | Case-level adjudicated labels with informative observations and realistic negative/alternative cases |

## Prospective protocol

Start with one fresh Terra/high attempt at stage 0. If it passes, give a fresh
Terra/high session stage 1, without the earlier session, solutions, workbench,
author solvers or reference future meshes. If a normally completed valid stage
misses its fixed targets, run Sol/xhigh once on exactly those task bytes. Do not
retry to obtain a preferred outcome. Each model has 1800 seconds, ordinary
Python/scientific libraries and no automatic retry. This is a bounded diagnostic
screen, not a success-rate estimate or final benchmark admission.

Freeze task files and the independent verifier; run oracle and no-output
controls under the same task checksum. Verifier data reside in a separate
container, not the agent image. Retain logs, code and submissions locally. Audit
runtime model/effort, normal completion, source exposure, and independently
replay scores before any capability interpretation. Infrastructure faults or
timeouts are excluded from capability-failure conclusions.

Stage 0 validates full finite-strain tensors, directional engineering strain,
Jacobian ratios and missing-axis support on the source sequence and analytic
rigid/affine cases. Stage 1 recomputes mechanics from predicted coordinates;
submitted colors/scalars do not substitute for geometry. Four observed planes
and four private planes are scored with cross-sectional myocardial masks.
Surface distance, tissue-volume error, material point error (including LV and
RV/unassigned breakdown), directional strain, regional peaks and timing are
reported separately. No per-frame spatial or time registration is permitted.

Development gates for stage 1: observed slice Dice >=0.90; withheld slice Dice
>=0.85; symmetric sampled-surface mean distance <=2 mm and p95 <=5 mm; tissue
volume curve mean relative error <=5%; material-point RMSE <=2 mm; no inverted
tetrahedra. The separate mechanics gate uses directional strain MAE <=5 pp,
regional peak MAE <=5 pp, and mean regional timing distance <=2 frames for each
direction. Near-equal reference extrema within 0.5 pp are accepted as timing
ties. These are pretrial engineering thresholds, not clinical limits.

Known limitations: one previously inspected simulated healthy case, public
source identity, exact supplied initial geometry and calibration, and limited
RV observations. Four planes cannot uniquely establish arbitrary 3D internal
motion. A miss can identify a method/observation limitation; it alone cannot
establish an intrinsically hard, uniquely solvable task. L1V and stages 2–8 are
conditional follow-ups, not implied completed work. Levels 6–8 remain blocked
by missing matched reference evidence in the current STRAUS package.

## State

Preparation in progress. No model outcome is asserted by this protocol.
