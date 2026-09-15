# BR-013 abdominal identity pilot

[Earlier-trial presentation and current verdict](../../../../docs/anatomy-experiments.md) ·
[Trace walkthroughs](../../../../docs/anatomy-traces.md)

Two source scenes, three tasks: anonymous recognition of 13 ordinary objects;
recognition of 11 objects with altered anatomy; an audit of the second scene
with whole pancreas/duodenum identities exchanged. All binary masks retain
their original 1.5 mm voxels and shared physical geometry. No tiny contour
defect or diagnostic label is graded.

The [protocol](../../../../docs/research-rounds/BR-013-abdominal-direction.md)
owns selection, exclusions and interpretation. The freeze and concise results
are under `docs/evidence/br013-*.json`; large raw evidence remains local under
`runs/br013-abdomen*`. This is a research pilot, not a submission-ready package.

## Files

* `screen.py`: source-mask statistics and leave-one-patient-out matching,
  including exact one-to-one assignment. No model calls.
* `build.py`: task export, whole-voxel/affine checks, scoring controls and
  immutable task hashes. Refuses to overwrite the existing freeze.
* `inspect_scene.py`: public label-free loader, measurements and focused views.
* `scoring.py`: exact object identities/corrections, no image judgments.
* `run_trials.py`: isolated Harbor/Docker oracle, nop and one Sol/xhigh attempt
  per task, sequentially with no retries. Terra requires a separately reviewed
  valid failure. Uses this workshop's retained harness configuration.
* `collect.py`: resource accounting, runtime model/effort checks, answer replay,
  an independent exact-set comparison and frozen-task checks.

## Local reproduction

Use the retained original TotalSegmentator small v2.0.1 masks under
`runs/br004-v1/source/` and the existing NumPy/NiBabel/Pillow environment.
Source masks are CC BY 4.0; taxonomy is Apache 2.0. Tasks include attribution
and license files. The source review receipt was written before export.

```sh
.venv-br003/bin/python probes/revisions/br013/authoring/screen.py
.venv-br003/bin/python probes/revisions/br013/authoring/collect.py
```

The first command reproduces source screening, not model attempts. The second
replays retained completed artifacts and validates hashes. Build/run commands
are deliberately separate: never rewrite a freeze or repeat a model attempt
to obtain a preferred result. A fresh reproduction needs a new output path
and its own protocol record. The original source acquisition and local raw
results are not bundled in this authoring directory.

Clinical cause and contour quality are outside the grade. The paired tasks
share one patient; one attempt per condition gives an observation rather than
a success-rate estimate. The cross-round verdict includes subsequent rescues.
