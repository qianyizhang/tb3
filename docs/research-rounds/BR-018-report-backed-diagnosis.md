# BR-018 — Report-backed diagnostic reading

**State: preparation; zero admitted cases and zero model trials.**

## Request and scope

2026-09-15, current conversation: the user asks whether the retained
TotalSegmentator cases have abnormality ground truth and requests realistic
diagnostic cases for Terra and Sol: what they find, how they reach a diagnosis,
and the process behind the result. The user explicitly says they are not a
doctor and does not want the author model's reading to become the reference.
Individual message IDs are unavailable. This is a new user-authorized research
round, separate from the closed interview submission. Preserve all earlier
snapshots, outcomes and unrelated unfinished work.

The proposed first cohort is 12 distinct patients with chest CT and original
radiologist reports. Modality and access preferences were asked asynchronously;
this proposal is not a recorded user selection. Access is currently unavailable:
no local Hugging Face token was configured when checked. No gated data have been
downloaded and no case IDs or diagnoses have been invented.

## What our existing references establish

The retained TotalSegmentator inputs provide reference anatomical masks.
BR-004 and BR-017 additionally know their deliberately injected mask errors.
Those references do not establish a complete diagnostic report or confirmed
disease history for the patient. BR-016 has source aneurysm labels, but its
own protocol limits the task to aneurysm localization and retains review gaps.
None of these is a general diagnostic ground-truth report.

## Source screen, checked 2026-09-15

| Source | Independent reference | Fit and limitations | Access |
| --- | --- | --- | --- |
| [CT-RATE](https://huggingface.co/datasets/ibrahimhamamci/CT-RATE) | Clinical radiologist findings and impressions | Recommended CT route; one center, noncontrast chest CT. English reports are translations, reviewed by bilingual final-year medical students. The 18 abnormality labels are largely automatically extracted; use them to shortlist, not to adjudicate. | Gated acceptance/contact sharing; current card shows CC-BY-NC-SA-4.0 and additional terms including no redistribution. No configured local token. |
| [VinDr-CXR](https://physionet.org/content/vindr-cxr/1.0.0/) | Test labels reflect a five-radiologist process | Stronger consensus for the specified findings, but chest X-rays and a fixed label set, not unrestricted narrative diagnosis. | PhysioNet credentialing and data-use terms. |
| [Indiana University / Open-i](https://lhncbc.nlm.nih.gov/LHC-publications/pubs/Preparingacollectionofradiologyexaminationsfordistributionandretrieval.html) | Paired clinical chest X-ray reports | Practical alternative for an accessible report-backed pilot, subject to checking source image access/terms and image-report matching. Public, older benchmark; prior exposure is plausible. | Public search/report pages verified; bulk and image access not yet verified locally. |
| [RadGenome-Chest CT](https://arxiv.org/abs/2404.16754) | CT-RATE plus model-generated grounding/VQA | Useful tooling/research lead; derived LLM answers are not a new independent clinical reference. | Inherits source/access considerations. |
| [AbdomenAtlas 3.0 / RadGPT](https://openaccess.thecvf.com/content/ICCV2025/supplemental/Bassi_RadGPT_Constructing_3D_ICCV_2025_supplemental.pdf) | AI-assisted report construction with expert review | Reserve for abdominal scope; verify case-level review provenance and coverage before admission. Do not silently equate generated reports with contemporaneous clinical reports. | Not investigated to admission. |

CT-RATE methods: [primary paper](https://arxiv.org/html/2403.17834v5), dataset
creation and report processing sections. Its reports support imaging findings
and radiologist impressions; they do not automatically supply pathology or
longitudinal outcome confirmation. Keep original report text, source version,
translation provenance and hashes locally. Do not copy restricted data into
the tracked report or submission.

## Task, hypothesis, observations and evaluation

**Task:** read the complete supplied examination and available pre-exam context;
write findings and an impression with evidence locations and uncertainty. No
target disease list, lesion count, segmentation labels or reference report is
shown. Cases can contain multiple findings or no reported acute abnormality.

**Hypothesis:** broad independent reading may reveal missed findings,
unsupported specificity, or incomplete image search that focused anatomical
tasks do not measure. This is an exploratory capability pilot, not a known
external benchmark failure or an original TB3 submission candidate.

**What to observe:** reported abnormalities, their location and confidence,
correspondence to source statements, image views, measurements, explicit
limitations and final concise rationale. A rendered slice is an available view,
not proof of attention or comprehension. Do not request private chain-of-thought
or treat a retrospective explanation as a faithful internal reasoning trace.

**How to evaluate:** score source-backed findings separately from diagnosis
specificity, explicit contradictions, unreferenced additions and trace quality.
Use original report evidence as the reference. Do not make the curator model
the final judge of disputed image interpretations.

## Prospective curation

1. Obtain authorized source access. Read current correction notes and pin the
   dataset revision before selecting files; do not obtain gated files through
   unofficial mirrors. For CT-RATE deduplicate patient, exam and reconstruction.
2. Produce a local candidate ledger from the validation cohort. Proposed 12-case
   mix: three with no reported acute abnormality (retain chronic findings), three
   with a dominant reported abnormality, three with multiple findings, three
   with explicitly qualified/uncertain impressions. Assign strata in that order
   with no patient overlap. Use a fixed seed of 18092026 for within-stratum order.
   Strata must be manually checked against report text before they count.
3. Admit only paired, complete scans/reports with valid geometry, intensity
   scaling and sufficient available context for the scored claims. Log every
   exclusion and replacement. A prior-dependent claim without the prior study
   is unscorable; it need not invalidate all current-image findings.
4. Freeze all selected cases and reference claim tables before any solver run.
   Every expected claim links to an exact source-report excerpt and preserves
   negation, uncertainty and laterality. Curator extraction is explicitly marked
   as such; it is not new expert annotation. Separate imaging observation,
   radiologist impression and independently confirmed outcome.
5. For each case make a solver directory containing only anonymous examination
   files, safe pre-exam context, instructions and generic viewing tools. Keep
   reports, source IDs, keys and curator notes in a separate host-only reference
   directory. Inspect filenames, image headers and pixels for identifying or
   answer-bearing information. Preserve clinical details needed for reading.

The target is diverse realistic reading, not rare-disease enrichment or a
failure hunt. No synthetic pathology, answer-conditioned cropping, shortened
reasoning budget or post-result replacement. This sample is too small and
stratified to estimate population performance or clinical deployment readiness.

## Matched Terra / Sol challenge

- Use fresh isolated sessions for `openai/gpt-5.6-terra` and
  `openai/gpt-5.6-sol`, both at `xhigh`, same input bytes and tools. No grader
  feedback, answer access, source lookup or cross-model conversation. The
  execution container receives only a single solver case; it must not mount
  this repository, host reference directories or credentials for dataset access.
- Start with two plumbing cases, one from each of the first two strata, then
  the remaining ten only after checking image delivery and normal completion.
  A plumbing change creates a new version; retain any exposed attempts and
  label them as development, not untouched evaluation.
- One attempt per model per frozen case, no repeated sampling to obtain a miss.
  Alternate model order by case. Allow up to 1,800 seconds initially as an
  operational limit; truncation is an incomplete run, not a diagnostic failure.
  Confirm memory and image delivery capacity on actual volumes before freezing
  the resource specification. No launch configuration is final yet.
- Supply complete native data and orientation-aware axial/coronal/sagittal
  windowing, individual slice access and measurements. The helper logs rendered
  image hashes and view settings; the runtime must separately retain images
  actually returned to the model, tool calls, public summaries, output, elapsed
  time and token/cost accounting. The helper alone is not a sandbox or an
  authoritative execution logger.
- No pathology/classification model is supplied initially. General image
  rendering and numerical tools are allowed. Record any future specialist-model
  assistance as a different condition.

## Reference agreement, not an automatic clinical pass/fail

For every expected report claim mark `matched`, `missed`, `contradicted`, or
`unresolved`, with exact source and model excerpts. Keep uncertain source claims
uncertain; never force a specific diagnosis from a qualified report.

For every model addition mark `supported`, `explicitly_contradicted`, or
`unmentioned_needs_review`. Report omission alone does not prove a false
positive. Reported absence of acute disease does not mean absence of chronic
findings. Etiology, malignancy or temporal stability need the matching source
evidence; image appearance alone may support only a descriptive finding.

Report source-claim recall, explicit contradiction counts, unreferenced additions,
and unresolved counts per patient and model. Do not collapse unresolved findings
into true/false positives or report clinical precision without adjudication.
Publish the raw claim comparisons so another person can audit extraction and
matching. Any automated semantic comparison is provisional and labeled by its
judge/model version. Clinical significance and disputed findings need independent
radiologist adjudication; the exploratory report-agreement trial can run while
those remain unadjudicated. Zero completed specialist reviews at preparation.

Validate mechanics using synthetic fixtures: left/right and physical coordinates,
window transforms, scan/report pairing and separate packet contents. Diagnostic
controls include an empty report, an indiscriminately positive report and a
deliberately contradicted finding; these test the evaluation procedure, not
whether the clinical reference is complete. A source-report copy is a host-only
reference baseline, never a solver input. No invented numeric oracle reward for
free-text diagnosis.

## Preparation artifacts and pending steps

[Authoring scaffold](../../probes/diagnostic-reading/authoring/README.md) provides
a local manifest packer, solver prompt, native CT rendering with a view log, and
mechanical tests. It does not download gated data, certify anonymization or
score diagnoses. The execution harness must still enforce reference isolation.

Pending: user's source preference/access, actual case retrieval and curation,
source/image checks, patient-level freeze, container integration and matched
trials. No model challenge is ready to launch until these are done.
