# Convert EHR tables into MEDS events

Adapt an existing conversion pipeline to produce a standardized, timestamped MEDS cohort.

## Value

A common event representation makes downstream analysis less dependent on the hospital database layout.

## Given

### Original data

MIMIC-IV demo tables staged in the task environment.

### Supplied helpers

The MIMIC_IV_MEDS repository, its default event configuration, and explicit requested mappings and prefixes.

### Callable tools

A coding environment and the source project’s task-specific software. Availability of each optional dependency requires separate setup.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Copy the default configuration, retain the default wiring, add the requested admission-demographic events and OMR/HOSP_LAB/ICU_CHARTEVENT prefixes, then run conversion with the custom config.

## Expected output

A complete MEDS cohort produced using a separate custom configuration, with the required event fields and code prefixes.

## Evaluation

verify_output.py checks the generated cohort and required custom events against a demo reference summary; any failed check gives zero reward.

## Visual explanation

### Workflow

- Raw hospital tables + converter
- Configure and execute event conversion
- Validated MEDS cohort

### Input

**Contract view; native sample not yet illustrated.** MIMIC-IV demo tables staged in the task environment.

### Supplied helpers

**Given material, not an answer reveal.** The MIMIC_IV_MEDS repository, its default event configuration, and explicit requested mappings and prefixes.

### Reference or output

**Expected artifact, not an actual prediction.** A complete MEDS cohort produced using a separate custom configuration, with the required event fields and code prefixes.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | The MIMIC_IV_MEDS repository, its default event configuration, and explicit requested mappings and prefixes. | Preserve existing conversion behavior while changing time assignment and event naming. A pipeline that runs can still silently drop events. |

## Difficulty

Preserve existing conversion behavior while changing time assignment and event naming. A pipeline that runs can still silently drop events.

## Sources

- [Task prompt](https://github.com/microsoft/HealthAgentBench/blob/bcbb8085fd549469e2dc7455f4bfd68a1b98895a/tasks/ehr_to_meds_etl/instruction.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.
