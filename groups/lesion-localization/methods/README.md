# Experiment support and verification — Lesion localization

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
| [lesion-localization-br016](../experiments/br016/experiment.toml) · [protocol](../experiments/br016/protocol.md) | 10 / 10 | Historical source/protocol; no maintained family preparation or replay method declared. |

## Operation coverage

| Checklist item | Support and scoped verification evidence |
| --- | --- |
| 1. Evidence and interpretation | All entries above have canonical records and protocols and are referenced by the group finding. Counts are metadata, not independent replications; source-only entries remain explicit. |
| 2. Input and environment recovery | Source locators are retained in the experiment records and [group source index](../sources.json). Operation-specific exact input sets and runtime recovery have not been audited in this backfill. |
| 3. Task preparation | Historical method sources are linked from [group.json](../group.json). No maintained family preparation method is declared by these configs; do not import historical authoring modules. |
| 4. Execution and collection | The [shared runner and Harbor collector](../../../docs/workflow.md#collect-and-inspect) are maintained. Imported record counts are listed above. This does not verify fresh execution or every historical result format. |
| 5. Saved-output scoring replay | No workbench-native replay method is declared for these entries. Historical scoring/review sources remain evidence; no claim that every earlier replay receipt has been audited here. |
| 6. Inspection and derived artifacts | The [authored story](../presentation/story.md) is available through `med present`. Raw-data regeneration and native `med view` support are separate; no maintained family `med view` method is declared. |
| 7. Portable export | The shared exporter exists; no family-specific standalone recovery/replay package is verified by this backfill. Preserve historical exports as dated evidence. |
| 8. Fresh execution verification | Historical attempts retain their original outcomes. No fresh execution of a migrated family recipe was performed or established by this backfill. |

## Next bounded backfill

Suggested scope (assistant recommendation): **BR-016 saved aneurysm localization scoring**. Cover the three selected BR-016 scans before adding another lesion family.

- [x] Enumerate every canonical experiment, its protocol, imported record counts and current support boundary (2026-09-21, metadata inspection).
- [x] Separate shared collection/presentation from family preparation/replay and link retained proof where identified (2026-09-21).
- [ ] Inventory scan geometry, weak reference regions, point tolerance, saved answers and verifier. Keep the source-assisted N03 negative condition explicit.
- [ ] For that scope, name the reusable preparation/scoring entry point, required files and comparison criterion; retain a selected recovery/replay receipt before checking this off.
- [ ] Add or verify the inspection/export operation needed by the next use; explicitly record why any item is out of scope.
- [ ] If fresh execution is selected and authorized, record its new attempt and runtime proof separately from saved-output replay.

The [source discussion](../../../discussions/experiment-support-backfill-2026-09-21.md)
records the user's consolidation/backfill request and the assistant's terminology
and scope recommendations. These checkboxes do not change experiment progress,
scientific assessment, historical scores or permission to launch a trial. Update
this list when a scoped deliverable is verified; retain dated receipts and missing
input details rather than silently upgrading family-wide coverage.
