# Generate a report from a frontal CheXpert Plus X-ray

**Symbolic explanation — exact staged JPEG, case mapping and reference report are absent.** [Official source and acquisition](https://aimi.stanford.edu/datasets/chexpert-plus). Public mirror metadata is available; it does not identify Full's staged cases or establish derivative redistribution terms.

Generate one report per staged study from a single frontal JPEG, preserving the task's declared method condition and submitting all required reports. This draft illustrates the pinned contract; no image finding, patient report, model output or score is available.

## Value

Image-grounded reporting connects an image input to a readable text artifact. Fluency, format acceptance and text-proxy similarity do not establish factual or clinical accuracy.

## Given

### Original data

The Full config stages `CheXpert_Plus_Report/test_100_v1/public/<case_id>/images/` with manifest.json and one frontal JPEG. Its grouping unit is study. No exact case list, patient join or staged image is recovered. `test_100_v1` is a configured name, not proof of a 100-case denominator. The named pilot file is absent, while discovery uses public directories; this is not a demonstrated loader failure. One input image per study does not establish one case per patient.

Stanford's original CheXpert Plus supplies DICOM and metadata, whereas the named X-iZhang/CheXpert-plus-RRG mirror packages JPEG report-generation subsets. Current mirror metadata lists 62 Findings and 202 Impression validation rows; no exact Full test-case join is available. These sets and native formats must remain distinct.

### Supplied helpers

Pinned config, 12-concept observation schema and tier guidance. Lite names CheXagent-2-3b. Standard asks comparison of at least two named report-generation candidates and documents gated candidates. These are source instructions; current checkpoint availability and performance are unverified. No model weight is bundled or used.

### Callable tools

Terminal and provisioned task-specific model/library tooling, followed by filesystem report submission. This explanation executes no model, image preprocessing, source loader, private scorer or optional LLM judge.

### Reference-only material

Private `<case_id>/report.txt`, labels.json and manifest.json are evaluator material. None is packaged or displayed. The public regex schema is a scoring rule, not a patient diagnosis or private answer. Public mirror narratives, if later exactly sourced, require explicit reader reveal and must retain their validation-source status.

## Task specification

Complete the plan, setup, validation, inference and submission stages under Lite or Standard conditions. Generate a report from the allowed single frontal view. This is report generation, not a 14-class prediction CSV. The staged image boundary remains separate from the private reference report and labels.

## Expected output

Write singular `agent_outputs/<case_id>/report.txt` for every discovered case. The format checker requires UTF-8 decoding, 40..8000 characters, at least20 alphabetic characters, nonblank content and characters in Python string.printable plus newline/tab. Most non-ASCII characters fail that printable test despite valid UTF-8 encoding. The explanation's report remains empty; no fabricated clinical narrative is supplied.

## Evaluation

All cases must have valid output and the case count must be positive. Completion is valid cases divided by all discovered cases, not inferred from the split name. Any missing/invalid case forces rating F and gates aggregate clinical components to zero; some raw micro diagnostics may remain in the report.

Configured lightweight score is **0.7 mean observation F1 + 0.3 mean ROUGE-L F1**, averaged across all case IDs. Observation flags come from 12 binary regex concepts, distinct from the original14 CheXpert labels: support_devices, no_acute_process, clear_lungs, low_lung_volumes, consolidation, pleural_effusion, pneumothorax, pulmonary_edema, cardiomegaly, adenopathy_or_mass, granuloma_or_calcified_nodule and post_surgical_changes. A negative match globally overrides a positive match; uncertain wording can match positive. There is no independently verified original-label uncertainty conversion or image-finding adjudication.

The selector prefers nonempty Findings; otherwise it uses the entire stripped report, rather than independently selecting Impression. Truthy private labels are used when present; otherwise flags are extracted from the private report. Empty positive sets on both sides receive F1=1 by convention. Micro F1 pools TP/FP/FN separately. ROUGE-L uses normalized-token longest-common-subsequence F1; text overlap is not clinical factuality. MLRG/RadGraph is not the configured backend.

Workflow weights are .25/.15/.35/.15/.10 across five stages. S1-S3 are zero without the optional judge. S4=.5completion+.5format and S5=.5anyvalid+.5format. Overall=.5workflow+.5clinical; valid-report clinical thresholds .80/.55 determine good/okay. These are rules, not observed results. No evaluator was run.

## Visual explanation

### Workflow

- Study image socket and method guidance
- Single-view report-generation operation
- Unsubmitted text artifact and all-case scoring contract

### Input

**Symbolic input; exact frontal JPEG absent.** Empty image socket and unresolved Full case/patient join, with official source route permanently visible.

### Supplied helpers

**Public guidance, not an answer.** Inspect the named tier paths and 12 regex concepts without exposing a patient narrative or private label.

### Reference or output

**Required output schema, not a prediction.** Empty report path, explicit character constraints, all-case denominator and text-proxy limits. No reference report, generated report or measured score.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: Open-source chest X-ray report-generation VLM. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |


## Difficulty

A single view limits available visual information. Preprocessing, report generation and full-submission format must agree with source requirements; generic text overlap and regex agreement do not establish diagnostic quality or calibration.

## Sources

- [Pinned Full task package](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/report/chexpert-plus-cxr-task.tar.gz).
- [Official Stanford CheXpert Plus](https://aimi.stanford.edu/datasets/chexpert-plus) and [canonical acquisition](https://stanford.redivis.com/datasets/5yyj-1a9f6ap0x?v=next), DOI10.71718/6nvz-pm34.
- [Named JPEG mirror](https://huggingface.co/datasets/X-iZhang/CheXpert-plus-RRG); source revision/terms and Full case mapping unresolved.

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.


## Gaps

No exact staged JPEG, generated report, private reference, Full case/patient mapping or measured result. Official and mirror metadata GET200 reads are retained; they do not prove image access denial or a usable derivative license. Reopen matching-data claims with exact source bytes, licensing, staged IDs and separated private evaluator material. Reopen clinical claims only with appropriate independent evidence.
