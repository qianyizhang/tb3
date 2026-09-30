# Correct an existing chest X-ray findings section

Review a junior draft against the current CXR study and available prior history, then repair **existing** FINDINGS claims. This explanation is symbolic: no patient radiograph, report sentence, correction, judge call or score was acquired.

## Given

### Original data

The pinned case manifest names **12** chronological study folders for one patient. The highest-numbered folder, `study_12`, is the target (one listed CXR view); 11 earlier folders list 20 prior views. These are manifest counts, not locally staged patient files. The case requires credentialed [MIMIC-CXR reports](https://physionet.org/content/mimic-cxr/2.1.0/) and [MIMIC-CXR-JPG images](https://physionet.org/content/mimic-cxr-jpg/2.1.0/).

### Supplied helpers

At task runtime, earlier studies provide images and full prior reports. The target report gives non-generated sections and a populated **counterfactual draft FINDINGS** for correction. These are solver helpers, not true answers. The bootstrap-only manifest contains answer-bearing swap cues and must not be presented as a solver helper or initial reader content.

### Callable tools

The source task gives a terminal workspace and up to one hour. This explainer does not run the task, a report model, image preparer, verifier or judge.

### Reference-only material

The original full target report is staged for the verifier; its true FINDINGS are injected into the answer key in memory and compared with a candidate by CheXprompt. They are not available in this pack. The symbolic clause labels below are authored placeholders, not recovered patient text.

## Task specification

For each **existing** draft clause, compare its claim against the current images and relevant prior report evidence. Keep supported wording, correct the existing claim, or remove it. Do **not** add a finding the draft did not mention. Return only corrected FINDINGS, no IMPRESSION. This is constrained editing, not free report generation.

## Expected output

Set `final_answer` in the one-row `/workspace/submission.json` with `task_id="case_01"`. Begin with the literal `FINDINGS:` header on its own line and then the corrected body. The task directory ID `xray_report_correction_case_01` is distinct from the submitted row ID. No actual final answer exists in this explanation.

## Evaluation

The pinned wrapper extracts candidate and private gold FINDINGS. By default it asks CheXprompt for **five** error-count calls and passes a row only when at least **three** return zero *clinically significant* errors. `CHEXPROMPT_VOTES` and `CHEXPROMPT_PASS_THRESHOLD` can override these numbers. Insignificant counts are diagnostic. Missing gold is an infrastructure error; partial judge errors can prevent three passing votes. The task instruction requires the literal header even though the parser tolerates some missing headers. No call or measured score was produced. The pinned Dockerfile installs CheXprompt from unpinned `main`, so the exact judge prompt/parser version of any future build requires its own pin.

## Visual explanation

An empty image/report socket opens the story. A chronology card then identifies prior studies and the highest-numbered target without showing patient content. The operation scene presents two abstract **existing-clause slots**: inspect evidence status, choose keep/correct/remove, and watch a gate reject unchecked or contradictory choices. It cannot invent a new clause or output a clinical sentence. The output remains an empty FINDINGS schema; gold remains unavailable.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | A draft FINDINGS section and prior reports/studies. These supplied texts reduce the writing burden but may anchor the agent to incorrect claims. | Distinguish a wrong claim from a changed finding and avoid importing a historical observation into the current study. |

## Difficulty

Prior observations can differ from the current study, while a draft can anchor the reader to an incorrect claim. The symbolic gate explains the editing constraint but cannot establish correctness, report quality, or clinical performance.

## Sources

- [Pinned instruction](https://github.com/microsoft/HealthAgentBench/blob/bcbb8085fd549469e2dc7455f4bfd68a1b98895a/tasks/xray_report_correction_case_01/instruction.md).
- [PhysioNet MIMIC-CXR reports](https://physionet.org/content/mimic-cxr/2.1.0/) and [JPG views](https://physionet.org/content/mimic-cxr-jpg/2.1.0/).
- [PhysioNet guidance on MIMIC data and online services](https://physionet.org/news/post/llm-responsible-use/).
- [Source resolution receipt](../sources/healthagentbench-cxr-correction-resolution.json).

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

The official file route returned HTTP 403 without credentialed access in the retained receipt. No matched patient files, target draft, original report, private answer, judge output, or result are present. Before any task run, the source-declared service environment boundary, report-text data handling and unpinned judge revision require separate governed review; this brief makes no runtime-compliance determination.

## Cases

The placeholders are deliberately nonclinical. No patient finding, report sentence, study identity, or current-versus-prior change is depicted.
