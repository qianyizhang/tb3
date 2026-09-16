# BR-022 authoring and reproduction

The [frozen protocol](../../../docs/research-rounds/BR-022-registration-failure-analysis.md)
owns the predeclared comparisons; [results](../../../docs/research-rounds/BR-022-results.md)
own the conclusions. This extension preserves BR-021 code, freezes and receipts.
All new local outputs are under `runs/br022-registration-postmortem/`, and new
model jobs use `runs/br022-*`. No file in this authoring directory is copied into
a fresh model image.

## Stages and information boundaries

1. `br022_recover.py` extracts the original solver's recorded heredocs and literal
   text edits from the BR-021 trajectory, without running model shell commands
   on the host. `recovery.json` records source-step and recovered-file hashes.
2. `br022_replay.py` runs the recovered code inside the retained
   `br021-deform-2d-author` image. Mount recovered scripts read-only at
   `/recovered`, this entrypoint read-only at `/runner.py`, and a dedicated output
   folder at `/output`. Run `python /runner.py`, with network disabled, four CPUs
   and 4 GB RAM. Only the frozen public payload is already in the image.
   Output transforms and stage diagnostics go into the replay folder.
3. `br022_counterfactual.py` uses the same isolated image, `/recovered`, and
   read-only replay state at `/state`; its own output folder is `/output`.
   The complete fixed mapping/bounds/seed grid runs in this one entrypoint.
   No target coordinates are mounted or read.
4. `br022_baseline_ablation.py` uses the same public image and read-only original
   `baseline_patches.py` at `/baseline.py`. Mount the wrapper at `/runner.py`
   and a dedicated output folder at `/output`. Run `python /runner.py --kind 2d
   --data /app/data --out /output/MODEL-CONTEXT.json --model MODEL --context CONTEXT`
   for each model (`translation`, `affine`) and context (`small`, `multiscale`). The wrapper changes
   only the predeclared local motion model and context schedule. Keep each
   output; do not choose an answer using private scores.
5. `br022_analyze.py` is a **privileged offline analyzer**, run on the host after
   public-input solvers finish. It independently scores their outputs, computes
   search-box distance bounds, and evaluates the objective at/near manual
   targets. This file and its label-assisted results must never be mounted in
   a permitted solver or agent environment.
6. `br022_run_trials.py` ran the predeclared oracle/nop and two fresh Terra/high
   replications sequentially, with zero retries and an unchanged task. It refuses
   to overwrite an existing job. The delegated supervisor independently audited
   initial images, trace behavior, runtime context and final frozen bytes. Its
   final audit is `bench-audit.json`. Do not rerun or create more trials merely
   to regenerate a report. Runtime configurations contain credentials and remain
   local; never export or print them.
7. `br022_collect.py` extracts allowlisted result fields, independently regrades
   all four new submissions, checks runtime contexts and hashes, and joins the
   original selected attempt with the two separately identified prospective
   replications. `br022_present.py` plus `br022_review.html` create the local
   interactive review from actual CT pixels and retained outputs.

The original model image no longer existed. Replay used immutable retained
image `sha256:eba0354cc009141864421730b5f60c78d74c3acfbc6edc099991c6155e82138b`,
built from the identical frozen public Dockerfile. The image audit checks every
public file, absence of private payload, and pinned packages. Output coordinates
match the original submission to rounding. See
[execution evidence](../../../docs/evidence/br022-author-execution.json).

For read-only receipt/report regeneration from existing local artifacts:

```sh
.venv-br021/bin/python probes/registration-deformation/authoring/br022_collect.py
.venv-br021/bin/python probes/registration-deformation/authoring/br022_present.py
```

These commands rewrite only BR-022 derived receipts/report. They do not execute
models or change the frozen BR-021 task. The analyzer likewise reproduces
derived evidence, but includes a finite privileged objective search and should
be kept separate from solver execution.
