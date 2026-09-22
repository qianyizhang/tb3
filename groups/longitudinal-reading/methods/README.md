# 2026-09-21 reproduction baseline — Longitudinal reading

This page preserves the group-owned backfill accepted on 2026-09-21. It is not the
current experiment inventory; use `uv run med list --group longitudinal-reading`
for that. See the [shared capability checklist](../../../docs/reproduce.md#experiment-support-and-verification)
and the [decision record](../../../discussions/experiment-support-backfill-2026-09-21.md).

## Baseline experiment list

Counts are canonical attempt/evaluation records, including controls and replays;
they are not counts of independent model runs. A zero-record entry may retain an
author pilot in its source. The [verification receipt](../../../docs/evidence/experiment-support-backfill-20260921.json)
checks the 38 experiment records and 187 source hashes across the workbench.

| Experiment and protocol | Attempts / evaluations | Maintained reproduction scope |
| --- | ---: | --- |
| [longitudinal-reading-br018](../experiments/br018/experiment.toml) · [protocol](../experiments/br018/protocol.md) | 0 / 0 | Source-only entry; no canonical attempt imported and no maintained execution recipe selected. |
| [longitudinal-reading-br037](../experiments/br037/experiment.toml) · [protocol](../experiments/br037/protocol.md) | 12 / 12 | [Recipe](../experiments/br037/reproduction/README.md): 4 task variants, 8 saved-output pairs. |

## Current method guides

- [Second-pair selection](longitudinal-ct-case02/README.md)
- [Image-only baseline](longitudinal-ct-image-only/README.md)
- [Revised image-only task](longitudinal-ct-image-only-v2/README.md)
- [Context comparison](longitudinal-ct-context-v1/README.md)
- [Comprehensive curation](longitudinal-ct-curation-v1/README.md)

## Using this baseline

The checklist applies only to the named recipes and cases. The tracked receipt is
the authority for what was checked; complete local bundles remain untracked. Use
the [shared reproduction guide](../../../docs/reproduce.md) for commands and proof
semantics. Reassess an unselected entry before reuse; never rewrite its old outcome.
