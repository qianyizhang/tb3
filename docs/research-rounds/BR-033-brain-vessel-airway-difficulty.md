# BR-033 — harder vessel and airway decisions

Captured 2026-09-16. Resumed after the user replied “yes, proceed.”
Status: **airway pilot completed; Terra/high passes its narrow frozen task**.
User review found its two preservation routes were inside detached fragments.
The initial TopBrain download block was subsequently resolved: the
[brain resumption](BR-033-brain-resumption.md) completed five MRA predictions,
but admitted no clean hard task and ran no brain coding-agent trial. See the
[airway execution record and scope correction](BR-033-results.md).

Source: the user's follow-up in the BR-030 vessel conversation:
“whats next difficulty level” and “perhaps brain vessel or lung airway are
more challenging?” The preceding request authorized the completed coronary
experiment. The later “yes, proceed” authorizes this investigation. A separate cardiac task
already owns BR-032. No source-message ID was supplied for this follow-up;
the quotation, date and preceding round preserve available provenance.

[BR-030 results](BR-030-results.md) show why a change of decision is needed:
both image-guided and geometry-only repair/trace baselines pass. Terra's only
failure concerns the CPR distance axis. Additional exports do not establish
anatomical difficulty.

## Initial recommendation and source evidence

Prioritize **named-vessel repair and routing in TopBrain**. Keep **pathological
airway repair in AeroPath** as a complementary candidate. This is a curation
priority, not a measured ranking of model difficulty across organs.

| Source | Available evidence | Candidate and limitation |
| --- | --- | --- |
| [TopBrain paper, May 2026 preprint](https://www.medrxiv.org/content/10.64898/2026.05.28.26354312v1.full), [official data description](https://topbrain2025.grand-challenge.org/data/) | Whole-brain artery and vein labels; 50 public training volumes. The challenge reports smaller vessels and inter-class confusion as remaining problems. Top methods already have near-zero invalid-neighbor counts, so a false connection cannot be assumed to exist in any chosen prediction. | Correct a real local class/connection error, identify the requested vessel and trace its route. Published segmentation results motivate screening; they are not coding-agent failures. |
| [AeroPath paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11446458/), [official repository](https://github.com/raidionics/AeroPath) | 27 contrast-enhanced CTs with airway/lung masks. Manually refined annotations and public inference software. The paper reports difficult connected false positives and pathology-distorted airways, but also valid predicted branches missing from references. | Repair a discontinuity or remove leakage using wall/image evidence; preserve supported abnormal anatomy. Binary masks alone do not supply named bronchi or biopsy-target truth. Exclude unresolved distal annotation disagreements. |
| [ATM26 official repository](https://github.com/EndoluminalSurgicalVision-IMR/Airway-Tree-Modeling-26/blob/master/README.md) | Extends binary airway segmentation to anatomical branch labeling. Registration and a signed Data Usage Agreement are required. | Later candidate for named bronchial routing; access and payload rights remain unverified. Do not treat the new challenge as completed failure evidence. |

The TopBrain paper's 48-class union and modality-specific 40/42-label inventories
are different counts; use the selected release's label map when implementing.
Direct opens of the TopBrain data page and Zenodo record were unsuccessful in
this turn; the official indexed page and paper were readable. Dataset contents,
individual examples, checkpoints and redistribution terms were not inspected.
The AeroPath repository's MIT statement explicitly covers code; do not infer
the dataset's license from it. These are sources for curation, not frozen inputs.

## Proposed next task

Give an angiographic region with enough proximal context to identify its
branches, an unchanged model prediction with anatomical labels, a review region,
and a named target vessel. Ask the agent to:

1. Decide whether the local segmentation needs repair, relabeling or no change.
2. Return the corrected labeled mask and an ordered route to the named target.
3. Produce one inspectable vessel-following view and cross-sections using the
   existing BR-030 geometry conventions. A mesh remains an optional export.

The conceptual crux is choosing the anatomically supported branch when a nearby
continuation is geometrically plausible. Local class confusion, a false join,
and a true variant are candidate mechanisms; no specific case is admitted yet.
Use a proximal anchor if needed, but avoid giving the full route or an endpoint
that makes the anatomical identity task trivial. Retain sufficient context
rather than manufacturing ambiguity through an excessively tight crop.

For the airway counterpart, provide a distal target point on a verified airway
and ask for a route from the trachea after local repair. A target point defines
an engineering endpoint; it does not establish lesion identity or physical
bronchoscope reachability. A suspected real obstruction is a preservation
control only after independent adjudication, never an automatic gap to bridge.

## Admission and evaluation before a model trial

Screen a small set of public predictions, keeping model/version/split provenance.
Aim for six local cases: two real discontinuities, two real false joins or class
confusions, and two intact/variant controls. Availability may change that mix;
do not synthesize errors while calling them natural. Patient separation matters
more than the number of crops. Training cases are development fixtures.

Compare unchanged output, nearest-endpoint/morphological repair, a fixed
image-guided method and its matched image-ablation counterpart. Retain candidates
where ordinary geometry misses a verified decision and an input-legal solution
succeeds. This is a selection screen, not general proof that images are necessary.
Confirm the contrast on separate cases before claiming generalization.

Freeze the case, annotation scope, tolerances and independent verifier before
any coding-agent run. Evaluate target identity, labeled branch adjacency,
route containment and centerline agreement, false added connections, and edits
outside the review region. Score CPR coordinates and metadata separately from
anatomical correctness. Uncertain reference areas need a predeclared exclusion
or adjudication; they cannot become failures after seeing the output.

The proposed ladder is: geometrical gap repair (BR-030 calibration),
image-dependent repair/preservation, then named anatomical routing. Disease
grading or intervention planning requires its own reference data and validation.
No clinical diagnostic claim is established. The later airway trial passes;
its scope and limitations are recorded in [BR-033 results](BR-033-results.md).
