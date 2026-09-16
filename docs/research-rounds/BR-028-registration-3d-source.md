# BR-028 — add source depth to the failing registration case

Status: matched-input protocol fixed before new author or model outcomes.

The user asked whether BR-024 supplied only 2D patches and what happens if the
input is 3D, in the owning [research task](codex://threads/01a0a845-7c2d-7992-a662-24d52831af90).
Exact message IDs are not exposed. BR-024 supplied a complete oblique exhale
slice and a full inhale CT. The displayed patches were derived views, not the
entire input. This follow-up adds the full exhale CT to that exact failing case.

## Fixed contrast

Use patient 3 / view 1 from BR-024. Add `reference_volume.npz`, containing the
same source exhale acquisition from which the 2D view was sampled. Keep every
old public data file, the eight query pixels, plane geometry, destination CT,
private reference answers, grader, tolerances, packages, CPU, memory and model
time limit byte-identical. Amend only the task name and the prompt passages
describing availability of the full source volume. The original view remains
available so the new condition adds information without removing an input.

Source locations remain those calculated from the existing query pixels and
plane frame, including the original <=0.35 mm through-plane approximation.
Do not replace them with hidden manual source coordinates. Verify that the new
volume matches the retained source NIfTI and reproduces the old view with an
independent interpolator. The only added NPZ members are HU and voxel-to-world;
no labels, patient identifiers, answer artifacts or prior solver enter the image.

## Feasibility, controls and one fresh attempt

Audit the actual initial public image. Replay the existing passing 2D
translation-only author baseline there; its successful behavior remains a
feasibility control since those inputs are unchanged. Also run the existing
local-affine author matcher in 3D, with source query positions derived solely
from the public plane frame. This supplementary method's success is not an
admission gate: the retained 2D route already demonstrates permitted solvability.
No new author tuning or label-based initialization is allowed.

Freeze all task bytes and run matched oracle/nop controls, then exactly one
fresh Sol/xhigh attempt, 1,800 seconds, four CPUs, 4 GiB, zero retries and
ordinary software/network access. Supply no earlier answers, solver code,
failure diagnosis or hints. Retain the immutable initial image, trace and
intermediate artifacts, then independently grade and inspect the approach.

Compare with the completed BR-024 2D-source attempt (12.731 mm RMS / 32.203 mm
maximum, normal completion). A new pass would demonstrate that this enriched
instance is solvable by that fresh attempt; a miss would show that source depth
alone did not rescue that attempt. One fresh run per condition cannot isolate
the effect of information from strategy choice and model variability, or prove
that a 2D ambiguity is information-theoretically irresolvable. Any further repeat
or ablation requires a separate study; none is scheduled here.

## Ownership

Use only new `br028_*`, `runs/br028-*`, and BR-028 documentation/evidence paths,
plus an additive round-register entry. Preserve all prior task/evidence bytes,
the concurrent cardiac/vessel work, the closed site and sibling submission.
Raw credentials, scans, sessions and generated HTML stay local. No publication
or commit is part of this request.
