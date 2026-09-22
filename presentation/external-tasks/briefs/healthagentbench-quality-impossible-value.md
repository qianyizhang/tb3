# Find impossible clinical values

Identify implausible measurements, decimal shifts, conversion mistakes and mismatched units.

## Value

Data-quality checks can reveal errors that otherwise propagate into analysis or predictive models.

## Given

### Original data

Eight compressed EHR tables, including patients, admissions, laboratory values, prescriptions and ICU charted measurements. Rows retain a stable _row_id.

### Supplied helpers

Table dictionaries and a description of the error category. The clues condition additionally names injected error mechanisms and likely tables.

### Callable tools

A coding environment and the source project’s task-specific software. Availability of each optional dependency requires separate setup.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Identify implausible measurements, decimal shifts, conversion mistakes and mismatched units.

## Expected output

flagged_rows.csv with columns table and _row_id. Flag affected source rows, not rewritten values.

## Evaluation

The source verifier reports row-detection F1 against injected-error labels. This measures agreement with the benchmark’s error construction, not general clinical data quality.

## Visual explanation

### Workflow

- EHR tables + row identifiers
- Cross-check values and records
- CSV of flagged rows

### Input

**Contract view; native sample not yet illustrated.** Eight compressed EHR tables, including patients, admissions, laboratory values, prescriptions and ICU charted measurements. Rows retain a stable _row_id.

### Supplied helpers

**Given material, not an answer reveal.** Table dictionaries and a description of the error category. The clues condition additionally names injected error mechanisms and likely tables.

### Reference or output

**Expected artifact, not an actual prediction.** flagged_rows.csv with columns table and _row_id. Flag affected source rows, not rewritten values.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Without clues | Error category and data tables. | Infer the concrete error patterns. |
| With clues | Injection types and likely tables are named. | Locate the actual affected rows without the answer list. |

## Difficulty

Use units, patient identity and timing to distinguish a data-entry error from a rare but legitimate observation.

## Sources

- [Task prompt](https://github.com/microsoft/HealthAgentBench/blob/bcbb8085fd549469e2dc7455f4bfd68a1b98895a/tasks/ehr_data_quality_task_impossible_value/instruction.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.
