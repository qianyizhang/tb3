# Correct an existing chest X-ray findings section

Repair unsupported claims in a draft findings section using the current study and available history.

## Value

Editing an existing report tests evidence checking separately from generating a report from scratch.

## Given

### Original data

Chronologically organized chest X-ray studies; the highest study_NN is the target study.

### Supplied helpers

A draft FINDINGS section and prior reports/studies. These supplied texts reduce the writing burden but may anchor the agent to incorrect claims.

### Callable tools

A coding environment and the source project’s task-specific software. Availability of each optional dependency requires separate setup.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Within one hour, edit existing claims only. Do not add new findings or write an IMPRESSION section.

## Expected output

submission.json with final_answer containing the corrected text and the literal FINDINGS header.

## Evaluation

The source evaluator assesses significant report errors and emits a pass/fail reward. Missing answer keys or evaluator failures are infrastructure problems, not evidence of a model error.

## Visual explanation

### Workflow

- Current/prior X-rays + draft report
- Check and repair existing claims
- Corrected FINDINGS text

### Input

**Contract view; native sample not yet illustrated.** Chronologically organized chest X-ray studies; the highest study_NN is the target study.

### Supplied helpers

**Given material, not an answer reveal.** A draft FINDINGS section and prior reports/studies. These supplied texts reduce the writing burden but may anchor the agent to incorrect claims.

### Reference or output

**Expected artifact, not an actual prediction.** submission.json with final_answer containing the corrected text and the literal FINDINGS header.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | A draft FINDINGS section and prior reports/studies. These supplied texts reduce the writing burden but may anchor the agent to incorrect claims. | Distinguish a wrong claim from a changed finding and avoid importing a historical observation into the current study. |

## Difficulty

Distinguish a wrong claim from a changed finding and avoid importing a historical observation into the current study.

## Sources

- [Task prompt](https://github.com/microsoft/HealthAgentBench/blob/bcbb8085fd549469e2dc7455f4bfd68a1b98895a/tasks/xray_report_correction_case_01/instruction.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.

## Cases

The current/prior studies and draft report change between patients. Case-specific images and drafts are not loaded here.
