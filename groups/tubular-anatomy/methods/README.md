# Experiment support and verification — Tubular anatomy

This is the canonical group-owned coverage list, using the
[shared capability checklist](../../../docs/reproduce.md#experiment-support-and-verification).
The user accepted the selected core backfill on 2026-09-21: another agent must be
able to recover data, prepare an environment, execute and score; stochastic model
outputs may differ. [Decision and scope](../../../discussions/experiment-support-backfill-2026-09-21.md).

## Explicit experiment list

Counts are canonical attempt/evaluation records, including controls and replays;
they are not counts of independent model runs. A zero-record entry may retain an
author pilot in its source. The [verification receipt](../../../docs/evidence/experiment-support-backfill-20260921.json)
checks the 38 experiment records and 187 source hashes across the workbench.

| Experiment and protocol | Attempts / evaluations | Maintained reproduction scope |
| --- | ---: | --- |
| [br042-v4-6h](../experiments/br042-v4-6h/experiment.toml) · [protocol](../experiments/br042-v4-6h/protocol.md) | 5 / 8 | [Recipe](../experiments/br042-v4-6h/reproduction/README.md): 1 task variants, 3 saved-output pairs. |
| [tubular-anatomy-br025](../experiments/br025/experiment.toml) · [protocol](../experiments/br025/protocol.md) | 0 / 0 | Source-only entry; no canonical attempt imported and no maintained execution recipe selected. |
| [tubular-anatomy-br026](../experiments/br026/experiment.toml) · [protocol](../experiments/br026/protocol.md) | 6 / 6 | Historical source/protocol; no maintained execution recipe selected. |
| [tubular-anatomy-br030](../experiments/br030/experiment.toml) · [protocol](../experiments/br030/protocol.md) | 3 / 3 | Historical source/protocol; no maintained execution recipe selected. |
| [tubular-anatomy-br033](../experiments/br033/experiment.toml) · [protocol](../experiments/br033/protocol.md) | 3 / 3 | Historical source/protocol; no maintained execution recipe selected. |
| [tubular-anatomy-br041](../experiments/br041/experiment.toml) · [protocol](../experiments/br041/protocol.md) | 5 / 5 | [Recipe](../experiments/br041/reproduction/README.md): 1 task variants, 4 saved-output pairs. |
| [tubular-anatomy-br042](../experiments/br042/experiment.toml) · [protocol](../experiments/br042/protocol.md) | 15 / 16 | [Recipe](../experiments/br042/reproduction/README.md): 4 task variants, 9 saved-output pairs. |

## Core capability checklist

Each checked item applies only to the recipe/cases above, not every historical
experiment. Runtime proof is in the shared receipt and its per-experiment entries.
Scientific assessments, clinical disputes and old scores remain separate.

- [x] Evidence and interpretation: canonical protocols, attempt/observation links,
  group findings and all experiment-level source hashes reconciled.
- [x] Inputs/environment: complete prepared bundles, file size/SHA-256/mode checks,
  source records and declared Docker/pinned Python requirements.
- [x] Preparation: fresh materialization, plus recovery from transferred data in an
  isolated directory without historical author paths. This restores prepared
  fixtures; it does not regenerate every fixture from upstream raw datasets.
- [x] Execution/collection: selected frozen task definitions use the shared
  launcher/collector; portable Docker oracle/no-op execution is checked. No LLM
  trial was launched as part of this backfill.
- [x] Saved-output scoring: frozen scorers invoked through maintained adapters;
  metric comparison excludes only declared timing fields and uses 1e-8 numeric
  absolute/relative tolerance. Original outcomes are unchanged.
- [x] Inspection: portable task instructions/input inventory and existing group
  stories. This does not claim new native-image viewers or regeneration of every
  historical figure. Landmarks retain their existing native CT/MRI viewer.
- [x] Export: fresh complete handoff, concrete review flags/lineage, and recovery
  plus scoring outside the checkout on this machine. Other-machine proof remains
  to be established by the receiver.
- [x] Fresh execution: oracle/no-op controls for every listed variant. Where listed,
  frozen submitted-program transfer execution is separately checked. Fresh
  stochastic model reruns remain an intentional, unperformed operation.

## Commands and retained limits

Use the experiment ID and a case from its manifest:

```sh
uv run med prepare EXPERIMENT --case CASE --execute
uv run med replay EXPERIMENT --case CASE
uv run med bundle EXPERIMENT /path/to/NEW-bundle --include-flagged
uv run med verify-package /path/to/NEW-bundle
```

A receiver runs `reproduce.py verify`, `replay`, `container-controls` and `evaluate`
from the bundle. Read its README for declared dependencies and fresh model launch
commands. Copy the whole bundle; a source URL or Git clone alone does not include
large prepared fixtures. Local checked bundles are under
`runs/support-backfill-20260921/final/EXPERIMENT/`.

The unselected historical entries above are the remaining backfill list. Reopen a
specific recipe when reused; preserve its original configuration/outcomes and
record actual missing inputs. No historical-only entry is silently marked runnable.

The verified handoff index is `runs/support-backfill-20260921/HANDOFF.md`.
It selects the corrected BR-040 bundle under `final-corrected/`; the earlier
pre-commit draft remains local but is superseded. Exact bundle paths and hashes
are recorded in the verification receipt.
