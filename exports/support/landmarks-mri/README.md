# Frozen anatomical-landmark MRI research package

Run `python3.12 replay.py` from this directory. It first verifies every selected
file digest, then replays the saved Terra/high and Sol/xhigh answers with the
unchanged BR-038 MRI scorer and truth. It checks the saved oracle and an empty
output as local controls. No source checkout, ignored run folder, NumPy, Docker,
network or model call is needed for this replay.

The runnable Harbor task is tasks/mri32-full. Solver data are under environment;
evaluator-only truth is under tests. The source notice retains attribution,
license declaration and source revision. The base Docker image is a historical
mutable tag; dependency versions are pinned but the image/package artifacts have
not been independently restored. Rebuilding Docker or rerunning an external model
is a separate validation step. Source case data are public; prior model training
exposure cannot be excluded. Sol's atlas-assisted workflow is described in the
included audit and historical results report.

This is a draft research export. It is not a TB3 submission-ready designation.
Check then-current upstream format, policy, licensing, human-authored requirements
and qualification trials before submission. Current evidence validity is captured
at export; later reviews in the workbench can flag the lineage record. After an
explicit handoff, this repository is independently maintained. Do not regenerate
over edits: build a new destination and review any intentional backports.
