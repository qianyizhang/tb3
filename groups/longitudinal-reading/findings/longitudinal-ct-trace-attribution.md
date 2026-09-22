# Why the image-only CT attempts fell short

2026-09-22 · [User request](codex://threads/01a0c4d1-741f-76e3-9023-1064e5a9a0c5)
· [Frozen comparison](longitudinal-ct-image-only-comparison.md)
· [Trace excerpts, source hashes and measurements](evidence/longitudinal-ct-trace-attribution.json)

The mechanisms differ. Astra recognized the dominant abnormal region and built
useful masks, but combined baseline instances, missed a separate reference focus,
and approximated boundaries. Sol spent longer inspecting and rejecting candidates,
then deliberately submitted no lesions. Its principal failure was upstream of
segmentation and linking: anatomical interpretation and lesion acceptance.
The instruction's confluence rule plausibly contributed to Astra's partition;
it cannot explain Sol's empty masks or either model's omission of the separate focus.

These are evidence-based attributions of one attempt each, not percentages of
causal responsibility or a general model ranking. No prompt ablation, expert
blind reader comparison or additional inference was performed. This review uses
observable messages, tool calls, saved scripts, rendered images and final artifacts.
Statements by the models are evidence of their stated decisions, not proof those
decisions were anatomically correct. Frozen task bytes, GT and scores are unchanged.

## Reconstructed methodologies

### Astra medium: recognize, contour, refine, link

1. **Survey and select.** Loaded geometry and CT values; created coarse full-volume
   axial sheets, then denser odd/even axial atlases, lung-window views and targeted
   abdominal reformats. At 00:18:40 UTC, step 12, it identified an abnormal region
   around the abdominal aorta. The dense atlases cover the missed reference focus's
   native coordinates; that target was not absent from the rendered field.
2. **Commit to one abdominal instance.** At 00:20:07, step 17, it said the region
   appeared confluent and would treat the connected portions as one instance per
   visit. This predates contour construction and the private author review. At
   00:22:28, step 26, it reported no other definite tumor and excluded thyroid
   nodularity. The wording does not identify the exact source lymph-node target,
   so calling this a proven thyroid-versus-node confusion would overstate the trace.
3. **Construct native masks.** Wrote polygon control points on 23 baseline and
   24 follow-up planes, interpolated signed-distance fields, and smoothed them.
   It then clipped lateral boundaries; excluded seeded bright aortic components,
   low-HU fat/gas and high-HU tissue; and retained the largest connected component.
   The final contour ranges are baseline k=82–125 and follow-up k=86–131. The
   separate GT focus lies outside both ranges and was never a candidate for this
   segmentation code. Largest-component filtering did not remove that focus.
4. **Refine and associate.** Inspected overlays and corrected vessel centers and
   lateral contours. It linked the two regions by their relationships to the aorta,
   vena cava, vertebrae and renal vessels, producing one persistent group. It used
   anatomy rather than a fitted image registration. Native geometry and JSON ID
   checks passed. It stopped after about 17 minutes of a two-hour allowance.

The final baseline mask includes most voxels of all three abdominal reference
instances, even though one-to-one localization can assign it to only one of them:

| Reference instance | Reference volume | Fraction covered by Astra's final mask |
| --- | ---: | ---: |
| Baseline 1 | 18.16 mL | 73.1% |
| Baseline 2 | 1.21 mL | 99.8% |
| Baseline 4 | 49.65 mL | 93.3% |
| Baseline 3, separate focus | 5.41 mL | 0% |
| Follow-up 4 | 116.90 mL | 93.7% |
| Follow-up 3, separate focus | 7.41 mL | 0% |

Coverage is voxel recall, not Dice, and does not penalize excess tissue. It is a
post-hoc diagnostic, not a replacement detection score. Two of the four scored
instance false negatives reflect under-separation within the covered abdominal
region; the other two are an omitted reference focus at both visits. Thus
“localized 2/6 instances” must not be paraphrased as “never saw four lesions.”

The ordered reconstruction of Astra's saved algorithm shows that refinement
improved union overlap overall: baseline Dice rises from 0.586 after polygon
interpolation to the final 0.685. The lateral, aortic and intensity exclusions
remove 17,575 non-GT voxels and 1,218 GT voxels; largest-component filtering removes
another 51 non-GT voxels and zero GT voxels. Its remaining excess tissue mostly
comes from the initial contour extent, not a catastrophic cleanup operation.
This describes operations relative to GT; it does not clinically adjudicate every
removed voxel. Follow-up stages show the same overall improvement (approximately
0.666 to 0.779), with a one-voxel reconstruction discrepancy documented below.

### Sol xhigh: generate views, pursue candidates, reject, abstain

1. **Survey and pair by coordinates.** Created native soft-tissue/lung views and
   axial pairs at equal RAS world Z, plus coronal and sagittal sheets. At 00:42:07,
   step 24, it called a breast-region structure a dominant suspicious finding and
   said it had not found a convincing abdominal/pelvic tumor.
2. **Concentrate on alternative candidates.** Spent many subsequent calls on
   breast/axillary structures and a right basal thoracic contour, using ROI crops,
   HU probes, component thresholds, opposite-side comparisons and orthogonal
   views. It created threshold-grown breast candidate masks (>20 HU, seeded
   components, closing and hole filling). A below-threshold seed problem was
   corrected. Both retained candidate masks have **zero overlap with GT**.
   Restoring them would therefore not rescue true-lesion detection on this pair.
3. **Add coordinate-based fusion.** Step 58 resampled follow-up onto the baseline
   grid using NIfTI affines, with no image-estimated transform. Step 68 printed
   slice-wise phase-correlation shifts; no later application of those shifts or
   fitted three-dimensional registration is evident in the saved calls/scripts.
   Equal scanner coordinates are not proof of anatomical alignment across visits.
4. **Inspect relevant regions but reject the findings.** Later calls include
   native abdominal grids (step 101), dense adrenal/abdominal ROIs (105), and
   dense neck sheets (107) containing the reference target coordinates. At
   01:14:50, step 111, it rejected the candidates as normal structures and chose
   zero instances. Its final report explicitly says it favored specificity and
   that negative annotation does not establish clinical absence of malignancy.
5. **Validate an intentional empty output.** Wrote zero masks and `groups: []`,
   passed shape/affine/type/ID checks, and finished after about 41 minutes. This
   is not a failure to save files, a timeout, or an unsuccessful segmentation
   program that happened to produce empty arrays.

Sol's final report claims no abdominal nodal mass even though its saved native
views include the region Astra localized. This supports a recognition/acceptance
failure relative to GT, rather than a pure mask-generation or correspondence
failure. Repeated visualization did not produce a reliable lesion inventory.
Its rejection of non-GT candidates may have prevented false positives, but that
does not compensate for failing to accept the actual reference regions.

![Scanner coordinates do not establish correspondence](../../../.local/longitudinal-ct-image-only-v1/trace-analysis/scanner-coordinate-mismatch.png)

The persistent GT-3 centroid differs by **29.5 mm in world Z** between visits.
At the baseline target's maximal-area plane k=213, matching scanner Z selects
follow-up k≈206; the follow-up target's maximal-area plane is k=216. The figure is
GT-selected after the attempts; neither solver saw its overlays. This displacement
includes anatomy, positioning and shape change, and is not a measured registration
error. It demonstrates why scanner-Z pairing alone cannot synchronize this focus.
It is a plausible impediment to Sol's comparisons, not a sufficient explanation
for its misses: it also had independent native views with the targets present.

## Attribution by failure, not by overall score

| Failure | Strongest supported mechanism | Instruction contribution | What remains uncertain |
| --- | --- | --- | --- |
| Astra abdominal instance count and merge event | Early deliberate connected-region grouping, then one mask ID per visit | Plausible and directly relevant: prompt says a confluent region is one instance; report equates connection with one instance | Whether expert readers would distinguish all baseline lesions under a clarified image-only convention; wording's causal effect requires a new controlled trial |
| Astra missed separate focus | Lesion recognition/inclusion or search follow-through; source focus is rendered but never segmented | “Tumor” inclusion threshold is unspecified; no evidence the confluence rule affects this target | Exact anatomy it assigned to this focus; whether a native interactive crop or clinical context would change its judgment |
| Astra boundary disagreement | Hand-specified contours/interpolation around adjacent structures; both excess and missing voxels | No concrete misleading boundary instruction found | Expert adjudication of disputed margins; contribution of slice thickness versus model contour skill |
| Sol zero detection | Wrong candidate priorities followed by conservative lesion acceptance; no correct candidate mask | Unspecified uncertainty/false-positive operating point may encourage over-abstention; confluence cannot explain emptiness | Relative contributions of visual recognition, anatomy knowledge, view design and lack of clinical context |
| Sol comparison difficulty | Scanner-affine resampling without established anatomy registration | No instruction required using scanner coordinates as correspondence; this is a method choice | Causal impact on final detection; native review should still have allowed recognition |
| Low link/event scores | Missing or over-combined lesion endpoints upstream | Instance convention changes what event can be represented | Standalone correspondence capability is not identified: Astra recovered its 1/1 eligible edge; neither had a complete eligible GT event group |

The shared sample is genuinely demanding in the operational sense: full-volume
search, malignancy-versus-normal judgment, six volumetric instance annotations
across two visits, nonuniform anatomy/positioning, and touching baseline labels.
It is not defensible to explain everything as imperceptibly small lesions: the
reference abdominal burden is substantial and Astra recognized it. Nor do these
observations establish that this patient is unusually hard for expert readers.

The [dataset paper](https://www.nature.com/articles/s41597-026-07466-y) describes
exhaustive annotation of lesions experts deemed malignant, without a minimum-size
cutoff, followed by consensus review. Its annotator interface used deformable
registration for synchronized review. These source facts help explain the
difference between reproducing expert annotations and blind image-only discovery;
they do not prove that extra clinical evidence was used for this particular label.
The paper's nnU-Net usability baseline also reports imperfect detection/segmentation,
but its different population, training and scoring make it unsuitable for ranking
these two attempts. No such cross-study numerical comparison is made here.

## Instruction audit and smallest useful next comparisons

The output format worked for both models. Independent visit IDs, persistence as
identity rather than size stability, and explicit event cardinalities were clear.
There is no observed JSON-format misunderstanding. The illustrative persistent
example could in principle anchor a response, but the trace offers no evidence
that it caused the event choice; Astra explicitly gave an anatomical rationale.

Two semantic rules deserve revision **before a new freeze**, without adding any
case-specific location, count, disease or event hint:

> Give distinct lesions separate IDs when their boundaries remain distinguishable,
> even if their masks touch. Connectivity alone does not establish confluence.
> Treat a region as one instance only when separate lesions cannot be distinguished
> on the images. Record uncertain separations in the report.

For lesion presence, choose and document a generic annotation operating point.
“All visible tumor lesions,” “do not label normal tissue,” and “best complete
outputs even if uncertain” do not specify how to handle suspicious but unconfirmed
tissue. The current `unresolved` event concerns correspondence, not whether a
finding is tumor. A possible policy is to submit best-estimate lesion masks and
separately list doubtful candidates, reasons and confidence in the report. This
needs alignment with expert reference intent; forbidding empty answers or announcing
that this pair contains lesions would introduce an unjustified positive-case hint.

Recommended experiments, not launched by this review:

- **Keep the requested raw-pair setting as the primary task.** Use a clarified
  generic instance/uncertainty convention, a compact native viewer with an explicit
  candidate ledger, and independent cases. That tests whether better instructions
  and inspection workflow improve discovery without lesion-specific help.
- **Isolate wording effects.** Compare old/new wording across fresh attempts on
  the same held-out cases with otherwise identical tools and budgets. Do not infer
  a prompt effect from simply retrying this known case once.
- **Use optional diagnostic controls to separate capabilities.** A target-crop or
  localization-supplied condition isolates recognition/segmentation from search;
  both masks supplied with independent IDs isolates linking/events. These controls
  intentionally relax the primary task and require separate reporting. A native
  viewer alone does not supply targets and can preserve the no-mask condition.
- **Adjudicate the reference partition.** Review touching baseline labels under
  the stated annotation rule before treating exact merging as decisive. Retain
  original scores and annotate scope; do not relabel this case to improve results.

The best present conclusion is that Astra demonstrated useful image-to-mask and
anatomical linking behavior, with a meaningful instruction/partition interaction;
Sol demonstrated extensive inspection but failed to turn the relevant anatomy into
accepted lesion candidates. Neither trace justifies a standalone event-reasoning
failure claim, and neither supports a general claim that the task is solved.

## Reproduction and limits

The diagnostic script reads literal saved contour definitions without importing or
executing either solver's authoring scripts. It computes per-label coverage,
candidate overlap, ordered mask-operation counts, coordinate displacement and the
figure. Run from any directory with absolute paths and the existing imaging runtime:

```sh
MPLCONFIGDIR=/tmp/longitudinal-ct-mpl /Users/zhangqy/pkgs/tb3/.venv-br037/bin/python \
  /Users/zhangqy/pkgs/tb3/groups/longitudinal-reading/methods/longitudinal-ct-image-only/analyze_traces.py \
  --root /Users/zhangqy/pkgs/tb3 \
  --output /Users/zhangqy/pkgs/tb3/.local/longitudinal-ct-image-only-v1/trace-analysis
```

The baseline stage reconstruction reproduces every saved mask voxel. Follow-up
differs at one voxel, native (267,230,93), in this different local library runtime;
the cause of this one-voxel discrepancy is not established. Follow-up intermediate
stage values are therefore approximate diagnostics. All coverage values and prior
scores use the original saved masks. This is distinct from the earlier independent
scorer replay, which reproduced every score exactly. No reconstructed mask is
written over an answer or used as a replacement prediction.

Trace excerpts are copied from original ATIF steps with timestamps and source
fingerprints. Dense montage exposure demonstrates available visual evidence, not
that the model attended to every lesion. The audit does not inspect inaccessible
internal activations, establish training-data exposure, or clinically adjudicate GT.
