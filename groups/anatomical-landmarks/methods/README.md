# Experiment support and verification — Anatomical landmarks

This is the group's current coverage and gradual backfill list, using the
[canonical checklist](../../../docs/reproduce.md#experiment-support-and-verification).
Baseline: 2026-09-21. Support is read from current configs/code; proof below is
linked retained evidence, not a new raw-input audit or trial.

## Retained experiments

Attempts / evaluations count canonical files owned by this experiment, not all
cross-experiment dependencies, model trials or independent repetitions. Evaluations
may include controls, replay or review. Zero means no imported attempt records;
it does not erase an author pilot in a linked source.

| Experiment and protocol | Attempts / evaluations | Current support boundary |
| --- | ---: | --- |
| [anatomical-landmarks-br036](../experiments/br036/experiment.toml) · [protocol](../experiments/br036/protocol.md) | 12 / 12 | Historical source/protocol; no maintained family preparation or replay method declared. |
| [anatomical-landmarks-br038](../experiments/br038/experiment.toml) · [protocol](../experiments/br038/protocol.md) | 6 / 6 | Historical source/protocol; no maintained family preparation or replay method declared. |
| [anatomical-landmarks-br039](../experiments/br039/experiment.toml) · [protocol](../experiments/br039/protocol.md) | 6 / 6 | Historical source/protocol; no maintained family preparation or replay method declared. |
| [anatomical-landmarks-br040](../experiments/br040/experiment.toml) · [protocol](../experiments/br040/protocol.md) | 3 / 15 | Maintained CT/MRI preparation, scoring replay and native-plane view; proof scoped below. |

## Operation coverage

| Checklist item | Support and scoped verification evidence |
| --- | --- |
| 1. Evidence and interpretation | All entries above have canonical records and protocols and are referenced by the group finding. Counts are metadata, not independent replications; source-only entries remain explicit. |
| 2. Input and environment recovery | BR-040 has an exact [input manifest](../experiments/br040/inputs.json); selected local copies were hash-verified at [main cutover](../../../docs/migration/main-cutover.md). Historical Docker image recovery remains unverified; other landmark entries do not inherit this proof. |
| 3. Task preparation | `med prepare anatomical-landmarks-br040 --case CASE` previews; `--execute` restores selected frozen task files through `tb3_medical.landmarks`. This does not rebuild scans from upstream data. [Native closeout](../../../docs/migration/native-closeout.md) records CT-partial preparation. |
| 4. Execution and collection | The [shared runner and Harbor collector](../../../docs/workflow.md#collect-and-inspect) are maintained. Imported record counts are listed above. This does not verify fresh execution or every historical result format. |
| 5. Saved-output scoring replay | `med replay anatomical-landmarks-br040` covers ct-full, ct-partial and mri32-full, Terra/high and Sol/xhigh. Six exact metric matches are recorded in [main-cutover.json](../../../docs/migration/main-cutover.json) and the experiment evaluations. No fresh replay was run for this checklist. |
| 6. Inspection and derived artifacts | [Story](../presentation/story.md), retained figures/tour and native-plane `med view` are supported. The [native closeout](../../../docs/migration/native-closeout.md) records a CT-partial review image; optional imaging inputs/dependencies are still required. |
| 7. Portable export | The [MRI recipe](../../../exports/recipes/landmarks-mri-v2.json) has [two fresh-destination rebuilds and isolated saved-answer replay proof](../../../docs/migration/recovery-v2-check.json). Scope is one MRI task on the same machine, not every case or a fresh model runtime. |
| 8. Fresh execution verification | Fresh Docker/model execution of the native recipe is unverified. Saved oracle/empty-output scoring in the MRI package is not a fresh runtime control execution. |

## Next bounded backfill

Suggested scope (assistant recommendation): **BR-040 CT/MRI saved-output replay**. Keep the three BR-040 cases as the maintained baseline. BR-036/038/039 remain linked historical comparisons; extend native coverage only for a selected reuse need.

- [x] Enumerate every canonical experiment, its protocol, imported record counts and current support boundary (2026-09-21, metadata inspection).
- [x] Separate shared collection/presentation from family preparation/replay and link retained proof where identified (2026-09-21).
- [ ] Separate frozen-task restoration from upstream scan preparation; record runtime recovery before any fresh execution.
- [x] BR-040 names the maintained method, three-case input manifest and exact saved-metric criterion; six retained replay observations and the main-cutover receipt provide scoped proof (2026-09-21 cutover).
- [x] Selected CT-partial view and standalone MRI replay export have retained proof linked above; other views/packages remain outside that proof.
- [ ] If fresh execution is selected and authorized, record its new attempt and runtime proof separately from saved-output replay.

The [source discussion](../../../discussions/experiment-support-backfill-2026-09-21.md)
records the user's consolidation/backfill request and the assistant's terminology
and scope recommendations. These checkboxes do not change experiment progress,
scientific assessment, historical scores or permission to launch a trial. Update
this list when a scoped deliverable is verified; retain dated receipts and missing
input details rather than silently upgrading family-wide coverage.
