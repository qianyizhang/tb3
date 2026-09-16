# BR-023 authoring and reproduction

See the [protocol](../../../docs/research-rounds/BR-023-sol-registration.md),
[fixed component plan](../../../docs/research-rounds/BR-023-component-plan.md),
and [results](../../../docs/research-rounds/BR-023-results.md). This extension
preserves all earlier rounds. No authoring code or analysis enters a fresh
agent image.

- `br023_run_trials.py` ran matched oracle/nop and exactly one Sol/xhigh
  attempt on the original frozen task. It refuses to overwrite/retry jobs.
  Raw runtime configurations contain credentials and remain local. Do not
  print, export or include them in receipts. No rerun is authorized merely
  to regenerate derived reports.
- The delegated supervisor audited initial-image contents, model/effort,
  fresh session, task bytes and trace. It retained the immutable initial
  image and content-addressed exploratory arrays/panels in
  `runs/br023-sol-registration/captured-agent-artifacts/`. Read-only snapshots
  did not modify the agent environment or supply feedback.
- `br023_recover.py` parses completed command events with JSON and shell
  lexical parsing, then extracts Python heredocs literally. It never runs
  model shell commands on the host. `br023_trace.py` exports text/calls while
  excluding image blobs. Raw sessions remain authority.
- `br023_components.py` instruments the recovered `item_26-0.py` and changes
  only the frozen settings. `br023_run_components.py --condition NAME` runs
  one named condition in the actual initial image, network disabled, four
  CPUs, 4 GB RAM, read-only public code mounts and a separate output mount.
  Private labels are never mounted. Existing condition folders cannot be
  overwritten. Exact final-stage replay was checked before interpreting
  other conditions. Earlier autonomous decisions remain fixed as recorded
  public-derived starts; this is not an end-to-end reasoning replay.
- `br023_analyze.py` is the **private offline grader/analyzer**. It reads
  manual targets only after solver execution, checks output/code hashes,
  grades all fixed variants and recorded affine settings, and computes
  geometric search bounds. Never mount it or its results into a solver.
- `br023_collect.py` independently regrades the model and controls and
  extracts allowlisted runtime/trace evidence. It checks all prior result
  receipts and frozen task membership. `br023_present.py` plus
  `br023_review.html` build the local interactive CT comparison.

The frozen component plan records the actual initial image ID:
`sha256:dd4a6f96b30342bd15fedb795dc9371d0ddd15b03e7e2eadef843e41325a3014`.
The retained tag is `tb3-br023-deform-2d-sol-initial:20260916`. The task contains
NumPy 2.2.6, SciPy 1.15.3, Pillow 11.3.0 and SimpleITK 2.5.2. Sol used NumPy,
SciPy and Pillow; SimpleITK was inspected but not used for its registration.

To regenerate derived evidence and the report from existing local artifacts,
without executing another model or modifying old evidence:

```sh
.venv-br021/bin/python probes/registration-deformation/authoring/br023_collect.py
.venv-br021/bin/python probes/registration-deformation/authoring/br023_analyze.py
.venv-br021/bin/python probes/registration-deformation/authoring/br023_present.py
```

Do not re-extract or edit files included in the frozen component manifest
before verifying their hashes. A reproduction in another folder must preserve
the declared variants and retain all outcomes, including failed executions.
