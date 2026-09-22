# 2026-09-21 reproduction baseline — Cardiac motion

This page preserves the group-owned backfill accepted on 2026-09-21. It is not the
current experiment inventory; use `uv run med list --group cardiac-motion` for that.
See the [shared capability checklist](../../../docs/reproduce.md#experiment-support-and-verification)
and the [decision record](../../../discussions/experiment-support-backfill-2026-09-21.md).

## Baseline experiment list

Counts are canonical attempt/evaluation records, including controls and replays;
they are not counts of independent model runs. A zero-record entry may retain an
author pilot in its source. The [verification receipt](../../../docs/evidence/experiment-support-backfill-20260921.json)
checks the 38 experiment records and 187 source hashes across the workbench.

| Experiment and protocol | Attempts / evaluations | Maintained reproduction scope |
| --- | ---: | --- |
| [cardiac-motion-br025](../experiments/br025/experiment.toml) · [protocol](../experiments/br025/protocol.md) | 0 / 0 | Source-only entry; no canonical attempt imported and no maintained execution recipe selected. |
| [cardiac-motion-br027](../experiments/br027/experiment.toml) · [protocol](../experiments/br027/protocol.md) | 0 / 0 | Source-only entry; no canonical attempt imported and no maintained execution recipe selected. |
| [cardiac-motion-br029](../experiments/br029/experiment.toml) · [protocol](../experiments/br029/protocol.md) | 0 / 0 | Source-only entry; no canonical attempt imported and no maintained execution recipe selected. |
| [cardiac-motion-br031](../experiments/br031/experiment.toml) · [protocol](../experiments/br031/protocol.md) | 10 / 10 | Historical source/protocol; no maintained execution recipe selected. |
| [cardiac-motion-br032](../experiments/br032/experiment.toml) · [protocol](../experiments/br032/protocol.md) | 3 / 3 | Historical source/protocol; no maintained execution recipe selected. |
| [cardiac-motion-br034](../experiments/br034/experiment.toml) · [protocol](../experiments/br034/protocol.md) | 3 / 3 | [Recipe](../experiments/br034/reproduction/README.md): 1 task variant, 2 saved-output pairs, 5 submitted-program transfers. |
| [cardiac-motion-br035](../experiments/br035/experiment.toml) · [protocol](../experiments/br035/protocol.md) | 6 / 6 | [Recipe](../experiments/br035/reproduction/README.md): 2 task variants, 4 saved-output pairs, 2 submitted-program transfers. |

## Using this baseline

The checklist applies only to the named recipes and cases. The tracked receipt is
the authority for what was checked; complete local bundles remain untracked. Use
the [shared reproduction guide](../../../docs/reproduce.md) for commands and proof
semantics. Reassess an unselected entry before reuse; never rewrite its old outcome.
