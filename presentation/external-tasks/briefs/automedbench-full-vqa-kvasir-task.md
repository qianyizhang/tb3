> **Public raw example only — Full IDs, benchmark permission and private answers absent. Acquire through [the official Kvasir-VQA route](https://huggingface.co/datasets/SimulaMet-HOST/Kvasir-VQA).**

# Answer a gastrointestinal endoscopy question

Explain one image-question unit, short-answer submission and lexical scoring; public annotation remains reader-only.

## Value

Bind one endoscopy image to its question and retain the real raw decode, short-answer processing and declared evaluator branch. The public source answer/category supports educational reveal only; it is not a clinical finding, Full reference or model output.

## Given

### Original data

Full unit is **question**, generic question.json fields question_id/question/image_paths/question_type; task-specific LiteS1 says **one endoscopy image per sample**. Official raw row0 supplies one native **720×576 JPEG, 35,381 bytes**, source img_id **cla820gl0s3nv071u4fgd7xgq**, source question “Are there any abnormalities in the image? Check all that are present.”. Input view retains source border/embedded acquisition text unchanged; no crop, segmentation, color transform or new findings. Actual Full IDs/submissions count **0**, source image/question count **1**. Row0 is a source locator, not recovered Full question_id.

Official pinned card describes **6,500 images** and **58,849 question-answer rows**, including six question types. These are different units; this pack does not independently count unique images, recover Full selection or prove split equivalence. Raw split has public annotations rather than verified heldout isolation. No A–E option map staged in the retained row/config, despite source question wording “Check all”. Task config answer_mode=open_ended; source category and answer are withheld from input.

### Supplied helpers

Lite fixes microsoft/llava-med-v1.5-mistral-7b; Standard selects an image-capable model under task guidance. LiteS2 requests one actual forward pass, then task-specific LiteS3 and StandardS3 validate **1–10 staged questions**, with raw decode retained and deterministic short-answer postprocess. **No 15-public-gold calibration requirement is in the Kvasir task-specific S3**; the shared generic S3 separately requests ≥10 public rows (15 recommended) and optional gold. That is not the task-specific 1–10 staged-question instruction; effective composite prompt assembly remains unverified. Standard S1 compares all six model_info candidates including LLaVA-Med; current availability/performance unverified. Actual setup, loading, smoke/calibration and model calls are absent. Smoke validation must not consult private labels or substitute heuristic answers.

### Callable tools

Image inspection, model loading/inference, deterministic postprocess and six-field submission guidance. This explainer performs no model, judge, calibration, runtime installation or benchmark staging.

### Reference-only material

Official raw source **answer and category** live in separate reference.json, only revealed later by reader. Initial source.json includes image/question/locator without either answer or category. Public annotations are not Full private gold or independent clinical adjudication; raw/helper vs heldout overlap unknown. Private ground_truth.csv preferred over per-question answer.json; both unavailable. Educational reveal is a display boundary, not security; no private data bundled.

## Task specification

One endoscopy image + question → real model decode → concise postprocessed predicted_answer → question-owned answer.json. Lite plan requires predicted_label empty for open-ended task; six-key schema still requires it. Full archive revision f894057807cc334421784e702ead2c1883583e1b and 47 internal hashes verified; envelope code ref release-owned-v1@1e6471746c94adfd53f552a7bc0b81386f5a5f78 is declared, not independently fetched Git equality. Config/47 source hashes are authority; actual mounts/effective composite prompt unresolved.

## Expected output

**<question_id>/answer.json**, submission root`.`; required keys question_id, predicted_label, predicted_answer, raw_model_output, model_name, runtime_s. Exact question ID, nonempty short-answer/raw backing, nonempty model string and nonnegative numeric runtime; checker permits extra keys, whitespace-only model strings, booleans and nonfinite numeric runtimes (no finite guard); predicted_label empty by task guidance, no A–E validation in open-ended checker. Placeholder/mock/fallback/unknown prefixes rejected; empty raw decode alongside nonempty answer considered forged. All actual output values null here, public answer never copied to participant artifact.

## Evaluation

Pinned vqa_scorer/answer_metrics/normalizer mechanics were inspected; prior retained nonclinical checks were not rerun. Normalize lowercase, ASCII punctuation/whitespace, whole-answer yes/no synonyms, number-word tokens and medical abbreviation tokens; **articles remain**, semantic correctness not adjudicated. Exact match and token Counter-overlap F1 give0–100 then/100. **Nonbinary=.5EM+.5tokenF1**; binary gold uses strict normalized equality (“yes because red” ≠ “yes”). A separate postprocess may collapse prefixes before scoring; actual decode pipeline absent.

Default primary averages over **all supplied question IDs**, including missing/invalid/placeholder predictions; binary yes_no_accuracy uses **gold-binary subset** denominator. Existing-file completion, parsed-answer validity and complete schema are distinct: scorer accepts nonempty answers without checker’s full fields; graded submission requires≥50%valid; output_format_valid uses all-files check. Empty IDs yield vacuous all-format-valid but graded false. Main loop does not deduplicate IDs; missing public question/private reference files can raise instead of yielding a model verdict. All reported fractions are 0–1, not clinical accuracy.

Optional answer judge enabled by run_eval --enable-answer-judge or VQA_ANSWER_JUDGE=1/true/True can replace primary with **judge score sum/all IDs**, while lexical accuracy_heuristic remains diagnostic. Missing backend/key may cause heuristic-fallback judge branch; cached scores/backend/fallback counts must stay visible. No judge run or clinical/model performance exists. Workflow weights .25/.15/.35/.15/.10 active-renormalized, overall task/workflow50/50, default medal settings .40/.25 plus guards are source configuration only.

## Visual explanation

### Workflow

- Native public raw source frame/question; category/answer covered, Full socket absent.
- Canonical controls inspect one-image binding, schema and lexical/strict-binary/optional-judge mechanics with nonclinical tokens.
- Explicit later reader reveal shows source answer/category; exit/reset covers them; participant output remains empty.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: microsoft/llava-med-v1.5-mistral-7b. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

Open-ended lexical normalization is distinct from clinical truth. Full frozen question membership, raw/helper/test isolation and actual pipeline remain unresolved.

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/vqa/vqa-kvasir-task.tar.gz)
- [Official Kvasir-VQA dataset](https://huggingface.co/datasets/SimulaMet-HOST/Kvasir-VQA)
- [Pinned source card](https://huggingface.co/datasets/SimulaMet-HOST/Kvasir-VQA/blob/26df9125b98cbad664e5b1801aac1f70a02689e2/README.md)
- [Original dataset paper](https://doi.org/10.48550/arXiv.2409.01437)
- [Resolution receipt](../sources/automedbench-full-vqa-kvasir-task-resolution.json)

## Gaps and attribution

Full IDs/private answers/benchmark permission absent. Source-original pixel equivalence beyond delivered cached JPEG not established. Source label is annotation, not our diagnosis/performance. Official card permits research/educational CC BY-NC4.0 and requires prior written permission for competitions/commercial use; Full harness separately requires written benchmark permission. Local educational use does not recover benchmark staging authorization. Attribution: Sushant Gautam, Andrea Storås, Cise Midoglu, Steven A. Hicks, Vajira Thambawita, Pål Halvorsen, Michael A. Riegler, Kvasir-VQA:A Text-Image Pair GI Tract Dataset (2024), arXiv2409.01437 and DOI10.1145/3689096.3689458, SimulaMet-HOST distribution derived from HyperKvasir/Kvasir-Instrument. Source bytes unchanged; no publication.

## Coverage

One public raw image/question; zero Full IDs, participant submissions, private references or measured results. Public card image and QA counts are different units.
