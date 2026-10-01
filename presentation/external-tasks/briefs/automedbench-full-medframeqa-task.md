# Answer a question from supplied medical frames

Develop the declared method to answer each staged multiple-choice question using all referenced frames. **Mixed illustration — upstream frames only; exact Full case and option mapping absent.** [Official acquisition](https://huggingface.co/datasets/SuhaoYu1020/MedFrameQA). No source answer, model output or score is shown.

## Value

The task links a question, its frame list and explicit option tokens to one answer record. Label agreement does not establish independent image diagnosis or clinical benefit.

## Given

### Original data

Full question.json supplies question_id, question, image_paths and options. The question is the scoring unit; frames, videos and patients are different units. This pack includes two byte-identical upstream public test JPEG frames at1280x720, pinned revision96083ae9405b2fdb687005c65902f2ee3d7c9f12. Source image_1/image_2 slots establish display order only, not video timestamps, native CT slice order, orientation, spacing or HU. Exact Full row/frame membership is unknown.

The public card lists2851 test questions and video_id, but supplies no video/patient-disjoint split guarantee. Its sample has6 options; Full acceptsA..E. A list normalizer zips only5 slots and drops the6th; do not silently truncate this row into a Full question. Source clinical question/options/keywords/gold/reasoning are withheld from the pack.

### Supplied helpers

Pinned config and loader/prompt guidance. Lite fixes microsoft/llava-med-v1.5-mistral-7b via LLaVA-Med loader/conversation prompt; Standard supplies bounded candidates and source priority guidance. Source availability/performance assertions are instructions, not verified current access or outcomes. All listed frames must be passed to the actual method.

S3 guide requests15 public calibration rows and reads question.reference_answer or reasoning_chain.answer if present. Actual verifier accepts>=10 records and optional gold, with raw/invalid-gold checks. Smoke config1..10 is separate. Exact staged calibration/evaluation overlap and answer visibility remain unaudited.

### Callable tools

inspect_image records dimensions, declared intent and logs, not a learned finding. public_medical_search applies a URL whitelist and term sanitization; this is not proof of private isolation. submit_answer atomically writes WORKSPACE_DIR/<question_id>/answer.json; evaluator uses the corresponding agent_dir path. No helper, model, postprocess probe or grader ran here.

### Reference-only material

Private ground_truth.csv by question_id is preferred, otherwise private/<question_id>/answer.json. Public upstream correct_answer/reasoning_chain is answer-bearing benchmark material, retained audit-only and absent from the teaching pack. Future educational reference text requires explicit reader reveal and public-source partition, never an alleged model result or private Full answer. Runtime filesystem isolation is untested.

## Task specification

Plan, provision, validate multi-frame prompt/postprocess, infer and submit under Lite or Standard. This configured task is multiple_choice; generic open-ended EM/F1/judge branches are not its answer mode. Keep raw model evidence separate from label normalization and exact option-text mapping. No real decoded output is available.

## Expected output

Write <agent_dir>/<question_id>/answer.json with six required fields (extra keys are accepted): question_id, predicted_label, predicted_answer, raw_model_output, model_name and runtime_s. Require matching ID, label stripped/uppercased to A..E, string fields, nonempty model_name and numeric runtime_s ≥ 0. The checker does not enforce an exact key set, finite runtime or exclude booleans as numbers; whitespace-only model_name is truthy. These are implementation boundaries, not recommended output. If selected option exists and predicted_answer is nonempty, strict checker demands exact option text. Empty-text loophole is not an output recommendation. Placeholder/generic/fallback records are distinct from both-empty honest skip; empty label still fails MCQ parsing. If a valid A..E label is retained while both text fields are empty, both checker and scorer can accept the record and award label credit. This is a source loophole, not evidence of inference or an output recommendation. All teaching values remain null.

## Evaluation

Accuracy is exact normalized predicted_label agreement with private answer_label divided by **all evaluator-selected question IDs (an explicit list, or IDs discovered for the selected split)**, rounded 4 and zero when empty. Missing/invalid/placeholder stay in denominator. Scorer label validity is weaker than full format validity, so a raw correct label can come from a strict-schema-invalid record. Private gold is not normalized by the matching step; missing gold errors do not establish model failure.

output_format_valid requires every file strict-valid; submission_format_valid uses strict-validfilefraction>=0.5 with max(expected,1). Completion counts prediction files, not valid inference; parse/valid/placeholder rates use all questions. Rating F if gradedformatfalse, no scorer-valid answers or completion<.5; otherwise A accuracy>=.40, B>=.25, else C. These are thresholds, not outcomes. No all-case report-task zeroing is assumed.

Workflow renormalizes non-None active weights. S2 uses env/model-call/smoke binary evidence. S4 half completion/half parse has placeholder>.05→.2, undetectedmodelcall→.3, nearlycomplete genuine lowaccuracy<.05→.5 caps. S5 half anyvalid/half gradedformat. Optional workflow judge and postprocess guards affect steps. Overall half workflow/half accuracy. fail_rate uses 1-filecompletion despite a valid-answer comment. No score, runtime, model or verifier run exists.

## Visual explanation

### Workflow

- Upstream native frame slots and unresolved Full question
- Method-specific prompt and A..E contract
- Empty six-field answer and question-based scoring boundaries

### Input

**Native upstream input, not a Full case.** Switch between two exact JPEG source slots; no diagnostic overlay or invented CT geometry. Source order is not time or native slice order.

### Supplied helpers

**Public rule and assistance view, not an answer reveal.** Compare 6 upstream option slots against 5 Full token slots; inspect Lite/Standard prompt and calibration roles without source gold.

### Reference or output

**Unsubmitted schema, not a generated answer.** Six null fields, strict/graded validity gates and all-question denominator; private answers and public gold are absent.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: microsoft/llava-med-v1.5-mistral-7b. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

Preserve every actual frame and the declared option mapping without treating 6 source options as 5. Source public-gold calibration may change assistance; decoding/schema/log evidence does not independently establish patient interpretation.

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/vqa/medframeqa-task.tar.gz); harness source ref 99c166a3546bba348dd618fd310f5d4b8821e77f.
- [Pinned public dataset](https://huggingface.co/datasets/SuhaoYu1020/MedFrameQA/tree/96083ae9405b2fdb687005c65902f2ee3d7c9f12) and [CC BY4.0](https://creativecommons.org/licenses/by/4.0/).
- [Resolution and source receipts](../sources/automedbench-full-medframeqa-task-resolution.json).

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

## Gaps

Exact Full question/frame/options/split mapping, calibration/reference isolation and any participant output or metric absent. Retained successful HTTP 200 acquisitions establish two upstream frames, not Full equivalence. No source request was repeated during this refresh. Reopen Full-data claims only after exact mapping and 6-to-5 conversion audit; reopen clinical/model claims only with independent authorized evidence.
