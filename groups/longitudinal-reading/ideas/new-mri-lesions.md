+++
schema_version = 2
kind = "idea"
id = "new-mri-lesions"
group_id = "longitudinal-reading"
title = "Find new lesions between brain MRIs"
next_action = "Assistant ranks this strongest for a new domain, conditional on official access, use terms and revised/adjudicated masks."
source = "codex://threads/01a0bde4-e30d-71c3-8ae4-19d377aee51d"
decision_provenance = "Assistant proposal; user requested explanation, not trial selection."
historical_ids = [
    "BR-043-C02",
]
idea_state = "exploring"

[[links]]
label = "Proposal and visual explanation links"
path = "docs/research-rounds/BR-043-medical-next-tasks.md"
+++

# Find new lesions between brain MRIs

## Question

Find new lesions between brain MRIs

## Prior findings

Paired FLAIR can isolate new lesions from existing lesions, registration error and intensity change. The BR-043 source screen notes revised MSSEG-2 references and expert disagreement; local agent difficulty is untested.

## Reopen when

Assistant ranks this strongest for a new domain, conditional on official access, use terms and revised/adjudicated masks.

## Image reasoning source screen — 2026-09-21

Actor: assistant. Source: [current task](codex://threads/01a0c4ad-5c0e-77d0-8589-320b19bbff1d).
The user requested proposed medical tasks and data/GT for testing reasoning with
images. This is a recommendation, not a user selection or trial authorization.

Define the target behavior as connecting evidence across slices, sequences or
time, selecting useful views and returning image-grounded conclusions. A fluent
explanation or correct patient diagnosis alone does not validate that behavior.

**Recommended first task:** compare baseline/follow-up FLAIR and localize genuinely
new lesions. Use lesion-level sensitivity, false positives per case and correct
no-new-lesion decisions; assess mask overlap separately if segmentation is asked.
Existing-lesion enlargement is outside this endpoint. Start with a small balanced
diagnostic pilot, for example six positive and six no-new-lesion pairs, selected
and reviewed before model outcomes; do not interpret that sample as prevalence
or population performance.

- **MSSEG-2 source and GT:** 100 paired FLAIR cases, historically split 40/60,
  with four-reader annotations and senior-adjudicated consensus described by
  [challenge participants](https://pmc.ncbi.nlm.nih.gov/articles/PMC9412001/).
  The [2026 organizer analysis](https://www.nature.com/articles/s41598-026-52150-1)
  reports 81 additional test lesions accepted after methods exposed initial
  omissions. Pin the reference revision and retain disagreement for adjudication.
  The [official data portal](https://portal.fli-iam.irisa.fr/msseg-2/data/)
  remains blocked to the research browser by robots.txt; current download access,
  use terms and revised-mask availability were not verified.
- **Temporal correspondence alternative:** [Deep Longitudinal Study / DLT](https://github.com/JimmyCai91/DLT)
  provides 3,891 lesion pairs with source/target boxes, centers, RECIST marks,
  diameters and spacing. Give a baseline target and ask for its follow-up match
  despite changed appearance/position. Score matching and physical localization;
  measurement is a separate endpoint. Images are DeepLesion CT subvolumes and
  annotations cover selected targets: this is not exhaustive detection, proof
  of disappearance, or a complete patient-level response assessment. Affine
  predicted target fields are assistance and must be withheld or declared.
- **Spatial topology alternative:** the [TopCoW release](https://zenodo.org/records/15692630)
  includes CTA/MRA, labeled vessel masks and explicit graph-edge presence YML.
  Ask which communicating connections exist, with image evidence; score graph
  edges and vessel identity separately from segmentation. Review ambiguous
  small vessels. The training release requires attribution and owner permission
  for commercial use; external sets have separate terms. The
  [previous repair pilot](../../tubular-anatomy/ideas/idea-vessel-connectivity-repair.md)
  is not evidence that this proposed graph-reading task is difficult.
- **Anatomical numbering alternative:** [VerSe](https://github.com/anjany/verse)
  releases CT, named vertebral masks and centroids under CC BY-SA 4.0, including
  variant labels such as T13/L6. Select cases with visible counting anchors;
  score localization and numbering separately. See the
  [existing idea](../../anatomical-landmarks/ideas/variant-vertebral-numbering.md).
- **Clinical cross-sequence extension:** [PI-CAI images](https://zenodo.org/records/6624726)
  contain 1,500 prostate MRI exams. T2W, ADC and high-b-value DWI enable a
  localized suspicion task. The [label repository](https://github.com/DIAGNijmegen/picai_labels)
  now combines original human labels and Pooch25 additions; AI-derived masks
  are separately marked. Positive csPCa status is histologically confirmed;
  public-set negatives can be histology- or MRI-defined without follow-up.
  These labels do not grade an explanatory rationale. The current repository
  warns against using this convenience sample to benchmark AI systems: retain
  it as exploratory case material, with independent evaluation data needed for
  a formal clinical benchmark. Public data are CC BY-NC 4.0.

For a reasoning-focused condition, allow common viewing/registration tools and
accept coordinates or bounded regions instead of requiring dense masks. Compare
the full-image condition with a relevant missing-context condition and a fixed
pipeline using the same allowed tools. For MSSEG-2, use follow-up-only and
registration/subtraction controls; an unchanged-pair control is calibration,
not a substitute for real no-new-lesion patients. Require short image-cited
evidence, not a narrated private reasoning trace. Hide GT, diagnostic reports,
source identifiers and label-bearing metadata; preserve sequence/geometry/time
information needed to solve the task. Public-data training exposure remains a
limitation even after local leakage controls.

Next decision remains source access and reference feasibility, then task family
selection. No scans were downloaded, no new fixtures frozen and no model trials
launched in this source screen.
