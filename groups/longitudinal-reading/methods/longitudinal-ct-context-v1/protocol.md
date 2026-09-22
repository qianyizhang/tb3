# Clinical-context hypothesis on the second CT case

User-selected, 2026-09-22, decision `decision-0025c01d8f434bf6`:
[source task](codex://threads/01a0c4d1-741f-76e3-9023-1064e5a9a0c5).
The hypothesis is that missing major clinical context contributed to earlier
recognition/inclusion failures. Use the latest selected case, with two independent
fresh Astra-medium sessions. No prior outputs or trace feedback enter either.

## Conditions fixed before inference

1. **Context inference:** same two deidentified whole CTs and headers; a narrow
   structured task asks what broad/specific diagnosis, demographics, interval,
   scan purposes, systemic treatment and surgical context are supportable.
   It explicitly permits unknowns and requests evidence/confidence/alternatives.
   No supplied diagnosis, dates, masks, locations, counts or source identity.
2. **Context supplied:** same CTs, instance segmentation/link/event contract,
   scientific scorer, private GT, runtime and ceilings as the completed case02
   image-only baseline (`attempt-92800845745342f4`). Add only the frozen
   [context block](context-block.md); change “image-based judgment” to judgment
   based on images and supplied broad context. All other instructions remain
   unchanged. The context-inference output is not passed to this session.

The supplied block contains patient-specific released age 44, recorded sex female
and interval 121 days; cohort-level metastatic malignant melanoma, systemic
therapy and staging/therapy-response assessment. Cohort facts are explicitly
distinguished from an individual clinical record. No regimen, surgery timing or
individual examination report is available. Do not invent these. No patient ID,
source dataset name, anatomical distribution, lesion descriptions, count, points,
masks, growth, response, correspondence or event facts are provided.

Broad diagnosis intentionally changes the clinical prior; it is not free of
information relevant to recognition. The exclusion boundary is direct target
information. This is a partial-context test, not restoration of all information
available to the annotators, who used clinical reports.

## Execution and controls

One fresh `openai/gpt-6-astra` / `medium` attempt per condition, sequentially,
two-hour ceilings, unchanged 4 CPU/12 GiB solver configuration and pinned image.
Reusing the exact case02 data image ensures the CTs and installed tools match.
The context-supplied condition reuses the exact private case02 evaluator. The
context-inference evaluator checks only the output schema and report presence.
New native oracle/no-op controls must pass/fail respectively on each fresh digest.
Keep instruction hashes, input hashes, exact image identities, quota clearance,
live isolation, complete outputs and traces. No automatic retry, continuation,
extra model installation, reset credit or additional model condition.

## Predeclared interpretation

Context inference: report field-by-field what was observed/inferred/unknown,
agreement with released metadata, and whether the evidence supports the claim.
Exact age, recorded sex, 121-day interval, histology, regimen and surgical history
are not assumed identifiable from CT appearance. Correct abstention is not a
failure. A coincidentally correct value is not proof of inference. Source cohort
diagnosis supports a private reference, not image-only identifiability. Patient
clinical records are absent, so some claims cannot be adjudicated. Schema reward
does not measure diagnostic correctness, and confidence calibration cannot be
estimated statistically from one patient.

Context-supplied rerun: independently replay the unchanged scorer. Report strict
localization TP/FP/FN; per-visit foreground Dice; equal-GT-instance macro Dice;
matched overlap; end-to-end and endpoint-conditional links and exact events.
Retain case02 size strata <=1 mL, >1–10 mL, >10 mL and all 22 GT instances.
Review whether the prior explicit vessel exclusion at follow-up native
(190,235,536), inside GT14, is now accepted, rejected or not explicitly discussed.
This coordinate/reference is author-only and never supplied to the solver.
Compare methods, whole-volume inspection, inclusion policy, false positives and
mask construction. Do not treat better foreground Dice alone as better detection.

A single fresh rerun confounds context with run-to-run variation and bundles
multiple context fields. Improvement would support the hypothesis, not prove
causality or identify which field helped. No improvement would not rule out
effects of the unavailable individual clinical report. Failure to guess context
from deidentified CT is different from failure to use context when supplied.
Retain source-agreement wording; no clinical adjudication or population claim.
