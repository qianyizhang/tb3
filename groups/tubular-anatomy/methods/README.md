# 2026-09-21 reproduction baseline — Tubular anatomy

This page preserves the group-owned backfill accepted on 2026-09-21. It is not the
current experiment inventory; use `uv run med list --group tubular-anatomy` for that.
See the [shared capability checklist](../../../docs/reproduce.md#experiment-support-and-verification)
and the [decision record](../../../discussions/experiment-support-backfill-2026-09-21.md).

## Baseline experiment list

Counts are canonical attempt/evaluation records, including controls and replays;
they are not counts of independent model runs. A zero-record entry may retain an
author pilot in its source. The [verification receipt](../../../docs/evidence/experiment-support-backfill-20260921.json)
checks the 38 experiment records and 187 source hashes across the workbench.

| Experiment and protocol | Attempts / evaluations | Maintained reproduction scope |
| --- | ---: | --- |
| [br042-v4-6h](../experiments/br042-v4-6h/experiment.toml) · [protocol](../experiments/br042-v4-6h/protocol.md) | 5 / 8 | [Recipe](../experiments/br042-v4-6h/reproduction/README.md): 1 task variant, 3 saved-output pairs. |
| [tubular-anatomy-br025](../experiments/br025/experiment.toml) · [protocol](../experiments/br025/protocol.md) | 0 / 0 | Source-only entry; no canonical attempt imported and no maintained execution recipe selected. |
| [tubular-anatomy-br026](../experiments/br026/experiment.toml) · [protocol](../experiments/br026/protocol.md) | 6 / 6 | Historical source/protocol; no maintained execution recipe selected. |
| [tubular-anatomy-br030](../experiments/br030/experiment.toml) · [protocol](../experiments/br030/protocol.md) | 3 / 3 | Historical source/protocol; no maintained execution recipe selected. |
| [tubular-anatomy-br033](../experiments/br033/experiment.toml) · [protocol](../experiments/br033/protocol.md) | 3 / 3 | Historical source/protocol; no maintained execution recipe selected. |
| [tubular-anatomy-br041](../experiments/br041/experiment.toml) · [protocol](../experiments/br041/protocol.md) | 5 / 5 | [Recipe](../experiments/br041/reproduction/README.md): 1 task variant, 4 saved-output pairs. |
| [tubular-anatomy-br042](../experiments/br042/experiment.toml) · [protocol](../experiments/br042/protocol.md) | 15 / 16 | [Recipe](../experiments/br042/reproduction/README.md): 4 task variants, 9 saved-output pairs. |

## Using this baseline

The checklist applies only to the named recipes and cases. The tracked receipt is
the authority for what was checked; complete local bundles remain untracked. Use
the [shared reproduction guide](../../../docs/reproduce.md) for commands and proof
semantics. Reassess an unselected entry before reuse; never rewrite its old outcome.
