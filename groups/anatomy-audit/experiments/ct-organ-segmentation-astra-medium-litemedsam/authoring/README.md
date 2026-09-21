# Preparing and operating this condition

These scripts are passive on import. Raw CT, reference masks, checkpoint,
dependencies, smoke images and run artifacts stay under `.local/`.

`prepare.py` accepts the exact original frozen task, the existing host runtime
source directory, a Linux ARM64 wheelhouse, a **fresh** output task directory,
and an immutable solver image ID. It copies only the inference package,
`tiny_vit_sam.py`, Apache license and
pinned checkpoint; it never copies calibration inputs or results. The canonical
skill is copied from `src/tb3_medical/skills/litemedsam`.

Build the supplied Dockerfile from the prepared task's `environment/` directory,
after verifying that `tb3-ct-organ-solver:v1` resolves to the baseline ID in the
protocol. Use a new tag, `tb3-ct-organ-litemedsam-solver:v1`, never overwrite the
baseline tag. The Linux venv shares baseline scientific packages and adds pinned
torch, torchvision, timm and OpenCV; the image retains its resolved package list.
Download wheels on the host with `pip download --only-binary=:all:` and target
Python 3.12 / cp312 / manylinux ARM64 (2.28, 2014 and 2.17 platform tags), using
the pinned requirements. The first online Docker build was stopped before
inference after a range probe showed approximately 38x slower transfer inside
Docker. Its log and diagnosis are retained. The replacement build uses
`--network=none` and a read-only BuildKit wheelhouse mount; wheel archives do not
remain in the solver image. Their names and hashes are retained with the task.
Bind the resulting content ID in the task's `[environment]`, leaving the separate
evaluator ID and compose transport unchanged. `skills_dir = "/skills"` makes
Harbor register the task's skill in the fresh Codex context.

The initial build can use the baseline image ID as a temporary `--solver-image`
argument solely to assemble its build context. Replace that binding with the
completed new image ID **before any freeze, control or agent run**. The local
operation plan and exact-task controls must name the final digest.

Run a real image+box call on a synthetic ellipse PNG in the actual new image with
CPU backend and network disabled. Keep that smoke fixture and receipt outside the
task. Save image identity, dependency versions and checkpoint/code hashes.
`preflight_host.py` uses `.local/ct-organ-segmentation-astra-medium-litemedsam/`
and a uniquely named disposable preflight image/compose project; copy the adjacent
`preflight.py` to that base's `runtime/` first. It checks solver file visibility,
the one authorized checkpoint and the original network restrictions.

Run fresh native oracle and no-op controls against the new experiment, review
their records and preserve their exact digest. `run_condition.py` then binds a
private instance of the previously reviewed comparison runner to this **single**
new condition. It never edits or executes the old completed comparison plan.
The new operation plan pins that helper's source hash. The wrapper also verifies
hashed control/preflight evidence, parent launch clearance, fresh account quota,
exact image identities and host idleness. Its exclusive dispatch marker prevents
duplicate or repeated inference. The operator and per-condition state remain local.

Launch the runner in a foreground persistent tool session; retain session/PID
ownership before handing supervision to the heartbeat. Do not use a detached
shell that the tool may terminate at return. The heartbeat checks quota and live
progress; the runner records live container isolation and transport logs. Stop
only verified owned processes if the reserve or isolation boundary is reached.

After termination, replay saved masks with the original experiment's standalone
`replay_score.py`; do not regenerate any old answer or freeze. Follow the protocol
for the per-organ comparison and trace/tool-use audit. Generated plots and media
remain local, while concise provenance and qualified findings are tracked.
