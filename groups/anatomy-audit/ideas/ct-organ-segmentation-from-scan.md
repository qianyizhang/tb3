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

## Method analysis and comparison authorization — 2026-09-21

The user subsequently requested a trace explanation and two fresh conditions:
Sol/xhigh and Astra/medium. This explicitly opens the
[fixed three-condition comparison](../methods/ct-organ-three-condition-comparison/protocol.md),
using the original frozen task, unchanged reference and scorer, sequential runs,
the same per-attempt limits and no feedback or prior solution supplied to solvers.
The prior Astra/xhigh result remains frozen. One case and one attempt per condition
will support a descriptive comparison rather than a general model ranking.

[Assistant methodology analysis](../findings/ct-organ-methodology-astra-xhigh.md)
reconstructed all ten original masks voxel-exactly. The dominant construction is
visually drawn sparse polygons plus signed-distance interpolation. Hole filling
and component cleanup were used, but systematic CT-edge fitting was absent.
With final polygons held fixed, reconstructed macro Dice is 0.71414 before cleanup,
0.71430 after smoothing, 0.73624 after HU trimming/hole filling, and 0.73803 final.
These are post-hoc numerical stages, not a chronological reasoning trajectory.

## Three-condition finding — assistant interpretation, 2026-09-21

The [authorized comparison is complete](../findings/ct-organ-three-condition-comparison.md).
All three fresh attempts completed normally; independent replay matches each
original verifier output exactly. Semantic macro Dice is 0.73803 Astra/xhigh,
0.73419 Astra/medium and 0.32907 Sol/xhigh. Both Astra runs preserve ten matched
identities, with persistent adrenal contour weaknesses. Sol has major central-
organ localization errors; optimal relabeling only raises its score to 0.34878.
Medium improves spleen, kidneys and gallbladder but worsens the other six organs;
the nearly equal mean does not establish effort equivalence or a stable ranking.

All three use visual polygons and shape interpolation, with morphology/intensity
cleanup. Sol's duodenum instead uses manually placed ellipsoids with no intensity
constraint. Structural validity and connected masks did not ensure localization.
The two new runs received no earlier answer, analysis or reference information.
No further cases, repetitions, retries or model dispatch are authorized here.

## Tool-enabled follow-up authorized — user, 2026-09-21

After the completed three-condition comparison, the user requested one fresh
Astra/medium attempt with the LiteMedSAM skill enabled, citing the
[tool calibration task](codex://threads/01a0c423-5d0a-7ee3-97b4-66939a8c9e20).
The [separate experiment](../experiments/ct-organ-segmentation-astra-medium-litemedsam/protocol.md)
holds CT, taxonomy, reference and scoring fixed while adding the canonical skill
and a pinned CPU segmenter. All agent prompts must come from CT inspection;
calibration reference boxes, selected slices and prior answers stay private.
Original freezes and results remain unchanged. This opens only one bounded new
attempt, not a general benchmark campaign. Interpretation must separate actual
tool use, localization/identity and contour changes, and retain the unknown
training-overlap and single-case limitations.

## Tool-enabled result — assistant interpretation, 2026-09-21 UTC

The [authorized LiteMedSAM condition](../findings/ct-organ-segmentation-astra-medium-litemedsam.md)
completed normally in 17m 28s. Independent replay confirms macro Dice 0.75697
versus 0.73419 for standalone Astra/medium; seven organs improve and three worsen.
The agent actively used the skill and made 670 box-mask predictions through the
canonical adapter and a CPU batch adaptation. Stomach/kidneys improved, while
gallbladder/pancreas/right adrenal regressed. Post-hoc prompt coverage identifies
incomplete localization, especially right adrenal; morphology still appears in
final cleanup and does not guarantee aligned boundaries. This supports an
organ-dependent benefit in one composite tool/skill condition, not a general
causal advantage. The original three runs and all scores remain frozen. The
one authorized follow-up is complete; no additional trial is implied.
