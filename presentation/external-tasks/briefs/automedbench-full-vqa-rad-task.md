> **Public train example only — exact Full case and private answer absent; acquire through [VQA-RAD](https://osf.io/89kps/).**

# Answer English radiology questions from VQA-RAD

Answer each staged English image question under the declared Lite or Standard method. **Full case absent; public train example only.** [Official acquisition](https://osf.io/89kps/). No model output or score is shown. Fractions are evaluator agreement in 0–1 units, not clinical accuracy.

## Value

A short question links image interpretation, answer normalization and an inspectable submission. Reference agreement does not establish independent diagnosis or clinical benefit.

## Given

### Original data

Full question.json supplies question_id, question and image_paths. Config names VQA-RAD and open_ended, including open phrases and closed yes/no. There is no multiple-choice option mapping or A-E requirement. A question ID is the scoring unit; repeated images and patients are different units.

This illustration uses the exact566x555 public mirror JPEG and English question “are regions of the brain infarcted?”. This is source question text, not an independently established finding. Source revision bcf91e7654fb9d51c8ab6a5b82cacf3fafd2fae9; The source row has no native question ID; row0 is a mirror index, not a verified Full ID. Original MedPix watermark/uploader/source/date markings remain in the pixels; they are source markings, not added annotations. JPEG viewer pixels supply no DICOM acquisition geometry, physical spacing, trustworthy anatomical orientation or patient identity; no modality/HU/diagnosis inferred. The card declares1793 train and451 test question rows and313/203 images, after removing3 duplicate training triplets and1 triplet shared with test. Repeated images remain across splits; triplet de-duplication is not image or patient independence. Exact Full mapping and patient boundaries remain unknown.

### Supplied helpers

Pinned task configuration and tier/stage guidance. Lite fixes microsoft/llava-med-v1.5-mistral-7b with LLaVA-Med loader/conversation prompt. Standard S1 requires comparison of exactly six candidates including LLaVA-Med, while model_info lists five and incorrectly describes multiple-choice inputs. Config and task S1 declare open-ended. This source disagreement is preserved; source access/priority assertions are not current availability or measured performance. S3 guide asks exactly15 public calibration samples and reads reference_answer or reasoning_chain.answer when supplied. The task example reads the first 15 rows and drops missing public gold without implementing a top-up; its checklist requires ≥15 real-gold records. Generic verifier accepts ≥10 with optional gold/raw checks. Smoke1-10 is separate; staged answer visibility and calibration/evaluation overlap remain unaudited. VQA-RAD S3 example reads image_paths[0], so multiple-image completeness is not proven by that example.

### Callable tools

inspect_image records dimensions, stated intent and tool logs, not an inferred finding. public_medical_search whitelists routes and sanitizes terms; neither proves private filesystem isolation. submit_answer writes WORKSPACE_DIR/<question_id>/answer.json atomically; evaluator reads agent_dir/<question_id>/answer.json. Its docstring's outputs/ prefix is inconsistent with executable path. No helper, model, postprocess import or evaluator was executed here.

### Reference-only material

Private ground_truth.csv by question_id is preferred, else private/<question_id>/answer.json. Gold text is answer_text or answer. Public train row0's yes/no annotation is shown only after explicit educational reveal and resets on scene exit or backward replay. It is source annotation, not Full private gold, generated output or independent diagnosis. Other answer-bearing source fields are excluded from the default input display. Private references are absent. Runtime isolation is untested.

## Task specification

Plan, provision the method, validate postprocessing, infer and submit under the declared condition. Full open_ended mode ignores predicted_label. Preserve a concise phrase or exact yes/no and separate it from raw model text. Source S4 explicitly warns against a five-word cap because some answers have6-10 words; it describes typical1-10-word phrases, not a schema length limit.

## Expected output

Write <agent_dir>/<question_id>/answer.json with question_id, predicted_label, predicted_answer, raw_model_output, model_name and runtime_s. Require matching ID; predicted_answer nonempty string; raw output string; model name nonempty string; runtime nonnegative number in seconds. Empty label is conventional and ignored in open mode. Python bool satisfies the numeric type check, there is no explicit finite-runtime guard, whitespace-only model names and extra keys are not rejected; those implementation limits are not recommendations. No output value is supplied here.

Both-empty raw/answer is an honest skip, not a placeholder, but open mode then remains invalid and earns no credit. Nonempty answer with empty raw is a placeholder; generic raw and specified prefixes are rejected. Scorer is weaker than strict format: it string-coerces answer text and does not validate every provenance field. Parse/format validity does not prove a real inference.

## Evaluation

Effective heuristic per-question score is strict normalized yes/no for binary gold, otherwise **0.5 normalized exact match +0.5 token F1**. Metrics internally0-100 are divided by100 into0-1. Normalization lowercases, removes punctuation, collapses whitespace and maps selected yes/no synonyms, number words and standalone medical abbreviations. A longer yes/no sentence need not normalize to exact yes/no. Mean heuristic accuracy/EM/F1 use **all evaluator-supplied question IDs (default: discovered split IDs)**, rounded4 and zero whenempty; missing, invalid and placeholders remain denominator. yes_no_accuracy uses the binary-gold subset denominator. Breakdowns count sample_score>=1 as correct, so are distinct from mean fractional heuristic accuracy.

Optional --enable-answer-judge or VQA_ANSWER_JUDGE=1/true/True activates the answer judge for open mode. It promotes sum of judge scores/all evaluator-supplied IDs to primary accuracy and retains heuristic diagnostics. Only parsed records are judged, but invalid/missing IDs remain in denominator. Backend fallback count/rationales are reported; judge score is not necessarily independently LLM-graded. Workflow --llm-judge is a separate route. No active backend/result is known here. Missing private gold errors do not establish model failure. Explicit --question-ids overrides discovery and is not deduplicated; the exact Full denominator remains unknown.

Strict output_format_valid requires every file valid; graded submission_format_valid requires strict-valid fraction>=0.5 using max(expected,1). Completion counts files/all IDs, not validity. Rating F if graded gate false, no scorer-valid answers or filecompletion<0.5; otherwise A primaryaccuracy>=0.40, B>=0.25, else C. Workflow renormalizes active non-None weights; guarded S4 uses halfcompletion/halfparse with placeholder/model-call/low-quality caps; S5 halfanyvalid/halfgradedformat. Overall halfworkflow/halfprimaryaccuracy. fail_rate is1-filecompletion despite its valid-answer comment. No score or measured rating exists.

## Visual explanation

### Workflow

- Inspect native public training image and exact question
- Reveal public annotation explicitly; inspect assistance and normalization
- Read an empty output contract and question-denominator/judge boundaries

### Input

**Native public train input; Full test absent.** One byte-identical566x555 public mirror JPEG and its English source question. No measurement overlay or clinical claim.

### Supplied helpers

**Source annotation only after reader reveal.** Explicit reveal/hide and reset on scene exit/backward replay. Lite/Standard and public calibration are separate assistance conditions.

### Reference or output

**Unsubmitted schema; no private reference.** Six null values, phrase/yes-no rules, strict/graded gates and optional judge; no generated answer or metric.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: microsoft/llava-med-v1.5-mistral-7b. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

Keep source/public calibration/private gold separate, preserve question/image pairing and exact short-answer normalization. Neither repeated-image questions nor a training annotation establish patient-independent generalization.

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/vqa/vqa-rad-task.tar.gz); source ref99c166a3546bba348dd618fd310f5d4b8821e77f. Archive5835dda60acd2c1eea2c4aa5bd3e10a351f7be27669f2ff02f1899bff08d6c6d.
- [Pinned VQA-RAD dataset](https://huggingface.co/datasets/flaviagiammarino/vqa-rad/tree/bcf91e7654fb9d51c8ab6a5b82cacf3fafd2fae9), [project](https://osf.io/89kps/), [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
- [Source resolution](../sources/automedbench-full-vqa-rad-task-resolution.json).

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

## Gaps

Exact Full ID/image/test split mapping, exact mirror-to-Full join, repeated-image/patient independence and calibration/private isolation remain unverified. Pinned mirror card/row/image GET200 records dated 2026-09-30 and the identical retained JPEG establish only this public training pair. The dated original OSF read returned403; current access was not retested and original OSF terms were not independently verified. The mirror CC0 declaration is retained rather than treated as fresh original-source authorization. Reopen Full-data claims after exact join and visibility audit; model/performance/clinical claims need separately authorized evidence.
