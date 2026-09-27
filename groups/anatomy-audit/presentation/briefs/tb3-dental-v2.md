# Segment dental anatomy — F002 contract v2

Segment the same native F002 dental CBCT under an explicit naming and boundary
contract, once without an example and once with an annotated F008 case. The
example-assisted attempt improves tooth identity and canal agreement but loses
pulp agreement; retained intermediate masks explain several of those losses.

## Value

Separates whole-tooth geometry, tooth identity and fine structures when an
annotated example is available. This is one exploratory pair on a development
case, with different realized compute and self-chosen methods. It does not
estimate an isolated assistance effect or clinical performance.

## Given

### Original data

The complete F002 ToothFairy3 CBCT: **410 × 410 × 274 voxels**, approximately
0.3 mm isotropic, supplied as `/app/data/ct.nii.gz`. Both conditions have identical
target, labels, common instructions and private evaluator bytes. Case identifiers
and source records are author context; solver files use neutral names.

### Supplied helpers

Both conditions receive the full dataset-wide dictionary: background 0 and
**77 sparse foreground IDs through 148**. It covers jaws, air spaces, canals,
restorations, 32 possible tooth identities and their corresponding pulp classes.
The dictionary does not reveal the target inventory.

The assisted condition additionally receives F008 CT and its original dense
annotation at `/app/reference/ct.nii.gz` and `segmentation.nii.gz`. F008 has
410 × 410 × 270 voxels at the same spacing. Its annotation contains all 32
tooth/pulp pairs and five canals, but **no restoration labels**. A source inventory
and selected views supported choosing it; they do not certify a clinically normal
case or every annotated voxel. F031 was rejected before any freeze or trial.

### Callable tools

Installed NumPy, SciPy, scikit-image, nibabel, PIL and image inspection in a CPU
container. No external data, websites or pretrained weights. Each independent
Astra/medium attempt has a two-hour ceiling and four CPUs, without a GPU.
The assisted agent attempted to retrieve SimpleITK; the proxy blocked it and
installation failed. It continued with available tools.

### Reference-only material

F002 dense labels, scoring, source identity, previous answers and target-specific
findings are withheld from both solvers. The second solver receives no first-run
feedback. F008 annotation is authorized assistance only in the second condition.

All target reference overlays, scores, GT-selected sections, corrected-match
tables and fine-structure diagnostics are later reader/evaluator material.
Target true-tooth masks in the pulp-rule experiment are an author-only oracle
diagnostic, never solver inputs.

## Task specification

Locate, outline and name supported anatomy on the full CT. The explicit v2
contract assigns increasing native **i, j, k to Right, Posterior, Inferior** for
semantic names. Retain the original dimensions, affine, qform and sform; do not
flip the scan to make the legacy header canonical. This operational rule does
not adjudicate physical acquisition laterality.

Every voxel receives one integer label. Natural mineralized tooth tissue and
its paired pulp are exclusive classes; their union forms the whole tooth.
Jawbone, air spaces, canals and prosthetic structures have explicit general
boundaries. Do not infer target occupancy from the dictionary or invent anatomy
to use every ID. Uncertainty notes do not exempt missed reference voxels.

The contract defines internal pulp chambers and root-canal spaces but leaves
occupied, treated or calcified chamber contents insufficiently specified.
Restoration subtype consistency and clinical acquisition orientation remain
under review. V2 is a separate contract from the original and later v3 tasks.

## Expected output

`/app/answer/segmentation.nii.gz`: one exclusive integer NIfTI using allowed IDs
on the unchanged target grid, preserving affine and qform/sform including codes.
`/app/answer/method.md` documents the method, uncertainty and omissions.

## Evaluation

The frozen custom scorer checks geometry and label validity, then measures
whole-volume reference agreement. Per-label Dice excludes classes empty in both
reference and answer; false-positive-only or missed classes score zero.
The macro weights each active foreground ID equally. There is no clinical pass
threshold, and this is not official challenge leaderboard scoring.

Whole-tooth evaluation unions each tooth with its paired pulp and finds a
one-to-one assignment maximizing total Dice. Unmatched objects contribute zero;
Dice ≥0.5 defines detection. Identity accuracy among detections and correctly
identified GT recall have different denominators. Group-pooled Dice ignores
IDs within the group; it does not measure correct tooth numbering.

| Retained measure | No example | F008 example |
| --- | ---: | ---: |
| Original macro Dice; active foreground classes | 0.454233; 61 | 0.501169; 59 |
| Whole-tooth matched geometry Dice | 0.778375 | 0.788633 |
| Detected teeth / 22 reference teeth | 19/22 | 20/22 |
| Correct identity among detected teeth | 17/19 | 19/20 |
| Correctly detected and identified / 22 reference teeth | 17/22 | 19/22 |
| Pulp macro Dice | 0.337878 | 0.314702 |
| Pulp pooled Dice | 0.470050 | 0.364235 |
| Main-canal macro Dice | 0.111758 | 0.196409 |
| Small-canal macro Dice | 0.001495 | 0.127071 |
| Agent time | 22m55s | 49m04s |
| Output tokens | 33,743 | 67,173 |

**Denominator diagnostic:** scoring both answers over the same union of 61 active
IDs, assigning both-empty IDs zero only for this diagnostic, gives
0.454233 → 0.484738. This is not a replacement for either original score.
No ID permutation, output editing or new segmentation is performed.

Reference teeth 26/27 match output IDs 27/28 without an example and 26/27 with
F008. Reference tooth 37 still matches output 38 in both; the first match is
below the detection threshold. Both answers contain 22 tooth objects, so
matching object count alone does not establish correct identity.

Pooled pulp precision falls from 0.3954 to 0.3213, and recall from 0.5795 to
0.4204. Main-canal recall improves from 8.04% to 14.40%; assisted small-canal
recall remains 8.49%. Improvements do not imply adequate coverage.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| No annotated example | F002 CT, full dictionary, v2 contract, local scientific tools | Locate, outline and name target anatomy |
| F008 example | Identical target and common contract, plus F008 CT and original annotation | Adapt example geometry and conventions to the distinct target |

## Difficulty

The no-example agent used CT inspection, agent-selected envelopes and paths,
thresholds, morphology and exclusive-label assembly. The assisted agent actively
used F008 for affine/smooth registration, transferred labels, jaw/tooth priors
and pulp calibration. It adapted and edited those priors rather than simply
returning the example. Saved scripts and command events establish these actions;
they do not expose hidden reasoning.

Three measured mechanisms explain why assistance did not solve fine structures:

- **Intensity transfer:** the same fixed pulp rule (smoothed intensity <1250,
  interior distance >2 voxels) gives pooled Dice 0.765 on F008's matching 22 tooth
  IDs and 0.299 on true F002 tooth masks. Target true masks are an author-only
  diagnostic. Example calibration is not held-out validation.
- **Harmful prior clipping:** in tooth 14, the saved 1.05 mm prior-distance rule
  deletes 440 of 443 correctly placed pulp voxels, leaving 3. It also removes
  false positives; retention alone does not assess its full tradeoff. The exact
  saved deletion reproduces voxel for voxel.
- **Canal placement and width:** only 19.8%/43.6% of assisted main-canal path
  samples lie inside reference masks. Of missed main-canal voxels, 98.6% already
  lie outside the uncut tubes. Enlarging radii helps only partially in a diagnostic;
  it is not a validated repair or a revised submission.

**Unresolved convention:** target pulp labels 116/131 include 838/858 and 331/333
voxels above raw intensity 3000, mostly at the scan maximum. F008 lacks this
appearance. The images establish a mismatch, not material identity or clinically
wrong GT. Excluding the two IDs raises assisted pooled pulp Dice only
0.364 → 0.417 diagnostically, so they do not explain all residual errors.

## Coverage

One selected target, two independent completed model attempts, two exact-reference
controls and two no-output controls. The source audit replays all six saved
evaluations exactly, verifies frozen task/source fingerprints and independently
reproduces the retained fine-structure diagnostics. No new model attempt or
historical solver program runs during explainer preparation.

Retained isolation and command records show the intended input boundary and no
observed target-GT or external-dataset retrieval. They cannot adjudicate encrypted
transport content or pretraining exposure. Unequal realized compute and methods
prevent a clean causal claim about the example. Original scores remain intact.

Source-selected views are local teaching derivatives, not exhaustive clinical
review. The publisher's CC BY-NC-SA 4.0 notice is retained alongside conflicting
archive CC-BY-SA metadata. Raw data remain local; publication is outside this work.

## Sources

- [Canonical comparison and mechanism story](../stories/dental-v2.story.md)
- [F002 v2 without an annotated example](../../experiments/dental-f002-contract-v2-astra-medium/protocol.md)
- [F002 v2 with the F008 example](../../experiments/dental-f002-reference-v2-astra-medium/protocol.md)
- [Shared contract and preparation boundaries](../../methods/dental-reference-ablation/README.md)
- [Paired results and method comparison](../../findings/dental-reference-example-comparison.md)
- [Pulp and canal mechanism diagnosis](../../findings/dental-fine-structure-failure-analysis.md)
- [Dataset direction and annotation audit](../../findings/dental-dataset-contract-audit.md)
- [Current source and replay audit](../sources/dental-v2-audit.json)
- [Native asset provenance and limitations](../../../../presentation/task-explorer/dental-v2/NOTICE.md)
