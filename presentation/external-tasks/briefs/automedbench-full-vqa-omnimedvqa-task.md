> **Matching image and Full IDs/private answers absent; source terms differ. Acquire via [official OmniMedVQA](https://huggingface.co/datasets/foreverbeliever/OmniMedVQA) with per-source authorization.**

# Bind four-option medical image questions to exact answer labels

Explain source row → staged question/options → real decode → label extraction → exact option text and answer JSON. Public README QA is source material; the missing image socket is symbolic, not reconstructed patient evidence.

## Given

### Original data

Full unit **question**; task plan normalizes authorized rows to question_id/question/image_paths/options/valid_labels. Modalities vary by source, never infer one common image convention. Pinned README public example **Covid CT_0082**, modality CT, question “What anatomical area is shown in this picture?”, options A:Upper arm region;B:Chest region.;C:Leg region;D:Shoulder and upper back region. Source path **Images/Covid CT/CT_COVID/bmj.m606.full-p4-22%3.png** is a locator, not an acquired image or mounted Full path. **0 matching images,1 public README QA item,0 Full cases/submissions**. No anatomy classification or image interpretation is performed. View is an explicit missing-image socket and real source options.

Official card claims73datasets/118,010images/127,995QAitems/12modalities/>20anatomicalregions; these are published coverage counts, not Full evaluation denominators or locally verified asset counts. Some source images are split from3D, with dimension/slice naming; for this example exact clinical geometry/stack/window/rescale unspecified. Retained tree exposes one10,698,178,715B ZIP; bounded viewer row returns29B error, pinned README recovered7,677B. No small matching image/authorized pair resolved in this pass; broad ZIP acquisition omitted.

### Supplied helpers

Lite fixed microsoft/llava-med-v1.5-mistral-7b, Standard picks task-compatible image model. Task-specific LiteS3/StandardS3 require1–10smoke records, extract one standalone uppercase label **in per-question valid_labels A–D**, copy options[label] exactly and reject parser misses instead of guessing. No task-specific15publicgold calibration requirement; effective generic composite prompt unresolved. Standard S1 compares all six model_info candidates for modality coverage, MCQ behavior, access, memory and reproducibility. These source prescriptions are not current backend availability or model results. Source dataset/options/gt_answer are public source information, not private test helper authorization. Model/weights/setup/smoke/calibration/inference absent.

### Callable tools

Image/model/postprocess/submission guidance only. No model/judge/clinical/evaluator trial or installation.

### Reference-only material

Public README gt_answer “Chest region.” maps to source option B; separate reference.json later reader reveal only. Not private Full gold, actual prediction or clinical adjudication. Source input omits gt_answer/answer_label. Private evaluator ground_truth.csv or per-questionanswerJSON absent. Educational reveal/exit/reset preserves distinction; display hiding is not security.

## Task specification

Per-source authorized image + question + exact A–D option texts → actual decode → deterministic standalone label in allowed set → copy exact option text → six-key answer.json. Actual example image and Full normalizer/stager/mount isolation unverified. Config answer_mode multiple_choice, A–D; generic helper/checker accepts A–E and prose labels, a material discrepancy. Package47 internal pins/archivef894057807cc334421784e702ead2c1883583e1b verified; declaredrelease-owned-v1@1e6471746c94adfd53f552a7bc0b81386f5a5f78 not independently acquiredGitproof.

## Expected output

**<question_id>/answer.json**, submission root`.`; six required keys question_id/predicted_label/predicted_answer/raw_model_output/model_name/runtime_s. Task guidance requires exactID, actual rawdecode, one validA–D label, exact options[label] string, nonempty model and nonnegative runtime. Generic checker weaker: accepts A–E; empty predicted_answer permitted inMCQ and option mismatch only checked conditionally. Scorer can parse label without fullschema. All actual fields null; illustrative parser strings A/E/unparsed are authored controls, not model output or a solved source question.

## Evaluation

Normalize label via generic A–E uppercase/extracted-letter helper, compare directly against private answer_label without normalizing gold. Default primary **correct parsed labels/all evaluator-supplied question IDs (default discovered split IDs)**, including missing/invalid/placeholder outputs; per-modality/type aggregates have their own counts. No open-ended EM/token-F1 or answer-judge primary promotion in this multiple-choice branch. Scorer marks A–E label parsed even without complete fields/option text; checker is stricter for six fields but fails to enforce task A–D and only compares option text if label exists in options and answer is nonempty. Pure synthetic controls show E+empty answer passes generic checker, incomplete B can score yet fail schema, lower-case gold does not match uppercase predicted B. This is a source mismatch, not a benchmark result. Actual staging/parser/schema enforcement must separately reject E, absent labels, ambiguous decodes and option-copy errors.

File completion, parse rate and full-format validity differ. Graded submission≥50%valid predictions vs output_format_valid all-files; missing outputs stay in allIDs denominator; empty IDs vacuous all-format-valid but gradedfalse. Private CSV preferred then question-owned answer.json; no private references retained. Workflow weights .25/.15/.35/.15/.10 active-renormalized, overall task/workflow50/50, default medal settings .40/.25 and guards are settings, not performance. Public README gt_answer is source text, requiring exact mapping to B; actual Full stager/private label conversion unverified.

## Visual explanation

### Workflow

- Public source README question/A–D options with explicit missing image socket; answer covered.
- Canonical controls show label extraction, allowed-set rejection and option-copy/schema-scoring boundaries with authored raw strings.
- Explicit reader reveal shows public source text/mapped letter, exit/reset covers it; participant output empty.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: microsoft/llava-med-v1.5-mistral-7b. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/vqa/vqa-omnimedvqa-task.tar.gz)
- [Official pinned dataset card](https://huggingface.co/datasets/foreverbeliever/OmniMedVQA/blob/1ba51c28fc0773bdf7efb8396e5bcfd4227e22da/README.md)
- [Original paper](https://arxiv.org/abs/2402.09181)
- [Resolution receipt](../sources/automedbench-full-vqa-omnimedvqa-task-resolution.json)

## Gaps and attribution

Public README QA only; matching image/per-source authorization, Full IDs/private gold/submissions/scores absent. No global image license; independently authorize original source dataset, preserve attribution. Public card QA/source architecture discussed for noncommercial local explanation; no medical image copied. AuthorsYutaoHu,TianbinLi,QuanfengLu,WenqiShao,JunjunHe,YuQiao,PingLuo, OmniMedVQA:A New Large-Scale Comprehensive Evaluation Benchmark for Medical LVLM(2024),arXiv2402.09181; foreverbeliever distribution. Symbolic socket/controls originalteaching; no clinical/modelperformance, publication or source-license grant.
