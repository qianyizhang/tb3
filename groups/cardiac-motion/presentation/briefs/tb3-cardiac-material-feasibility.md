# Study dynamic myocardial models and reference mechanics

Recover a deforming myocardial body from four synthetic ultrasound planes and
an initial material mesh. **BR-029 is an author feasibility study, not an
independent model trial or a clinical strain evaluation.**

## Value

Separate accurate geometry calculations from accurate recovered motion. Positive
Jacobians and a plausible tissue-volume curve can coexist with large material
point and directional strain errors.

## Given

### Original data

Four fixed planes extracted from the STRAUS `patient01_healthy` simulation:
three long-axis orientations at 0/60/120 degrees and one short-axis plane.
Each has 30 grayscale frames at 192 × 192 pixels and **0.75 mm/pixel**.
Only these **120 images**, rather than the complete source volumes, are supplied.

The extraction uses one initial rigid pose, documented in `geometry.json`.
It aligns the anatomical reference to the first source mesh with maximum error
0.00763 mm. The native volume grid is 208 × 224 × 208 with spacing
0.82235/0.83450/0.72558 mm; trilinear sampling and a first-volume intensity limit
of 202 produce the byte-matched input images. Later meshes do not determine
the planes. Physical frame duration is unknown.

### Supplied helpers

`initial_mesh.npz` supplies 11,370 material points in mm, 47,186 fixed tetrahedra,
point/cell AHA labels and reference directions. `geometry.json` supplies the
plane poses, spacing and coordinate transform; `TASK.md` and a hash manifest
complete the public package. There are **123 payload files plus the manifest**.

Initial anatomy removes meshing from this condition. AHA 0 has no directional
basis. Three positive-AHA tetrahedra also lack usable axes; unknown directions
must remain unavailable rather than being filled with zero strain.

### Callable tools

The author implementation uses CPU NumPy/SciPy, Pillow, meshio and OpenCV DIS
optical flow. It selects material seeds within 1.5 mm of the initial planes:
402/321/478/483 seed observations across the four views. The affine baseline
fits one global 12-parameter deformation from the tracked in-plane observations.

The later tissue method fits vertex displacements using the same image evidence,
edge smoothness and a finite-Jacobian penalty. It uses scales of 0.75 mm for
image observations, 0.30 for edge gradients and 0.15 for Jacobian deviations,
three nonlinear steps per frame and positive-Jacobian backtracking. This is a
development-informed kinematic fit, not an active-force or circulation solver.

### Reference-only material

All later healthy source meshes are private to evaluation. Known material
correspondences also supply the privileged best uniform-scaling and affine
controls; these are representation checks, not input-legal video methods.
The static control repeats the initial body. `patient04_lbbb` is a separate
reference playback, not an inferred diagnosis or a second reconstruction test.

Public-only access was reviewed in code, not enforced by an isolated provider
runtime. The author had inspected the source. Reader figures and viewers include
private references and must not become solver inputs. Simulator material motion
is not independently measured patient strain.

## Task specification

Keep the initial material IDs and tetrahedral connectivity fixed while recovering
30 point arrays. Recompute deformation gradients F from corresponding tetrahedral
edges, Green–Lagrange tensors E=(FᵀF−I)/2, directional engineering strain
sqrt(eᵀFᵀFe)−1 and Jacobian J=det(F). Engineering strain and directional components
of E are distinct quantities. Use frame 1 as the reference, without asserting
that it is clinically adjudicated end diastole. Do not align each later frame
to remove displacement errors.

## Expected output

Retained analyzed models contain `points[30,11370,3]`, shared
`tetra[47186,4]`, cell labels/directions, directional engineering and
Green–Lagrange fields `[30,47186,3]`, and `jacobian[30,47186]`.
Missing directional values are NaN; geometry/Jacobians still cover those cells.
Volume-weighted nodal fields support the viewer without replacing element data.

The retained tissue export additionally contains full `F` and `E_green_lagrange`
tensors `[30,47186,3,3]`, boundary triangles, units and reference-frame metadata.
Its tensors are derived from the saved point arrays. Regional curves, peaks and
tissue-volume diagnostics remain separate outputs. Tissue volume is **not cavity
volume or EF**; no cavity/valve-plane partition was validated.

## Evaluation

Motion RMSE uses **341,100 point/frame pairs: 11,370 × 30 from one simulation**.
Geometry and Jacobian checks cover all **1,415,580 tetrahedron/frame pairs**.
Directional metrics use **31,241 of 31,244 positive-AHA cells**, representing
99.9928% of labelled LV reference volume. All 15,942 AHA-0 cells and the three
unsupported positive cells are excluded only from directional statistics.

Strain MAE averages absolute directional error with reference-volume weighting
within frames and then across 30 frames. Regional peak error averages the 17 AHA
regions per direction. Tissue-volume error averages relative curve error over
30 frames. These are correlated measurements, not independent patients.

| Method / information | Material RMSE | Long. / circum. / radial MAE | Tissue-volume error |
| --- | ---: | ---: | ---: |
| Static initial body | 6.19 mm | 4.11 / 6.49 / 11.27 pp | 1.87% |
| Uniform fit, reference motion supplied | 2.53 mm | 3.53 / 3.09 / 16.72 pp | 13.85% |
| Affine fit, reference motion supplied | 2.08 mm | 2.99 / 3.03 / 17.02 pp | 13.45% |
| Affine fit from four videos | 3.76 mm | 2.56 / 3.53 / 16.67 pp | 11.91% |
| Coupled tissue fit from four videos | 4.03 mm | 4.94 / 5.97 / 6.79 pp | 1.35% |

All five models have zero inverted elements, but **none passes all provisional
targets**: motion RMSE ≤2 mm, each directional MAE ≤5 pp, each direction's mean
regional peak error ≤5 pp, and zero inversions. These targets preceded the first
reconstruction results; they are development criteria, not clinical tolerances.

The tissue method reduces radial MAE from 16.67 to 6.79 pp and regional radial
peak error from 30.02 to 8.07 pp, while global point RMSE worsens. The retained
regional audit separates LV-labelled vertices (2.31 → 1.67 mm) from
RV/unassigned vertices (5.28 → 6.10 mm); the supplied views are centered using
initial LV geometry. Sparse image coverage and representation assumptions remain
alternatives to a general recovery limitation. The healthy reference itself
changes tissue volume by about 6%; a strict 1% incompressibility gate would reject it.

Comparability is **endpoint-only** across privileged and image-driven controls.
The video methods share observations but differ in model and development history;
their contrast is not a controlled causal estimate. LBBB playback is separate.

The 2026-09-27 audit verified 121 source files, all 120 extracted images, seven
saved model analyses and the existing full-tensor export. Original numeric scores
reproduce within 1e-8; saved float32 element/nodal fields and exported tensors
match the recomputed arrays. No fitting or new model execution occurred.

## Retained corrections

- **Numerical recovery:** 81 of 87 first-run CG solves hit the iteration limit.
  Raising the allowance from 300 to 2,000 preserved inputs and regularization and
  made all 87 converge. Three nonlinear steps still do not prove full stationarity.
- **Missing directions:** the superseded evaluator assigned −100% reference-frame
  engineering strain to three positive-AHA cells with zero axes. Corrected results
  mark them unavailable. All seven analyzed point arrays are unchanged; original
  outputs and executed code remain retained.
- **Reference scope:** the healthy/LBBB source manifest attribution erratum is
  recorded separately; native file IDs and hashes remain intact. Physical timing,
  chamber partition and clinical interpretation are still unqualified.

## Difficulty

Initial anatomy and numerical validity do not solve material tracking. The static
body's 1.87% tissue-volume error coexists with 6.19 mm motion error; the privileged
affine fit still misses radial strain. Four sparse planes leave unobserved motion,
so these author failures establish neither unique identifiability nor agent
difficulty. No clinical strain rate, blood flow, force balance or diagnosis is tested.

## Coverage

The source/package/mechanics audit and selected local visual inspection are
complete. A staged [operation-specific canonical story](../stories/cardiac-material-feasibility.story.md)
and [local source-derived pack](../../../../presentation/task-explorer/cardiac-material/manifest.json)
show the actual four-plane images, supplied initial mesh, fixed-ID saved motion,
one valid tetrahedron's F/E/J and directional fields, a missing-axis cell, and
the private simulator reference after a reader reveal. The display sample is a
deterministic excerpt of retained arrays; metrics concern the full arrays.
Integrated review, export and acceptance remain unfinished.

The public STRAUS project, collection and root-folder metadata inspected on
2026-09-27 supply no explicit redistribution license. The user's current scope
allows local noncommercial task interpretation without public redistribution;
native images, meshes and derived source views remain local. Open download does
not grant onward distribution rights.

## Sources

- [BR-029 protocol and source amendment](../../experiments/br029/protocol.md)
- [Corrected result interpretation](../../../../docs/research-rounds/BR-029-dynamic-heart-results.md)
- [Reference/control metrics](../../../../docs/evidence/br029-dynamic-heart-results.json)
- [Tissue-fit metrics](../../../../docs/evidence/br029-dynamic-heart-tissue-results.json)
- [Original integrity and correction record](../../../../docs/evidence/br029-dynamic-heart-integrity.json)
- [Source/package/mechanics audit](../sources/cardiac-material-audit.json)
- [Source-resolution receipt](../sources/cardiac-material-resolution.json)
- [STRAUS project](https://humanheart-project.creatis.insa-lyon.fr/multimodalityStraus.html)
- [Human Heart Project access guidance](https://humanheart-project.creatis.insa-lyon.fr/faq.html)
