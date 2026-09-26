# Reproduction and presentation

Experiment TOML, manifests and stored records are the executable authority. Use
`uv run med list QUERY` for current inventory. Dated verification records are
evidence snapshots, not a live backlog. Historical metadata does not imply that every task
has a maintained runner.

## Experiment support and verification

Document support and proof separately. A command may exist without having been
checked, while a retained replay may have proof without being a supported daily
command. Status badges follow the [shared vocabulary](status-vocabulary.md).

| Capability | Minimum evidence for a named scope |
| --- | --- |
| Evidence and interpretation | Stable experiment, protocol, conditions, sources, finding and limitations; distinguish pilot, model attempt, replay and review. |
| Input and environment recovery | Exact files, origins, access terms, hashes, runtime requirements and missing items. Presence or a URL alone is not recovery. |
| Task preparation | Fresh destination, checked task bytes and explicit solver/private-reference boundary; state whether inputs are restored or rebuilt. |
| Execution and collection | Declared runtime, conditions, controls, result contract, attempt identity and interruption handling. |
| Saved-output scoring | Scorer and input hashes, original observation, comparison rule and discrepancies. A replay is not a new model run. |
| Inspection | Named story, viewer or regeneration command plus checked geometry/measurement invariants. Viewing and regenerating are different claims. |
| Portable export | Fresh package, manifest, licenses, origins and a checked operation outside the source checkout; state same-machine limits. |
| Fresh execution | New attempt with runtime/config, outcome and comparison criterion. Controls, previews and saved-answer replays do not satisfy this item. |

Keep scientific/reference assessment separate from technical replay. Exact-byte
checks apply to frozen inputs. Metric equivalence uses the recipe's named tolerance;
fresh stochastic output need not match byte-for-byte. A runtime failure, scorer
error and negative result remain distinct.

## Workbench commands

Select an experiment and a case from its manifest:

```sh
uv run med list QUERY
uv run med prepare EXPERIMENT --case CASE
uv run med prepare EXPERIMENT --case CASE --execute
uv run med replay EXPERIMENT --case CASE
uv run med evaluate EXPERIMENT --case CASE --answer /path/to/NEW-answer
uv run med view EXPERIMENT --case CASE
uv run med bundle EXPERIMENT /path/to/NEW-bundle
uv run med verify-package /path/to/NEW-bundle
```

`prepare` previews unless `--execute` is supplied. `replay` rescores a saved answer
and appends an observation for the same attempt. `evaluate` scores an explicit new
answer; use `med collect` to retain an actual trial. `view` supports only the
inspection declared by that experiment.

Flagged experiments require `--include-flagged` for a labeled research handoff.
That does not resolve the review. Complete bundles include large prepared inputs;
a Git clone or source URL alone does not. Recover transferred data with
`med bundle ... --input-root /path/to/TRANSFERRED-bundle` rather than an author cache.

## Standalone bundles

From a complete bundle:

```sh
python3.12 reproduce.py verify
python3.12 -m venv .venv-reproduction
.venv-reproduction/bin/python -m pip install -r requirements-evaluation.txt
.venv-reproduction/bin/python reproduce.py replay --output /tmp/NEW-replay.json
python3.12 reproduce.py container-controls --output /tmp/NEW-controls.json
.venv-reproduction/bin/python reproduce.py evaluate --case CASE --answer /path/to/NEW-answer
```

`container-controls` uses Docker with separated solver/private-verifier mounts and
no execution-time network. Docker build may fetch pinned inputs. A mutable historic
base tag must be paired with the tested image ID in the receipt. BR-034 and BR-035
also expose `method-replay`; their package READMEs distinguish retained outputs from
fresh deterministic submitted-program execution.

Fresh model trials require an explicit model, effort and the package's declared
Harbor invocation. Use `med run` and `med collect` for common launch/collection.
Portable controls do not satisfy model-run qualification gates.

## Optional imaging and presentation

```sh
uv run med present
uv run med present --serve
uv run med check --assets
```

The portable site is written to `.local/site/`; `--serve` binds locally and does
not publish. Tracked stories and static fallbacks work without raw scans. Optional
local inputs remain explicit unavailable states.

Guided tour inputs are pinned in
[presentation/tours/inputs.json](../presentation/tours/inputs.json):

```sh
uv run med media prepare
uv run med media check
uv run med present --serve --local-media
```

These commands restore/check the retained derived snapshot, not every raw
preprocessing step. The [media guide](../presentation/tours/TOOL.md) owns imaging
setup, media optimization and rendering. Its
[browser verification section](../presentation/tours/TOOL.md#browser-verification)
covers navigation checks, disposable profiles and the macOS execution boundary.

## Verification history

The [2026-09-21 baseline receipt](evidence/experiment-support-backfill-20260921.json)
records the dated inventory, hashes, controls and replay counts.
Unselected experiments retain evidence without implying a maintained runner.
A clone depends on tracked receipts and per-experiment recipes; the optional local
`runs/support-backfill-20260921/HANDOFF.md` is an operational convenience.

## Recovery boundaries

- Do not run retired authoring generators to repair historical links; use
  [archive recovery](../archive/README.md).
- Raw runs, environments, datasets and generated media remain local.
- Missing inputs, licensing, mutable container bases and independent backup are
  separate recovery concerns.
- Restore, replay and presentation checks do not establish clinical validity or
  submission readiness.
