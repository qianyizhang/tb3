# Segment and name ten organs from CT

Construct ten independent organ masks from a complete native CT, then compare
localization, boundary quality and semantic identity separately.

## Value

This task begins with CT intensities and target definitions. It requires new
contours, unlike the group's supplied-object identity and mask-audit tasks.

## Given

### Original data

One CT, 265 × 265 × 401 voxels at 1.5 mm isotropic spacing, with its RAS affine.
The finite dictionary contains spleen, both kidneys, gallbladder, liver, stomach,
pancreas, both adrenal glands and duodenum. Numeric filenames map to organ names.

### Supplied helpers

The three standalone conditions receive no masks or pretrained segmenter. They
have ordinary scientific imaging libraries. The separate Astra/medium tool
condition adds a generic LiteMedSAM skill, adapter and pinned CPU model. The agent
chooses every image, crop, slice, box and semantic assignment.

### Callable tools

Shell and image inspection with NumPy, SciPy, NiBabel, scikit-image and Pillow.
Only the tool condition has LiteMedSAM. Its checkpoint is pinned in the protocol.
There is no new tool execution in this reader explanation.

### Reference-only material

Source identity (TotalSegmentator v2.0.1 small release, s1233), case selection,
source masks, scorer, scores and prior answers are private to preparation or
post-submission evaluation. Reader crops are selected after submission, with
reference outlines and scores revealed separately. Research labels retain possible
residual errors; this is not a new independent clinical contour adjudication.

## Task specification

Create ten binary NIfTI masks with exactly the input shape and affine, and a method
note. Use patient anatomy for right/left. Preserve independent masks: they may
overlap, and the source masks share 57 voxels. Do not force an exclusive label volume.
Stomach, gallbladder and duodenum include the specified envelope and contents;
kidneys exclude separately classed cysts. Other anatomy is outside this taxonomy.

## Expected output

`01.nii.gz` through `10.nii.gz`, mapped to the supplied names, plus `method.md`.
Each mask contains only 0 and 1 and uses the native CT grid.

## Evaluation

Semantic Dice pairs each mask with its declared organ. The primary score averages
all ten organs equally. Optimal one-to-one matching estimates geometry recoverable
by relabelling; identity is assessed only for positive-overlap matches. Foreground
union measures are separate. Oracle/no-op and perturbation controls preserve this
separation. There is no invented clinical pass threshold.

| Retained condition | Semantic macro Dice | Matched macro Dice |
| --- | ---: | ---: |
| Astra/xhigh | 0.73803 | 0.73803 |
| Astra/medium | 0.73419 | 0.73419 |
| Sol/xhigh | 0.32907 | 0.34878 |
| Astra/medium + LiteMedSAM | 0.75697 | 0.75697 |

One selected case and one attempt per condition. The tool condition improves 7/10
organs; gallbladder, pancreas and right adrenal regress. Three standalone attempts
share frozen task bytes. The tool arm holds CT, labels, reference and scorer fixed,
but changes instruction, skill and runtime. These are descriptive matched-endpoint
results, not a causal tool test or population model ranking.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| CT only | CT, dictionary and scientific libraries | Discover, delineate, complete and name organs |
| Callable LiteMedSAM | CT, dictionary, generic skill and segmenter | Choose images/prompts, inspect candidates, reconstruct volumes and name organs |

The standalone runs mainly interpolate sparse visual polygons, followed by image
thresholds and morphology. The tool condition interpolates boxes but infers masks
from each actual image. It unions selected candidates and applies further cleanup.
Saved method views preserve this difference; neither animation runs a model.

## Difficulty

Knowing a target's name does not provide its location or contour. Small structures,
endpoint coverage and nearby organs remain difficult even when a segmenter is
available. Prompt coverage diagnoses localization separately from learned contours;
it is not a hard score ceiling. Image displays, explicit authoring, repeat inference
and demonstrated correction are distinct operations.

## Coverage

The source audit replays eight saved model/control evaluations across two task
digests. The independent slice analysis reproduces all 40 final organ scores.
Original scores, references and frozen tasks remain unchanged. Training overlap
is unknown. Full-volume research Dice does not certify clinical correctness.

The canonical story uses seventeen native source views: one centre section, ten
post-submission diagnostic sections and six consecutive stomach method planes.
These selected views do not constitute exhaustive visual review of the full volume.

## Sources

- [CT-only ten-organ segmentation — Astra xhigh](../../experiments/ct-organ-segmentation-astra-xhigh/protocol.md)
- [CT-only ten-organ segmentation — Astra medium](../../experiments/ct-organ-segmentation-astra-medium/protocol.md)
- [CT-only ten-organ segmentation — Sol xhigh](../../experiments/ct-organ-segmentation-sol-xhigh/protocol.md)
- [Astra medium with LiteMedSAM](../../experiments/ct-organ-segmentation-astra-medium-litemedsam/protocol.md)
- [Three-condition comparison](../../findings/ct-organ-three-condition-comparison.md)
- [Tool result, prompts and limitations](../../findings/ct-organ-segmentation-astra-medium-litemedsam.md)
- [Slice construction and correction audit](../../findings/ct-organ-slice-construction-audit.md)
- [Current source audit](../sources/ct-organ-audit.json)
- [Canonical story](../stories/ct-organ-segmentation.story.md)
- [Reader asset notice](../../../../presentation/task-explorer/ct-organ/NOTICE.md)
