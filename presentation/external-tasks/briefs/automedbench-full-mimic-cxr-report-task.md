# Generate findings from one or more MIMIC-CXR views

**Symbolic explanation — exact staged JPEG, case mapping and reference report are absent.** [Official source and acquisition](https://physionet.org/content/mimic-cxr/2.1.0/). Official credentialed source requires training and signed DUA; anonymous documented JPEG read returned HTTP403. No patient data was acquired.

Generate one report per staged study from one or more JPEG views, preserving the task's declared method condition and submitting all required reports. This draft illustrates the pinned contract; no image finding, patient report, model output or score is available.

## Value

Image-grounded reporting connects an image input to a readable text artifact. Fluency, format acceptance and text-proxy similarity do not establish factual or clinical accuracy.

## Given

### Original data

The Full config stages `MIMIC_CXR_Report/test_mimic_100_v4/public/<case_id>/images/` with manifest.json and one or more JPEG views. Its grouping unit is study. No exact case list, patient join or staged image is recovered. `test_mimic_100_v4` is a configured name, not proof of a 100-case denominator. The named pilot file is absent, while discovery uses public directories; this is not a demonstrated loader failure. Multiple images may belong to one study, and multiple studies to one patient; exact Full joins remain unknown.

Native MIMIC subject_id, study_id and image/dicom_id are distinct units. Config declares grouping_rule first_three_underscore_fields, but exact filename grouping and Full native join require the missing staging manifest. Use every view listed in the actual manifest without assuming frontal/lateral, view count or longitudinal priors. Random study IDs are not temporal order.

Official MIMIC-CXR is DICOM with reports; MIMIC-CXR-JPG is a processed derivative. Its documented unsigned 0..255 mapping, inversion and equalization describe display values, not HU or quantitative intensity; Full's unstaged conversion is unverified. Source annotations include uncertain/absent/unmentioned distinctions and are not interchangeable with this Full 12-rule regex scorer.

### Supplied helpers

Pinned config, public 12-concept regex schema and tier guidance. Lite compares suitable report pipelines and has no fixed checkpoint. Standard compares at least 3 candidates from MLRG, CXRMate, HERGen and R2-LLM, recording multi-view/longitudinal support when relevant, official checkpoint/inference/export and source evidence in plan.md. These are task instructions; availability and performance are unverified. Pro prose mentions MLRG metrics, but envelope tiers are Lite/Standard and configured backend is lightweight. No model weight is bundled or used.

### Callable tools

Terminal and provisioned task-specific model/library tooling, followed by filesystem report submission. This explanation executes no model, image preprocessing, source loader, private scorer or optional LLM judge.

### Reference-only material

Private `<case_id>/report.txt`, labels.json and manifest.json are evaluator material. None is packaged or displayed. The public regex schema is a scoring rule, not a patient diagnosis or private answer. No public training annotation or report is acquired. Future authorized training annotations require explicit reader reveal, exact partition identity and permission; private evaluator reports/labels remain excluded.

## Task specification

Complete the plan, setup, validation, inference and submission stages under Lite or Standard conditions. Generate a report from the allowed supplied views. The target is findings-only text. The source selector prefers nonempty Findings but otherwise accepts full stripped text; format does not strictly enforce a Findings-only section. These boundaries remain distinct from the authoring target. The staged image boundary remains separate from the private reference report and labels.

## Expected output

Write singular `agent_outputs/<case_id>/report.txt` for every discovered case. The format checker requires UTF-8 decoding, 40..8000 characters, at least20 alphabetic characters, nonblank content and characters in Python string.printable plus newline/tab. Most non-ASCII characters fail that printable test despite valid UTF-8 encoding. The explanation's report remains empty; no fabricated clinical narrative is supplied.

## Evaluation

All cases must have valid output and the case count must be positive. Completion is valid cases divided by all discovered cases, not inferred from the split name. Any missing/invalid case forces rating F and gates aggregate clinical components to zero; some raw micro diagnostics may remain in the report.

Configured lightweight score is **0.7 mean observation F1 + 0.3 mean ROUGE-L F1**, averaged across all case IDs. Observation flags come from 12 binary regex concepts, distinct from the original 14 CheXpert labels: support_devices, no_acute_process, clear_lungs, low_lung_volumes, consolidation, pleural_effusion, pneumothorax, pulmonary_edema, cardiomegaly, adenopathy_or_mass, granuloma_or_calcified_nodule and post_surgical_changes. A negative match globally overrides a positive match; uncertain wording can match positive. There is no independently verified original-label uncertainty conversion or image-finding adjudication.

The selector prefers nonempty Findings; otherwise it uses the entire stripped report, rather than independently selecting Impression. Truthy private labels are used when present; otherwise flags are extracted from the private report. Empty positive sets on both sides receive F1=1 by convention. Micro F1 pools TP/FP/FN separately. ROUGE-L uses normalized-token longest-common-subsequence F1; text overlap is not clinical factuality. MLRG/RadGraph is not the configured backend.

Workflow weights are .25/.15/.35/.15/.10 across five stages. S1-S3 are zero without the optional judge. S4=.5completion+.5format and S5=.5anyvalid+.5format. Overall=.5workflow+.5clinical; valid-report clinical thresholds .80/.55 determine good/okay. These are rules, not observed results. No evaluator was run.

## Visual explanation

### Workflow

- Study image socket and method guidance
- Multi-view report-generation operation
- Unsubmitted text artifact and all-case scoring contract

### Input

**Symbolic input; exact staged views absent.** Empty image socket and unresolved Full case/patient join, with official source route permanently visible.

### Supplied helpers

**Public guidance, not an answer.** Inspect the named tier paths and 12 regex concepts without exposing a patient narrative or private label.

### Reference or output

**Required output schema, not a prediction.** Empty report path, explicit character constraints, all-case denominator and text-proxy limits. No reference report, generated report or measured score.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Candidate report-generation methods, rather than one fixed checkpoint. | Compare suitable pipelines, select one and validate findings-only generation. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

One or more study views limit available visual information. Preprocessing, report generation and full-submission format must agree with source requirements; generic text overlap and regex agreement do not establish diagnostic quality or calibration.

## Sources

- [Pinned Full task package](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/report/mimic-cxr-report-task.tar.gz).
- [Official MIMIC-CXR acquisition](https://physionet.org/content/mimic-cxr/2.1.0/), DOI10.13026/4jqj-jw95; [JPG derivative and label contract](https://physionet.org/content/mimic-cxr-jpg/2.1.0/), DOI10.13026/jsn5-t979.
- [Source acquisition/contract receipt](../sources/automedbench-full-mimic-cxr-report-task-resolution.json).

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

## Gaps

Credentialed source views, exact Full case/study/view manifest, patient join, generated report, private reference and score absent. Official pages GET200 and documented anonymous native JPEG GET403 retained; no login, DUA acceptance or account entitlement audit. Reopen after independent authorized acquisition and exact staging/view mapping, separated private evaluator and verified section adapter. Clinical findings require independent evidence.
