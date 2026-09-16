# Real ultrasound case study: a fitted animation, with a fixed-table limitation

One fresh Sol/xhigh attempt completed normally in 657 seconds. Given four
calibrated real ultrasound videos, with no input mesh or contours, it produced
an 18-frame cavity surface and three alternative interpretations. It inspected
the images, chose a chamber boundary and stored per-frame visual measurements
in explicit tables. Its saved executable generates meshes from those tables;
it does not re-estimate geometry from image pixels.

The repeated-frame control makes this limitation concrete: replacing 68 of the
72 input PNGs so that each view contains only its first image produces exactly
the same primary coordinates and all alternatives. Changing the coordinate
system is handled correctly, with about 2.2e-14 mm point RMS disagreement after
the known rigid transform. These are executable response checks, not evidence
that the original agent ignored the images or memorized the case.

[Interactive case](http://127.0.0.1:8770/index.html) ·
[Protocol](BR-032-real-echo-case.md) ·
[Source and contamination audit](BR-032-source-notes.md) ·
[Evidence](../evidence/br032-real-echo-results.json) ·
[Reproduction](../../probes/cardiac-reconstruction/authoring/real_echo/README.md)

## What was supplied and what was produced

| Aspect | Actual evidence |
| --- | --- |
| Images | One real volunteer scan from the official EchoSlicer release, selected by archive order before model results |
| Sampling | 18 source volumes, 161.15 ms declared frame interval; four 256² calibrated reslices per frame |
| Input geometry | Pixel calibration and coordinate axes; no initial mesh, contours, source identifiers, full volume or pretrained cardiac weights |
| Output | 1,202 vertices and 2,400 consistently oriented triangles, same connectivity over 18 frames, plus three alternatives |
| Mesh checks | Finite coordinates, closed oriented edges and positive signed volume; no independent general self-intersection test |
| Primary volume | 54.08–177.57 mL, determined by the inferred boundary and basal cap; no reference volume or clinical EF |
| Alternative spread | 42.01–219.73 mL across all variants/frames; assumption sensitivity, not confidence bounds |
| Held-out observations | Four other image planes, never supplied to the model; independent mesh intersections retained for review |
| Accuracy truth | No reference 3D anatomy, material trajectories, myocardial strain, clinical EF, flow or diagnosis |

This is an image-only reconstruction case with calibration supplied. It is not
the full uncalibrated multiview level from the original hierarchy, nor a recovered
four-chamber muscle model. Persistent surface vertices establish geometric
correspondence only. The task has no basis for measuring myocardial strain.

## Image review and its limits

The independently generated overlays show a changing cavity envelope near
visible dark/bright transitions in several supplied and withheld long-axis
views, and in the supplied 105 mm cross-section. Review covered frames
1, 2, 4, 6, 10, 11, 14 and 18, including declared extrema. These are qualitative
author observations, not a blinded clinician assessment or contour accuracy.

The agent identifies the deeper thick-walled chamber as LV and excludes the
shallower chamber. That anatomical assignment and its inferred basal cap remain
unadjudicated. The primary surface has no intersection with the 65 mm input
plane, and intersects the withheld 85 mm plane only at frames 3, 4, 9, 10, 15
and 16. The cap therefore materially controls which anatomy is included. No
reference contour establishes that this choice is correct.

Image-ring brightness differences are saved only as exploratory diagnostics.
They exclude empty intersections, differ in support across shapes and can
reward an incorrect boundary. They must not be interpreted as Dice, 3D accuracy
or proof that a particular alternative is more anatomically correct.

## Separate meanings of success

The task's automatic reward is artifact validity only. A deliberately static,
image-ignorant ellipsoid also receives reward 1; the no-output control receives
0. This demonstrates why a green format check is insufficient. Model and control
task checksums match. The model's complete artifact was independently checked.

The original session provides evidence of visual inspection and case-specific
construction. The unchanged executable does not support automatic recovery on
new video inputs: its `OBSERVED` arrays determine the pulse, while its PNG reads
serve overlay drawing. Its repeated-frame output retains 5.40 mm RMS geometric
vertex motion relative to the first frame, with exactly zero coordinate change
from the original submission. This is not material-motion accuracy.

Both altered-input replays ran with networking disabled and read-only inputs
and solver mounts. Initial replay invocations did not start because the trial
runner had removed its image; the unchanged frozen Dockerfile was rebuilt and
successful replays were kept in separate v2 directories. Those infrastructure
records are preserved. The replay output does not copy `solve.py` into its output
folder, so the original whole-artifact checker reports that missing auxiliary
file; the retained executable hash, coordinates, topology and volumes are
assessed separately. It is not classified as an anatomical failure.

## Leakage conclusion

The official archive contains 29 DICOM scans and no paired reconstruction.
The selected scan is public, so prior training exposure remains unknown.
Suppressing source identifiers, changing coordinates, withholding image planes
and using a fresh task reduce opportunities for direct answer reuse during a
run; they do not prove unseen anatomy or absence from pretraining.

The initial image's input hashes match the declared 73-file inventory, with
no reference/solution directory. Runtime records match Sol/xhigh and contain the
frozen instruction. Reviewed command records show no external source retrieval
or delegation. These statements describe observable execution, not provider-side
training data. The user explicitly selected a public scan after being offered
the stronger alternative of a permissioned, never-public local acquisition.

## Implication for the next task design

Keep a case-specific mesh deliverable separate from an automatic reconstruction
pipeline. A future pipeline task should explicitly require re-estimation on
changed pixels and include a repeated-frame control plus a second hidden case.
That requirement should be declared before scoring, not retroactively used to
relabel this case's artifact reward. For anatomical acceptance without a 3D
reference, obtain independent expert contours on withheld planes and adjudicate
chamber identity and basal closure. Those checks still cannot certify material
strain. Never-public acquisition provenance is needed for a strong claim that
the source scan could not have entered training.

The [approved full-volume simulator comparison](BR-031-cardiac-agent-results.md)
is complete separately: adding 3D ultrasound improved some image overlap but
did not pass material-motion/mechanics thresholds. No model received review
feedback or a second attempt in either case. No publication or commit occurred.
