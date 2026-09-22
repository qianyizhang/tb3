# Compare two imaging studies over time

Compare study dates or slice counts, or mark a new lesion relative to an earlier study.

## Value

Tests a specific part of using a medical image viewer; success in navigation or metadata lookup is separate from diagnostic accuracy.

## Given

### Original data

A paired current and prior study with source longitudinal metadata.

### Supplied helpers

Study pairing, identifiers and viewer navigation/annotation tools.

### Callable tools

ABRA viewer and submission tools on the OHIF/Orthanc stack.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Compare study dates or slice counts, or mark a new lesion relative to an earlier study.

## Expected output

An integer interval/count difference for metadata questions, or a new-lesion annotation for image questions.

## Evaluation

Metadata questions use exact match; lesion tasks check annotated location against references with a 20-pixel distance threshold.

## Visual explanation

### Workflow

- Study or rendered observation
- Requested viewer / reasoning action
- Final state or submitted answer

### Input

**Contract view; native sample not yet illustrated.** A paired current and prior study with source longitudinal metadata.

### Supplied helpers

**Given material, not an answer reveal.** Study pairing, identifiers and viewer navigation/annotation tools.

### Reference or output

**Expected artifact, not an actual prediction.** An integer interval/count difference for metadata questions, or a new-lesion annotation for image questions.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | Study pairing, identifiers and viewer navigation/annotation tools. | Match the studies and distinguish a genuinely new lesion from a different slice or acquisition. |

## Difficulty

Match the studies and distinguish a genuinely new lesion from a different slice or acquisition.

## Sources

- [Task generator](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/scripts/task_generators/tier4.py)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.
