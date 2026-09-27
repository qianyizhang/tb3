# Segment dental anatomy — F018 contract v3

Segment a complete native CBCT under explicit anatomical-compartment rules.
Compare two retained Astra/medium attempts: the target alone and the same target
with one separately annotated F008 example. This is a repeated **development
case**, with one attempt per condition; it does not isolate a general benefit of
examples or the v3 instruction revision.

## Value

Separates valid output, tooth identity, whole-tooth shape and thin-structure
localization. Both runs identify **29/29 teeth** correctly, while shape agreement
improves and substantial canal/pulp disagreements remain. The v3 contract makes
boundaries explicit without asserting that the original GT follows every rule.

## Given

### Original data

ToothFairy3 F_018, supplied under an anonymous filename: a single-channel
**410 × 410 × 264** CBCT, **0.3 mm isotropic**, with stored scaling applied.
Both conditions use byte-identical target CT, dense private reference, sparse
label dictionary and scorer. F018 is the original paired viewer-source package;
no archive-header variant is substituted. The complete volume is supplied.
Selected sections in the explainer are post-hoc reader views, not solver crops.

### Supplied helpers

The v3 instruction and dictionary contain **77 foreground IDs plus background**,
with gaps through ID 148. Preserve FDI anatomical slots; pulp ID is tooth ID +100.
Main canals use IDs 3/4; small canals use 103/104/105. ID 150 is invalid.
No target-specific label inventory, count, landmark, threshold or prior score is given.

The example condition alone adds the original **F008 CT and dense annotation**,
410 × 410 × 270, using the same dictionary and semantic axis contract. It is the
previously selected example, not a newly selected match to F018's GT. Free-text
example header fields are stripped; source arrays and geometric fields match.
Its anatomy and label inventory must not be assumed to describe the target.

The operational naming contract is native **i→Right, j→Posterior, k→Inferior**.
Stored metadata must be preserved independently: target header codes are LPI,
example LPS. These task names do not adjudicate physical acquisition laterality.
Reader panels label native indices; they do not use screen-left as patient side.

### Callable tools

Both conditions use the retained local scientific Python/Codex runtime, **4 CPUs,
no GPU**, nominal **12 GiB** container ceiling and **7,200 agent seconds** maximum.
The shared Docker VM has less physical memory, so the historical runs were serialized.
No extra tools, pretrained weights, external dataset, previous solver workspace,
parent conversation or evaluation feedback was supplied. Model and effort are
`openai/gpt-6-astra` / `medium` in both conditions. The example may be inspected
and used by any allowed method; the contract does not prescribe registration.

### Reference-only material

The evaluator alone receives the original F018 dense label map and scorer.
Target GT, case identity, prior methods/findings and earlier target results are
withheld from each solver. F008 annotation is a permitted input only for its arm.
Target masks, scores, GT-selected detail planes and diagnostic search-eligibility
counts in the explainer are explicit **reader-only reveals**. The author had seen
earlier F018 results, so this is not untouched held-out validation.

## Task specification

Return one mutually exclusive native-grid label volume and a method/uncertainty
note. Apply the [exact frozen operational rules](../../methods/dental-f018-contract-v3/instruction.md):

**Tooth and pulp:** mineralized natural tooth and supported internal chamber/root
canal are separate. Pulp is an anatomical compartment, including supported
occupied filling/post portions; bright contents alone do not make it hard tooth.
Do not invent unresolvable or obliterated space. Whole-tooth geometry uses their union.

**Jaws and canals:** jaws include cortical and enclosed marrow compartments,
excluding distinct empty sockets and separately labeled anatomy. Canals contain
supported intrabony lumen to the imaged openings, excluding walls and extraosseous
nerves. Branches/components may be present; no fixed diameter or count is required.

**Cavities:** sinus cavity includes supported fluid/lining but excludes bony wall
and septa; pharynx contains air lumen only. Respect anatomical openings and the field of view.

**Restoration ownership:** standalone crown, connected bridge and implant body/
abutment follow distinct rules. An implant does not acquire a tooth/pulp ID;
distinguishable prosthetic coronal units keep their restoration label.

**Uncertainty:** use best-supported single-class assignments, with conservative
continuation only across short supported gaps. Unlisted distinguishable materials
remain background. Do not extrapolate beyond the image or infer target presence
from the dictionary. Method notes do not create ignored regions.

## Expected output

`/app/answer/segmentation.nii.gz`: integer, finite, exclusive labels on the original
shape, affine, qform/sform and codes. Background is 0; no invented or renumbered IDs.
Record inverses of any internal reformatting and use nearest-neighbour mask sampling.
`/app/answer/method.md` explains method, transforms, omissions and uncertainty.
Both retained answers satisfy the frozen validity checks; missing classes or invalid
files do not explain the remaining geometric disagreements.

## Evaluation

The custom evaluator reports active-label macro Dice, omitting both-empty labels
and assigning one-empty labels zero. Both answers have **68 active labels**:
2 jaws, 2 sinuses, 1 pharynx, 29 tooth-tissue, 29 pulp, 2 main canals and 3 small canals.
The nine unused foreground labels do not inflate the mean. Restoration classes
are empty in GT and both outputs and contribute no tested restoration performance.

Whole-tooth matching maximizes total Dice independently of FDI names, scores
unmatched objects zero and reports identities among matches with Dice ≥0.5.
Canal ASSD and HD95 use stored spacing in millimetres; lower is better. HD95 here
is the larger directional 95th-percentile surface distance. Pooled foreground/group
Dice and per-label averages answer different questions. These are custom research
measures, not official leaderboard scores or clinical pass/fail criteria.

| Retained whole-volume endpoint | No example | F008 example |
| --- | ---: | ---: |
| Original active-label macro Dice, 68 labels each | 0.71084 | 0.82395 |
| Whole-tooth matched geometry Dice, 29 objects each | 0.78523 | 0.92613 |
| Correct detected GT identities, Dice ≥0.5 | 29/29 | 29/29 |
| Tooth-tissue macro Dice, 29 labels | 0.77406 | 0.91771 |
| Pulp macro Dice, 29 labels | 0.69887 | 0.80387 |
| Pooled pulp Dice | 0.67967 | 0.81442 |
| Main-canal macro Dice, 2 labels | 0.36062 | 0.47882 |
| Small-canal macro Dice, 3 labels | 0.14324 | 0.18527 |
| Jaw / sinus macro Dice, 2 labels each | 0.83329 / 0.92042 | 0.85835 / 0.94789 |
| Pharynx Dice, 1 label | 0.96395 | 0.97710 |
| Measured agent duration | 23m48s | 28m59s |
| Output tokens | 36,510 | 46,941 |

Six saved evaluations replay exactly: two model outputs, two oracle controls at
1.0 and two no-output controls at 0.0. This is replay, not fresh inference. Both
model attempts completed normally with unchanged freezes. Retained command and
proxy reviews observed no forbidden access; encrypted payload/pretraining remain
unadjudicated. Different self-chosen methods and realized compute limit attribution.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| No annotated example | Complete F018 CT, dictionary and v3 operational rules | Localize and partition all represented anatomy from the target |
| F008 example | Identical target/contract plus separate F008 CT and annotation | Transfer useful information while correcting anatomical differences and target boundaries |

The no-example method constructed tooth territories and reviewed canal paths,
then refined with intensity, morphology and local geometry. The assisted method
used an affine pull map plus dense and regional registration, corrected tooth
correspondences and an impacted molar's orientation, transferred masks, then
refined boundaries against target CT. Saved code/arrays establish actual example
use. The reader transfer wipe samples the saved final field; it is not a replay
of optimizer iterations. A complete 168,100-voxel k=55 atlas and warped-CT plane
are reproduced exactly from the saved mapping.

## Difficulty

**Aggregate improvement contains counterexamples.** Pulp improves for 20/29
labels, with pooled precision 55.5%→74.6% and recall 87.6%→89.7%. Pulp 122 is the
largest Dice gain, 0.33291→0.85467, and is selected post hoc as a successful contrast.
Pulp 127 declines 0.75759→0.18608. Its transferred prior has zero overlap with
827 GT voxels; initial tooth refinement recovers 28. Before the final intensity
filter, the retained mask plus eligible expansion region contains only **128/827**
GT voxels. The saved final mask contains **115/827**, exactly reproduced from the
saved inputs. Only 345 GT voxels lie in the preceding whole-tooth object; 494 lie
within six voxels of the pulp prior. These overlapping restrictions are not
additive losses and do not isolate a unique cause of the registration error.

**Canal 104 is outside the operation's reach.** Both submitted masks have zero
Dice for this label. The assisted prior's crop is
`i=[274,291), j=[109,128), k=[193,209)`, its bounding box expanded four voxels.
It contains **0/355** target-GT voxels. Local refinement changes 189 prior voxels
to 203 final voxels but cannot reach that reference region. Its final centroid
is 11.18 mm from GT and ASSD 8.64 mm. The historical six-voxel proximity measure
is a separate diagnostic; it is not the canal algorithm's search radius.

**Overlap and extent can disagree.** Main-canal 4 Dice improves
0.33062→0.43880 while HD95 worsens **3.09→7.32 mm**. Complete-axis silhouettes
show the retained geometry; they are not CT sections and projected overlap can
come from different depths. Selected native sections provide intensity context.
No one view or metric certifies the reference or output clinically.

## Coverage

**Matched endpoints, limited inference:** same target, GT, rules, scorer and maximum
budget; one attempt per arm, different chosen methods and realized compute. The
source audit verifies original arrays/grids, frozen bytes, saved-score replay and
actual refinement operations. It does not establish population benefit, clinical
correctness, a fresh execution or the isolated benefit of revising v2 to v3.

**Untested conventions:** target GT and both outputs contain no restoration labels;
neither solver confidently identifies treated occupied pulp. This case therefore
does not validate v3's new occupied-pulp or restoration definitions. Source
annotation intent, physical laterality and ambiguous compartment boundaries remain
under review. No GT or original outcome is changed to fit the explanation.

**Selected visual evidence:** native reader sections and all-depth canal silhouettes
have explicit coordinates, crops, legends and roles. Masks and GT remain separate
from input-only views. Source license is retained as publisher CC BY-NC-SA 4.0;
conflicting archive CC-BY-SA metadata remains unresolved. This is local teaching
work with no publication decision or new medical/model run.

## Sources

- [No-example protocol](../../experiments/dental-f018-contract-v3-astra-medium/protocol.md)
- [F008-assisted protocol](../../experiments/dental-f018-reference-v3-astra-medium/protocol.md)
- [Fixed v3 design and operational decisions](../../methods/dental-f018-contract-v3/README.md)
- [Original comparison finding](../../findings/dental-f018-contract-v3-comparison.md)
- [Source-contract and annotation audit](../../findings/dental-dataset-contract-audit.md)
- [Explainer audit: hashes, saved replays and exact refinement diagnostics](../sources/dental-v3-audit.json)
- [Reader-asset derivation, boundaries and attribution](../../../../presentation/task-explorer/dental-v3/NOTICE.md)
