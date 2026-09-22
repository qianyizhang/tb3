# Reproduction and presentation

Experiment TOML, manifests and stored records are the executable authority. Use
`uv run med list QUERY` for current inventory; dated tables below are evidence
snapshots, not a live backlog. Historical metadata does not imply that every task
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

## 2026-09-21 verification baseline

This dated baseline covered 38 then-canonical experiments and eleven selected core
records. It is not current inventory. Each group page preserves the original table;
the [tracked receipt](evidence/experiment-support-backfill-20260921.json) is the
authority for checked hashes, controls and replay counts.

| Group baseline | Selected scope |
| --- | --- |
| [Anatomical landmarks](../groups/anatomical-landmarks/methods/README.md) | BR-040 saved CT/MRI replay |
| [Anatomy audit](../groups/anatomy-audit/methods/README.md) | BR-017 broad and pair-focused supplied-mask audit |
| [Cardiac motion](../groups/cardiac-motion/methods/README.md) | BR-034 clinical tracking; BR-035 supplied-mask construction |
| [Lesion localization](../groups/lesion-localization/methods/README.md) | BR-016 saved localization scoring |
| [Longitudinal reading](../groups/longitudinal-reading/methods/README.md) | BR-037 mechanical report contract |
| [Registration](../groups/registration/methods/README.md) | BR-024 and BR-028 physical-error scoring |
| [Tubular anatomy](../groups/tubular-anatomy/methods/README.md) | BR-041, BR-042 and the separate six-hour continuation |

Unselected rows retain evidence; they are not silently runnable. The optional local
operational index is `runs/support-backfill-20260921/HANDOFF.md` when that untracked
handoff exists. A clone depends on the tracked receipt and per-experiment recipes,
not that machine-local file.

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

In a shared local environment, preserve separately installed research dependencies:

```sh
uv sync --locked --inexact --group dev --extra imaging
```

`--inexact` keeps undeclared packages already used by local research runtimes;
declared packages still come from the lock. Then use:

```sh
uv run med present
uv run med present --serve
uv run med check --assets
```

The portable site is written to `.local/site/`; `--serve` binds locally and does
not publish. Tracked stories and static fallbacks work without raw scans. Optional
local inputs remain explicit unavailable states.

For browser navigation, source panels, keyboard/mobile behavior and deferred tours:

```sh
make presentation-check
# Use the Playwright-managed browser instead of installed Chrome.
PLAYWRIGHT_CHANNEL=chromium make presentation-check
```

Use the declared setup in the [media guide](../presentation/tours/TOOL.md). Browser
tests require their approved macOS execution boundary; ordinary `make check` does
not launch a browser.

Browser reports and screenshots go to `.local/presentation-qa/`, separate from
the site. Override `PRESENTATION_OUTPUT` and `PRESENTATION_REPORTS` when needed.

Guided tour inputs are pinned in
[presentation/tours/inputs.json](../presentation/tours/inputs.json):

```sh
uv run med media prepare
uv run med media check
uv run med present --serve --local-media
```

These commands restore/check the retained derived snapshot, not every raw
preprocessing step. Media optimization and rendering dependencies are documented
in the media guide.

## Recovery boundaries

- Do not run retired authoring generators to repair historical links; use
  [archive recovery](../archive/README.md).
- Raw runs, environments, datasets and generated media remain local.
- Missing inputs, licensing, mutable container bases and independent backup are
  separate recovery concerns.
- Restore, replay and presentation checks do not establish clinical validity or
  submission readiness.
