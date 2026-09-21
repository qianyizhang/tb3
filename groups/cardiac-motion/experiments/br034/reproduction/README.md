# Reproduce cardiac-motion-br034

This package is self-contained once `verify` succeeds. Use Python 3.12. Solver
inputs are under `cases/CASE/task/environment`; `tests`, `solution`, `oracle` and
`saved` are evaluator-only and must never be mounted into a model's environment.
Read acquisition.md and source-records.json before sharing data.

```sh
python reproduce.py verify
python -m venv .venv-reproduction
.venv-reproduction/bin/python -m pip install -r requirements-evaluation.txt
python reproduce.py controls --python .venv-reproduction/bin/python --output /tmp/controls-NEW.json
python reproduce.py replay --python .venv-reproduction/bin/python --output /tmp/replay-NEW.json
python reproduce.py evaluate --case CASE --answer /path/to/new/answer --python .venv-reproduction/bin/python
python reproduce.py inspect --case CASE --output /tmp/task-NEW.html
# Docker must be installed and running; builds use declared pinned Python packages.
python reproduce.py container-controls --case CASE --output /tmp/docker-controls-NEW.json
```

`container-controls` builds the original solver and verifier Dockerfiles, executes
oracle/no-op controls with separate private-reference mounts, and checks rewards.
Host `controls` only invokes the scorer against oracle/starter answers. Neither
command launches an LLM. Saved-output replay compares scientific fields using
absolute/relative tolerance 1e-8; grading time is excluded. A passing replay is not
a positive model result, extraction reproduction or clinical adjudication.

## Fresh model execution by another agent

Install Harbor 0.18.0 in a separate environment (the historical version), configure
your provider credentials outside the package, then use its `harbor trials start`
interface with `--path cases/CASE/task`, `--agent codex`, an explicit model and
reasoning effort, and a fresh output directory. Use `harbor trials start --help`
for the installed version's provider options. For example (replace `CASE`, `MODEL`
and the fresh output directory):

```sh
harbor trials start --path cases/CASE/task --agent codex --model MODEL \
  --agent-kwarg reasoning_effort=xhigh --trials-dir /path/to/NEW-trials
``` In the workbench, prepare the selected
case and use `med run EXPERIMENT --case CASE --agent oracle` and `--agent nop` to
retain bound control records before a nondiagnostic model launch. Reviewed evidence
still requires scoped reassessment, or an explicitly diagnostic new study.

LLM outputs are stochastic; compare the declared task criteria, not identical text.
Always evaluate a new answer directory with the supplied private scorer. Preserve
all earlier outcomes. The instruction and frozen task.toml specify resource limits,
input visibility and deliverables. Runtime failures remain distinct from task failures.

## Frozen submitted-program transfers

These operations need no LLM or credentials. The first scores saved transfer
outputs; the second rebuilds the declared solver environment and executes the
retained submitted code on the exact input variants, then scores its fresh outputs.
The code and input mounts are read-only; execution has no network. Use a new output
directory. Five BR-034 variants and two BR-035 clinical conditions are enumerated
in `manifest.json`, each tied to its original attempt and observation.

```sh
python reproduce.py method-replay --python .venv-reproduction/bin/python --output /tmp/method-saved-NEW.json
python reproduce.py method-replay --python .venv-reproduction/bin/python \
  --work-dir /path/to/NEW-transfer-outputs --output /tmp/method-fresh-NEW.json
```

Clinical BR-035 scoring has no myocardial material truth. BR-034 clinical volume
and shape references do not validate etiologic diagnosis. Metric differences are
reported separately from execution failure; earlier infrastructure failures remain
in historical evidence. Numeric comparison uses absolute/relative tolerance 1e-8.
