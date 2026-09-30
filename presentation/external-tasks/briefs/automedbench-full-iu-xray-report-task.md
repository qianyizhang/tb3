> **Symbolic IU study — matching image/report and Full staging absent. Acquire through [official Open-i](https://openi.nlm.nih.gov/faq).**

# Generate one chest X-ray report per IU/Open-i study

Consume every JPEG in the staged study manifest and write findings or impression text. The authored nonclinical fixture teaches file validity; it is not a radiology report or a model prediction.

## Value

Study-level reporting connects all permitted views to one text artifact. Format validity and text similarity do not establish factual or clinical quality.

## Given

### Original data

Full declares dataset.included=false and release_owned_unstaged. The grouping unit is **study**, with **one or more images per case**; image count is not the report denominator. **0 matching source images, 0 source reports, 0 actual cases** acquired. The symbolic two-image study is illustrative only; frontal selection/view metadata and actual case/image mapping are unverified. Open-i associates reports and images through XML parentImage tags. Two bounded official API attempts (primary and vip hosts) each timed out after 30 seconds with 0 bytes.

### Supplied helpers

Lite S1 prescribes the release-owned CheXagent-2-3b inference path and consumption of every JPEG in the public study manifest; output is plain text rather than JSON/debug tokens. Standard compares at least three source report candidates (CheXagent variants, CXRMate/MLRG, MAIRA-2 when authorized) for multi-view support, public availability, inference path and report quality. S2/S3 stage environment and validate bounded source baseline output. Model weights, baseline inference and metric resources absent. A public source report, if later acquired, is source/reference helper material: never initial solver input or a private Full answer; reader-only explicit reveal is required. None bundled here.

### Callable tools

Source terminal/model guidance is descriptive. No model, metrics, medical evaluator trial, installation or runtime setup occurred.

### Reference-only material

Private case report.txt and optional labels.json are evaluator-only; no private records bundled. labels.json takes precedence over regex-extracted report labels. Missing private reports cause read failure, not a zero-score clinical finding. Filesystem mount isolation and supplied case-list completeness remain unverified.

## Task specification

The envelope separates /data/public and /data/private. task_loader discovers sorted public directories, while run_eval uses the explicitly supplied --cases list. Treat each listed case as one study regardless of image count. Write one cleaned findings or impression text file for each requested study. Schema/config pin is release-owned-v1@1e6471746c94adfd53f552a7bc0b81386f5a5f78, archive revision f894057807cc334421784e702ead2c1883583e1b; package MANIFEST hashes verified, upstream Git equivalence not independently established.

## Expected output

**agent_outputs/<case_id>/report.txt** (singular agent). UTF-8 decoding, raw character length **40–8000 inclusive**, at least **20 alphabetic characters**, nonempty stripped text and characters in Python string.printable are checked. Unicode alphabetic characters can still fail the ASCII printable test. No JSON envelope, class label, image mask or debug output requested. Actual report remains null. A generic English fixture has no clinical content and only demonstrates checker acceptance; validity is not semantic quality.

## Evaluation

**Config declares equal seven-component metrics; executable defaults to lightweight .7 observation F1 + .3 report similarity because clinical_score_backend and clinical_metric_weights are absent. MLRG path/checkpoints unresolved.** Config names bleu, meteor, rouge_l, f1_radgraph, micro_precision, micro_recall, micro_f1 equally weighted (each 1/7 intent). The optional adapter takes mean BLEU1–4, partial RadGraph F1 and CheXbert all-label micro metrics. Its dependencies/checkpoints are absent; exact external metric tokenization is not established. Local lightweight tokenizer lowercases/removes FINAL REPORT and uses alphanumeric/hyphen token regex; ROUGE-L is token-LCS F1, while schema regex labels produce observation overlap F1. Uppercase FINDINGS section extraction takes precedence; otherwise whole text is used. Empty overlap sets return F1=1; this is a scorer convention, not negative-finding accuracy.

Completion denominator is **all supplied case IDs**, not images: valid_count/N, empty list returns 0 and invalid. Mean per-case metrics divide by max(N,1); micro sums TP/FP/FN across supplied cases. A missing prediction becomes empty text and remains in denominator. Any missing/invalid requested report forces F and zeroes aggregate clinical components, although retained raw micro fields may remain nonzero. Step weights .25/.15/.35/.15/.10 and clinical/workflow half-and-half overall aggregation are implementation defaults; no score or calibrated performance claim. Without judges, S1–S3 are None and treated as 0 in weighted workflow. No S4/S5 Markdown prompts are included in this package; tier preset and evaluator weights alone do not establish effective end-to-end prompt assembly.

## Visual explanation

### Workflow

- Symbolic study with two image sockets illustrates study-vs-image unit only.
- Canonical controls inspect grouping, raw text-format limits, then declared-vs-executable metrics.
- Reader reveal exposes evaluator mechanics; reset covers them. No source/private report exists.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Release-owned CheXagent-2-3b path and study-manifest guidance. | Provision the exact baseline, validate every permitted view and submit one report per study. |
| Full · Standard | Comparison of at least three source candidates and report-task contract; effective prompt assembly remains unresolved. | Resolve the exact method/resources and metric binding before authorized execution. |
| Related source listing | Same target family; release/staging equivalence is not established. | Follow that listing's exact source and conditions; this brief does not merge releases. |

## Difficulty

Study/image correspondence, report cleaning, all-case validity and declared-versus-executable metric binding must agree. External metric assets and effective prompts remain unresolved.

## Coverage

Full release task meaning under Lite/Standard conditions; related inventory listings remain separately identified. No patient image, reference report or observed model result is bundled.

## Sources

- [Pinned task harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/report/iu-xray-report-task.tar.gz)
- [Official acquisition and terms route](https://openi.nlm.nih.gov/faq)
- [Open-i API](https://openi.nlm.nih.gov/services)
- [Resolution receipt](../sources/automedbench-full-iu-xray-report-task-resolution.json)

## Gaps

No matching IU image/report acquired; Full study manifest, private references and metric assets absent. No outputs or scores. The retained official HTTP headers contain no FAQ text, and the current FAQ request timed out; exact dataset terms and any redistribution grant remain unverified. Exact source report/license/view mapping and external metric tokenization remain unresolved. No clinical diagnosis or performance evidence.
