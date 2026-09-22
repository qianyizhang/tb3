# Experiment support and verification — Registration

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
| [registration-br019](../experiments/br019/experiment.toml) · [protocol](../experiments/br019/protocol.md) | 6 / 6 | Historical source/protocol; no maintained execution recipe selected. |
| [registration-br020](../experiments/br020/experiment.toml) · [protocol](../experiments/br020/protocol.md) | 3 / 3 | Historical source/protocol; no maintained execution recipe selected. |
| [registration-br021](../experiments/br021/experiment.toml) · [protocol](../experiments/br021/protocol.md) | 6 / 6 | Historical source/protocol; no maintained execution recipe selected. |
| [registration-br022](../experiments/br022/experiment.toml) · [protocol](../experiments/br022/protocol.md) | 4 / 4 | Historical source/protocol; no maintained execution recipe selected. |
| [registration-br023](../experiments/br023/experiment.toml) · [protocol](../experiments/br023/protocol.md) | 3 / 3 | Historical source/protocol; no maintained execution recipe selected. |
| [registration-br024](../experiments/br024/experiment.toml) · [protocol](../experiments/br024/protocol.md) | 3 / 5 | [Recipe](../experiments/br024/reproduction/README.md): 1 task variants, 2 saved-output pairs. |
| [registration-br028](../experiments/br028/experiment.toml) · [protocol](../experiments/br028/protocol.md) | 3 / 3 | [Recipe](../experiments/br028/reproduction/README.md): 1 task variants, 2 saved-output pairs. |

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

## Proposed RESECT sample rendering

`render_resect_sample.py` reads the locally retained three-case NIfTI/tag sample,
creates compact reader-only orthogonal views and writes the checksum/geometry
manifest used by the proposed task brief. It does not create an experiment or
expose reference points to a solver.

```sh
uv run python groups/registration/methods/render_resect_sample.py \
  --source .local/datasets/resect-sample/e86fb37 \
  --output groups/registration/presentation/figures/resect-sample \
  --manifest groups/registration/presentation/sources/resect-sample.json
```
