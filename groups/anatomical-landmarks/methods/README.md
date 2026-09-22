# 2026-09-21 reproduction baseline — Anatomical landmarks

This page preserves the group-owned backfill accepted on 2026-09-21. It is not the
current experiment inventory; use `uv run med list --group anatomical-landmarks`
for that. See the [shared capability checklist](../../../docs/reproduce.md#experiment-support-and-verification)
and the [decision record](../../../discussions/experiment-support-backfill-2026-09-21.md).

## Baseline experiment list

Counts are canonical attempt/evaluation records, including controls and replays;
they are not counts of independent model runs. A zero-record entry may retain an
author pilot in its source. The [verification receipt](../../../docs/evidence/experiment-support-backfill-20260921.json)
checks the 38 experiment records and 187 source hashes across the workbench.

| Experiment and protocol | Attempts / evaluations | Maintained reproduction scope |
| --- | ---: | --- |
| [anatomical-landmarks-br036](../experiments/br036/experiment.toml) · [protocol](../experiments/br036/protocol.md) | 12 / 12 | Historical source/protocol; no maintained execution recipe selected. |
| [anatomical-landmarks-br038](../experiments/br038/experiment.toml) · [protocol](../experiments/br038/protocol.md) | 6 / 6 | Historical source/protocol; no maintained execution recipe selected. |
| [anatomical-landmarks-br039](../experiments/br039/experiment.toml) · [protocol](../experiments/br039/protocol.md) | 6 / 6 | Historical source/protocol; no maintained execution recipe selected. |
| [anatomical-landmarks-br040](../experiments/br040/experiment.toml) · [protocol](../experiments/br040/protocol.md) | 3 / 15 | [Recipe](../experiments/br040/reproduction/README.md): 3 task variants, 6 saved-output pairs. |

## Using this baseline

The checklist applies only to the named recipes and cases. The tracked receipt is
the authority for what was checked; complete local bundles remain untracked. Use
the [shared reproduction guide](../../../docs/reproduce.md) for commands and proof
semantics. Reassess an unselected entry before reuse; never rewrite its old outcome.
