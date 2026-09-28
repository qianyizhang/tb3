# Read imaging against private clinical reports

**This is an archived, unexecuted proposal: zero admitted cases and zero model
trials.** The solver would read a complete examination and safe pre-exam context.
The original radiologist report would remain private for evaluation. “Report-backed”
describes the reference, not report assistance to the solver.

## Value

Assess source-grounded findings, unsupported specificity and incomplete image
search beyond a focused anatomical task. Report agreement is not independent
clinical adjudication or proof that every image abnormality was reported.

## Given

### Original data

Proposed complete native examinations, with chest CT the author's recommended
first source. The proposed 12-patient mix and CT-RATE route were not a recorded
user source selection. No case manifest, admitted image/report pair or frozen
patient claim ledger is retained for this experiment.

### Supplied helpers

Only verified pre-exam context: age, sex, indication, technique and available
comparisons, omitting unknown values. The archived packer allowlists those fields
and anonymously names examination files. No target diagnosis, lesion count,
segmentation labels, expected findings or source report would be supplied.

### Callable tools

The archived CT viewer specifies orientation-aware axial, coronal and sagittal
display, window/level and physical RAS-millimetre slices. It logs rendered views;
the runtime would separately have to retain images actually delivered to the
solver. General numerical tools were proposed; no specialist diagnostic model
was supplied. Neither a renderer nor sibling folders enforce runtime isolation.

### Reference-only material

The original clinical report, source mapping, patient key and curator-extracted
claim table belong outside the solver's runtime. Claims would preserve the
report's negation, uncertainty, laterality and exact supporting excerpts.
Radiologist impressions, image observations and independently confirmed outcomes
remain distinct. No completed specialist review or clinical scoring is retained.

## Task specification

Inspect the complete examination without source lookup. Write findings and a
prioritized impression with evidence locations, measurements where relevant,
uncertainty, limitations and a concise evidence summary. Preserve possible and
indeterminate findings; missing prior studies can make individual temporal claims
unscorable. No case-specific coordinate or output example is currently available.

## Expected output

The archived prompt requests `answer.json` with `findings`, `impression`,
`limitations` and `evidence_summary`. Each finding includes observation, location,
certainty (`present`, `possible` or `indeterminate`) and evidence with an image
filename plus view/slice or physical coordinates. These are proposed fields,
not a retained model answer or a frozen schema validator.

## Evaluation

The protocol proposes two separate comparisons. Expected report claims would be
matched, missed, contradicted or unresolved. Solver additions would be supported,
explicitly contradicted or unmentioned and needing review. Report omission alone
does not establish a false positive. Unresolved findings must not be forced into
clinical precision or an automatic diagnostic pass/fail.

Empty, indiscriminately positive and deliberately contradictory reports were
proposed evaluator controls. A copied source report would be a host-only reference
baseline. None is a retained clinical evaluation result. The archived packer and
three synthetic mechanical tests do not implement diagnostic grading, certify
deidentification or show a clinical/model trial occurred.

## Difficulty

Complete-volume search, evidence-grounded conclusions and calibrated uncertainty
must remain separate from fluent report writing. The intended report isolation is
clear in the retained protocol, but no admitted case or enforced runtime boundary
has been demonstrated.

## Coverage

The original proposal specified 12 distinct patients across four report strata,
then a matched Terra/Sol comparison. This is a plan, not a sample denominator or
observed model comparison. No trial, data acquisition or source change is implied
by this explanation audit.

## Visual explanation

### Workflow

- Review complete images and safe pre-exam context without the private report.
- Return evidence-qualified findings, impression and explicit limitations.
- Compare against preserved report claims, retaining unresolved additions.

### Missing source views

No admitted examination, source report or case-specific answer is available.
The legacy schematic is not an accepted explainer. This entry remains unfinished
pending an authorized source pair and case contract, or an explicit user decision
to limit its scope to a protocol-only explanation.

## Sources

- [BR-018 — Report-backed diagnostic reading](../../experiments/br018/protocol.md)
- [Original proposal and exact reference boundary](../../../../docs/research-rounds/BR-018-report-backed-diagnosis.md)
- [Source audit and archive hashes](../sources/report-backed-reading-audit.json)
- [Recovery manifest](../../../../archive/manifest.json)
- [CT-RATE retained access screen](../../../../datasets/ct-rate.json)
- [Current explanation decision and reopening conditions](../../ideas/report-backed-diagnostic-reading.md)
