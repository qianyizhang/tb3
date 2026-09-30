> **Symbolic PathCap500 — native image/caption and selected Full case IDs absent. Acquire through [official PathCap](https://huggingface.co/datasets/jamessyx/PathCap).**

# Caption one histopathology image per case in the 500-case condition

Implement the selected inference-only captioning method and emit concise plain text per staged case. The symbolic image socket and nonclinical text fixture teach input/output boundaries; they are not histology evidence, captions or model results.

## Value

Image-grounded captioning connects one histopathology image to a readable text artifact. Format acceptance and text-proxy agreement do not establish pathology accuracy.

## Given

### Original data

Config defines **image** as grouping unit, **exactly one JPEG per case**, and **expected_case_count=500**. The release_owned_500_unstaged split is not included. **0 native source images, 0 source captions, 0 actual Full cases** retained. Magnification, tissue, staining, specimen, crop/slide correspondence and patient overlap cannot be inferred. Full manifests/IDs are absent. Public images/manifest belong under /data/public; private caption/labels/manifest under /data/private.

The 100 condition has expected_case_count=100 and release_owned_100_unstaged. These are different declared selections, not a proven subset relation; both have the same source and caption contract. No common IDs, ordering, selection seed, exclusion rule or patient independence is recovered. A symbolic index/count is never an actual case ID.

### Supplied helpers

Lite prescribes Salesforce/blip-image-captioning-base inference-only baseline, explicitly release-owned rather than website checkpoint authority. Standard compares at least three public inference-only candidates (BLIP/BLIP2, Qwen2.5-VL or documented pathology-aware VLM) using public evidence and a public-input pilot. Training/fine-tuning on benchmark cases forbidden. Source model_info and prompts are guidance, not acquired weights or execution evidence. Training/helper annotations must stay distinct from selected test captions; split leakage/overlap unverified. No training image/caption bundled.

### Callable tools

Terminal/model guidance only. No installation, preprocessing, model selection trial, image inference or medical/metric evaluator execution occurred.

### Reference-only material

Private report.txt and optional labels.json are evaluator-owned, absent here. Public source captions, if later acquired, are reader-only source annotations behind explicit later reveal, never initial solver text or a recovered private Full reference. None bundled. Actual container mount isolation remains unverified.

## Task specification

One JPEG case → deterministic chosen preprocessing → concise caption → one plain report.txt. Lite S3 pilots one public case before all 500; Standard S3 validates preprocessing/file shape/runtime before 500. No S4/S5 Markdown files included; effective prompt assembly unverified. task_loader sorts public case directories; evaluator uses explicit --cases list and does **not enforce expected_case_count=500**. Declared500 is task intent; denominator is supplied IDs. Use all frozen selected cases once staging is established.

## Expected output

**agent_outputs/<case_id>/report.txt** (singular agent). UTF-8, **1–8000 raw characters inclusive**, **at least 1 alphabetic character**, nonempty stripped text, Python string.printable. A single ASCII letter passes syntax but establishes no caption meaning. Unicode letters may fail printable check. Plain caption without a JSON wrapper, class label or debug text is a task instruction; the checker does not parse or reject wrapper structure. Actual participant caption null; authored nonclinical fixture unrelated to any patient/image.

## Evaluation

**Equal seven metrics are declared; backend/weights/schema bindings absent. Executable defaults to .7 CXR-regex observation F1 + .3 token-LCS similarity, not a validated pathology score.** Config lists bleu, meteor, rouge_l, f1_radgraph, micro_precision, micro_recall, micro_f1 equally weighted; clinical_score_backend/clinical_metric_weights/observation_schema_file omitted. Scorer defaults chest-Xray cxr_12class patterns. Config flags metric_compatibility=unresolved_for_histopathology and blocked_metric_assets. A CXR observation match is not pathology correctness; empty regex-positive sets yield F1=1 by implementation convention, not evidence of a meaningful caption.

Optional MLRG requires repo/checkpoint paths and unavailable resources. Adapter BLEU averages 1–4, maps partialRadGraph and CheXbert all-label micro metrics. Pathology relevance, exact external tokenization and reference validity unresolved. Lightweight tokenizer lowercases/removes FINAL REPORT, splits alphanumeric/hyphen tokens, and computes token-LCS F1; uppercase FINDINGS extraction takes precedence despite caption mode not consumed here, otherwise whole text. labels.json precedes regex-derived labels. These implementation defaults are not a qualified pathology evaluation.

Completion **valid_count/N supplied IDs**, not pixels/slides nor an enforced500. Empty list invalid; missing prediction becomes empty and remains in means/micro counts. Mean per-case metrics divide by max(N,1); micro sums TP/FP/FN. Any invalid/missing requested file forces F and zero aggregate clinical components, while raw micro fields may remain. Workflow weights .25/.15/.35/.15/.10, defaults .80/.55 rating thresholds, 50/50 clinical/workflow overall aggregation are source settings, not observed performance. S1–S3 absent without judges treated 0. No report or score was generated.

## Visual explanation

### Workflow

- One symbolic image socket; selected 500 case manifest empty.
- Canonical controls inspect one-image unit, permissive text syntax and pathology/CXR metric mismatch.
- Explicit reader reveal exposes count/validity mechanics; private/public captions remain absent and reset covers reveal.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Release-owned BLIP inference-only baseline guidance, not website checkpoint authority. | Choose deterministic preprocessing, validate a public pilot and caption every staged case without benchmark training. |
| Full · Standard | Public inference-only candidate guidance. | Compare at least three candidates, validate setup and preprocessing, then caption every staged case without benchmark training. |
| Related source listing | Gallery, branch or Lite-package listing describes a related caption target; release equivalence is unverified. | Follow that entry's exact dataset, method and evaluation conditions; do not infer shared selected IDs. |

## Difficulty

One image per case provides limited visual context. Missing selected-case staging and pathology-compatible metric assets prevent image-grounded demonstration and qualified scoring. A permissive format check is not evidence of caption meaning.

## Sources

- [Pinned Full500 harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/report/pathology-caption-500-task.tar.gz)
- [Official gated PathCap](https://huggingface.co/datasets/jamessyx/PathCap)
- [Pinned official metadata](https://huggingface.co/api/datasets/jamessyx/PathCap)
- [Resolution receipt](../sources/automedbench-full-pathology-caption-500-task-resolution.json)

## Coverage

Pinned Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings remain separately identified; identical data, selected cases and evaluation are not established.

## Gaps

Retained historical anonymous PathCap annotation read returned HTTP401; matching histology image/caption and frozen500case IDs absent.500/100 membership relation unknown; pathology-compatible metric assets absent. No participant outputs or scores. Official metadata revision17205b19b89ab4ad812a81e9b166d0bcbdaa928e declares auto-gated CC-BY-NC2.0; retained metadata exposes noncommercial-use and citation click-through fields. Bounded unauthenticated data.json request returned401; no terms accepted/auth supplied. Bulk images.zip13GB not downloaded. No matching caption-to-image pairing, heldout selection, clinical finding or model quality established.
