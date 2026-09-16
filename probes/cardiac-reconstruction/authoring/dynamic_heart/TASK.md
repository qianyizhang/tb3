# Dynamic heart modeling — larger task contract

Build a beating myocardial model that explains the supplied cardiac images.
Recover a **material deformation**, not independent surfaces or an animation
with painted strain colors. Keep geometric plausibility, agreement with images,
material motion, strain and physiology as separately evaluated claims.

## Target deliverable

One reference body with chamber/tissue labels and a time-dependent deformation
map over a cycle. Export reference coordinates, fixed tetrahedral connectivity,
deformed coordinates, reference time and physical coordinate conventions.
Compute deformation gradients, Green–Lagrange tensors, directional engineering
strain and local volume ratios from that map. Return regional strain curves,
peak timing, tissue-volume conservation diagnostics and reconstruction error.

When supported by audited labels, include LV/RV endocardial/epicardial surfaces,
valve annuli and closed cavity volumes with explicit cap definitions. EF must
come from cavity volume. Blood velocity, pressure, stress and disease require
additional measurements or a declared simulation model; do not infer them
merely from a moving grayscale boundary.

The workbench currently demonstrates **biventricular material motion and LV
directional strain**. Four-chamber mechanics, detailed leaflets, active fibers
and circulation are the larger target, not claimed current outputs.

## Difficulty and evidence tracks

| Track | Inputs | Required reasoning | Appropriate reference |
|---|---|---|---|
| Full-volume motion | Initial material mesh + 3D US cycle | Track a deforming tissue body; distinguish translation/rotation from strain | STRAUS moving tetrahedra and anatomical axes |
| Sparse-view mechanics | Initial mesh + calibrated multiview videos | Infer missing motion with explicit mechanical assumptions and uncertainty | STRAUS full motion plus held-out image planes; qualify observability |
| Geometry and motion | Video + sparse contour anchors | Recover wall surfaces, material correspondence and regional deformation together | Synthetic matched geometry/motion first; real FeEcho4D for contour validation only |
| Whole-heart mechanics | Four-chamber anatomy, fibers, loading and motion evidence | Couple chambers, septum, annuli and active contraction without violating mechanics | Matched 4D anatomy/strain where available; validated forward simulation otherwise |
| Pump and circulation | Above + pressure/Doppler/flow evidence | Couple valves and circulation; reconcile inflow/outflow with changing chamber volume | Pressure/flow references; wall motion alone is insufficient |

All frames and views from a subject remain in one split. STRAUS healthy and
pathological labels describe simulated scenarios. Never treat them as proof
of clinical diagnosis from an ultrasound reconstruction.

## What “realistic strain” means here

For a material point X, compute F = d(phi)/dX and E = (F^T F − I)/2.
Directional engineering strain is sqrt(e^T F^T F e) − 1. State which measure
is shown; the two are not numerically interchangeable at cardiac deformations.
Strain must be derived from geometry and correspondence. Rigid motion has zero
strain. A shrinking solid balloon shortens its wall in every direction;
contracting myocardial tissue also changes thickness and rotates regionally.

Physical regularity must be supported by the source and constitutive model:
positive Jacobians, plausible wall thickness, controlled tissue-volume change,
continuous phase behavior, and regional timing. A finite-volume regularizer
does not establish force equilibrium, active-fiber physiology or a measured
patient strain field. Unknown anatomical directions remain missing.

## Evaluation and admission

Recompute mechanics from submitted coordinates with an independent evaluator;
do not trust a submitted strain array or EF scalar. Score material-point error
when correspondence is known, surface/section errors when it is not, and
strain/phase errors only where their reference and coordinate system exist.
Report per-region and tail errors as well as averages. Do not align away
translation, rotation, scale or time errors separately at every frame.

The current author screen fixed provisional numerical targets before its
reconstruction outcomes: material RMSE <=2 mm; each directional strain MAE
<=5 percentage points; each direction's mean regional peak error <=5 points;
zero inverted elements. Source-frame strain must vanish on supported axes,
and numerical solves must converge before interpreting a result as a valid
method outcome. These targets are **not clinical limits or final TB3 gates**.

For a force-based model, additionally verify numerical force/energy balance,
mesh/time-step convergence and sensitivity to loading/fiber assumptions. For
circulation, verify dV/dt = Qin − Qout using the same time/volume units. Lock
solver tolerances and validation references before a model trial.

Required controls: rigid motion, known affine strain, static body, uniform
scaling, a privileged best global deformation fit, an input-legal image method,
and a tissue method with declared regularization. Include examples where a
convincing surface or scalar measurement coexists with wrong tissue motion.

Sparse videos do not uniquely determine all unobserved 3D deformation. Before
benchmark admission, use full-volume cases or a specified simulation family to
test identifiability, and reward appropriately bounded uncertainty. The current
one-case controls do not establish a unique patient-specific inverse solution.
