# 2026-09-21 reproduction baseline — Anatomy audit

This page preserves the group-owned backfill accepted on 2026-09-21. It is not the
current experiment inventory; use `uv run med list --group anatomy-audit` for that.
See the [shared capability checklist](../../../docs/reproduce.md#experiment-support-and-verification)
and the [decision record](../../../discussions/experiment-support-backfill-2026-09-21.md).

## Baseline experiment list

Counts are canonical attempt/evaluation records, including controls and replays;
they are not counts of independent model runs. A zero-record entry may retain an
author pilot in its source. The [verification receipt](../../../docs/evidence/experiment-support-backfill-20260921.json)
checks the 38 experiment records and 187 source hashes across the workbench.

| Experiment and protocol | Attempts / evaluations | Maintained reproduction scope |
| --- | ---: | --- |
| [anatomy-audit-br003](../experiments/br003/experiment.toml) · [protocol](../experiments/br003/protocol.md) | 6 / 6 | Historical source/protocol; no maintained execution recipe selected. |
| [anatomy-audit-br004](../experiments/br004/experiment.toml) · [protocol](../experiments/br004/protocol.md) | 39 / 39 | Historical source/protocol; no maintained execution recipe selected. |
| [anatomy-audit-br010](../experiments/br010/experiment.toml) · [protocol](../experiments/br010/protocol.md) | 0 / 0 | Source-only entry; no canonical attempt imported and no maintained execution recipe selected. |
| [anatomy-audit-br011](../experiments/br011/experiment.toml) · [protocol](../experiments/br011/protocol.md) | 0 / 0 | Source-only entry; no canonical attempt imported and no maintained execution recipe selected. |
| [anatomy-audit-br012](../experiments/br012/experiment.toml) · [protocol](../experiments/br012/protocol.md) | 0 / 0 | Source-only entry; no canonical attempt imported and no maintained execution recipe selected. |
| [anatomy-audit-br013](../experiments/br013/experiment.toml) · [protocol](../experiments/br013/protocol.md) | 10 / 10 | Historical source/protocol; no maintained execution recipe selected. |
| [anatomy-audit-br014](../experiments/br014/experiment.toml) · [protocol](../experiments/br014/protocol.md) | 6 / 6 | Historical source/protocol; no maintained execution recipe selected. |
| [anatomy-audit-br015](../experiments/br015/experiment.toml) · [protocol](../experiments/br015/protocol.md) | 6 / 6 | Historical source/protocol; no maintained execution recipe selected. |
| [anatomy-audit-br017](../experiments/br017/experiment.toml) · [protocol](../experiments/br017/protocol.md) | 12 / 12 | [Recipe](../experiments/br017/reproduction/README.md): 4 task variants, 12 saved-output pairs. |
| [anatomy-audit-mr-frame-association](../experiments/mr-frame-association/experiment.toml) · [protocol](../experiments/mr-frame-association/protocol.md) | 5 / 5 | Historical source/protocol; no maintained execution recipe selected. |

## Current method guides

- [CT organ slice audit](ct-organ-slice-audit/README.md)
- [Dental reference ablation](dental-reference-ablation/README.md)
- [Dental trace audit](dental-trace-audit/README.md)
- [Dental F018 contract v3](dental-f018-contract-v3/README.md)

## Using this baseline

The checklist applies only to the named recipes and cases. The tracked receipt is
the authority for what was checked; complete local bundles remain untracked. Use
the [shared reproduction guide](../../../docs/reproduce.md) for commands and proof
semantics. Reassess an unselected entry before reuse; never rewrite its old outcome.
