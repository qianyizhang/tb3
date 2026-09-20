# Set the viewer to a requested state

Navigate to a specified slice or series and set the requested display window.

## Value

Tests a specific part of using a medical image viewer; success in navigation or metadata lookup is separate from diagnostic accuracy.

## Given

### Original data

A loaded study in an OHIF viewer backed by Orthanc.

### Supplied helpers

Exact target slice/window parameters or a series description; metadata-query tools.

### Callable tools

ABRA viewer and submission tools on the OHIF/Orthanc stack.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Navigate to a specified slice or series and set the requested display window.

## Expected output

Viewer state matching the requested series, slice and/or window settings.

## Evaluation

State-difference scoring checks requested fields; window values allow the generator’s tolerance.

## Visual explanation

### Workflow

- Study or rendered observation
- Requested viewer / reasoning action
- Final state or submitted answer

### Input

**Contract view; native sample not yet illustrated.** A loaded study in an OHIF viewer backed by Orthanc.

### Supplied helpers

**Given material, not an answer reveal.** Exact target slice/window parameters or a series description; metadata-query tools.

### Reference or output

**Expected artifact, not an actual prediction.** Viewer state matching the requested series, slice and/or window settings.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | Exact target slice/window parameters or a series description; metadata-query tools. | Coordinate multiple UI operations and verify the final state; anatomical interpretation is usually unnecessary. |

## Difficulty

Coordinate multiple UI operations and verify the final state; anatomical interpretation is usually unnecessary.

## Sources

- [Task generator](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/scripts/task_generators/tier1.py)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.
