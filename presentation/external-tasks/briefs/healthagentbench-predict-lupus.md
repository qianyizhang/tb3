# Predict first diagnosis of systemic lupus erythematosus

Estimate the probability of a first systemic lupus erythematosus diagnosis after hospital discharge.

## Value

A timed prediction tests whether earlier health records contain useful warning signals; benchmark discrimination does not establish clinical benefit.

## Given

### Original data

A longitudinal event log and test rows identified by patient_id and prediction_time.

### Supplied helpers

Labeled train/validation rows, patient split mapping, code conventions and the target’s disease definition. Labels are withheld for test rows.

### Callable tools

A coding environment and the source project’s task-specific software. Availability of each optional dependency requires separate setup.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Predict onset in the source-defined (1,365]-day window, at discharge-day 23:59. Exclude previously diagnosed patients as specified; only events with start < prediction_time may be used. One-hour task budget.

## Expected output

predictions.csv: patient_id,prediction_time,probability. Submit one continuous value in [0,1] for every test row.

## Evaluation

Held-out AUROC measures ranking of positive versus negative outcomes. The evaluation implementation also calculates average precision and Brier score, and compares AUROC with a published baseline.

## Visual explanation

### Workflow

- History before discharge + labeled examples
- Fit and apply a risk predictor
- One probability per test time point

### Input

**Contract view; native sample not yet illustrated.** A longitudinal event log and test rows identified by patient_id and prediction_time.

### Supplied helpers

**Given material, not an answer reveal.** Labeled train/validation rows, patient split mapping, code conventions and the target’s disease definition. Labels are withheld for test rows.

### Reference or output

**Expected artifact, not an actual prediction.** predictions.csv: patient_id,prediction_time,probability. Submit one continuous value in [0,1] for every test row.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | Labeled train/validation rows, patient split mapping, code conventions and the target’s disease definition. Labels are withheld for test rows. | Aggregate a large, irregular history without including any event at or after the prediction time. Rare disease onset and split leakage can dominate the result. |

## Difficulty

Aggregate a large, irregular history without including any event at or after the prediction time. Rare disease onset and split leakage can dominate the result.

## Sources

- [Task prompt](https://github.com/microsoft/HealthAgentBench/blob/bcbb8085fd549469e2dc7455f4bfd68a1b98895a/tasks/ehr_event_modelling_new_lupus/instruction.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.
