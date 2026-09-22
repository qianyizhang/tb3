# Migration record

The 2026-09-20 medical pivot, native implementation and main-branch cutover are
complete. Current operations are documented in the [workflow](../workflow.md).

- [Accepted workbench decisions](native-workbench-plan.md): authoring scope,
  diagnostic runs, assessment and preservation semantics.
- [Independent MRI replay receipt](recovery-check.json): retained at its original
  path because the frozen BR-040 protocol cites it directly.
- [Retired interface locators](retired-interfaces.json): original launcher and
  helper paths, commits and hashes.
- [Recovery guide](../../archive/README.md#documentation-pruning--2026-09-22):
  completed plans, reviews, inventories, conversion receipts and cutover records.

The cutover preserved original task/scorer bytes and scientific observations.
Retained adapters are historical sources; new work uses the installed `med`
interface. Restoring a migration record does not authorize executing it.
