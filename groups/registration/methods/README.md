# Methods

[Group overview](../README.md)

Use `uv run med list --group registration` for current experiments.
The [shared reproduction guide](../../../docs/reproduce.md) defines preparation,
replay, controls and export evidence. A supported recipe is not proof of fresh
execution or scientific validity.

## Method guides

- [RESECT point audit](resect-point-audit/README.md)

## Maintained reproduction recipes

- [BR-024 — harder real-deformation cases for Sol](../experiments/br024/reproduction/README.md)
- [BR-028 — add source depth to the failing registration case](../experiments/br028/reproduction/README.md)

## RESECT sample rendering

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

## Verification history

The [2026-09-21 verification receipt](../../../docs/evidence/experiment-support-backfill-20260921.json)
records the original checked scope, hashes, controls and replay counts.
