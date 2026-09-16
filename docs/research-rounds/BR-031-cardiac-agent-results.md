# Cardiac agent experiments — supplied motion to reconstructed mechanics

Four fresh model trials are complete. Terra correctly computed finite strain
from supplied motion. With only four calibrated ultrasound views and the initial
mesh, both Terra and Sol missed complete reconstruction acceptance. Sol recovered
the LV considerably better and passed several independent component checks.
The approved full-volume Sol follow-up also completed normally. It modestly
improved image-plane overlap but did not rescue material motion or mechanics.

[Prospective protocol](BR-031-cardiac-agent-levels.md) ·
[Predeclared volume contrast](BR-031-volume-contrast.md) ·
[Reproduction and code](../../probes/cardiac-reconstruction/authoring/levels/README.md) ·
[Verified final evidence receipt](../evidence/br031-cardiac-agent-results.json) ·
[Earlier partial receipt](../evidence/br031-cardiac-agent-results-pending-approval.json)

## Completed outcomes

| Task / agent | Observed Dice | Withheld Dice | Material RMSE | LV / RV-unassigned RMSE | Strain MAE L / C / R | Outcome |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| L0, Terra/high | — | — | Supplied motion | — | Calculation errors below 2e-15 in fractional units | Pass, including independent rigid/affine/shear/missing-axis checks |
| L1, Terra/high | 0.823 | 0.771 | 4.91 mm | 4.24 / 5.80 mm | 5.52 / 8.66 / 12.87 pp | Misses geometry/motion and mechanics |
| L1, Sol/xhigh | 0.884 | 0.881 | 3.66 mm | 1.77 / 5.42 mm | 3.43 / 3.97 / 5.39 pp | Partial component success; misses complete geometry/motion and mechanics |
| L1V, Sol/xhigh, native volume added | 0.893 | 0.895* | 4.45 mm | 1.85 / 6.73 mm | 5.13 / 3.85 / 8.49 pp | Partial component success; misses complete geometry/motion and mechanics |

*L1V's other-plane score is off-plane agreement, not withheld generalization:
the added volume contains those planes.

Terra took 81 seconds for L0, 812 seconds for L1; Sol took 998 seconds for L1.
Sol's L1V attempt took 935 seconds.
Each attempt had 1800 seconds available and ended normally. They were fresh
sessions with no earlier solution, author solver or target future mesh supplied.
Runtime traces match the requested model and effort and contain the frozen
instruction. Reviewed tool-call records show no external reference retrieval or
delegation. These are trace-based observations, not proof of provider-side
identity or absence of training exposure.

Sol's independent component results are informative:

- Withheld slices pass the 0.85 Dice target, although observed slices miss 0.90.
- Surface mean / p95 error is 1.32 / 3.13 mm, passing 2 / 5 mm targets.
- Whole-myocardium volume-curve error is 0.94%, passing the 5% target.
- LV material RMSE is 1.77 mm; the full-body 3.66 mm fails the fixed 2 mm target.
  RV/unassigned error is 5.42 mm. The LV result is a component finding, not a
  retrospective change to the original whole-body acceptance rule.
- Longitudinal and circumferential strain MAEs pass 5 pp. Radial MAE is 5.39 pp,
  while radial regional peak error is 9.31 pp, failing the 5 pp peak target.
- Regional peak timing passes in all directions: mean errors 1.12 / 1.41 / 0.76
  frames, against a 2-frame target with near-equal reference extrema treated as
  ties. All predicted tetrahedra remain positive; local J spans 0.592–1.366.

Terra passes tissue-volume error (1.97%) and has zero inverted tetrahedra, yet
its material error and strain errors are much larger. Its minimum local J is
0.0041: merely positive elements can still be nearly collapsed. This result
illustrates why a global volume check cannot certify local mechanics. It does
not justify tightening this frozen task's gates after seeing the submission.

## What the agents did

Terra ultimately used direct-from-initial-frame Farneback optical flow, a coarse
trilinear displacement lattice, a divergence penalty, temporal filtering and
an inversion safeguard. It independently noticed and replaced an earlier
over-regularized solution that barely moved. Sol used bidirectional tracking
confidence, a finer 12 mm deformation lattice and a temporal decomposition with
periodic smoothing. Its submitted method explicitly discusses weakly observed
RV and through-wall motion. No reference-strain feedback was given during either
attempt. These are descriptions of the submitted methods, not isolated causal
attributions of each method component's contribution.

L1V Sol used direct reference-to-phase 3D TV-L1 optical flow, Gaussian spatial
regularization and a five-harmonic temporal fit. It supplied an exact initial
frame and kept all tetrahedra positive. Its surface mean/p95 error is 1.35/3.33
mm, tissue-volume error 2.92%, and regional timing errors 1.41/1.18/1.35 frames;
those components pass. Whole-body material motion and longitudinal/radial
strain fail. Local J spans 0.0816–3.923, despite a much steadier global volume.
Its longitudinal/circumferential/radial regional peak errors are 7.31/3.73/10.23
pp. More observations did not produce an acceptable result in this attempt.
Different fresh strategies and one attempt per condition preclude a causal
claim that extra volume data worsen reconstruction.

The [local report](http://127.0.0.1:8769/index.html) includes the actual submitted
meshes in a copy of the Dynamic Heart Lab. It defaults to the most recently
completed agent reconstruction, with source reference and author controls
available in the selector. The older workbenches are preserved. A standalone
comparison figure is retained under `runs/br031-cardiac-levels/agent-comparison`.

## Refined hierarchy and acceptance

Inputs 0–4 and outputs 5–8 should be separate axes. Strain is already scored at
L1: it is not an automatic benefit of a convincing 3D surface. At L2, specify
whether contours cover only the initial frame or the entire cycle; adding dense
temporal contours can supply more motion evidence despite removing a mesh.
For a newly generated mesh, material error requires an evaluable material map
or common reference probes; unrelated vertex indices cannot be compared.

Raw multiview data need obtainable calibration/scale and a stated phase-alignment
task if those are not supplied. Sparse/single-view recovery needs explicit priors
and uncertainty evaluation across cases, rather than treating one unobserved
3D completion as uniquely determined. Geometry, tissue motion, strain, regional
timing and uncertainty remain independently reported quantities.

The current sources do not establish cavity/EF, hemodynamics or diagnosis:
myocardial tissue volume is not blood-pool volume; optical flow is not blood
velocity; healthy/LBBB simulator names are not clinical diagnostic adjudication.
L2–L4 and output tracks 6–8 were not tested. A one-case miss at L1 is not a general
agent ceiling or proof of an intrinsically hard, uniquely solvable benchmark.

## Completed observation-depth comparison

Only 14.39% of initial vertices lie within 1.5 mm of any supplied plane and within
its image field: LV 16.48%, RV/unassigned 11.11%. This proximity measure is not
proof of usable image correspondence, but motivates testing more image evidence.
The conditional Sol/xhigh L1V test adds the same case's 30 native 3D US images.
All image values round-trip exactly; resampling four phases reproduces all four
PNG views with zero pixel difference. Initial geometry, reference meshes,
verifier and numerical thresholds remain unchanged.

L1V's formerly withheld evaluation planes lie inside the added 3D volume. Their
metric is then off-plane agreement, not unseen-view generalization. This contrast
was declared while the first L1 trial was running, before any L1 model score.
Its oracle/nop controls pass. Automatic approval review initially rejected the
launch twice; the earlier pending receipt preserves that state. The user then
explicitly said "go ahead" on the proposed trial, and it launched successfully
without changing task bytes, thresholds or resources. The approval resolution,
initial-image audit, normal completion and independent score replay are retained.

## Source and verification boundaries

The case is from [Multimodality STRAUS](https://humanheart-project.creatis.insa-lyon.fr/multimodalityStraus.html),
which provides synthetic images and known electromechanical material motion.
It is the same previously inspected healthy case used by the BR-029 author
prototype, not measured human strain or a held-out patient study. The user's
hierarchy was pasted from another chat; that chat was not identified or opened.

Six Docker controls are complete: oracle=1 and no-output=0 for L0, L1 and the
prepared L1V package. Task checksums match within each condition. Controls used
Harbor 0.18.0 and model runs used the existing Codex wrapper in Harbor 0.14.0;
the separate verifier's task bytes are identical within each condition. Initial
L1 images were inventoried for both agents and L1V for Sol: input hashes match, and
verifier/solution directories are absent. Saved submissions were independently
regraded and scores match the container results.

The grader derives fields from coordinates, checks signed tetrahedra, rasterizes
myocardial sections and measures sampled surface distances. It does not score
rendered colors. Surface samples comprise boundary vertices and triangle
centroids; the metric is not exact continuous Hausdorff distance. Directional
strain excludes source regions without complete axes. A small surface-preserving
interior perturbation remains within the fixed strain tolerances and passes;
the record does not claim every local hidden defect is caught.

All runtime traces, predictions and generated media remain local. No commit,
publication or alteration of the closed interview report occurred.
