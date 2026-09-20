# Answer questions about study metadata

Count slices or series, or list the distinct modalities in a study.

## Value

Tests a specific part of using a medical image viewer; success in navigation or metadata lookup is separate from diagnostic accuracy.

## Given

### Original data

Study and series metadata accessible through the viewer’s tools.

### Supplied helpers

Study identifiers and a precise answer-format instruction.

### Callable tools

ABRA viewer and submission tools on the OHIF/Orthanc stack.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Count slices or series, or list the distinct modalities in a study.

## Expected output

An integer count or alphabetically sorted comma-separated modality list, submitted through submit_answer.

## Evaluation

Exact-match scoring against metadata-derived reference answers.

## Visual explanation

### Workflow

- Study or rendered observation
- Requested viewer / reasoning action
- Final state or submitted answer

### Input

**Contract view; native sample not yet illustrated.** Study and series metadata accessible through the viewer’s tools.

### Supplied helpers

**Given material, not an answer reveal.** Study identifiers and a precise answer-format instruction.

### Reference or output

**Expected artifact, not an actual prediction.** An integer count or alphabetically sorted comma-separated modality list, submitted through submit_answer.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | Study identifiers and a precise answer-format instruction. | Query the right level of metadata and avoid counting studies, series and slices interchangeably. |

## Difficulty

Query the right level of metadata and avoid counting studies, series and slices interchangeably.

## Sources

- [Task generator](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/scripts/task_generators/tier2.py)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.
