# Migration record

[Current documentation](../README.md) describes the installed workbench. This
directory records the 2026-09-20 pivot and its successive implementations. Read
later closeouts before treating an older plan or review as the current state.

| Record | Role today |
| --- | --- |
| [Original pivot design](tb3-medical.md) | Accepted purpose, semantic ownership and historical investigation; superseded implementation detail is not a daily contract. |
| [First-pass completion](status.md) | Evidence for the index/archive foundation before the native refactor. |
| [Architecture review](architecture-review.md) | Defects reproduced against `02b9287`; subsequent fixes are recorded in the native closeout. |
| [Minimal workbench plan](native-workbench-plan.md) | Accepted simplification and behavior decisions. |
| [Native implementation closeout](native-closeout.md) | Delivered code, replay/export checks, review fixes and remaining limits at `7177822` / `f5b2ced`. |
| [Experiment coverage](native-experiment-inventory.md) | Dated operation support and recovery gaps; consult experiment configs for later changes. |
| [Main cutover](main-cutover.md) | Completed experiment absorption, canonical Task Explorer integration and main-branch consolidation. |
| [Documentation audit](documentation-audit.md) | Consolidation of current guides and retirement of obsolete guidance. |

Baseline/source inventories, import/conversion reconciliations, preservation checks
and replay/recovery receipts are retained here as JSON. They are point-in-time
proof, not a migration engine or a new recurring validation requirement.
[Retired interface locators](retired-interfaces.json) identify removed launchers
and helpers; [archive recovery](../../archive/README.md) explains inspecting Git bytes.

## Integration boundary

The native implementation, documentation audit and completed BR-042 continuation
are consolidated on `main`. [The cutover receipt](main-cutover.md) records the
source commits, metadata conversion, concurrent Task Explorer handoff and checks.
The original task/scorer bytes, runtime artifacts and scientific observations
remain preserved. New work uses the installed `med` interface; the old launcher
is retired, and retained one-shot adapters are historical sources only.
