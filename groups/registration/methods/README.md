# 2026-09-21 reproduction baseline — Registration

This page preserves the group-owned backfill accepted on 2026-09-21. It is not the
current experiment inventory; use `uv run med list --group registration` for that.
See the [shared capability checklist](../../../docs/reproduce.md#experiment-support-and-verification)
and the [decision record](../../../discussions/experiment-support-backfill-2026-09-21.md).

## Baseline experiment list

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
| [registration-br024](../experiments/br024/experiment.toml) · [protocol](../experiments/br024/protocol.md) | 3 / 5 | [Recipe](../experiments/br024/reproduction/README.md): 1 task variant, 2 saved-output pairs. |
| [registration-br028](../experiments/br028/experiment.toml) · [protocol](../experiments/br028/protocol.md) | 3 / 3 | [Recipe](../experiments/br028/reproduction/README.md): 1 task variant, 2 saved-output pairs. |

## Current method guides

- [RESECT point audit](resect-point-audit/README.md)

## Using this baseline

The checklist applies only to the named recipes and cases. The tracked receipt is
the authority for what was checked; complete local bundles remain untracked. Use
the [shared reproduction guide](../../../docs/reproduce.md) for commands and proof
semantics. Reassess an unselected entry before reuse; never rewrite its old outcome.

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
