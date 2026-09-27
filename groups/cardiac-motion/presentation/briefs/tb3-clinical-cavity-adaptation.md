# Adapt a cavity model and measure contraction

Track an initialized LV blood-pool surface through real clinical ultrasound,
then compare cavity contraction and functional interpretation with withheld
source surfaces. Correct executable responses to changed inputs coexist with
substantial contraction error in the retained study.

## Value

Separates tracking, transfer to another acquisition, geometric proximity,
volume/EF accuracy and interpretation. BR-034 improves on BR-032's fixed
measurement tables by using current volume pixels, but this does not by itself
establish accurate physiology or a reusable clinical tool.

## Given

### Original data

The primary input is `volumes.npy`, **18 consecutive acquired B-mode frames**
on a `[18,134,82,93]` Cartesian grid in `[t,z,y,x]` order. Spatial sampling is
**1 mm** along each axis. These are resampled native images, not synthetic
motion, beat stitching or a segmentation volume.

Source: EchoXFlow `recording_8aef1d9a69fc3bae`. Native indices 3–20 of 25
frames align with the annotated beat at about 22.6 volumes/s. The author applies
the published scanner-to-render convention `(-X,Z,Y)`, then an initial-surface
PCA basis and an 18 mm padded crop. Both axes and crop use only the initial
surface. The local axes are not adjudicated anatomical planes.

### Supplied helpers

`initial_mesh.npz` supplies the expert/software-derived LV endocardial surface
and its basal closure at `initial_mesh_frame=0`. `geometry.json` supplies origin,
1 mm spacing, shape and timestamps. The coordinate rule is
`XYZ_mm = origin + spacing * [x,y,z]` for `volumes[t,z,y,x]`.

The primary **58-file** public inventory contains those three files,
54 unannotated orthogonal preview PNGs and BR-032's optional
`previous_case_solve.py`. Its fixed-table limitation is disclosed. No later
surface, EF, disease label, Doppler, patient history or source identifier is
given. Supplying the initial cavity removes segmentation and meshing at that
frame; later tracking remains the task.

### Callable tools

The frozen Python 3.12 environment provides NumPy 2.2.6, SciPy 1.15.3,
Pillow 11.3.0, OpenCV 4.12.0.88, meshio 5.3.5 and scikit-image 0.25.2.
The model allowance is 1,800 s on four CPUs and 8 GiB RAM, with no GPU.
The submitted executable must finish a replay within 300 s on the same CPU/RAM
budget. Prompt restrictions forbid source scans, reference reconstructions,
pretrained cardiac models and previous workbench retrieval. Primary execution
declares public network mode; the retained independent replays disable network.

### Reference-only material

Later source endocardial surfaces and their volume/EF curves are private to
the verifier. They are operator/software-derived clinical annotations, with
observer uncertainty and no independent cardiologist adjudication. Dense cavity
indices are not measured myocardial material trajectories or disease etiology.

Two additional cases reach only the unchanged executable after the attempt:
a hidden reduced-function case with 35 annotated frames and a supplementary
preserved-function case with 48 frames. Each replay receives its own initial
surface, calibration and current images; no model feedback is supplied.
Their input grids are `[35,112,84,85]` and `[48,131,84,88]`, with
108 and 147 public files respectively. Reader reference reveals are not inputs.

## Task specification

Inspect images and save `pre_model_assessment.json` before fitting. Then recover
all phases from the current volumetric pixels while retaining the supplied
initialization at its declared frame. The executable must handle different
frame counts/grids, repeated-initial-frame inputs and a circular frame shift
with an updated initialization index.

The actual solver replaces the previous case's tables with sequential 3D TV-L1
optical flow. It smooths a 12 mm padded tracking crop, registers consecutive
frames including the last-to-first edge, samples displacement at cavity
vertices and distributes accumulated loop drift linearly over the cycle.
Identical neighboring arrays explicitly yield zero flow. The initial mesh
remains exact; the basal closure follows the image displacement. This is
kinematic cavity tracking, not myocardial material identification or mechanics.

## Expected output

`prediction.npz` contains finite `points[T,N,3]` in mm and shared integer
`faces[M,3]`, with at most 10,000 vertices and 20,000 triangles. Surfaces must
be closed and consistently oriented, including the declared basal closure.
The retained outputs have **1,946 vertices and 3,888 triangles** per frame.

Also provide executable `solve.py --input ... --output ...`, `method.md`,
inspectable overlays and `summary.json`: one independently calculated mL volume
per frame, `EF=100*(max(volume)-min(volume))/max(volume)`, zero-based ED/ES indices,
uncertainty and a bounded functional interpretation. The four supplied pilot
categories are EF below 30%, 30–40%, above 40% to below 54%, and at least 54%.
These task bins are not a complete clinical guideline or a heart-failure diagnosis.

## Evaluation

The frozen pilot reward requires valid arrays/topology and all five numerical
gates: mean sampled symmetric surface distance at most 3 mm, maximum framewise
distance p95 at most 6 mm, EF error at most 8 percentage points, and EDV/ESV
relative errors at most 15%. The declared functional category must also match
the private reference category. Distances sample vertices, edge midpoints and
triangle centroids; they are not exact continuous Hausdorff distances. The
historical implementation uses absolute signed volume and has no general
self-intersection check. Original results remain unchanged.

| Case and execution role | Frames | Reference EF | Saved EF | EF error | Mean distance | ESV error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Primary; one model attempt | 18 | 45.31% | 22.01% | 23.30 pp | 1.89 mm | 47.18% |
| Hidden reduced; executable replay | 35 | 47.62% | 21.68% | 25.94 pp | 1.85 mm | 57.70% |
| Supplementary preserved; executable replay | 48 | 60.29% | 29.80% | 30.49 pp | 2.24 mm | 76.79% |

All three pass mean-distance and EDV gates; only the hidden reduced case also
passes the p95-distance gate. All fail EF, ESV and reference-category checks.
Initial-frame agreement benefits directly from the supplied reference surface.
The primary attempt completed normally in **1,207.81 s**; its valid artifact
has original reward **0**. This is a scored selected-case result, not an
infrastructure exclusion or an estimate of a capability ceiling.

The exact-reference control passes. The static initial-surface control fails,
yet achieves **2.70 mm mean distance** while making **45.31 pp EF error**.
The no-output control fails as expected. Mean geometric proximity alone is
therefore insufficient for this dynamic task.

Retained executable checks establish narrower successes:

- **Original input:** the replay reproduces every output vertex exactly.
- **Static input:** repeated initialization volumes produce stationary vertices
  and EF 0%, passing the predeclared limits of 0.25 mm RMS motion and 1 pp EF.
- **Phase shift:** after undoing the five-frame shift, points and volumes equal
  the original exactly, with 0 mL volume MAE against a 2 mL limit.
- **Hidden execution:** the reduced and preserved cases complete in 102.76 s
  and 168.77 s, within 300 s. Successful execution does not repair their
  clinical-reference disagreement.

An initial original-input replay exited 125 before execution because its image
was missing. A separate `original-v2` result preserves the successful replay.
The current audit checks saved arrays; it does not rerun flow, a model or Docker.

## Difficulty

Speckle motion, regularization, boundary dropout and basal ambiguity can produce
a smooth surface with too little contraction. Selected reference-systolic
sections show the saved solver envelope remaining larger than the private
reference. These views explain a measured disagreement without declaring the
source annotation clinically infallible.

The initial image-only impression was mild-to-moderate reduction with substantial
uncertainty. The final report selected severe reduction from its own 22.01% EF,
disagreeing with the primary source category. Its heuristic range 16.3–27.7%
excludes the 45.31% reference. The other two ranges also exclude their references.
These are uncalibrated sensitivity estimates. The within-session change does not
establish a causal benefit or harm of modeling. Etiology, flow and myocardial
strain remain outside the supplied evidence.

## Coverage

One selected development case and one actual `gpt-5.6-sol`/xhigh attempt, plus
controls and unchanged-executable replays. The initial target of 25–45% reference
EF was broadened before model results. The supplementary preserved case was
added after dispatch and replaced on input-quality grounds before completion;
it is not retroactively part of the original preregistered model reward.

The rejected preserved candidate had 17.78% of initial vertices outside the
acquired sector. The replacement has 0.21% initially and 0.0086% overall; the
primary and hidden reduced cases have zero. Preserve both control freezes and
the superseded coordinate export; the corrected admitted inputs are separate.

Three selected archives match publisher LFS hashes, and 114 extracted recording
files match those archive members. Direct Blosc decoding equals Zarr. All
101 prepared volumes and 303 unannotated previews reproduce. The publisher's
per-array digest differs from decoded C-order hashing; its serialization remains
unresolved, so this is not reported as an array-hash match. Public source exposure
is unknown and the cases are not a matched diagnostic cohort.

Source attribution: Elias Stenhede et al., **EchoXFlow**, CC BY-NC-SA 4.0.
The pinned catalogue and retained license agree with the official dataset card
inspected on 2026-09-28. Source-derived images, surfaces and media remain local
with attribution and license information. The source audit and selected still
review do not yet constitute canonical story, integrated visual acceptance or
completed exports.

## Sources

- [BR-034 — Clinical LV adaptation and functional assessment](../../experiments/br034/protocol.md)
- [Original contract and source selection](../../../../docs/research-rounds/BR-034-pathological-echo.md)
- [Supplementary control and input-quality correction](../../../../docs/research-rounds/BR-034-preserved-control-amendment.md)
- [Original result interpretation](../../../../docs/research-rounds/BR-034-results.md)
- [Frozen results, controls and replay receipts](../../../../docs/evidence/br034-clinical-adaptation-results.json)
- [Native source and retained-output audit](../sources/clinical-cavity-audit.json)
- [EchoXFlow dataset](https://huggingface.co/datasets/Ahus-AIM/EchoXFlow)
- [EchoXFlow source tools](https://github.com/Ahus-AIM/EchoXFlow)
- [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
