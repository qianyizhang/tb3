# BR-042 V3: why the small branches underperformed

Post-hoc investigation, 2026-09-20. Original task, model answers, scoring and reference files are unchanged. This review uses reference locations, original segmentation, saved model candidates and submitted courses. Its case-specific findings must not be supplied to a future blind trial on this case.

## Findings

The evidence supports a mixture of small-vessel discovery misses, numbering errors caused by missed upstream branches, and unresolved PDA identity/taxonomy. It does not support calling these vessels impossible to extract. It also does not establish that the reference labels are wrong.

| Reference category | Astra-medium geometry / correctly labeled coverage at 1 mm | Interpretation |
| --- | --- | --- |
| D2 | 3.1% / 0% | Short branch genuinely missed; the larger downstream diagonal was then named D2 instead of benchmark Other. |
| OM1 | 0% / 0% | Small, faint proximal LCx branch missed; plausible extraction limitation. |
| OM2 | 100% / 0% | Geometry succeeded. Nearly all was named OM1, consistent with overlooking upstream OM1. |
| R-PDA | 91.2% / 23.4% | Mostly recovered geometry; large disagreement about which courses retain label 10 versus more specific ventricular names with label 0. |

Sol misses almost the entire left coronary tree, so its failures on these branches do not specifically demonstrate their intrinsic difficulty. Astra-xhigh is a timed-out partial output; its geometry is diagnostic evidence, not a completed-run comparison.

### D2: discovery miss with downstream consequences

The source branch is `left-6`, from native zero-based XYZ approximately (316,314,176) to (350,311,169), between the reference D1 and the later diagonal labeled Other. It is 14.1 mm of scored D2. Its narrow central signal is continuous in two perpendicular reference-guided curved views and successive cross-sections. Median center intensity is 195 HU; median mask-derived diameter proxy is 1.30 mm, around 3.5 in-plane pixels.

Astra-medium's final output covers only 0.44 mm near the parent LAD. Even the union of **all retained candidate tree paths**, densely resampled for this diagnostic, covers only 4.6% of D2 at 1 mm. Thus this was not simply a well-extracted path forgotten during JSON export. The retained candidate set itself lacked the branch. This does not prove that the model never visually considered it; no complete cognition claim follows from saved files.

The submitted downstream D2 follows the reference Other course. Missing the intervening branch plausibly explains the numbering shift. The prompt already explicitly required upstream inspection before numbering; this part is principally an execution/discovery failure, rather than a missing branch-order instruction.

### OM1: the faintest of these missed branches

Source `left-10` runs from the LCx near (285,258,157) toward (309,244,164), with 11.45 mm scored as OM1. Median center intensity is 124 HU, with the 10th–90th percentile approximately 101–153 HU; median diameter proxy is 1.06 mm. The clean curved views show a faint connected course near a brighter neighboring vessel. Native slices are provided to inspect the connection without relying solely on a straightened view.

Both Astra outputs miss it. The medium run's union of retained candidate paths also has 0% coverage at 1 mm. Its initial segmentation used Gaussian smoothing followed by a 170-HU threshold, which is a plausible obstacle for this branch. However, it also used a lower-threshold vesselness stage, so the initial threshold alone is **not a proven causal explanation**. Establishing a specific algorithmic cause would require replaying intermediate segmentation stages; this review did not modify or rerun the extraction.

There is no demonstrated annotation error here. Low conspicuity and small scale make the miss understandable; guided visibility does not quantify unaided human or model discoverability.

### OM2: recovered geometry, wrong number relative to GT

Source `left-0` starts near (298,191,104), ending near (328,189,91). Medium covers all 14.13 mm scored as OM2 within 1 mm: 13.57 mm is nearest its submitted OM1 and 0.57 mm its LCx near the junction. The centerline clearly follows the local tubular signal in the visual review. This is direct evidence that this course was extractable in the completed trial.

The model's method explicitly says it did not confirm a separate OM2. Combined with the missing proximal OM1, this is consistent with numbering the branches it found rather than recovering the complete branch order. The task already warned against this. An anatomical reader can still question the dataset's branch identity, but this review has no positive evidence that its OM1/OM2 order is wrong.

### R-PDA: two reference branches, different model interpretations

The original right VTK contains **two separate label-10 courses**, connected through label-9 RCA rather than one continuous label-10 path. This is present in the source, not introduced by our JSON conversion.

| Source course | Location, native XYZ | Medium geometry / label | Xhigh partial geometry / label |
| --- | --- | --- | --- |
| `right-2` (review A) | (217,292,45) to (292,306,34) | 94.5% / 33.6% | 97.6% / 97.6% |
| `right-3` (review B) | (192,314,43) to (227,315,37) | 83.7% / 0% | 89.3% / 0% |

On course A, medium matches 10.77 mm as R-PDA and 19.50 mm as an inferior LV branch of R-PDA, label 0. On course B, it matches 11.75 mm as an inferior RV branch of RCA, label 0. Xhigh also names course B an inferior RV branch. Agreement between two models is not independent anatomical ground truth.

The dataset protocol explicitly allows multiple PDA/PLA vessels and selected daughter branches; continuation is decided by anatomical course rather than size. This creates a genuine convention question absent from the task's compact vocabulary. See [ImageCAS-X Appendix B](https://arxiv.org/html/2608.30404v1#A2).

The task's generic instruction to stop a parent label at a daughter, together with its label-0 rule, leaves the mapping of named ventricular daughters versus benchmark PDA variants insufficiently explained. That can contribute to disagreement, but does not automatically vindicate the model: it may also have chosen the wrong daughter as PDA, especially where its own notes acknowledge arterial/venous ambiguity.

**Adjudication needed:** inspect the posterior interventricular groove and the full connections to decide whether reference B is an additional PDA or an inferior RV branch; inspect the fork around (248,289,38) to decide which course should continue as PDA. The present evidence supports “identity/convention disagreement requiring review,” not “GT proven wrong.”

## Related underperforming labels

D1 and Other illustrate the same coupling between branch discovery and naming. Medium covers the full reference D1 correctly, but its full geometric coverage of reference Other is assigned D2. Xhigh geometrically covers the full D1 course but calls it ramus intermedius (8), and covers 99.1% of Other while naming it D1 (4). Its partial reconstruction extends LM to the early lateral branch; medium instead places that branch downstream of the LM bifurcation and calls it D1. These are identity/segment-boundary decisions on largely recovered geometry, not evidence that the vessel itself cannot be extracted. Medium's method explicitly documented the ramus alternative. Confirming the actual LM/LAD junction is the relevant anatomical review.

The smaller LM and proximal LAD label losses likewise mix boundary conventions with nearest-course attribution near bifurcations. Xhigh's LCx geometry coverage is 86.6%, whereas the completed medium run reaches 99.8%; this does not suggest an intrinsically impossible LCx. Its timeout also limits what can be concluded about unfinished discovery and review. The existing full viewer and per-category results retain these broader comparisons.

## Reference and measurement checks

The original VTK centerlines were inspected directly, alongside the original native segmentation. All sampled points on these five source courses lie within the binary coronary mask; 96–99% have the same mask class, with differences concentrated near shared junctions. This supports coordinate and label consistency, **not independent anatomical validation**: the dataset derives centerlines from corrected masks and propagates labels within the same pipeline. [ImageCAS-X methods](https://arxiv.org/html/2608.30404v1).

The diameter proxy is twice the physical Euclidean distance to the binary-mask background, sampled along the reference. It is affected by voxel resolution, noncircular lumen shape and reference centering; it is not a clinical diameter measurement. Center HU is trilinearly sampled, not a contrast-to-noise measurement. No claim of calcification, stenosis or image pathology is made.

The supplied branch figures include source junction portions; their displayed lengths may therefore slightly exceed scored category lengths. Coverage tables use the unchanged evaluator's dense, arc-length-weighted reference samples and fixed nearest geometric correspondence. Candidate-path coverage is a separate diagnostic and does not change any official score.

## Visual verification

Open `http://127.0.0.1:8796/branches/` while the existing local review server is running. Each branch has:

- two reference-guided curved planes and four cross-sections;
- clean versus reference/mask-overlay views;
- a slider through native axial, coronal and sagittal slices;
- source XYZ coordinates, model geometry/label coverage, and a specific anatomical review question.

The full original comparison viewer remains at `/`, including noncoronary outputs. Unsupported or beyond-reference geometry is still a human-review issue; this investigation adds no endpoint or precision failure gate.

Reproduce with `.venv-br030/bin/python probes/vessel-geometry/authoring/br042_v3/branch_review.py`. Retained compact measurements and input hashes: `docs/evidence/br042-v3-branch-audit.json`. Generated images/data: `runs/br042-all-vessels-v3/review/branches/`.

## Implication for subsequent experiments

Keep discovery/geometry and correctly labeled coverage separate. Add a private error classification for omitted course, recovered-but-renumbered course, boundary disagreement and unresolved reference identity. A future generic prompt may explain multiple PDA/PLA variants and benchmark label inheritance using a dataset-wide rule established from the annotation protocol. Do not include this case's branch counts, coordinates, relative positions or model mistakes. Preserve V3 as originally scored; any alternative adjudicated labels should be separately versioned and applied symmetrically to all runs.
