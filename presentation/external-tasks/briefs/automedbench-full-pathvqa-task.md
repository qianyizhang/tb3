> **Public PathVQA train example only — Full split/private answer absent. Acquire through [the pinned source dataset](https://huggingface.co/datasets/flaviagiammarino/path-vqa).**

# Answer an open-ended pathology visual question

Bind the question to its source image, return a short answer and preserve the declared answer-normalization/evaluator branch. A public train annotation is a source helper, not a heldout Full answer, model prediction or independent clinical finding.

## Value

Bind a pathology image and question to a short answer while keeping lexical agreement, public annotation and clinical interpretation separate. This source example cannot establish Full evaluation performance.

## Given

### Original data

Full unit is **question**, represented by question.json and referenced image_paths. **1 public train row 0 image/question**, **0 actual Full cases/submissions** retained. Cached source JPEG is **309×272**, **49,231bytes**, unchanged; black arrows/letter marks embedded by source are retained, no new overlays/crop/normalization. Source train row question is “where are liver stem cells (oval cells) located?”. No specimen, magnification, acquisition protocol or diagnostic interpretation is inferred. Row0 is a source locator, never a recovered Full question_id. Original dataset/Full partition equivalence unknown.

Official HF dataset distribution revision1685832883334b5bb5beaf4e4b333fdeecaa4ad9 reverified through metadata API; retained row links the cached native image to question and answer. Source JPEG delivery, not source-original pixel equivalence, established. The signed cached URL in old row is transport provenance, not a persistent acquisition guarantee. Main route remains the pinned dataset landing.

### Supplied helpers

Lite fixes microsoft/llava-med-v1.5-mistral-7b/helper inference. S3 asks **15 public calibration records with retrievable public gold**, while config smoke bounds 1–10 describe a different requirement. Script comments say top up if gold missing, but displayed loop reads first15 and can retain fewer; no successful calibration implied. Never read private gold or fabricate missing labels. Standard S1 requires comparison of exactly six candidates, including LLaVA-Med; model_info lists five and incorrectly calls the inputs multiple-choice. Config and task S1 declare open-ended image + question. These source disagreements remain unresolved; no comparison ran. Training/helper annotations must remain distinct from heldout test/private references; overlap and calibration eligibility unverified. Helper selects image_paths[0], not verified general multi-image handling.

### Callable tools

Source image inspection/model loading/postprocessing/submission guidance. No weights, inference, calibration, model/evaluator trial, runtime installation or publication.

### Reference-only material

Public **train answer** is reference.json, later reader reveal only. source.json has image/question without answer. It is not private Full answer or independent pathology adjudication. Private ground_truth.csv preferred over per-question answer.json; both absent. Missing gold can raise file error, not a model miss. Browser educational reveal is not a security boundary; no private data bundled.

## Task specification

Question + referenced image(s) → actual VLM raw decode → short-answer postprocess → answer.json. No A–E options are defined. Source config sets answer_mode=open_ended; required label field is present but unused by this branch. Full envelope ref 99c166a3546bba348dd618fd310f5d4b8821e77f declared; archive f894057807cc334421784e702ead2c1883583e1b/internal hashes verified, independent upstream code Git equality not established. Mount isolation/effective prompt assembly unresolved.

## Expected output

**<question_id>/answer.json** at submission root`.`. Required keys question_id, predicted_label, predicted_answer, raw_model_output, model_name, runtime_s. Nonempty predicted_answer string, exact ID, raw string, truthy model_name string and numeric runtime ≥ 0. Extra keys are accepted; no finite-runtime or boolean exclusion guard. Scorer can coerce non-string predicted_answer to text while strict format requires a string. No A–E label validation in open-ended mode. Target short-answer/plain content, not report or debug wrapper. Unknown/heuristic/fallback/mock prefixes count placeholders; a nonempty answer with empty raw text is forged by checker. All actual fields null in this pack; no public train answer copied into participant output.

## Evaluation

Executable normalized answer processing: lowercase, remove ASCII punctuation, collapse whitespace, whole-answer yes/no synonyms, token number-word mapping and standalone medical abbreviations. It does **not remove articles** or adjudicate synonym meaning generally; these are implementation transformations, not semantic/clinical equivalence guarantees. Exact match and Counter token-overlap F1 return 0–100 then scorer divides by 100. **Nonbinary sample score = .5 EM + .5 token F1**; binary gold uses **strict normalized yes/no equality**, so “yes because...” does not automatically match “yes”. Source postprocess may collapse yes/no prefixes before scoring; actual pipeline unexecuted.

Primary default score averages over **all supplied question IDs**, including missing/invalid/placeholder predictions. Binary-only yes_no_accuracy uses its own gold yes/no subset denominator. File completion counts existing files, parsing counts nonempty answers; scorer skips complete-schema validation, unlike checker. Grade validity≥50% valid files differs from all-files output_format_valid; empty list has vacuousall valid but graded false.

**Optional judge boundary:** if enabled for open-ended, primary accuracy becomes sum judge scores/all supplied IDs; heuristic accuracy remains diagnostic. Cached responses and heuristic-fallback judge branches must stay visible. run_eval CLI enables the answer judge via --enable-answer-judge or VQA_ANSWER_JUDGE=1/true, constructing it from environment; missing keys may invoke heuristic fallback rather than an LLM; this packet has no judge or score. No equivalence between lexical overlap, judge judgement and pathology correctness.

Workflow weights .25/.15/.35/.15/.10 renormalize over active steps; overall 50/50 task/workflow; defaults .40/.25 medal bands and completion/schema/model-call/placeholder guards are source settings, not performance. Pure toy examples red/blue tokens and yes/no strings test mechanics without a patient/answer association.

## Visual explanation

### Workflow

- Native public train image and actual source question; Full case socket empty.
- Canonical controls inspect short-answer schema and three lexical/strict-binary/judge branches using nonclinical mechanics.
- Explicit reader reveal shows public train annotation only; reset covers it, private reference remains absent.

### Input

**Native public training preview.** One unchanged 309×272JPEG with source arrows/letters; source question is visible. No new localization, magnification, clinical finding or Full ID is inferred.

### Supplied helpers

**Source-prescribed methods and calibration rules.** Lite fixed LLaVA-Med and Standard candidate guidance are unverified for current availability/performance. Public training answers may assist calibration; actual15-row requirement and config 1–10 smoke are different units. No pipeline ran.

### Reference or output

**Reader-only public train annotation.** A separate late reader disclosure covers the source answer initially and on backward/exit/reset. It is never a Full private answer, model output or independent pathology diagnosis. Six participant fields remain unset.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: microsoft/llava-med-v1.5-mistral-7b. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

Lexical overlap, binary exact agreement and optional judge scoring use distinct rules. Native training annotation does not identify the Full held-out split or establish clinical truth.

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/vqa/pathvqa-task.tar.gz)
- [Pinned dataset distribution](https://huggingface.co/datasets/flaviagiammarino/path-vqa)
- [Official revision metadata](https://huggingface.co/api/datasets/flaviagiammarino/path-vqa/revision/1685832883334b5bb5beaf4e4b333fdeecaa4ad9)
- [Resolution receipt](../sources/automedbench-full-pathvqa-task-resolution.json)

## Gaps

Public train row 0 image/question available; Full selectedIDs, split equivalence/private gold, submissions and scores absent. Pinned distribution metadata declares MIT, but dataset card reserves original image/caption copyright to textbook publishers/authors and PEIR owners; pack license is LicenseRef-PathVQA-MIT-distribution-image-rights-unresolved, not a blanket image redistribution grant. Clinical adjudication unestablished. No crop localization, biological conclusion, clinical/model performance or clinical advice.

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings remain separately identified; their datasets and recipes are not asserted identical.

Retained packet attributes original images/captions to textbook and PEIR owners. No separately pinned original copyright grant is available; MIT distribution metadata alone does not resolve underlying image rights. Local teaching use and main review remain separate from any publication.

Guidance requests 15 public calibration records; the generic executable verifier accepts ≥10 with optional gold and raw-output evidence guards. Task S3 samples the first 15, drops missing gold and instructs topping up to ≥15; its example loop does not implement that top-up. The mapper collapses yes/no prefixes and extracts the first punctuation-delimited clause; its roughly eight-word comment is not an enforced word cap. Config smoke bounds 1–10 are distinct. No actual calibration set or public/private runtime isolation was validated. Reference scene channels enable only eligibility; the public annotation still requires an explicit reader button and resets before paint on backward/exit.
