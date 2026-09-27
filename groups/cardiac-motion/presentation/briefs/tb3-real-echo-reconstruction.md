# Recover a dynamic cavity from real ultrasound

Construct a dynamic LV blood-pool surface from four calibrated planes of one
real 3D ultrasound sequence. The retained attempt produced an image-guided,
case-specific mesh; its artifact reward does not establish anatomical accuracy.

## Value

Separates original image interpretation, completion of unobserved shape and
the saved executable's response to changed inputs. This condition supplies no
initial anatomy, masks or reference reconstruction. It is distinct from the
FeEcho4D contour studies and STRAUS material-motion studies.

## Given

### Original data

**72 grayscale PNGs:** four simultaneous reslices, each with all 18 original
frames, at 256 × 256 pixels and **0.75 mm/pixel**. They come from EchoSlicer's
`dataset/A_0.dcm`, selected as the first lexicographic non-resource-fork DICOM
in the public v1.0 archive. Selection was not based on model performance.

The author decoded a native `[18,404,76,62]` uint8 array in spherical
rho/phi/theta coordinates, then sampled two long-axis planes and short-axis
planes at source depths 65 and 105 mm. All frames retain their original order
and 161.15 ms spacing; there is no synthetic motion or phase interpolation.
Eighteen samples do not by themselves establish one adjudicated heartbeat.

### Supplied helpers

`geometry.json` supplies four plane origins and orthonormal in-plane directions,
pixel centre 127.5, spacing, frame IDs 1–18, times 0–2.73955 s and task axes in mm.
The public inventory is exactly **73 files**. Source coordinates were rotated
and translated into the task frame; the rigid transform does not create new
anatomical information or demonstrate freedom from prior source exposure.

The solver receives no masks, seed points, initial mesh, full native volume,
DICOM identifiers or source acquisition link. Plane images are reslices of one
volume acquisition, not four separately acquired probe videos.

### Callable tools

The frozen Python 3.12 container provides NumPy 2.2.6, SciPy 1.15.3, Pillow
11.3.0, OpenCV 4.12.0.88, meshio 5.3.5 and scikit-image 0.25.2, with four CPUs,
8 GiB memory and no GPU. The agent allowance is 1,800 s; verification is separate.
The prompt permits local processing and forbids retrieval of the source case,
pretrained cardiac models or previous solvers. The primary task declares public
network mode, so this is a prompt restriction, not enforced network isolation.
The later retained executable replays used `--network none`.

### Reference-only material

The raw DICOM, native volume and four additional review planes remain author-side.
The withheld set comprises long-axis orientations 45/135 degrees and short-axis
depths 45/85 mm: another **72 images**, unavailable to the original solver.
They permit section/image inspection but provide no independent contours.

No paired 3D geometry, material correspondence, strain, clinical EF, flow or
diagnosis truth is supplied. Chamber identity and basal closure remain
unadjudicated. The control called `oracle` in historical execution receipts is
an image-ignorant static ellipsoid used to test format validity, not anatomy GT.

## Task specification

Infer cavity location, apical extent and a declared basal cap from the supplied
images. Construct 18 finite, closed, outward-oriented surface meshes with shared
triangle connectivity and positive signed volume in the supplied mm frame.
Persistent surface indices represent geometric correspondence; they do not
establish tracked myocardial tissue or permit a strain claim.

The original agent inspected individual images, contact sheets, enlarged regions
and pixel grids before recording framewise radii, centroids, basal depths and
apical depths in six `OBSERVED` tables. Its solver builds a smooth stack of
25 rings × 48 azimuths, plus basal and apical centre vertices. The planar basal
fan is a modeling convention, not an observed valve surface. Between-plane shape
comes from a fixed radial profile and mild harmonic modulation.

## Expected output

`prediction.npz` contains `points[18,N,3]`, integer `faces[M,3]` and
`alternative_points[K,18,N,3]`, with 2–5 alternatives, at most 10,000 vertices
and 20,000 triangles. Also provide executable `solve.py --input ... --output ...`,
`method.md` and `summary.json` with frame IDs, consistent mL volumes, inferred
extrema, basal-cap convention, assumptions and uncertainty.

The retained primary has **1,202 vertices and 2,400 triangles**. Three alternatives
change radial extent, apex or basal inclusion while sharing connectivity and
timing. Their spread is sensitivity to chosen assumptions, not a calibrated
confidence interval or guaranteed coverage of the true cavity.

## Evaluation

The automatic reward checks array shapes, finite values, index bounds,
oppositely oriented two-face edges, nondegenerate primary triangles, positive
primary/alternative volumes, required files and agreement with reported volumes.
It does **not** test anatomical accuracy or general self-intersection. The
original reward remains 1; the same reward for the static ellipsoid shows why
format validity must not be presented as reconstruction accuracy.

| Retained execution | Artifact reward | Supported observation |
| --- | --- | --- |
| One fresh `gpt-5.6-sol`, xhigh attempt | 1 | Completed in 657.06 s; valid submitted artifact |
| Static ellipsoid format control | 1 | Constant 80.53 mL despite ignoring image motion |
| No-output control | 0 | Expected missing prediction file |

Primary volume spans **54.08–177.57 mL**, with minimum at frame 14 and maximum
at frame 10. The 0.695 fractional change is a model-derived geometric quantity,
not validated clinical EF. The combined alternative/frame range is
42.01–219.73 mL. All signed volumes and retained motion statistics reproduce
from the saved arrays without running the solver.

Triangle-plane intersections are checked on all eight planes. The primary has
no section at short-65 and crosses withheld short-85 only at frames
3/4/9/10/15/16. These are consequences of the chosen envelope and basal cap,
not adjudicated anatomical successes or failures. Inner/outer brightness
contrasts exclude empty or poorly supported sections; they are image proxies,
not segmentation scores.

Retained altered-input runs further limit the reusable-executable claim:

- **Static inputs:** replacing each view's later frames with its first frame
  changes 68/72 PNGs, yet primary and all alternative points remain exactly
  unchanged, including 5.3973 mm RMS displacement from frame 1. The saved script
  reads pixels for overlays and does not re-estimate its measurement tables.
- **Changed coordinate frame:** unchanged images with rigidly transformed
  calibration produce the corresponding transformed points to below 1e-10 mm
  RMS. This supports coordinate handling, not new image interpretation.
- **Execution limits:** initial replay invocations exited 125 before running
  because the container image was absent. Separate v2 runs completed; their
  whole-artifact reward 0 reports that `solve.py` was not copied into the output
  directory. These records do not establish anatomical failure. Current checks
  inspect those retained outputs; they are not fresh replays or agent attempts.

## Difficulty

Sparse image sections leave out-of-plane shape and basal closure underdetermined.
The agent's original image viewing is retained in its trace; fixed replay output
does not show that it ignored those images or memorized the public source.
Public pretraining exposure remains unknown. A convincing animation, positive
volume or plausible extrema cannot settle chamber identity, material mechanics
or clinical function without an appropriate independent reference.

## Coverage

One selected source sequence, one actual model attempt and two format controls.
The historical experiment's `not_assessed` label is not an absence of execution.
The source audit verifies the native decode, frozen inventory, all 144 reslices,
retained surfaces, altered-input artifacts and section/brightness computations.
Selected native views and overlays are reviewed separately from full-cycle
motion, integrated Explorer, mobile and no-GPU acceptance.

The public project and release describe research availability, but the inspected
repository/release metadata provide no explicit redistribution license. Raw and
derived source assets remain local. This entry's canonical story, portable
exports and final visual review remain unfinished pending documented permission
or an explicit user-approved private-local delivery scope. Audit completion
alone does not count as explainer completion.

## Sources

- [BR-032 — real ultrasound without a reference reconstruction](../../experiments/br032/protocol.md)
- [Original source and task preparation](../../../../docs/research-rounds/BR-032-real-echo-case.md)
- [Original result interpretation](../../../../docs/research-rounds/BR-032-real-echo-results.md)
- [Frozen result and replay receipt](../../../../docs/evidence/br032-real-echo-results.json)
- [Source, saved-output and replay audit](../sources/real-echo-audit.json)
- [EchoSlicer project](https://github.com/echonet/3d-echo)
- [EchoSlicer v1.0 release](https://github.com/echonet/3d-echo/releases/tag/v1.0)
