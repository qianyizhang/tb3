# Construct deforming meshes from supplied masks

Build one deforming tetrahedral mesh from a complete cardiac mask sequence,
then separate geometric fit and correct tensor arithmetic from recovered tissue
motion. In this retained two-attempt pilot, both constructions pass; both miss
the simulator radial-strain target.

## Value

All-phase segmentation removes boundary discovery, but does not supply material
correspondence. Different tissue motions can occupy the same moving domain.
A plausible mesh and correct strain calculation therefore require a separate
check against withheld material trajectories.

## Given

### Original data

The primary case is one **30-phase STRAUS healthy biventricular myocardial wall**.
`masks.npz` supplies boolean `masks[T,Z,Y,X]` with shape **30 × 86 × 81 × 85**.
The second condition adds registered float32 ultrasound `images.npy` on exactly
the same grid. The masks and geometry files are byte-identical between conditions.
Ultrasound intensity is neither blood velocity nor reference deformation.

The masks were independently rasterized from each simulator mesh at voxel
centres. They include both inner and outer wall boundaries, without persistent
vertex IDs, tracked points, AHA labels or an initial mesh. Original material
identities cannot be read from the binary mask labels.

### Supplied helpers

`geometry.json` gives **1.5 mm isotropic spacing**, origin
**[81, −108, 95] mm**, reference frame 0 and dimensionless phases `0/30…29/30`.
World coordinates are `origin + spacing × [x,y,z]`; array order is `[t,z,y,x]`.
Synthetic physical frame duration is unknown (`timestamps_s=null`), so a
seconds-based strain rate is unavailable.

The transfer case supplies **18 all-phase clinical LV cavity masks**, with
optional registered images. It has a different grid and real timestamps.
These masks enclose blood pool and basal closure; they supply the volume curve
but neither epicardium nor myocardial material motion.

### Callable tools

The frozen environment provides ordinary NumPy/SciPy, scikit-image, meshio,
OpenCV and Pillow; ordinary meshing libraries are permitted. Each original
`gpt-5.6-sol`/xhigh attempt had 30 minutes, 4 CPUs and 8 GB, no evaluator feedback
and no retry. The unchanged submitted programs were subsequently executed on the
clinical transfer with a five-minute limit and runtime network disabled.
The masks+images program applies texture refinement only to myocardial-wall
inputs; its clinical cavity replay deliberately uses masks alone.

These are retained executions. Reviewing this entry does not launch a model,
rerun its solver or install a medical runtime.

### Reference-only material

The evaluator retains the simulator's complete moving mesh, AHA cell labels,
anatomical directions and reference-volume weights. The source has **11,370
vertices and 47,186 tetrahedra**; it is not the agent's required topology.
Every source-cell reference centroid is an independent material probe, located
barycentrically in the agent's initial tetrahedral mesh. Later predictions are
compared at those same material probes, without per-frame realignment.

Directional comparisons require positive AHA labels and three usable source
axes. Coverage and regional coverage remain explicit. Simulator material motion
is synthetic truth for this selected case, not measured patient strain. The
clinical surface sequence is a geometric comparator; it has no material-motion
truth. Exact-source oracle output is privileged evaluator material, not a legal
masks-only answer. Reader-facing reference reveals must remain separate from inputs.

## Task specification

Construct an initial tetrahedral mesh from frame 0, preserve its connectivity,
and infer vertex positions throughout the cycle. Fixed indices encode a
hypothesized material map; they do not prove tissue tracking.

For each tetrahedron, use reference and current edge-column matrices `Dm` and
`Ds`: `F=Ds·Dm⁻¹`, `E=(FᵀF−I)/2`, `J=det(F)`. F maps reference column vectors
to current column vectors; E is full Green–Lagrange strain in fractional units.
Negative or zero J fails the orientation check. Directional engineering strain
`||F·e||−1`, evaluated on private anatomical axes, is a different quantity from
E or its minimum principal value used in the historical viewer.

## Expected output

A runnable `solve.py --input DIRECTORY --output DIRECTORY`, `prediction.npz`
with `points[T,N,3]` in world mm, fixed integer `tetra[M,4]`, full `F` and `E`
arrays `[T,M,3,3]` and `J[T,M]`. `method.md` states meshing, correspondence
assumptions and uncertainty. `assessment.json` declares mask semantics,
limitations and whether the domain supports a myocardial-strain model.

For `lv_cavity`, the program must set `myocardial_strain_supported=false`.
Mathematical cavity deformation may support geometric volume/EF checks; it
cannot be reported as myocardial strain. For synthetic wall, a true domain flag
does not certify the inferred motion.

## Evaluation

Construction reward requires a valid finite mesh and fields, no duplicate or
initially degenerate tetrahedra, at most two tetrahedra per shared face, mean
voxel-centre Dice **≥0.90**, mean absolute relative domain-volume error **≤5%**,
zero `J≤0` cells and independently recomputed F/E/J errors **≤10⁻⁴**.

Separate material diagnostics require **≥95%** reference-volume and usable-LV
coverage, covered-probe motion RMSE **≤2 mm**, each directional and regional-peak
MAE **≤5 percentage points**, and regional peak timing MAE **≤2 frames**.
Motion and directional errors are reference-volume weighted; regional peaks
average across the represented AHA regions. Timing accepts reference frames
within 0.5 pp of the reference extremum. These diagnostic gates do not change
the construction reward. High coverage is not complete coverage.

| Retained result | Masks only | Masks + ultrasound |
| --- | --- | --- |
| Construction reward | 1 | 1 |
| Vertices / tetrahedra | 63,326 / 233,865 | 63,326 / 280,638 |
| Mean voxel-centre Dice | 0.9461 | 0.9328 |
| Material coverage | 98.06% | 98.06% |
| Covered-probe motion RMSE | 1.615 mm | 1.717 mm |
| Usable-LV directional MAE: longitudinal / circumferential / radial | 2.87 / 3.51 / **7.37 pp** | 2.90 / 3.22 / **5.45 pp** |
| Minimum J / nonpositive cell-frames | 0.0546 / 0 | 0.1877 / 0 |
| Material diagnostic outcome | Radial target missed | Radial target missed |

Both methods register signed-distance fields, regularize displacement and match
phase centroids and total volumes. Masks-only splits occupied voxels into five
tetrahedra; masks+images uses six and adds a smoothed texture residual capped
at 2 mm and projected tangent to the initial boundary. Volume agreement is an
explicit fitting constraint. The two independent programs differ in more than
image access: this is an **endpoint-only comparison**, not an identified causal
benefit of ultrasound. The lower radial error coexists with worse whole-body
motion RMSE and mask fit.

The exact-source oracle passes; a static reference mesh has Dice 0.704 and
motion RMSE about 6.00 mm and fails construction. The empty-answer control
fails. Retained analytic checks include rigid/affine maps, vertex permutation,
probe location and equal-occupancy cylinder motions with different strain.

**Post-hoc mesh limits.**

Both submitted meshes have **six boundary edges incident to four boundary
triangles**; the simulator has none. The frozen face-incidence gate does not
test this boundary-edge property. Worst-phase reference tissue volume with
`J<0.2` is **0.1653% / 0.0014%**; source value is zero. These are post-hoc
engineering indicators, not new frozen gates or clinical cutoffs. Positive J
alone establishes neither global injectivity nor physiological force balance.

**Clinical transfer.**

Both unchanged programs pass construction on the selected cavity case, with
Dice **0.9807 / 0.9806** and EF **45.3313%**. The original source surface gives
**45.3064%**: approximately **0.0249 pp** difference. Rasterization already
supplied the **45.3313%** mask EF. This demonstrates preservation of supplied
geometry, not independent recovery of contraction or improvement over BR-034's
image-tracking condition. Both assessments correctly reject myocardial-strain
interpretation; their reused claims that physical timestamps are absent are
incorrect for this clinical input. Preserve that limitation in the original files.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Masks only | All 30 binary wall masks and calibration | Own shared mesh and hypothesized material map |
| Masks and images | Identical masks plus registered ultrasound | Own mesh; optionally constrain motion with appearance |
| Clinical transfer | All 18 cavity masks; optional images and timestamps | Unchanged program preserves geometry and rejects myocardial strain |
| Exact-source oracle | Private source trajectories and mesh | Validate evaluator arithmetic; privileged control |
| Static / empty controls | Static reference geometry / no output | Test construction failure; not agent attempts |

## Difficulty

Tangential sliding and torsion can preserve domain occupancy. Smooth colors and
small global volume error cannot resolve those unobserved degrees of freedom.
Regional averages can also conceal local errors. There is one synthetic case,
two fresh model attempts and one shared clinical transfer, not a population
study, clinical strain validation, flow estimate or etiologic diagnosis.

## Coverage

The retained result records freeze identity, controls, actual runtime settings,
submitted artifacts, traces, independent saved-output regrades and historical
infrastructure failures. A dependency-cache build failure happened before the
clinical solver; later successful replay is retained separately. Saved-output
regrading does not constitute fresh model or solver execution. Public-source
training exposure is unknown; a trace search with no retrieval candidates does
not establish absence from pretraining.

The [source audit](../sources/mask-mechanics-audit.json) records exact file pins,
input derivation and saved-score checks. Source-only imagery, supplied-mask
overlays and result curves were inspected locally. STRAUS onward redistribution
or explicit private-local final scope remains unresolved under the existing
question in this chat. The canonical operation story, portable assets, export,
full-motion/mobile/no-GPU review and acceptance remain pending. This source audit
is not an accepted explainer and does not reduce the unfinished count.

## Sources

- [Frozen BR-035 protocol](../../../../docs/research-rounds/BR-035-segmentation-mechanics.md)
- [Retained results and engineering limits](../../../../docs/research-rounds/BR-035-results.md)
- [Original evidence receipt](../../../../docs/evidence/br035-segmentation-mechanics-results.json)
- [Exact masks-only instruction](../../experiments/br035/reproduction/cases/cardiac-masks/task/instruction.md)
- [Exact masks-and-images instruction](../../experiments/br035/reproduction/cases/cardiac-masks-images/task/instruction.md)
- [Independent frozen scorer](../../experiments/br035/reproduction/cases/cardiac-masks/task/tests/score.py)
- [Input and saved-answer manifest](../../experiments/br035/reproduction/manifest.json)
- [STRAUS source and terms audit](../sources/cardiac-material-audit.json)
- [Clinical source and terms audit](../sources/clinical-cavity-audit.json)
- [Mask-to-mechanics input/output audit](../sources/mask-mechanics-audit.json)
