# Study motion recovery from sparse contour anchors

Recover changing LV cavity contours from four ultrasound sequences and one or
two supplied contour frames. **BR-027 is an author development screen on one
previously inspected patient; no independent model attempt was run.**

## Value

Separate image tracking on unsupplied frames from interpolation into withheld
view directions. Score shape and volume/EF independently: a correct scalar EF
can accompany an incorrect cavity boundary.

## Given

### Original data

FeEcho4D Patient001, 30 frames from each of four native radial views at assumed
0/45/90/135 degrees: **120 images**, each 464 × 485 pixels. Native source planes
are 1/10/19/28, one-based. The public images are byte-identical to their source.

`geometry.json` supplies 0.089950 mm/pixel, x=242 px rotation axis and y=184.5 px
origin, derived only from the plane-1 frame-2 cavity mask. Image y increases down;
mesh coordinates use `x=r sin(phi) cos(theta)`, `y=r cos(phi)`,
`z=r sin(phi) sin(theta)` in millimetres. The radial pose convention remains an
assumption, not independently measured plane transforms.

### Supplied helpers

- **One anchor:** four binary cavity masks, all at filename frame 2.
- **Two anchors:** eight binary masks at frames 2 and 17.

Anchor pixels encode native cavity label 127 as foreground 255. Frame numbers
are explicit anchors, not supplied clinical phase labels. Both packages include
the same task instructions, geometry and a hash manifest. There are no additional
target-time masks, source config/EF values, OBJ meshes or dense answers.

### Callable tools

The retained author methods use CPU NumPy/SciPy/Pillow and OpenCV DIS optical
flow with the medium preset. Tracking warps signed-distance fields using
consecutive target-to-source flow. The two-anchor method blends the two
propagated fields, with weights clamped outside the anchor interval.

The image-free controls copy one anchor or linearly interpolate two anchor
signed-distance fields with endpoint hold. Periodic interpolation was not tested.
The stronger one-anchor method applies GrabCut to the saved tracking prediction:
60% interior-distance seed, 15-pixel exterior band, 20-pixel crop padding and five
iterations. These fixed settings were chosen after inspecting the first screen;
the method is **development-informed**, not blind.

### Reference-only material

All masks from source planes [3,8,12,17,21,26,30,35] and unsupplied times of the
four input views are evaluator material. The clean-contour control uses all 120
input-view masks. The dense comparator uses all 36 unique source directions,
including evaluation views; its overlap is source fit, not withheld accuracy.

Predictions were serialized and hashed before evaluation. Input access was
reviewed in code, without OS isolation; the author already knew this patient.
The source tree, private evaluator and reader viewer are not solver inputs.
The fitted dense reference is annotation-derived, not independent 3D or clinical
truth. Native OBJ cavity/shell and physical-transform questions remain unresolved.

## Task specification

Preserve every supplied anchor, recover the intervening cavity masks from images,
then interpolate their radial profiles into a closed mesh at each of 30 frames.
Use fixed connectivity and document units, frame IDs and anatomical assumptions.
Compute the complete cavity volume curve and its extrema; shared vertex indexing
is a surface parameterization, not myocardial material tracking.

## Expected output

The retained predictions contain `vertices[30,4538,3]` in mm, shared
`faces[9072,3]`, `volume_ml[30]`, `radius_px[30,72,65]` and
`input_view_masks[4,30,464,485]`. Solver receipts identify inputs, code and
prediction hashes, extrema frames and **EF = 100 × (1 − min(V)/max(V))**.
The controls computed by the evaluator omit input-view prediction masks.
These author packages are not a formally admitted or provider-isolated task.

## Evaluation

Each condition uses the same **240 withheld frame/plane pairs: 30 × 8 from one
patient**. HD95 is computed per pair and then averaged. Volume MAPE averages
relative error over the full 30-frame curve against the dense comparator.
EF uses curve extrema, without assuming the source clinical config's index base.

| Author method / assistance | Withheld Dice | Mean HD95 | Volume MAPE | EF error | Development gates |
| --- | ---: | ---: | ---: | ---: | --- |
| All-frame clean contours | 0.937 | 0.623 mm | 2.31% | 1.27 pp | Pass |
| Two-anchor DIS | 0.920 | 0.841 mm | 7.82% | 0.82 pp | Pass |
| One-anchor DIS | 0.887 | 1.114 mm | 29.16% | 21.60 pp | Fails all four metrics |
| One-anchor DIS + GrabCut | 0.869 | 1.636 mm | 7.70% | 1.32 pp | Fails shape |
| One-anchor static | 0.825 | 1.605 mm | 78.21% | 64.02 pp | Fails all four metrics |
| Two-anchor endpoint interpolation | 0.889 | 1.039 mm | 18.42% | 0.26 pp | Fails shape/curve |

The predeclared BR-027 development gates reuse BR-025's proposed targets:
Dice ≥0.90, mean HD95 ≤1 mm, volume MAPE ≤10%, EF error ≤5 pp, and closed,
nondegenerate positive-volume geometry. They are not clinical tolerances. All
saved meshes pass the topology/volume-sign checks. Dense derived EF is 64.02%;
its extrema are frames 3/17. One-anchor DIS gives 42.42% at frames 30/19;
refinement gives 65.34% at frames 2/20. These phase differences are descriptive.

Direct input-view Dice excludes supplied frames: **116 pairs** for one anchor
and **112 pairs** for two anchors. It is 0.897 for one-anchor DIS, 0.937 for
two-anchor DIS and 0.867 after refinement. This demonstrates disagreement before
3D interpolation; it does not clinically adjudicate the source contours.

Comparability is **matched for common withheld endpoints**, with assistance and
method differing. The direct-input endpoints have different excluded-frame sets.
GrabCut additionally has development-history confounding. The changed origin and
EF definition differ from BR-025; use BR-027's recomputed clean/dense controls.

The 2026-09-27 audit checked both exact public inventories, native source identity,
anchor preservation, original code/prediction hashes and all seven saved conditions
within 1e-10. It read saved outputs without tracking or refitting. Selected native
overlays separate direct input-view masks (plane 28, frames 17/25) from withheld
mesh sections (plane 8, frame 17). Plane-28 frame 17 is supplied only to the
two-anchor condition; its exact agreement there is not tracking success.

## Difficulty

One anchor supplies initial anatomy but requires recovering contraction and
relaxation from images. These baselines do not provide an input-legal complete
pass for that condition; the two-anchor condition does pass the same development
gates. Baseline failure does not establish model difficulty, unique 3D recovery,
material strain, clinical validity or performance on new patients.

## Coverage

The package and saved-output audit is complete. The [source-resolution receipt](../sources/cardiac-anchor-resolution.json)
confirms the matching FeEcho4D Patient001 inputs and saved author outputs are
available for local noncommercial interpretation. The [canonical story](../stories/cardiac-anchor-feasibility.story.md)
and [local source pack](../../../../presentation/task-explorer/cardiac-anchor/NOTICE.md)
use actual retained images, anchors and predictions. Integrated visual review and
export remain unfinished. FeEcho4D onward redistribution rights remain unresolved
under the [shared source review](../sources/cardiac-contour-audit.json); this
locally generated pack carries no public redistribution claim. This entry remains
incomplete until reviewer sign-off.

## Sources

- [BR-027 protocol and original interpretation](../../experiments/br027/protocol.md)
- [Original metrics](../../../../docs/evidence/br027-cardiac-results.json)
- [Original integrity receipt](../../../../docs/evidence/br027-cardiac-integrity.json)
- [Author implementation and access boundary](../../../../probes/cardiac-reconstruction/authoring/video_difficulty/README.md)
- [Package and saved-output audit](../sources/cardiac-anchor-audit.json)
- [FeEcho4D project and research-use terms](https://feecho4d.github.io/Website/)
