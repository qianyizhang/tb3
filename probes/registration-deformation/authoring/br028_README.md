# BR-028 — matched source-volume addition

The user requested 3D input for the failing BR-024 patient. That original task
already had a 3D target, but only one complete oblique source slice. BR-028 adds
the corresponding full source CT and retains all older public data and evaluation
bytes. See the [fixed protocol](../../../docs/research-rounds/BR-028-registration-3d-source.md).

## Evidence and generation

- `br028_prepare.py` verifies the BR-024 task and source receipt, fixes the new
  plan, adds HU/affine-only `reference_volume.npz`, and independently reproduces
  every original view pixel. Source query locations remain derived from public
  query pixels and plane geometry; hidden manual source coordinates are not added.
- `br028_freeze.py` audits the actual image, replays the unchanged passing 2D
  translation baseline, and runs the predeclared 3D-affine method with a public
  query adapter. The first proves retained solvability; the second is a
  supplementary result, not an admission gate or label-tuned rescue.
- `br028_run_trials.py` runs matched oracle/nop controls and exactly one fresh
  Sol/xhigh attempt, 1,800 seconds and zero retries. Do not rerun into existing
  jobs or print raw configs, which contain credentials.
- `br028_collect.py` independently grades both author methods and all trials,
  verifies runtime identity/effort and input matching, and checks the old frozen
  task and prior receipts remain unchanged.
- `br028_present.py` renders actual CT pixels in the original plane and three
  dataset coordinate planes. Those extra source views are review renders of
  the newly available 3D information, not inputs seen by the old 2D agent.
- `br028_stages.py` grades all retained named candidate point arrays and checks
  the broad local-search coverage after execution. It uses manual labels only
  for posthoc evaluation and never sends feedback to the model.

With retained local outputs, derived reports can be regenerated:

```sh
.venv-br021/bin/python probes/registration-deformation/authoring/br028_collect.py
.venv-br021/bin/python probes/registration-deformation/authoring/br028_stages.py
.venv-br021/bin/python probes/registration-deformation/authoring/br028_present.py
```

The bench audit retains the actual initial image and captures relevant scripts,
transforms, arrays and panels without sending feedback to the model. The source
NIfTI-to-NPZ check is exact; a separate einsum-based check confirms all 22,869
source view samples despite host NumPy floating-point warning flags in the
original matrix multiplication. Its maximum HU difference is 0.000031.

This is one fresh attempt on one selected case. Information, strategy selection
and model variability cannot be separated causally from this single contrast.
Old evidence, concurrent cardiac/vessel work, the closed site and the sibling
submission remain unchanged. No extra trials or publication are scheduled.
