# Track CT lesions — Original image-only contract

Find tumor instances throughout two full CT volumes, delineate them in their native grids, then link identities and classify complete longitudinal event groups. The retained original task has an **open instance/confluence convention review**; its unchanged scores remain diagnostic.

## Value

Separates discovery, foreground extent, instance partition and temporal identity. Good foreground overlap can coexist with missed instances and incomplete event groups.

## Given

### Original data

`/app/data/baseline.nii.gz` and `followup.nii.gz`: full native CTs, respectively 512 × 512 × 261 and 512 × 512 × 274 voxels. In-plane spacing is 0.822265625 and 0.84765625 mm; both have 3 mm slice spacing. Each native affine maps zero-based voxel centers to RAS mm. Visits are not registered.

Source case 0a09c8844b from Longitudinal-CT v3 is reader provenance, **not solver-visible identity**. Neutral filenames and scrubbed free-text NIfTI metadata preserve all original image pixels and geometry. No dataset name, source identifier, diagnosis, clinical history, target counts or locations were supplied.

### Supplied helpers

Only the two CT volumes, generic inclusion/confluence instructions, output schema and illustrative event syntax. No candidate centers, target masks, prior outputs or longitudinal reference links. Generic example IDs convey neither counts nor identities in this case.

### Callable tools

CPU image analysis with NumPy, SciPy, nibabel, scikit-image and Pillow; up to two hours per attempt. No GPU, pretrained weights, external dataset lookup or model downloads. The model transport route is separate from data/network assistance. Read the exact frozen protocol for execution details.

### Reference-only material

Private native instance masks and a source-derived event ledger: four baseline instances, two follow-up instances; B1+B2+B4 → F4 merging and B3 → F3 persistent. This is four links in two groups. No newly appearing or disappearing reference event occurs here. Source topology `UNCHANGED` means identity persists, not unchanged lesion size.

Source annotators used CT plus clinical examination reports; the solver had CT alone. Reader crops are reference-selected and remove localization search. The portable explanation embeds private-to-solver material and must never serve as a solver input packet.

## Task specification

Segment every visible tumor lesion with its full extent while excluding normal anatomy. The original instruction states: **“A confluent region is one instance.”** IDs are local to each visit; matching numerical IDs do not establish biological identity.

Return events with exact cardinalities: persistent 1→1; merging at least 2→1; disappearing 1→0; newly_appearing 0→1; unresolved any nonempty group. Every positive instance ID must appear in exactly one event group per visit. An unresolved group does not assert links. Check follow-up field of view before calling disappearance.

## Expected output

- `baseline_instances.nii.gz` and `followup_instances.nii.gz`: 3D integer maps on each exact input shape/affine. Zero is background; IDs are 1–65535, at most 4096 instances per visit.
- `events.json`: `schema_version: 1`, complete event groups with per-visit ID lists.
- `report.md`: method, uncertainty and representative image evidence citing a filename and zero-based native slice index. Preserve scripts and views under `/app/work`.

An empty mask pair with `groups: []` and a nonempty report can satisfy the artifact contract; validity does not establish a scientific or clinical pass.

## Evaluation

**Detection:** predicted centroid inside a reference mask or within 3 mm of its labeled voxel centers in physical space, with maximum-cardinality one-to-one assignment. This is not a centroid-to-centroid 3 mm test. Frozen IoU sensitivity thresholds are 0.10, 0.25 and 0.50.

**Segmentation:** foreground Dice ignores instance partition; GT-macro best one-to-one instance Dice assigns zero to missed references. Detected-only and localization-anchored variants have different denominators.

**Association:** map arbitrary local output IDs to reference IDs before edge precision/recall/F1. End-to-end links include detection misses; conditional scores must retain eligible/total reference counts. **Exact events** require the entire typed group. If no complete reference group is eligible, conditional event competence is unassessed; keep any retained numeric value without reinterpreting it as evidence of ability.

| Retained endpoint | Astra / medium | Sol / xhigh |
| --- | ---: | ---: |
| Artifact validity | valid | valid |
| Localized instances | 2/6 | 0/6 |
| Foreground Dice, baseline / follow-up | 0.68480 / 0.77921 | 0 / 0 |
| GT-macro instance Dice, all six | 0.23445 | 0 |
| Correct end-to-end links | 1/4 | 0/4 |
| Exact event groups | 0/2 | 0/2 |
| Complete reference groups eligible | 0/2 | 0/2 |

Astra's single saved instance at each visit maps to B4/F4. Conditional links are 1/1, but only 1/4 reference edges are eligible. Its baseline foreground covers parts of B1/B2/B4, so strict 2/6 localization does not mean four entirely unseen regions. The separate B3/F3 focus has no output coverage. Sol's final masks and event list are empty; both executions completed normally. These observations do not infer attention or clinically adjudicate candidate decisions.

## Difficulty

Reference B1/B2/B4 form one 6-connected foreground component, while the source retains separate baseline instances. Voxel contact alone establishes neither radiologic confluence nor erroneous expert labels. The wording/partition mismatch leaves fine-instance and merging interpretation **under review**; no original score is corrected.

## Coverage

One selected public pair; one `gpt-6-astra` medium and one `gpt-5.6-sol` xhigh attempt using the exact same 18-file task digest. The convention issue was recognized before Sol dispatch, with no prompt correction or reference feedback. Treat this as a **diagnostic comparison**, not a model ranking or causal model/effort estimate. Clinical-context differences, public-source exposure and absent event classes constrain generalization.

The ten-chapter reader story uses actual CT views and saved masks. A fresh audit checks all shared frozen files, seven source members, full pixel/affine identity, answer hashes, native instance measurements and exact saved-score replay. Replays are not new model execution. This original contract remains distinct from the revised-inclusion and comprehensive-candidate definitions.

## Sources

- [Original solver instruction](../../methods/longitudinal-ct-image-only/instruction.md) and [private scoring implementation](../../methods/longitudinal-ct-image-only/score.py).
- [Astra medium protocol](../../experiments/longitudinal-ct-image-only-astra-medium/protocol.md) and [Sol xhigh protocol](../../experiments/longitudinal-ct-image-only-sol-xhigh/protocol.md).
- [Retained comparison and native review](../../findings/longitudinal-ct-image-only-comparison.md), [instance-boundary review](../../examples/longitudinal-ct-instance-boundary-review.md) and [source/derivation audit](../sources/longitudinal-ct-original-audit.json).
- [Longitudinal-CT v3 source release](https://fdat.uni-tuebingen.de/records/qe950-g4h94), CC BY-NC 4.0; [teaching attribution and transforms](../../../../presentation/task-explorer/longitudinal-ct-original/NOTICE.md).
