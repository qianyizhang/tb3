# Decide which findings are present in a chest CT

Inspect one 3D scan and answer yes or no for every requested abnormality.

## Value

Finding specific abnormalities is one component of reading a chest CT. This task scores labels, not a complete clinical report.

## Given

### Original data

One non-contrast chest CT volume (NIfTI), staged as
`/workspace/data/scan.nii.gz`. The inspected task is `ct_abnormality_valid_16_a_1`
at HealthAgentBench commit `bcbb8085fd549469e2dc7455f4bfd68a1b98895a`.
Its exact CT-RATE volume remains unavailable locally.

### Supplied helpers

A scan-specific `labels.txt` list, described by the prompt as typically 4–12
findings. This is not the observed label count for the unavailable case. No lesion
coordinates, masks or reference report are specified as solver inputs.

### Callable tools

Terminal, internet and installable libraries. Published patient labels/reports
must not be looked up. The pinned runtime specifies two CPUs, 8 GiB memory,
8 GiB storage and no GPU. These are declared settings, not a locally verified run.

### Reference-only material

Bootstrap reads the paired report's English findings and impression, then derives
gold over 17 possible categories using fixed phrase rules. A category is retained
when positive or negative wording matches alone; conflicting or unmatched wording
is dropped. Some categories have no negative phrase rule. This selection is not
a complete inventory of absent and present disease.

Gold values and evidence sentences go to evaluator-only `gold.json`; only retained
names go to solver `labels.txt`. The Compose declaration isolates report download,
derivation code and dataset credentials in a separate bootstrap service. This
source audit did not launch containers or demonstrate runtime isolation. The README
describes hand verification; no case-specific adjudication record was retrieved.

## Task specification

Use the supplied volume; answer every listed finding within one hour. The agent
chooses its own image inspection method. No source-derived view or retained agent
inspection is available for this case.

## Expected output

`/workspace/submission/predictions.txt`: one `label: yes` or `label: no` per requested
name. Names are case-insensitive and order does not matter. The three labels in
the prompt's format example are not the unknown requested set for this patient.

## Evaluation

Every retained gold label must have a parseable matching prediction for binary
reward 1; one wrong or missing answer yields 0. Extra unrequested names do not
enter that loop. The evaluator writes per-label match records and diagnostic
accuracy separately; these do not change the reward. Comments and blank lines
are ignored; the parser also accepts listed yes/no synonyms.

This is report-derived label agreement, not full report quality, lesion
localization, completeness of image review or independently adjudicated diagnosis.
No local model answer, reward or case-specific gold was obtained in this audit.

## Visual explanation

### Workflow

- 3D chest CT
- Inspect requested findings
- Yes / no per label

### Input

Exact CT-RATE case valid_16_a_1 returned HTTP 401 on 2026-09-21: accepted dataset access and authentication are required. No unrelated CT has been substituted.

### Supplied helpers

The requested-label list is generated during data staging. Ten pinned public
prompt, runtime, derivation and verifier files were recovered and checked against
their Git blob hashes on 2026-09-28. The paired report and resulting list have not
been retrieved. Source-code recovery does not resolve the image dependency.

### Reference or output

No source report, gold labels or agent result was downloaded.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Published CT task | Requested-label list | Inspect the volume and classify every requested finding. |

## Difficulty

The label list narrows what to assess, but the agent must choose how to inspect the volume. One wrong finding loses the task reward.

## Sources

- [Exact task prompt](https://github.com/microsoft/HealthAgentBench/blob/bcbb8085fd549469e2dc7455f4bfd68a1b98895a/tasks/ct_abnormality_valid_16_a_1/instruction.md)
- [Evaluator](https://github.com/microsoft/HealthAgentBench/blob/bcbb8085fd549469e2dc7455f4bfd68a1b98895a/tasks/ct_abnormality_valid_16_a_1/tests/harbor_evaluator.py)

- [Dataset and access terms](https://huggingface.co/datasets/ibrahimhamamci/CT-RATE)
- [Sample download and rendering receipt](../samples.json)
- [Pinned source audit and exact missing inputs](../sources/healthagentbench-ct-audit.json)
- [Bootstrap and reference staging](https://github.com/microsoft/HealthAgentBench/blob/bcbb8085fd549469e2dc7455f4bfd68a1b98895a/tasks/ct_abnormality_valid_16_a_1/environment/bootstrap.sh)
- [Report phrase derivation](https://github.com/microsoft/HealthAgentBench/blob/bcbb8085fd549469e2dc7455f4bfd68a1b98895a/tasks/ct_abnormality_valid_16_a_1/environment/gold_derivation.py)

## Coverage

Also: CXR correction, pathology and other healthcare terminal tasks. This preview only inspects the CT example.

## Gaps

The exact CT-RATE scan and its row in `validation_reports.csv` are still missing.
The public dataset card checked on 2026-09-28 still requires access conditions and
contact sharing; no account authorization was tested or terms accepted. Its
additional redistribution restrictions also need resolution for portable source
assets. Authorized local copies were requested in the current completion chat.

The bootstrap does not specify a Hugging Face dataset revision. The earlier
download receipt pins a revision for its denied request; that does not freeze a
successful benchmark runtime. Recovery must pin and check both image and report
bytes before deriving the exact requested labels. This entry remains unfinished;
no unrelated CT or invented case labels substitute for the missing inputs.

## Cases

The scan and requested finding list change between cases. Their contents are not loaded here.
