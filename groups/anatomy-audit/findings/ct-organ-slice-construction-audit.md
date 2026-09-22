# CT segmentation: authored slices, interpolation, tool inference and revisits

2026-09-22 · [Source task](codex://threads/01a0c38d-fcff-7670-9ac7-80d0ca352c35)
· [Original comparison](ct-organ-three-condition-comparison.md)
· [LiteMedSAM condition](ct-organ-segmentation-astra-medium-litemedsam.md)
· [Reproduction](../methods/ct-organ-slice-audit/README.md)
· [Evidence](evidence/ct-organ-slice-construction-audit.json)

The user's proposed split is useful, with one necessary distinction: standalone
runs interpolate **mask geometry**, while LiteMedSAM receives an independently
processed CT image on every scheduled slice, often with an **interpolated box**.
A directly authored polygon is also different from a slice displayed to the agent.
This analysis separates construction, observation, reprocessing and correction.
No inference, pretrained-tool execution, source edit or replacement score occurred.

## Definitions and denominators

- An **organ–slice pair** means one named organ on one native axial plane. Multiple
  organs can share the same plane. All ten GT masks occupy 500 such pairs across
  131 distinct axial planes, within a 401-plane scan.
- The construction denominator includes pairs with **GT or final prediction**,
  excluding both-empty pairs and retaining false-positive planes. It therefore
  differs between conditions (511/524/619/539). Geometry scores use the complete
  original 2D plane, including false positives outside the organ.
- **Authored polygon** means at least one nonempty, explicit polygon for that
  organ at that z. Other components on that plane can still be interpolated.
  Explicit empty end anchors are separate. Between-anchor planes lack a nonempty
  direct contour; final HU/morphology changes do not change their source class.
- **Explicit box / interpolated box** describes prompt construction, not contour
  provenance. Both yield image-conditioned LiteMedSAM masks. Only the eight batches
  read by final assembly define this construction classification.
- A **view revisit** means the same native axial index occurs in more than one
  successful displayed image, including crops and overlays. It does not establish
  attention to every organ, a changed decision, or a new mask. Orthogonal views
  also provide information about axial locations, so no-direct-axial-view is not
  equivalent to unseen anatomy.

## How much was directly specified?

| Condition | Nonempty explicit polygon or box | Interpolated shape or box | Other construction | Outside construction extent |
|---|---:|---:|---:|---:|
| Astra/xhigh, 511 pairs | 116, **22.7%** | 376, **73.6%** | 8 empty end anchors, 1.6% | 11, 2.2% |
| Astra/medium, 524 pairs | 131, **25.0%** | 383, **73.1%** | None | 10, 1.9% |
| Sol/xhigh, 619 pairs | 69, **11.1%** | 412, **66.6%** | 76 duodenum ellipsoid planes, 12.3% | 62, 10.0% |
| Astra/medium + LiteMedSAM, 539 pairs | 119 explicit boxes, **22.1%** | 398 interpolated boxes, **73.8%** | Per-slice learned inference in both groups | 22, 4.1% |

![Construction coverage](../../../.local/ct-organ-slice-audit/report/construction-coverage.png)

Blue is an authored polygon; pale blue is interpolated shape. Green is an explicit
box followed by LiteMedSAM; pale green is an interpolated box followed by LiteMedSAM.
Amber marks empty end anchors, purple parametric ellipsoids, and red outside extent.
The legend uses matching filled swatches. These are plane-level provenance classes,
not a voxel attribution or a count of independent observations.

“Simply interpolated” would overstate the final mask's independence from CT or
cleanup. Only **70/376 (18.6%)** of xhigh's interpolated planes and **77/383 (20.1%)**
of medium's are voxel-identical before and after post-processing. These represent
13.7% and 14.7% of their entire active-pair denominators. Sol has 46/412 (11.2%)
unchanged interpolated planes. A changed plane may differ by very few voxels;
this is not proof of meaningful boundary correction.

## Is directly authored geometry better?

For each organ and stratum, compute Dice using all voxels in that stratum, then
average equally over organs. These are diagnostic conditional scores, not changes
to the original 3D score. Outside-extent misses and explicit empty boundaries stay
visible in the coverage table rather than being assigned to nonempty anchors.

| Condition | Final Dice on its nonempty anchor planes | Final Dice between its anchors |
|---|---:|---:|
| Astra/xhigh | 0.737 | 0.746 |
| Astra/medium | 0.727 | 0.739 |
| Sol/xhigh, nine polygon organs | 0.361 | 0.373 |
| Astra/medium + LiteMedSAM | 0.762 | 0.768 |

There is **no overall anchor advantage here**. This does not show that interpolation
improves cognition: anchors are selected by the agent, often at difficult endpoints,
and organs contribute differently to each conditional score. Restricting to planes
where GT area is at least 25% of that organ's maximum narrows medium's pooled
anchor/between gap to 0.895/0.900. It does not establish equality, independence or
causality. The retained distance-to-anchor bins do not show a uniform monotonic
accuracy decline with greater spacing on this one case.

Several failures already exist at the explicitly drawn coordinates. Medium's right
adrenal scores **0.301 at anchors / 0.315 between**; its stomach 0.634/0.673. Sol's
pancreas is **0.038/0.037**, and left adrenal **0/0**. Interpolation cannot be the
sole explanation for those errors. The kidneys remain much stronger at both kinds
of planes. Full per-organ/stratum measurements are retained in the evidence.

## What changes when the tool is used?

Comparing each condition's own anchors mixes different slice selections. A second
comparison therefore fixes the **baseline medium slice sets**, restricts to GT-present
pairs, and evaluates both unchanged predictions on exactly those planes:

| Shared baseline-defined set | Pairs | Baseline macro over ten organs | Tool macro over ten organs | Baseline pooled Dice | Tool pooled Dice |
|---|---:|---:|---:|---:|---:|
| Baseline authored anchors | 119 | **0.735** | **0.750** | 0.886 | 0.916 |
| Baseline between-anchor planes | 372 | **0.742** | **0.772** | 0.895 | 0.925 |

The tool improves both groups, with a larger organ-balanced gain between anchors
(+0.030 versus +0.015). There are also nine GT-present baseline outside-extent pairs,
retained separately. Fixing planes removes this selection difference; it does not
control agent stochasticity, different prompts, actual effort or the skill/runtime
intervention. Pooled Dice emphasizes large structures; the macro columns prevent
liver/kidney gains from hiding small-organ regressions.

![Matched-plane quality](../../../.local/ct-organ-slice-audit/report/matched-plane-quality.png)

Blue dots are standalone medium and orange dots the tool condition. Gray lines join
scores on the same organ/slice subset. Gallbladder, pancreas and right adrenal
worsen on both baseline-defined sets. The original final scores remain 0.73419 and
0.75697; these conditional scores are not replacements.

Tool work comprises 662 saved batch box predictions over **553 distinct organ–slice
pairs**. There are **136 distinct explicit anchor pairs** across the final batch
prompt schedules, 24.6% of those 553 processed pairs; remaining scheduled prompts
are interpolated. Among these pairs, **61/553 (11.0%)** were processed in more than
one batch, including exploratory tests. The eight final-assembly batches contain
628 masks; **36/553 (6.5%)** pairs receive candidates from more than one of those
batches. Multiple boxes for different duodenum parts within one batch are not
counted as a temporal revisit. Final assembly unions candidates, so an additional
call need not replace a bad earlier result. Eight additional canonical-adapter
exploratory masks lack explicit organ IDs in their box records and are excluded
from these organ-pair revisit counts, but retained in the earlier total of 670.

The final masks are not pure LiteMedSAM outputs. With the final selected candidates
held fixed, raw candidate unions have macro Dice **0.71869**, versus **0.75697** after
agent-programmed trimming, HU filters, filling, smoothing and component selection.
For context, independently reconstructed pre-refinement geometry → final Dice is
0.71414→0.73803 for xhigh, 0.68582→0.73419 for medium, and 0.25210→0.32907 for Sol.
These are numerical stage diagnostics with final decisions held fixed, not
chronological learning curves or isolated causal effects of individual operations.

## Observation, revision and reprocessing are different

| Condition | Successful displayed images | Distinct axial planes displayed, whole scan | Displayed among 131 GT-containing planes | Revisited among those displayed GT planes |
|---|---:|---:|---:|---:|
| Astra/xhigh | 37 | 62/401, 15.5% | 56/131, 42.7% | 46/56, 82.1% |
| Astra/medium | 43 | 56/401, 14.0% | 54/131, 41.2% | 26/54, 48.1% |
| Sol/xhigh | 29 | 45/401, 11.2% | 26/131, 19.8% | 26/26, 100% |
| Astra/medium + LiteMedSAM | 36 | 69/401, 17.2% | 56/131, 42.7% | 32/56, 57.1% |

These are **slice display statistics**, not percent of anatomy understood. A montage
can show many planes, a crop may omit an organ, and coronal/sagittal images provide
additional cross-plane information. There are respectively 13/8/10/3 successful
non-axial displays. Tool calls requested 39 image views, but three failed before an
image was observed; the earlier report's 39 was a request count.

Even explicit authoring does not imply a direct axial display at that exact index:
105/117 xhigh anchors, 119/137 medium anchors, 51/73 Sol anchors and 123/136 tool
anchors share z with some successful displayed axial image. These are permissive
upper bounds on directly seen organ anchors because crops are not organ-complete.
Counts include anchors outside the final active support, unlike the first table.
No inference about hidden mental interpolation is made from this correspondence.

A stronger correction diagnostic is available for saved polygons. Comparing first
and final coordinates on **identically indexed revised anchors**, before numerical
cleanup:

- Xhigh changed 14 existing polygon anchors across liver, stomach and both adrenals;
  pooled Dice on those planes improves **0.653→0.851**. Liver contributes strongly;
  right-adrenal improvement is **0.231→0.355**, still poor. Nine additional anchor
  positions (including empty endpoints) and three removed positions are separate.
- Sol changed 18 existing anchors: spleen and both adrenals. Their pooled Dice
  improves **0.325→0.400**, but right-adrenal redraws worsen **0.128→0.097**.
  Seven stomach anchors were replaced with different slice indices and are excluded
  from this matched-index comparison.
- Medium's later changes modify the shared mask-building algorithm rather than
  rewriting its saved contour JSON. There are four post-initial rebuild revisions.
  It would be misleading to count every plane touched by those programs as a
  separately reconsidered or redrawn anatomical decision.

These are net first-to-final contour comparisons on self-selected revised planes;
transient reverted edits and revisions on different indices are not scored here.
There was no GT feedback to the solver. Positive deltas support some observable
self-correction on this case, not a generally reliable correction policy.

## Better decomposition of observable capability

Use five axes instead of a single “true segmentation ability” number:

1. **Localization and identity:** correct organ, side and superior/inferior extent.
   Evaluate missed extent and spatial prompt coverage separately from contour Dice.
2. **Direct delineation:** polygon quality on authored planes, before cleanup;
   separate this from semantic naming and geometrically valid file writing.
3. **Spatial completion:** geometry between anchors, conditional on anchor quality,
   spacing and cross-section size. The present split cannot isolate it causally.
4. **Review and correction:** successful displays, coordinate changes, whole-program
   changes, reprocessing and measured first-to-final improvement are different events.
5. **Tool orchestration:** prompt placement, coverage, error recognition, candidate
   selection and post-processing belong to the agent; learned image-to-contour
   prediction belongs to LiteMedSAM. Their combined final mask measures the system.

A useful future controlled test would fix a blinded image-derived anchor/prompt
budget and compare dense direct authoring, interpolation from those anchors and
learned segmentation on the same planes. Add a no-revision condition and score
revisions with unchanged GT withheld throughout. Use multiple cases and repeats,
with small-structure and endpoint strata chosen before seeing outputs. No further
trial is authorized or launched by this recommendation.

## Verification and limits

The analyzer statically reads literal coordinates and tool provenance; it never
imports or executes solver scripts. All 40 final whole-organ Dice values match
original verifier values to 1e-12; the ten xhigh raw-stage scores also match the
previous independent reconstruction to 1e-12. Inputs are hashed before/after.
All successful image observations have a source-linked plane mapping. Original
files, task digests and result scores remain unchanged. Rendering uses saved
statistics; output goes to a fresh local directory.

One selected public case and one attempt per condition cannot identify intrinsic
model capacity or establish a population ranking. Slice pairs are correlated and
not 500 independent cases; no significance tests or confidence intervals are
invented. Reference anatomy remains research GT rather than a new clinical
adjudication. Unknown training overlap and the combined skill/tool intervention
remain limitations inherited from the completed experiment.
