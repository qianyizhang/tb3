> **Public dev example only; Full selection/private gold absent. [Official MedXpertQA](https://huggingface.co/datasets/TsinghuaC3I/MedXpertQA).**

# Answer a multimodal MedXpertQA-MM multiple-choice question

Bind each question to its required image(s), infer a single option letter and emit that letter with its exact option text. The public dev label is an educational source annotation, not a model result, clinical recommendation or recovered Full private answer.

## Given

### Original data

The Full unit is **question**, with question.json, image_paths, options and identifiers. **1 public dev question MM-2000 and 1 matching native JPEG** retained; **0 actual Full cases/submissions** established. Source row images points to MM-2000-a.jpeg; byte-range ZIP member CRC32=3ab54169 and uncompressed size 96,627 verified in retained acquisition. Native bytes unchanged, no crop/annotation/model transformation; whole ZIP hash/revision equivalence unverified because retained route used main. Upstream dataset metadata pinned 7e7c465a68eb2b866926bfa59c8c9d17a8daba65 verified through official API. Image/query language is source content, not an interpretation made here. Full frozen selection and train/dev/test overlap unknown.

### Supplied helpers

Lite names microsoft/llava-med-v1.5-mistral-7b and S2 run_llava_med helper. S3 asks exactly 15 public calibration records with gold in reference_answer or reasoning_chain.answer, the generic executable verifier accepts ≥10 records and makes gold optional, whereas config smoke_sample_min/max is 1/10: these different requirements must not be silently equated. S3 regex maps raw text to letter and options text, probes postprocess(raw) string signature. The helper takes image_paths[0]; general all-image consumption is not proven. This example has exactly 1 image. No weights, decode, calibration or preprocessing executed.

Public calibration gold is supplied helper information only where explicitly eligible; never tune on private/evaluation gold. Actual calibration split isolation not established. Standard method exploration remains task guidance, not an executed comparison.

### Callable tools

Task documents staged-image inspection, terminal/model loading and submission. No model or runtime/tool trials, setup or installation occurred.

### Reference-only material

Official dev row correct label is packaged **only in reference.json**, reader-only explicit later reveal/reset. Input source.json contains question/options/image metadata without label. This public educational annotation is not Full private gold or an independently adjudicated imaging finding. Private ground_truth.csv or per-question answer.json absent. Scorer prefers CSV row, then private per-case file; missing gold can raise, not evidence of model failure. Browser-visible reference is educational, not a confidentiality boundary; no private answer assets included.

## Task specification

Question + linked image(s) + A–E options → actual VLM decode → deterministic letter/option mapper → answer.json. This pack's canonical option selector demonstrates option-to-text association only; it does not infer an answer from the native image. Exact source task ref 99c166a3546bba348dd618fd310f5d4b8821e77f is envelope declaration; Full archive revision f894057807cc334421784e702ead2c1883583e1b and all MANIFEST entries verified, independent upstream Git equivalence not claimed. Actual prompt assembly and evaluation mount isolation unresolved.

## Expected output

**<question_id>/answer.json** at submission root `.`. Required keys: question_id, predicted_label, predicted_answer, raw_model_output, model_name, runtime_s. ID exact-match; A–E label trimmed/uppercased by checker; answer text must equal normalized selected option text when nonempty; raw/model strings and nonnegative numeric runtime. Runtime has no explicit finite or boolean exclusion. Unknown/fallback/heuristic/mock prefixes rejected as placeholders; an honest double-empty raw+answer is not placeholder, but does not prove inference. A label with empty answer can slip through the current checker because option-text comparison is conditional; target contract still requires exact option text. Fixture has null output fields rather than invented decode/runtime/checkpoint.

## Evaluation

Config selects **multiple_choice**. Executable scorer normalizes predicted letter (can extract standalone A–E), compares to **gold answer_label exactly**; it does not lowercase/normalize gold or validate all six schema fields/option text. **Accuracy=correct/all supplied question IDs**, missing/malformed/placeholder predictions remain in denominator. File completion counts existing files; parsed/valid rates count scorer-accepted letters. Ground-truth existence/quality must be audited independently. MCQ has no BLEU/F1 semantic partial credit or open-ended judge contribution.

Format checker is separate: output_format_valid requires every requested file; submission_format_valid requires ≥  50% valid files, allowing partial validity. Empty question list gives vacuous output_format_valid=True but submission_format_valid=False. Thus scorer-letter-valid is not full schema-valid. Source-only synthetic checks exercise this divergence, not patient/model performance.

Workflow weights .25/.15/.35/.15/.10 renormalize over active steps; task/workflow overall is 50/50. Source medal defaults good≥.40/okay≥.25; aggregation applies completion/schema/valid-output gates and placeholder/model-call guards. These are implementation thresholds, not calibrated clinical performance. Full denominator, trial traces and scores absent.

## Visual explanation

### Workflow

- Native public dev image and question/options; Full case socket empty.
- Canonical controls inspect question-image binding, option-to-text association and output/schema boundary without claiming prediction.
- Explicit educational reveal shows public dev label; reset covers it, private gold remains absent.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: microsoft/llava-med-v1.5-mistral-7b. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/vqa/medxpertqa-mm-task.tar.gz)
- [Official MedXpertQA](https://huggingface.co/datasets/TsinghuaC3I/MedXpertQA)
- [Pinned official dataset metadata](https://huggingface.co/api/datasets/TsinghuaC3I/MedXpertQA/revision/7e7c465a68eb2b866926bfa59c8c9d17a8daba65)
- [Resolution receipt](../sources/automedbench-full-medxpertqa-mm-task-resolution.json)

## Gaps

Public dev MM-2000 source image/question available; Full selected IDs, membership/private gold, submissions and scores absent. MIT declared dataset terms retained; source image copyright/clinical adjudication not independently established. No actual Full answer, calibrated performance, diagnosis or patient care advice.

### Source row and native image boundary

The official dev row uses `id=MM-2000` and `images=[MM-2000-a.jpeg]`; Full guidance instead expects `question_id` and `image_paths`. This packet does not assert their staging conversion or selected Full membership. The JPEG is unchanged 96,627 bytes, 945×999 RGB, no EXIF rotation tag; native rows y0–998/columns x0–944, no crop/rotation/resampling. Physical pixel spacing/orientation and Full coordinates are unknown. Native file CRC/SHA and decoded RGB pixels are verified; CSS display containment is not a new image derivative.

### Tier and calibration distinctions

Lite fixes microsoft/llava-med-v1.5-mistral-7b and mistral_instruct; no swap. Standard source says compare all five named candidates: UCSC-VLAA/MedVLThinker-3B-RL_m23k, MedVLSynther/MedVLSynther-3B-RL_13K, Qwen/Qwen2.5-VL-3B-Instruct, google/gemma-4-E2B-it and google/gemma-4-E4B-it. These are source prescriptions, not current availability, performance or local runtime proof.

Smoke uses 1–10 questions; S3 requests exactly 15 public gold samples and checklist ≥ 15 actual records, with absent/invalid gold skipped, never invented. Public helper fields reference_answer or reasoning_chain.answer do not authorize private/evaluation tuning; actual staging split isolation remains unknown. No calibration/model/tool execution occurs here.
