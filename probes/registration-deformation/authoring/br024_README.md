# BR-024 authoring and retained evidence

This is the user-requested harder-patient continuation of BR-021–023. Read the
frozen [protocol](../../../docs/research-rounds/BR-024-harder-registration.md)
and [results](../../../docs/research-rounds/BR-024-results.md) before interpreting
the receipts. Previous task snapshots and evidence remain unchanged.

## Ownership and isolation

`br024_screen.py` verifies the original source receipt and deterministically
selects three ranked oblique views per unused patient. Destination annotations
are used for explicit geometric curation and subsequent grading, never mounted
into the public-input author solver or agent image. All candidate pixels,
manual labels, selection statistics, outputs and failed methods are retained
locally in `runs/br024-harder-registration`.

`br024_feasibility.py` runs the unchanged local-affine baseline.
`br024_translation.py` runs the already existing BR-022 translation-only variant
under the separately fixed rescue plan. `br024_run_neighborhood.py` runs the
last fixed patient-2 rescue from `br024_neighborhood.py`. Each mounts only public
inputs and solver code into a network-disabled container; host grading occurs
after exit. The new solver code and plan were hashed before its results.

`br024_build_case.py` admits only a whole-answer pass after author image review,
checks interpolation independently, and copies a new task without editing the
old snapshot. `br024_freeze_case.py` verifies the actual new image's file set,
empty answer directory and absence of private inputs, then repeats the author
solver inside it and freezes all task files. Only patient 3 was admitted.

`br024_run_trials.py patient3` ran matched oracle/nop and one fresh Sol/xhigh
attempt with zero automatic retries. **Do not rerun it into existing jobs.**
No patient-2 model attempt is authorized by this round. Raw configs contain
credentials and must remain local; never print or publish them. Retained initial
images and content-addressed intermediate captures are listed in the bench audit.

## Read-only or derived reproduction

With the retained local runs and `.venv-br021` environment:

```sh
.venv-br021/bin/python probes/registration-deformation/authoring/br024_collect.py
.venv-br021/bin/python probes/registration-deformation/authoring/br024_curation_analysis.py
.venv-br021/bin/python probes/registration-deformation/authoring/br024_stages.py
.venv-br021/bin/python probes/registration-deformation/authoring/br024_present.py
```

The collector independently regrades submissions and all author outputs, checks
task membership, runtime model/effort, matched controls and prior receipts.
The two analysis scripts use private labels only for posthoc evaluation of
already saved states. Stage scores are observations, not causal ablations.
The presenter uses actual CT pixels and exposes every screened candidate,
including author failures. Generated HTML and full scans remain local.

No new trial, publication, deletion, tolerance change or source download is a
side effect of these derived-report commands. Image matching on public manual
annotations cannot rule out training contamination or establish clinical use.
