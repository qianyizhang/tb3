> **Public train example only; Full test selection/private gold absent. [Official SLAKE](https://huggingface.co/datasets/BoKelvin/SLAKE).**

# Answer English radiology questions from SLAKE

Answer each staged English image question under the declared Lite or Standard method. **Full case absent; public train example only.** [Official acquisition](https://huggingface.co/datasets/BoKelvin/SLAKE). No model output or score is shown.

## Value

A short question links image interpretation, answer normalization and an inspectable submission. Reference agreement does not establish independent diagnosis or clinical benefit.

## Given

### Original data

Full question.json supplies question_id, question and image_paths. Config names SLAKE-EN and open_ended, including open phrases and closed yes/no. There is no multiple-choice option mapping or A-E requirement. A question ID is the scoring unit; repeated images and patients are different units.

This illustration uses the exact 256x256 upstream train qid0 JPEG and English question “What modality is used to take this image?”. Source revision a9083ce6c34ac3ffb17671a605962924d8a8f9e9; img_name xmlab1/source.jpg and img_id1 are source associations, not verified Full IDs. JPEG pixels supply no physical spacing, orientation, native acquisition geometry or patient identity. Public train/validation/test exist; viewer9835 train rows include both language declarations and do not count unique images or English-only Full cases. Exact Full mapping, filtering and patient/image split independence remain unknown.

### Supplied helpers


Pinned task configuration and tier/stage guidance are instructions, not executed evidence. Config and Lite S1 identify **SLAKE-EN English radiology, open phrases or binary answers**. Lite fixes microsoft/llava-med-v1.5-mistral-7b with its declared loader/conversation prompt. No model weights, prompt, tool, calibration or runtime is executed here.

**Lite S3:** exactly 15 public samples and checklist ≥15 records. Its example selects only the first 15 question files, drops missing/invalid gold and does not top up, so fewer than 15 records may result. It reads public `reference_answer` or `reasoning_chain.answer`, and only `image_paths[0]`; general all-image use and calibration/private split isolation are unproven.

**Standard S3:** explicitly a 1–10 question smoke/schema check, despite its “unchanged from lite” opening. It does not repeat Lite's 15-sample prescription. **Generic executable verifier:** ≥10 records; gold may be absent/None without failing its invalid-gold guard. Supplied invalid gold or malformed raw text may each occupy at most 20% (failure is strictly >0.2). Malformed raw is non-string, shorter than five stripped characters or punctuation-led. These checks do not prove genuine calibration or private isolation.

**Source inconsistencies remain unresolved:** Standard S1 lists six candidates and asks comparison of all six, but model_info lists five Standard candidates; S1's choice justification incorrectly names a PathVQA single pathology image, and metadata repeats PathVQA/MCQ wording. These copied statements do not redefine SLAKE's configured input/mode. Access, one-GPU suitability and model quality are source claims, unverified locally; no source file is corrected here.

### Callable tools

inspect_image records dimensions, stated intent and tool logs, not an inferred finding. public_medical_search whitelists routes and sanitizes terms; neither proves private filesystem isolation. submit_answer writes WORKSPACE_DIR/<question_id>/answer.json atomically; evaluator reads agent_dir/<question_id>/answer.json. Its docstring's outputs/ prefix is inconsistent with executable path. No helper, model, postprocess import or evaluator was executed here.

### Reference-only material

Private ground_truth.csv by question_id is preferred, else private/<question_id>/answer.json. Gold text is answer_text or answer. Public train qid0's answer is shown only after explicit educational reveal and resets on scene exit or backward replay. It is source annotation, not Full private gold, generated output or independent diagnosis. Other answer-bearing source fields are excluded from the default input display. Private references are absent. Runtime isolation is untested.

## Task specification

Plan, provision the method, validate postprocessing, infer and submit under the declared condition. Full open_ended mode ignores predicted_label. Preserve a concise phrase or exact yes/no and separate it from raw model text. Source S4 explicitly warns against a five-word cap because some answers have 6–10 words; it describes typical 1–10 word phrases, not a schema length limit.

## Expected output

Write <agent_dir>/<question_id>/answer.json with question_id, predicted_label, predicted_answer, raw_model_output, model_name and runtime_s. Require matching ID; predicted_answer nonempty string; raw output string; model name nonempty string; runtime nonnegative number in seconds. Empty label is conventional and ignored in open mode. Python bool satisfies the numeric type check; extra keys and nonfinite runtime have no explicit rejection guard. Those implementation limits are not recommendations. No output value is supplied here.

Both-empty raw/answer is an honest skip, not a placeholder, but open mode then remains invalid and earns no credit. Nonempty answer with empty raw is a placeholder; generic raw and specified prefixes are rejected. Scorer is weaker than strict format: it string-coerces answer text and does not validate every provenance field. Parse/format validity does not prove a real inference.

## Evaluation

Effective heuristic per-question score is strict normalized yes/no for binary gold, otherwise **0.5 normalized exact match +0.5 token F1**. Metrics internally0-100 are divided by100 into0-1. Normalization lowercases, removes punctuation, collapses whitespace and maps selected yes/no synonyms, number words and standalone medical abbreviations. A longer yes/no sentence need not normalize to exact yes/no. S4 recommends removing articles, while the scorer normalizer retains articles; the recommendation is not an implementation equivalence. Mean heuristic accuracy/EM/F1 use **all evaluator-supplied question IDs (default: discovered split IDs)**, rounded4 and zero whenempty; missing, invalid and placeholders remain denominator. yes_no_accuracy uses the binary-gold subset denominator. Breakdowns count sample_score>=1 as correct, so are distinct from mean fractional heuristic accuracy.

Optional --enable-answer-judge or VQA_ANSWER_JUDGE=1/true/True activates the answer judge for open mode. It promotes sum of judge scores/all evaluator-supplied question IDs (default: discovered split IDs) to primary accuracy and retains heuristic diagnostics. Only parsed records are judged, but invalid/missing IDs remain in denominator. Backend fallback count/rationales are reported; judge score is not necessarily independently LLM-graded. Workflow --llm-judge is a separate route. No active backend/result is known here. Missing private gold errors do not establish model failure.

Strict output_format_valid requires every file valid; graded submission_format_valid requires strict-valid fraction>=0.5 using max(expected,1). Completion counts files/all evaluator-supplied IDs, not validity. Rating F if graded gate false, no scorer-valid answers or filecompletion<0.5; otherwise A primaryaccuracy>=0.40, B>=0.25, else C. Workflow renormalizes active non-None weights; guarded S4 uses halfcompletion/halfparse with placeholder/model-call/low-quality caps; S5 halfanyvalid/halfgradedformat. Overall halfworkflow/halfprimaryaccuracy. fail_rate is1-filecompletion despite its valid-answer comment. No score or measured rating exists.

## Visual explanation

### Workflow

- Inspect native public training image and exact question
- Reveal public annotation explicitly; inspect assistance and normalization
- Read an empty output contract and question-denominator/judge boundaries

### Input

**Native public train input; Full test absent.** One byte-identical 256x256 JPEG and its English source question. No measurement overlay or clinical claim.

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

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/vqa/slake-task.tar.gz); source ref99c166a3546bba348dd618fd310f5d4b8821e77f. Archive7274611eeefef1526636c85e7ea8a6999732d624d852f5e5bb1f9fa5f2047d7f.
- [Pinned SLAKE dataset](https://huggingface.co/datasets/BoKelvin/SLAKE/tree/a9083ce6c34ac3ffb17671a605962924d8a8f9e9), [project](https://www.med-vqa.com/slake/), [CC BY4.0](https://creativecommons.org/licenses/by/4.0/).
- [Source resolution](../sources/automedbench-full-slake-task-resolution.json).

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

## Gaps

Exact Full ID/image/test split mapping, English filtering, repeated-image/patient independence and calibration/private isolation remain unverified. Retained 2026-09-30 card/row GET200 receipts and the verified ZIP member establish only this public training pair. Reopen Full-data claims after exact join and visibility audit; model/performance/clinical claims need separately authorized evidence.
