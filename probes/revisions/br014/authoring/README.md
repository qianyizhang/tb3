# BR-014 authoring

[Earlier-trial presentation and current verdict](../../../../docs/anatomy-experiments.md) ·
[Trace walkthroughs](../../../../docs/anatomy-traces.md)

Two frozen local diagnostics: exact present-class inventory on BR013-A02, and
four substantial pancreas/duodenum fragments on BR013-A01. Both Sol/xhigh
attempts passed. See [results](../../../../docs/research-rounds/BR-014-results.md).

| File | Responsibility |
| --- | --- |
| `build_inventory.py` | Copy and verify the old freeze; change only class inventory and contract; freeze I01. |
| `screen_fragments.py` | Natural connectivity audit; lossless/6 mm splits, lineage and nearest-surface screen. |
| `build_fragments.py` | Admit F01 and check nine exact-scoring controls; freeze the task. |
| `common.py` | Paths, hashes, JSON and immutable per-task freezes. |
| `run_trials.py` | Sequential controls and one Sol attempt; Terra only after an authored valid failure. |
| `collect.py` | Replay answers; collect times, usage, runtime provenance and checksums. |
| `review.py` | Authored pass reviews and independent retained-voxel checks. |
| `make_visual.py` | Sample actual coordinates for the conversation's three-state comparison. |

Generated tasks, public NPZ inputs, source masks and raw jobs are local under
`runs/`. This authoring record depends on retained BR-013 and BR-004 fixtures;
it is not a standalone submission package. Source masks/data remain CC BY 4.0,
with copied task attribution and licenses; taxonomy attribution is retained.

The declared sequence was I01 build → controls/Sol → F01 controls/Sol, with the
component screen and F01 freeze completed independently before its trial.
Builders refuse an existing frozen task. Do not rerun completed jobs or mutate
their task bytes. Use a new round/condition for a new experiment.

To refresh the completed evidence without model calls:

```sh
.venv-br003/bin/python probes/revisions/br014/authoring/collect.py
.venv-br003/bin/python probes/revisions/br014/authoring/review.py
```

The review script intentionally asserts the final two-pass outcome. Its authored
interpretation is separate from the general collector and the frozen evaluator.
