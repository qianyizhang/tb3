# Find tumor-bearing slide tiles

Locate every tumor-containing grid tile in a whole-slide pathology image.

## Value

Finding tumor regions supports review of very large tissue slides; tile selection is coarser than drawing cell or tumor boundaries.

## Given

### Original data

A whole-slide image, a public task row and an editable submission template.

### Supplied helpers

A fixed grid: each displayed 256×256 tile at downsample 16 covers 4096×4096 level-zero pixels. Task ID and output schema are supplied.

### Callable tools

A coding environment and the source project’s task-specific software. Availability of each optional dependency requires separate setup.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Enumerate all tumor tiles within 90 minutes. Follow the source grid convention; training or fine-tuning models is forbidden by this prompt.

## Expected output

submission.json with predicted_tumor_tiles as integer column/row coordinates; retain task_id and instruction.

## Evaluation

Use the linked task’s evaluator and its reference data. This survey has not executed that evaluator or established a reproduced score.

## Visual explanation

### Workflow

- Whole slide + tile grid
- Inspect tissue and locate tumor
- List of tumor tile coordinates

### Input

**Contract view; native sample not yet illustrated.** A whole-slide image, a public task row and an editable submission template.

### Supplied helpers

**Given material, not an answer reveal.** A fixed grid: each displayed 256×256 tile at downsample 16 covers 4096×4096 level-zero pixels. Task ID and output schema are supplied.

### Reference or output

**Expected artifact, not an actual prediction.** submission.json with predicted_tumor_tiles as integer column/row coordinates; retain task_id and instruction.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | A fixed grid: each displayed 256×256 tile at downsample 16 covers 4096×4096 level-zero pixels. Task ID and output schema are supplied. | Search a large slide, ignore non-tissue and recognize tumor across variable tissue appearance. A selected crop would remove much of the search burden. |

## Difficulty

Search a large slide, ignore non-tissue and recognize tumor across variable tissue appearance. A selected crop would remove much of the search burden.

## Sources

- [Task prompt](https://github.com/microsoft/HealthAgentBench/blob/bcbb8085fd549469e2dc7455f4bfd68a1b98895a/tasks/tumor_area_selection_pathology_slide_0001/instruction.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.

## Cases

Each case uses a different whole-slide image. The slide contents and tumor locations are not loaded here.
