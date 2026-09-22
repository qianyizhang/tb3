# Comprehensive longitudinal tumor-candidate curation

Selected by the user in decision `decision-4d11c9538adb4521`, from
codex://threads/01a0c4d1-741f-76e3-9023-1064e5a9a0c5. One fresh Astra-medium
attempt on the same case02 pair. This is an exploratory prompt intervention,
not qualification or a population estimate. No feedback, retries or adaptation
of the instructions after dispatch.

## Fixed and changed conditions

Clone the verified context-supplied freeze
`ffdf321ba2637b46484309d8ec2c39fdffd5234b99e3152842c245a25a149215`.
Hold both CT voxel arrays/geometry, clean filenames, solver image, tools, model,
reasoning effort, two-hour ceiling, hardware caps, context block and private GT
fixed. Preserve the scientific scorer byte for byte. Use a fresh agent session;
never supply previous outputs, selected views, locations, counts or event mix.

Replace the previous more-likely-tumor-than-benign inclusion rule with all
plausible tumor candidates, explicitly including every size, indeterminate and
benign-favored-but-still-plausible findings. Add the directional purpose of a
comprehensive oncologic-review inventory. Ask for systematic full-volume review
with appropriate windows and separate confidence from inclusion. Keep touching
lesions distinguishable when images permit and allow unresolved correspondence.
Add a per-instance probability/reason sidecar so broader retrieval is observable.

These are bundled changes. Compare scientific endpoints as **endpoint_only**;
the question is whether this fresh combined condition recovers additional GT
lesions, not whether the goal wording alone caused any change. Compare primarily
to context-supplied `attempt-81ee755346d04be7`; retain image-only
`attempt-92800845745342f4` as historical context. One run cannot separate prompt
effects from stochastic variation.

## Reference policy and interpretation

The [paper](https://www.nature.com/articles/s41597-026-07466-y), reviewed live
2026-09-22, describes exhaustive annotation of lesions deemed malignant,
regardless of size; RECIST target labels are separate. The release also reports
use of clinical reports. Broad plausible-candidate curation is intentionally
wider than this malignant reference. Unmatched candidates are reference-negative
outputs, not adjudicated clinically false findings. Clinical reports and
independent malignancy adjudication remain unavailable.

## Predeclared outputs and evaluation

The original native-grid instance masks, correspondence/event JSON and report
remain required. `candidates.json` covers every mask ID exactly once, with
`p_tumor` in [0,1] and a brief reason. This is subjective malignancy confidence,
not a calibrated clinical probability. Zero candidates is structurally allowed.

Primary scientific metrics use **all retained candidates**, unchanged GT and
the frozen original scorer: strict centroid/3 mm one-to-one localization,
foreground Dice, GT macro best one-to-one Dice, <=1 / >1–10 / >10 mL reference
strata, end-to-end links/events and detection-conditional association. Report
unmatched candidate counts alongside TP/FN; do not mistake permissive inclusion
for greater diagnostic specificity. Preserve original metric definitions and
their differing detection versus overlap matching rules.

A predeclared secondary subset retains candidates with `p_tumor >= 0.5` and
recomputes localization and mask metrics with the same visit scorer. This
separates candidate retrieval from the agent's probable-tumor assessment.
Do not filter/reinterpret event groups to fabricate new/disappeared events;
all association metrics concern the full candidate inventory. Do not assess
probability calibration as clinical truth. Missing/invalid sidecar is a contract
failure; retain the independently evaluable original scientific endpoints.

A private wrapper checks the extra contract and subset; the scientific
`score.py` remains byte-identical. Oracle copies GT plus mechanical probabilities
of 1; nop supplies nothing. Both controls, data/network preflight, current ordinary
quota, frozen task digest and live isolation receipt precede/cover the one run.
Reward denotes output contract only. Independently replay saved outputs and
audit completion, input isolation, actual render/inspection and inclusion policy.
Native CT/GT/prediction panels are author-side post-run evidence only. Preserve
uncertainty: a missed GT target is not automatically search, recognition or a
clinical diagnostic error without supporting trace/coverage evidence.
