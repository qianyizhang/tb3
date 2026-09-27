# Segment dental anatomy — Original contract

Construct a native-grid dental segmentation from CBCT and a complete label
dictionary. Explain the three retained attempts without treating unresolved
source orientation as a clean measure of anatomical identity.

## Value

Separates finding and outlining anatomy from assigning the dataset's semantic
IDs. Large foreground overlap can coexist with opposing tooth IDs and missing
fine structures. These are exploratory development observations, not a clinical
or population evaluation.

## Given

### Original data

Two ToothFairy3 cases, named only in author/evaluator records. F018 uses the
official viewer pair: 410 × 410 × 264 voxels. F002 uses its archive pair:
410 × 410 × 274 voxels. Both have approximately 0.3 mm isotropic spacing.
The complete volume is supplied as `ct.nii.gz`; voxel values and affine are
preserved while descriptive NIfTI fields are removed.

F018 archive and viewer arrays are equal, but their third-axis affine metadata
differs. The original trials consistently pair the viewer CT with viewer labels.
F002 uses its internally aligned archive pair. No orientation conversion is
applied to these retained tasks or answers.

### Supplied helpers

The complete dataset-wide dictionary, including background 0 and **77 sparse
foreground IDs through 148**: jaws, canals, sinuses, pharynx, restorations, 32 tooth
identities and 32 corresponding pulp classes. It specifies possible labels, not
which structures occur in a case. No masks, exemplars, target counts, source
identity, prior answers or method suggestions are supplied.

### Callable tools

Local scientific libraries and image inspection in a CPU container. No external
data, websites, pretrained segmentation weights, reference mask or score feedback.
Each independent Astra attempt has a two-hour ceiling; F018 is tested once at
medium and once at xhigh, and F002 once at medium. The retained authentication-only
invocation is an infrastructure observation, not a fourth segmentation attempt.

### Reference-only material

Case/source identity, ground-truth masks, private scorer, scores and all
post-submission diagnostics are evaluator/reader material. The full taxonomy is
solver-visible; per-case reference occupancy is not. Selected diagnostic sections
and the reference-selected pulp example are teaching views, not supplied hints.

The publisher FAQ explicitly warns that NIfTI direction information is not
physically accurate. That convention was absent from the original solver package.
Header/label agreement and detailed annotation boundaries remain unadjudicated;
paired-grid validity alone does not settle clinical laterality.

## Task specification

Inspect the full CBCT, construct a three-dimensional integer segmentation of
visible structures and assign the supplied IDs. Preserve the input dimensions
and affine exactly. Every voxel receives one integer ID; background is zero.
Do not assume all dictionary classes occur in the image.

The original instructions provide semantic names without an operational manual
for every boundary. Laterality, occupied pulp, restoration subtype and related
reference-convention questions qualify interpretation of same-ID voxel scores.
Later v2/v3 contracts and annotated-example conditions are separate catalogue
entries; their instructions and results do not retroactively repair this task.

## Expected output

`segmentation.nii.gz`, containing allowed integer IDs on the untouched CT grid,
and `method.md`, describing the chosen method, limitations and uncertainty.

## Evaluation

The frozen custom evaluator computes whole-volume Dice separately for each
foreground ID. A class absent from both output and reference is excluded; a
false-positive-only or missed class receives zero. The macro gives every active
class equal weight. Invalid geometry or unknown IDs are rejected. Foreground
Dice pools all nonzero labels and ignores identity. There is no clinical pass
threshold, and these are not official challenge leaderboard scores.

| Retained attempt | Original macro Dice; active classes | Foreground Dice | Fixed L/R ID diagnostic; active classes |
| --- | --- | ---: | --- |
| F018 Astra/medium | 0.039394; 70 | 0.968609 | 0.692457; 68 |
| F018 Astra/xhigh | 0.044766; 70 | 0.970754 | 0.703420; 68 |
| F002 Astra/medium | 0.049641; 62 | 0.874451 | 0.463379; 57 |

The fixed side-ID permutation operates on the confusion matrix. It changes
neither voxel positions nor saved answers, and is **not a replacement score**.
It also changes the active-class denominator: its score difference is not a
fixed-denominator causal share of error. The original outcomes remain unchanged.

F018 medium/xhigh share exact frozen task bytes. F002 shares the output and
scoring contract but differs in case and class inventory. One attempt per
condition supports descriptive observations, not an effort or case-difficulty
ranking. Clinical acquisition laterality remains unresolved.

Residual disagreement persists after pooling or side-pairing. Both F018 attempts
omit the two incisive canal IDs; F002 omits all five canal IDs. F018 main-canal
contours remain offset in selected native sections. F002 restoration subtype
disagreement accompanies geometric errors, with no clinical subtype adjudication.

The retained F002 tooth-envelope and intensity gates explain one concrete source
of pulp loss. Across side-paired reference pulp, the distance gate retains 10,433
of 12,242 reference voxels; the following intensity gate retains 4,074. This is
reference retention, not precision or proof that raising the cutoff is a safe fix.
The reference-selected tooth-16 example loses 843 of 844 surviving reference
voxels at that intensity gate. Component/core filters and later cleanup follow.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| F018 Astra/medium | CT, full dictionary, local scientific tools | Locate, outline and name visible anatomy |
| F018 Astra/xhigh | Exactly the same frozen task | Same work; separate higher-effort attempt |
| F002 Astra/medium | Another native CT; same dictionary and output/scorer rules | Segment the separate case without prior-case feedback |

## Difficulty

The agents chose image-guided classical processing: thresholds, connected regions,
morphology, interpolated tooth envelopes and internal dark-component extraction.
Xhigh additionally used 3D watershed. Canal paths were constrained by chosen
landmarks or deliberately omitted. Fine anatomy can remain misplaced even when
large structures overlap. Missing source conventions are a separate task-context
limitation; they do not explain every residual geometry error.

## Coverage

Two cases, three completed segmentation attempts and one pre-inference
authentication failure. The current source audit verifies two frozen task digests,
403 source fingerprints and seven saved model/control evaluations (three model,
two oracle, two no-op). Original scores and the prior trace/pulp diagnostics
reproduce independently. No fresh model or historical solver script is executed.

The reader views use original pixels, saved output contours and separately
revealed research labels. Selected sections are not an exhaustive clinical
review. Public-data training overlap is unknown. The publisher's noncommercial,
share-alike notice is retained alongside the conflicting archive license string;
raw data stay local and public redistribution is outside this work.

## Sources

- [Dental CBCT segmentation from CT alone — Astra medium](../../experiments/dental-ct-only-astra-medium/protocol.md)
- [Dental F018 CT-only segmentation — Astra xhigh](../../experiments/dental-f018-astra-xhigh/protocol.md)
- [Dental F002 CT-only segmentation — Astra medium](../../experiments/dental-f002-astra-medium/protocol.md)
- [Original F018 medium result](../../findings/dental-ct-only-astra-medium.md)
- [F018 effort comparison](../../findings/dental-f018-effort-comparison.md)
- [F002 result](../../findings/dental-f002-astra-medium.md)
- [Trace and method audit](../../findings/dental-trace-root-causes.md)
- [Dataset contract audit](../../findings/dental-dataset-contract-audit.md)
- [Current source audit](../sources/dental-original-audit.json)
- [Publisher orientation description](https://ditto.ing.unimore.it/toothfairy3/)
- [Publisher FAQ](https://toothfairy3.grand-challenge.org/faq/)

- [Canonical original-contract story](../stories/dental-original.story.md)
- [Native teaching asset notice](../../../../presentation/task-explorer/dental-original/NOTICE.md)
