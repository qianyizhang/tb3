# BR-032 — real ultrasound without a reference reconstruction

Prospective case study requested 2026-09-16 in the cardiac task, after the user
approved the prepared BR-031 full-volume trial and raised possible internet
training exposure. This round is separate from the unchanged BR-031 test.

## Selection and scope, before any real-case solver result

Prefer a permissioned, never-public local scan if the user supplies a path.
Otherwise use the official EchoSlicer release, selecting the lexicographically
first non-resource-fork DICOM in the release archive. Selection depends on file
order and usability, not a model's outcome. Retain any decoding exclusions.
The authors describe 29 real 3D echo videos from four consenting volunteers:
https://github.com/echonet/3d-echo and https://arxiv.org/abs/2511.15946.
These videos are publicly downloadable; no redistribution permission is inferred.
Source data and generated case outputs remain local.

Bound the output to a dynamic LV cavity surface from calibrated image planes,
with initial anatomy/geometry inferred from images, shared connectivity, frame
references and explicit uncertainty. Without validated myocardial boundaries and
material correspondence, surface deformation is not a measured strain field.
No blood-flow, force-balance, pathology or clinical EF accuracy claim is made.

Prepare calibrated observed planes and separate review planes from the same
real 3D acquisition. No source mesh, source labels, pretrained cardiac weights,
or previous solver is supplied. Keep acquisition timing if reliable; otherwise
use frame indices. Fix the actual input and review-plane definitions before the
single fresh Sol/xhigh attempt, with a 30-minute allowance. This is a descriptive
case study, not an oracle-based benchmark pass/fail.

## Leakage and evaluation

Keep filenames/source identifiers outside the solver input; preserve attribution
in the author record. Use a newly chosen coordinate frame and phase window,
documented calibration, and exact image hashes. Such changes make literal answer
reuse less useful but do not prove absence from pretraining. Standard algorithms
learned from public research are permitted; retrieving the source case or a
reference answer is not. Audit exposed files and actual run commands. Keep
pretraining exposure explicitly unknown for any public case.

Report observed and withheld image overlays separately, mesh closure/orientation,
finite coordinates, temporal changes and model-dependent volume curves. Any
image-edge or intensity diagnostic is a proxy, not segmentation truth. Do not
report 3D accuracy, material-motion error, strain accuracy or disease accuracy
without independent labels. Use declared alternative plausible completions to
show how depth and basal assumptions affect the result. If feasible, replay the
submitted executable on a known coordinate transform and a repeated-frame control;
record response to changed inputs rather than treating it as a contamination test.

A public real-video experiment addresses simulation-to-scan transfer. Establishing
absence of training contamination requires independently controlled acquisition/
release provenance relative to the tested model, not just a new task prompt.

Ownership: this document, docs/evidence/br032-*, the authoring/real_echo directory,
and ignored runs/br032-real-echo*. Preserve earlier rounds and the closed report.
