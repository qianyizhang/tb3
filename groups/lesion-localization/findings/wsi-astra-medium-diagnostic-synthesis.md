# Astra medium WSI diagnostic studies

Five `openai/gpt-6-astra` medium conditions completed on four selected public pathology sources. Every final answer passed Harbor's **artifact contract**; their private task measures show partial agreement with the released references. These are one-case or three-ROI diagnostics, not population estimates or qualified clinical tasks. The [pinned evidence inventory](evidence/wsi-astra-medium-diagnostic-synthesis.json) retains task digests, attempts, evaluations and local raw-artifact pointers.

## At a glance

| Condition | Frozen private-reference measure | Reading |
| --- | --- | --- |
| HuBMAP full-slide glomerulus inventory | 86/99 polygons matched by 114 points; 13 missed references, 28 unmatched predictions | Object search worked on much of this slide; unmatched points need annotation-domain review. |
| TIGER image-only, three fixed ROIs | Cells matched 9/20, 136/175, 250/323; matched-cell compartment accuracy 0%, 12.5%, 64% | Cell localization was partial; attribution was weak in two ROIs. |
| TIGER tissue masks supplied, same ROIs | Cells matched 7/20, 141/175, 232/323; compartment accuracy 100%, 100%, 99.1% | The supplied mask made attribution nearly exact; cell matching changed in mixed directions. |
| CAMELYON16 positive-slide search | 4/6 Tumor polygons hit by 7 points; 3 points outside Tumor, 0 in Exclusion | Polygon hits on one large-region positive slide; no negative or sparse-lesion estimate. |
| HiESD coarse gastric map | 10,088/11,290 annotated pixels labeled (89.4%); 3,222/11,290 correct (28.5%) | Broad output covered annotated tissue but often assigned the wrong class. |

Harbor `reward=1` in each row means the answer file had the required shape and type. It is not the task score, a clinical verdict or task promotion. All four experiment records remain **Draft / Not assessed**.

## Task and reference boundary

| Task | Solver-visible input and requested output | Evaluator-only reference and scoring |
| --- | --- | --- |
| HuBMAP | Native PAS kidney TIFF, physical scale, GT-free overview and coordinate crop helper; submit deduplicated level-0 glomerulus centers. | 99 released polygons; one-to-one point inside a polygon or within 50 µm of its edge. |
| TIGER | Three fixed H&E ROI PNGs; submit merged lymphocyte/plasma-cell centers and compartment codes. The paired condition additionally supplies the official tissue masks. | Source cell boxes and tissue masks; centers within 20 ROI-local pixels, then compartment code at the matched source cell. |
| CAMELYON16 | Native positive lymph-node TIFF, GT-free overview and crop helper; submit level-0 suspected metastasis points. | Six Tumor polygons and one Exclusion polygon; fraction of polygons with a point, supported/outside/excluded points. Polygons are not independent lesions. |
| HiESD | Native gastric ESD SVS, GT-free overview and crop helper; submit a 623 × 448 one-channel six-class map with 0 for unknown. | Released coarse-grid XML raster; coverage and class correctness only at annotated pixels. Unannotated tissue is not known-normal GT. |

All conditions used pinned Docker task inputs and private separate verifiers. HuBMAP, CAMELYON and HiESD crop helpers logged calls, but direct TIFF reads were possible, so those counts are descriptive rather than enforced read budgets. The inspected model command traces had no explicit access to private `tests/` or `solution/` paths. This trace inspection does not establish absence of public-data pretraining exposure.

## Result and reference inspection

![GT-free HuBMAP overview beside post-hoc polygon and point overlay](figures/wsi-hubmap-astra-overview.jpg)

**HuBMAP post-hoc view.** Left: solver-visible GT-free overview of the complete `aaa6a05cc` PAS TIFF. Right: the same 814 × 1156 overview with evaluator-only polygons (magenta solid outlines), matched submitted centers (teal circles), unmatched predictions (amber triangles) and missed polygons (dark magenta X). The 13,013 × 18,484 level-0 coordinates were scaled linearly to the overview; symbols were enlarged for legibility. Matching is one-to-one with the frozen 50 µm edge tolerance. Amber points are unmatched to this reference, not adjudicated clinical false positives; many cluster near the lower tissue edge. The overlay was made **after** scoring and was not a search hint to the agent.

![HiESD input thumbnail, private coarse reference and Astra output](figures/wsi-hiesd-astra-coarse-map.jpg)

**HiESD post-hoc view.** The GT-free source thumbnail, evaluator-only XML-derived mask and submitted map share the 623 × 448 coarse grid. Display colors identify classes 1–6 only, with 0 transparent/unknown; the legend is inside the figure and is not a success/failure scale. The output assigns broad regions where the reference has smaller annotated regions. The model never emitted codes 4 (normal glands) or 5 (well differentiated adenocarcinoma). On annotated pixels, class 1 chronic gastritis was correct on 1,252/6,911; class 2 on 1,106/1,796; class 3 on 71/100; class 4 on 0/121; class 5 on 0/361; class 6 on 793/2,001. Those are selected-slide counts, not class-level population rates. Predicted labels on unannotated tissue cannot be judged against this reference.

## What the agent did

The [post-hoc trace diagnostic receipt](evidence/wsi-astra-medium-trace-diagnostics.json) recomputes matches with the pinned scorer and compares the saved answers with private references **after** the model runs. These checks did not change the task, score or answer. A generated crop can contain a reference object without proving the agent scrutinized that object; the helper ledgers also miss direct native TIFF reads.

| Condition | Consequential workflow in the saved trace | Execution effort |
| --- | --- | --- |
| HuBMAP | Read a GT-free overview, traversed native slide crops, entered candidate centers in resized-crop coordinates through `marks.py`/`add.py`, checked a marked overview and submitted 114 distinct level-0 points. | 22 logged helper crops; about 6 min 49 s wall time. |
| TIGER image-only | Split each of the three ROIs into four enlarged quadrants; typed cell centers into `annotate.py`, transformed them back to ROI coordinates, removed nearby duplicate marks and assigned compartment codes by visual judgment. | 12 enlarged quadrants, 448 submitted points; about 4 min 13 s. |
| TIGER tissue-supplied | Used a different set of four enlarged, partly overlapping tiles per ROI; typed cell centers and sampled each supplied tissue-mask pixel at the submitted center to fill the compartment code. | 12 enlarged tiles, 441 submitted points; about 4 min 2 s. |
| CAMELYON | Examined low-resolution pyramid crops and eight successful high-resolution helper crops, then wrote seven selected level-0 locations. One fragment crop initially exceeded the slide bounds and was corrected. | 8 logged helper crops; about 3 min 17 s. |
| HiESD | Examined a source overview, two direct pyramid crops and 19 native crops; then drew broad polygons for classes 1, 2 and 6 and one ellipse for class 3, clipped the map to an image-derived tissue-support mask, and saved a valid grayscale PNG. | 19 logged helper crops; about 4 min 19 s. |

Wall times include task startup and tool work and are only descriptive for these single attempts. The traces show no segmentation or cell-detection model inside the runtime. The work relied on visual sampling, coordinate transcription and hand-built scripts; the crop counts are not controlled read budgets.

## Where the outcomes diverged from the references

### HuBMAP: candidate decisions, especially at the lower tissue edge

The scorer matched 86/99 polygons. All **13 missed reference centroids** lie inside logged native-crop rectangles, so a simple uncovered-crop explanation is insufficient. The trace does not show a mark at those objects; omission during visual inspection, morphology confusion or a candidate-selection threshold remain possible. It cannot tell which one applies to each object without a blinded crop review.

Of the 28 unmatched submitted points, 20 have level-0 `y ≥ 12,000`; the [post-hoc overview](figures/wsi-hubmap-astra-overview.jpg) places many near the lower tissue edge. Only one would qualify for *any* released polygon before one-to-one assignment, and only two are within 200 level-0 pixels of a matched submitted point. Simple duplicate assignment explains little of this unmatched set. The agent explicitly described difficult, partly sclerosed profiles in the trace and included **19 points below 0.97 confidence**; none of those 19 matched the released polygons. All 86 matches carried 0.97 confidence, along with nine unmatched points. Thus a post-hoc 0.97 subset would retain 86 matches among 95 submissions, but this is a diagnostic slice on the same slide, not a validated confidence threshold or calibrated probability. The current scorer ignores confidence. Annotation-valid tissue scope and the disputed profiles still need pathology/reference review before calling the unmatched points false glomeruli.

### TIGER: tissue-label assistance works; cell detection remains variable

In the **image-only** answer, all nine matched roi1 cells were reference code 7 but submitted as code 0. In roi2 the answer gave code 2 to every one of its 154 points, while 118 of its 136 matched reference cells have code 6. This directly explains the low 0% and 12.5% matched-cell compartment accuracy in those ROIs; it is a tissue-attribution decision, not a matching or coordinate-transform failure. The coordinate marks themselves often matched within the 20-pixel tolerance.

In the **tissue-supplied** trace, the answer-generation command samples the official mask at each predicted center, so 7/7, 141/141 and 230/232 matched cells have the reference-center compartment code. The two remaining roi3 discrepancies are at mask boundaries: the predicted centers are 1.4 and 3.6 pixels from their matched reference centers, and their submitted codes equal the mask *at the predicted centers*. The scorer reads the mask *at the reference centers*. That is a precise coordinate/label-boundary mechanism, not evidence of failure to use the supplied mask.

Cell localization changed in mixed directions: reference cells matched by **both** runs numbered 6/132/205 across roi1/2/3; 3/4/45 were matched only image-only, and 1/9/27 only tissue-supplied. These are separate stochastic attempts with different tile layouts as well as different input assistance. The mask did not solve detection, and the observed detection differences cannot be attributed causally to mask availability. This is a **diagnostic** paired contrast on three fixed ROIs from one slide, not full-slide sTIL measurement.

### CAMELYON: coarse search found large regions, then missed two detail targets

Four of six released Tumor polygons contain a submitted point. The two unhit polygons fall inside a **direct low-resolution pyramid crop**, but neither intersects a logged high-resolution helper crop. That supports a failure to revisit those locations at detail scale in this run; it does not prove the agent recognized them in the low-resolution image. The three points outside every Tumor polygon are far from the released tumor boundaries, with nearest boundary distances of roughly 11,549, 13,315 and 18,655 level-0 pixels. They are unsupported *by this XML*, despite the answer's high confidence; whether they are actual malignant tissue, annotation omissions or lookalikes is unresolved. The failed out-of-bounds fragment crop cost two tool commands before correction, but did not invalidate the answer. The unit is **polygon hit**, not independent lesion detection, and this slide provides no negative-answer test.

### HiESD: broad class assignment, not just missing pixels

The agent labeled 10,088/11,290 annotated pixels, but 6,866 of those labels disagreed with the coarse XML; 1,202 annotated pixels remained unknown. The [source/reference/result view](figures/wsi-hiesd-astra-coarse-map.jpg) and `make_map.py` show broad hand-drawn class-2 and class-6 bands. Of 6,911 reference class-1 pixels, 2,288 were called class 2 and 2,610 class 6. The script never emitted code 4 or 5, so all 121 class-4 and 361 class-5 reference pixels were necessarily missed or mislabeled. This is a class-selection and coarse-boundary failure in the submitted map, though the trace alone cannot separate recognition from drawing/translation errors.

The output also labeled 31,865 pixels outside the XML-annotated region. The scorer does not penalize those pixels, and unannotated tissue is not known-normal; they are **unassessed**, not verified false positives. Broad filling can therefore produce high annotated coverage without a useful class map. The released XML is a coarse region reference, so this comparison cannot adjudicate individual glands, exact margins or invasion depth.

## Attribution and next discriminating checks

| Layer | What this evidence supports | What remains unresolved |
| --- | --- | --- |
| Agent workflow | HuBMAP misses remain after geometric crop coverage, placing the observable gap at the mark-selection stage; CAMELYON's two unhit polygons lacked detail review; HiESD's drawing script omitted two classes. | Whether every missed object was visually recognized, and whether reference-unmatched candidates are pathologically valid. |
| Assistance and coordinates | TIGER mask sampling largely fixes compartment coding; the two residual errors come from evaluating mask codes at a nearby *different* center. | Whether assistance changes cell detection under a fixed tile layout and replicated runs. |
| Task/reference/scorer | HuBMAP confidence is recorded but not scored; CAMELYON counts polygons; HiESD leaves outside-annotation labels unassessed and rewards coverage separately from correctness. | Annotation-domain adjudication, merged lesions, negative/small-lesion cases, and additional independent slides. |
| Runtime | All five Astra runs completed with valid artifact shape. Earlier auth/transport failures ended before image analysis. | No model-quality inference follows from those infrastructure attempts. |

The four task families have different units, targets, references and scorers, so their numeric scores are **not comparable** or poolable. All five completed conditions used Astra medium; there is no Sol-versus-Astra WSI performance comparison in this report. The most informative follow-ups are blinded review of HuBMAP unmatched points and missed crops, CAMELYON detail reads at the two unhit polygons plus negative/small-lesion slides, replicated TIGER runs with a fixed tile layout, and a HiESD class-level confusion review on additional annotated slides. These would be new experiments or adjudications, not retroactive score edits.

## Infrastructure and limits

Two earlier HuBMAP Sol/xhigh invocations ended before image analysis from credential/routing errors. The first Astra HuBMAP launch was interrupted after repeated WSI-sidecar `Network unreachable` errors. They remain separate `no_verdict` execution evidence; neither is a model miss. A corrected, restricted sidecar route then completed the five Astra conditions. Tiny route tests also showed that Sol/xhigh is accessible through the corrected route; the old host CLI error did not establish account-wide unavailability.

These public training examples may have appeared in model pretraining; exposure is unknown. Each source contributes one slide, except TIGER's three fixed ROIs from one slide. No model ranking, population sensitivity/specificity, clinical cell-count score, margin, invasion-depth or exact gland-boundary claim follows. The next evidence-changing work is independent slides and CAMELYON negative/small-lesion cases, adjudication of HuBMAP unmatched points, replicated TIGER assistance runs, and reference-domain review for HiESD. Existing scores and frozen bytes should remain unchanged.

## Provenance

- [Evidence manifest](evidence/wsi-astra-medium-diagnostic-synthesis.json) — 31 pinned records and 20 present selected local artifacts when collected; recheck it before reuse.
- [Post-hoc trace diagnostics](evidence/wsi-astra-medium-trace-diagnostics.json) — derived counts, scorer/geometry method and exact five attempt IDs. The local recomputation script is under `.local/wsi-agent-v1/trace-diagnostics.py`; raw agent traces and answers remain under the corresponding `.local/attempts/` directories.
- [HuBMAP protocol](../experiments/wsi-hubmap-inventory-astra-medium/protocol.md), [TIGER protocol](../experiments/wsi-tiger-context-astra-medium/protocol.md), [CAMELYON protocol](../experiments/wsi-camelyon-search-astra-medium/protocol.md), [HiESD protocol](../experiments/wsi-hiesd-map-astra-medium/protocol.md).
- The overview figures were derived offline after model completion from each task's GT-free source overview, saved answer and private evaluator reference. HuBMAP markers use the frozen one-to-one scorer rule; HiESD overlays use the same coarse grid and a display-only categorical palette. Full native images, raw answers, traces and credential material remain local under `.local/`.
