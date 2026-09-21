+++
schema_version = 2
kind = "idea"
id = "ct-organ-segmentation-from-scan"
group_id = "anatomy-audit"
title = "CT-only organ segmentation and semantic identity"
idea_state = "exploring"
source = "codex://threads/01a0c38d-fcff-7670-9ac7-80d0ca352c35"
+++

# CT-only organ segmentation and semantic identity

Can an agent delineate a fixed set of abdominal organs and assign their semantic
identities from CT intensities alone, without receiving masks, case metadata,
reference-derived measurements or a pretrained segmentation model?

## Why this is a new condition

BR-011 I2 asked for identities of 17 already segmented anonymous objects and did
not include CT or run a model. BR-013 through BR-017 supplied source masks and
tested identity, inventory, fragment ownership or annotation auditing; even the
CT-assisted branches did not require new contours. This idea starts from the CT
voxel array. The answer must contain both geometry and correct organ identity.

The first bounded pilot uses ten independently stored source masks: spleen,
right/left kidney, gallbladder, liver, stomach, pancreas, right/left adrenal
gland and duodenum. “Fully labelled” means complete reference files for this
declared taxonomy in the selected field of view, not every visible CT structure.
Colon and small bowel are outside scope because the TotalSegmentator v2 authors
explicitly warn that those source labels can be mixed or poor.

## Reference and case selection

The retained TotalSegmentator v2.0.1 small release is pinned at Zenodo record
10047263. The associated publication reports physician-supervised annotation and
manual review/correction of all examinations. That supports a reviewed research
reference, while the v2 release notes still warn of residual errors; it is not an
independent clinical contour adjudication.

Eight locally retained CT/reference pairs were screened before any solver output.
The first outlier candidate, s0915, was rejected because its 5.8 mL duodenum could
represent incomplete annotation rather than legitimate difficulty. The pilot uses
s1233, a validation-split thorax-abdomen-pelvis scan with all ten target masks
nonempty, internal to the field of view and each one 6-connected. Fresh axial,
coronal and sagittal overlays support the target identities and extents. Fifty-seven
source voxels carry more than one target mask, so the output is ten binary masks;
no arbitrary priority fusion changes the reference.

The case is challenging because pancreas, duodenum and adrenal contours must be
created from a full CT without mask prompts. No unusual anatomy or disease claim
is made. Case identity, source metadata and the selection review stay private.

## Conditions and interpretation

The first condition gives one fresh agent the scrubbed CT, the fixed ten-label
taxonomy and ordinary scientific imaging tools. It excludes pretrained medical
segmenter packages and weights. One Astra/xhigh attempt is bounded to 7,200 agent
seconds, four CPUs, 12 GiB configured memory and no GPU or automatic retry.

A future pretrained-segmenter-assisted condition would be a separate experiment
with exact weights, training-overlap review and tool provenance. Its result must
not be substituted for the standalone agent condition.

Evaluation keeps contour geometry and semantic identity separate: semantic
per-organ Dice, label-agnostic maximum-weight one-to-one organ Dice, the resulting
identity confusion, and foreground precision/recall. Exact oracle and empty/no-op
controls establish endpoints. Kidney-side exchange and cyclic label permutation
preserve geometry while damaging identity; translations and erosions damage
geometry without relabelling. Continuous results have no invented clinical pass
threshold.

## Leakage boundary and reopening

The solver-visible package uses generic filenames and contains only CT plus the
fixed taxonomy and output conventions. It excludes GT, evaluator code, source or
case IDs, pathology and split metadata, source URLs, prior findings, selection
statistics, expected volumes, scoring details and model suggestions. The runtime
blocks dataset hosts and direct egress while allowing only model-service transport;
that does not prove absence from pretraining or eliminate every external channel.

After the bounded pilot, inspect contours and the retained tool trace before making
an anatomical capability claim. Reopen case choice if reference review identifies
a concrete contour defect. Expand to more cases only with a prespecified cohort and
fresh authorization; one selected case cannot establish prevalence or model ranking.

## First pilot result — assistant interpretation, 2026-09-21

[Astra/xhigh completed the CT-only pilot](../findings/ct-organ-segmentation-astra-xhigh.md)
in 21 minutes 4 seconds with ten valid masks. Semantic and matched macro Dice both
equal 0.7380; all ten matched identities agree with the names. This supports
segmentation and naming from CT alone on this case. Contours remain uneven,
especially adrenals (0.3879 right, 0.6070 left), versus liver 0.9269 and spleen
0.9076. The bounded study is complete; no additional model run is implied.
