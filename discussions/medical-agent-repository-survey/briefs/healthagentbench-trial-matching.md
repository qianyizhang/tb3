# Match a patient to eligible trials

Read one patient’s history and select every eligible clinical trial from a supplied candidate pool.

## Value

Eligibility screening connects a patient’s circumstances to study requirements; a relevant topic alone does not establish eligibility.

## Given

### Original data

One synthetic patient admission note in topic.txt.

### Supplied helpers

Candidate trial XML files with inclusion/exclusion rules, plus the topic ID. No model or eligible-trial shortlist is supplied.

### Callable tools

Terminal and document-processing code; this task asks for evidence reasoning rather than model training.

### Reference-only material

Evaluation targets are references, not extra solver inputs. Local filesystem visibility has not been audited by running this external task.

## Task specification

Use the supplied note and XML pool within one hour. Do not retrieve benchmark answers online. Keep the candidate pool and patient identity attached to each case.

## Expected output

eligible_trials.txt: one NCT identifier per line, ordered by confidence; include all eligible trials and no excluded or unrelated trials.

## Evaluation

The inspected evaluator passes when every gold-eligible trial appears within the first 50 submitted candidates (recall@50 = 1). Precision and F1 are reported but do not determine pass/fail. This is weaker than the prompt’s request to include no ineligible trials.

## Visual explanation

### Workflow

- Patient note + candidate trial XML
- Apply inclusion and exclusion rules
- Ranked list of eligible NCT IDs

### Input

**Contract view; native sample not yet illustrated.** One synthetic patient admission note in topic.txt.

### Supplied helpers

**Given material, not an answer reveal.** Candidate trial XML files with inclusion/exclusion rules, plus the topic ID. No model or eligible-trial shortlist is supplied.

### Reference or output

**Expected artifact, not an actual prediction.** eligible_trials.txt: one NCT identifier per line, ordered by confidence; include all eligible trials and no excluded or unrelated trials.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | Candidate trial XML files with inclusion/exclusion rules, plus the topic ID. No model or eligible-trial shortlist is supplied. | Reconcile dates, treatments, diagnoses and negation across long documents. Every inclusion rule and every exclusion rule matters. |

## Difficulty

Reconcile dates, treatments, diagnoses and negation across long documents. Every inclusion rule and every exclusion rule matters.

## Sources

- [Eligibility evaluator](https://github.com/microsoft/HealthAgentBench/blob/bcbb8085fd549469e2dc7455f4bfd68a1b98895a/tasks/clinical_trial_matching_task_29/tests/harbor_evaluator.py)
- [TREC synthetic patient-vignette provenance](https://www.trec-cds.org/2021.html)

- [Task prompt](https://github.com/microsoft/HealthAgentBench/blob/bcbb8085fd549469e2dc7455f4bfd68a1b98895a/tasks/clinical_trial_matching_task_27/instruction.md)

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Native input/helper/reference views are still missing for this definition. The contract was read from source; no external model or benchmark run was launched.

## Cases

Patient vignettes are unavailable locally. Pool counts come from each case’s source manifest.
