# Explainer candidates: full catalogue map

Inventory snapshot: **2026-09-25**, composed from the [root catalogue](task-explorer/catalog.json), its eight collections and their linked briefs. This is a migration planning inventory, not authorization to migrate or an audit of native-asset readiness.

**205 entries / 145 task families / 8 repositories.** There are 195 agent tasks and 10 supporting entries (8 source studies, 1 calibration, 1 analysis). Variants retain separate IDs and contracts; 205 entries do not imply 205 independent rendering engines.

**Current delivery:** one canonical scripted story (`ours`), 199 other illustrated entries, and 5 WSI entries without an `illustration` binding. The last presentation run rendered 118 spatial and 82 static illustrations. Existing illustrations and native views are useful starting assets, but do not establish readiness for canonical HTML/MP4 exports.

## Scope and rollout choices

| Scope | Entries | Interpretation |
| --- | ---: | --- |
| Internal TB3 | 46 | 36 tasks + 10 supporting entries; closest to current group-owned contracts and local evidence |
| External catalogues | 159 | All task entries; source/asset rights and availability need checking per family |
| Already scripted | 1 | `ours`, an operation-only route-resampling teaching example |
| Remaining inventory | 204 | Planning candidates, including native WSI and non-task explanations |

**Recommended sequence (assistant recommendation):**

1. Make the pipeline genuinely support multiple recipes. The named-coronary/inventory pair is the nearest reuse test; it is only one option from this map.
2. Establish representative registration, cardiac motion, anatomy audit/localization and longitudinal stories. These test distinct transformations, time, object identity and correspondence rather than cosmetic variants.
3. Complete internal task families with native-image/WSI and segmentation support, preserving study/calibration/analysis roles. Use 2D where it communicates the operation more clearly.
4. Reuse proven recipes across external segmentation, localization, recognition, restoration and reporting variants; review contracts before sharing stories.
5. Add distinct CT/MRI, wave/optical reconstruction and physical-field recipes. Handle records, eligibility, forecasting and application workflows with appropriate 2D states.

Every batch delivers canonical stories, explicit bindings, complete HTML/MP4 exports, static fallbacks and acceptance receipts. A source/asset gap is recorded as deferred rather than filled with unrelated anatomy. Keep existing scenes available until their replacement passes review.

## Operation coverage

Counts use each entry’s primary catalogue category exactly once. These are scope counts, not effort estimates. A category can require several recipes, and several variants can share one.

| Operation | Entries | What the explanation must represent |
| --- | ---: | --- |
| [Recover paths and topology](#geometry) | 8 | Path selection, branch inventory, local repair with unchanged controls, and resampling; reflected-fringe geometry needs a separate recipe. |
| [Recover motion and mechanics](#motion-mechanics) | 7 | Time-indexed contours/meshes and corresponding material points; distinguish cavity deformation from myocardial mechanics. |
| [Register and match](#correspondence) | 6 | Moving/fixed views, linked points, transforms and residuals; distinguish rigid pose from deformation and cross-modality matching. |
| [Track findings and change](#longitudinal-analysis) | 5 | Visits, candidate identities, links, new/disappeared findings and measured change; separate detection from matching. |
| [Audit and correct annotations](#annotation-review) | 5 | Supplied interpretation, inspected inconsistency, local edit or unchanged control; never auto-reveal evaluator references. |
| [Find and localize](#localization) | 15 | Search region, positive/absent target and point/box/instance output; whole-slide search needs native multiscale imagery. |
| [Segment images](#segmentation) | 35 | Input pixels to semantic masks or separate instances; preserve binary/multiclass, count and measurement distinctions. |
| [Recognize and classify](#recognition) | 14 | Supplied object/candidate/image to identity or class; show evidence and ambiguity rather than inventing a discovery step. |
| [Reconstruct images](#image-reconstruction) | 46 | Measurements, acquisition geometry/forward model, reconstruction and data consistency; CT, MRI, optics and waves need distinct assets. |
| [Restore and synthesize images](#image-restoration) | 15 | Observed degradation and restored/synthesized image; distinguish denoising, resampling, super-resolution and modality synthesis. |
| [Estimate physical quantities](#quantification) | 7 | Observations, estimation and physical parameter/field with units; uncertainty is a distinct output, not decoration. |
| [Interpret and report](#reporting) | 22 | Evidence to claims/answers/report sections, including multimodal questions and tool chains; use readable 2D composition. |
| [Decode and transform data](#data-engineering) | 5 | Source records/frames, mapping and output structure; preserve identifiers, coordinates, temporal association and units. |
| [Check data quality](#data-quality) | 5 | Records or images, conflicting/invalid observations, and explicit issue evidence; avoid presenting an invented correction as truth. |
| [Predict outcomes](#prediction) | 8 | Available history, time cutoff, target and prediction; distinguish clinical risk from future physical fields. |
| [Apply eligibility criteria](#eligibility) | 1 | Patient evidence against individual criteria, with qualified match/non-match/unknown outcomes. |
| [Operate an application](#workflow-operation) | 1 | Requested UI state, actions and observable completion; explain the tool workflow without fabricated clinical inference. |

## Internal owners

| Owner | Entries | Tasks / supporting |
| --- | ---: | --- |
| anatomical-landmarks | 1 | 1 / 0 |
| anatomy-audit | 13 | 9 / 4 |
| cardiac-motion | 7 | 4 / 3 |
| lesion-localization | 6 | 6 / 0 |
| longitudinal-reading | 7 | 7 / 0 |
| registration | 5 | 4 / 1 |
| tubular-anatomy | 7 | 5 / 2 |

## External source catalogues

| Source | Entries |
| --- | ---: |
| healthagentbench | 15 |
| abra | 6 |
| bcer | 9 |
| automedbench | 50 |
| imaging101 | 58 |
| radagent | 2 |
| rexmle | 19 |

## Every candidate

Each entry appears once below, linked to its maintained brief. `legacy` means an existing conceptual illustration, not an accepted scripted migration. `native views` means no conceptual illustration binding; preserve the existing image/GT interaction. The recipe column names the present illustration kind, not a promised future implementation.

<a id="geometry"></a>
### Recover paths and topology — 8

| Candidate / source brief | Repository / role | Present recipe / state |
| --- | --- | --- |
| [Curate vessel connectivity tasks](../groups/tubular-anatomy/presentation/briefs/tb3-vessel-source-screen.md)<br>`tb3-vessel-source-screen` | tb3 / source-study | `vessel_source_screen` / legacy |
| [Repair a vessel connection without damaging anatomy](../groups/tubular-anatomy/presentation/briefs/tb3-vessel-connection-repair.md)<br>`tb3-vessel-connection-repair` | tb3 / task | `route_repair` / legacy |
| [Repair a vessel gap and unfold the route](../groups/tubular-anatomy/presentation/briefs/br030.md)<br>`ours` | tb3 / task | `route_unfold` / scripted pilot |
| [Repair an airway route while preserving supplied fragments](../groups/tubular-anatomy/presentation/briefs/tb3-airway-repair.md)<br>`tb3-airway-repair` | tb3 / task | `route_repair` / legacy |
| [Screen TopBrain predictions for a repair task](../groups/tubular-anatomy/presentation/briefs/tb3-topbrain-screen.md)<br>`tb3-topbrain-screen` | tb3 / source-study | `prediction_screen` / legacy |
| [Trace a named coronary artery](../groups/tubular-anatomy/presentation/briefs/tb3-named-coronary.md)<br>`tb3-named-coronary` | tb3 / task | `route_discovery` / legacy |
| [Discover and name coronary branches](../groups/tubular-anatomy/presentation/briefs/tb3-coronary-inventory.md)<br>`tb3-coronary-inventory` | tb3 / task | `route_discovery` / legacy |
| [Recover lens geometry from reflected fringe patterns](external-tasks/briefs/imaging101-differentiable-deflectometry.md)<br>`imaging101-differentiable-deflectometry` | imaging101 / task | `deflectometry` / legacy |

<a id="motion-mechanics"></a>
### Recover motion and mechanics — 7

| Candidate / source brief | Repository / role | Present recipe / state |
| --- | --- | --- |
| [Study cardiac reconstruction with supplied contours](../groups/cardiac-motion/presentation/briefs/tb3-cardiac-contour-feasibility.md)<br>`tb3-cardiac-contour-feasibility` | tb3 / source-study | `cardiac_contours` / legacy |
| [Study motion recovery from sparse contour anchors](../groups/cardiac-motion/presentation/briefs/tb3-cardiac-anchor-feasibility.md)<br>`tb3-cardiac-anchor-feasibility` | tb3 / source-study | `cardiac_anchors` / legacy |
| [Study dynamic myocardial models and reference mechanics](../groups/cardiac-motion/presentation/briefs/tb3-cardiac-material-feasibility.md)<br>`tb3-cardiac-material-feasibility` | tb3 / source-study | `cardiac_material` / legacy |
| [Recover cardiac material motion and compute mechanics](../groups/cardiac-motion/presentation/briefs/tb3-cardiac-material-motion.md)<br>`tb3-cardiac-material-motion` | tb3 / task | `dynamic_mesh` / legacy |
| [Recover a dynamic cavity from real ultrasound](../groups/cardiac-motion/presentation/briefs/tb3-real-echo-reconstruction.md)<br>`tb3-real-echo-reconstruction` | tb3 / task | `dynamic_mesh` / legacy |
| [Adapt a cavity model and measure contraction](../groups/cardiac-motion/presentation/briefs/tb3-clinical-cavity-adaptation.md)<br>`tb3-clinical-cavity-adaptation` | tb3 / task | `dynamic_mesh` / legacy |
| [Construct deforming meshes from supplied masks](../groups/cardiac-motion/presentation/briefs/tb3-mask-to-mechanics.md)<br>`tb3-mask-to-mechanics` | tb3 / task | `dynamic_mesh` / legacy |

<a id="correspondence"></a>
### Register and match — 6

| Candidate / source brief | Repository / role | Present recipe / state |
| --- | --- | --- |
| [Recover the pose of an oblique CT section](../groups/registration/presentation/briefs/tb3-oblique-pose.md)<br>`tb3-oblique-pose` | tb3 / task | `register` / legacy |
| [Transfer landmarks across respiratory deformation](../groups/registration/presentation/briefs/tb3-respiratory-correspondence.md)<br>`tb3-respiratory-correspondence` | tb3 / task | `point_correspondence` / legacy |
| [Analyze a single-view registration failure](../groups/registration/presentation/briefs/tb3-registration-analysis.md)<br>`tb3-registration-analysis` | tb3 / analysis | `registration_diagnosis` / legacy |
| [Audit MRI-to-intraoperative-ultrasound correspondences](../groups/registration/presentation/briefs/resect-mri-us-correspondence.md)<br>`resect-mri-us-correspondence` | tb3 / task | `point_correspondence` / legacy |
| [Correct two MRI-to-ultrasound point correspondences](../groups/registration/presentation/briefs/tb3-resect-point-pilot.md)<br>`tb3-resect-point-pilot` | tb3 / task | `point_correspondence` / legacy |
| [Align prostate MRI sequences](external-tasks/briefs/bcer-medium-register-prostate.md)<br>`bcer-medium-register-prostate` | bcer / task | `register` / legacy |

<a id="longitudinal-analysis"></a>
### Track findings and change — 5

| Candidate / source brief | Repository / role | Present recipe / state |
| --- | --- | --- |
| [Compare lesion extent and interpretation across MRI visits](../groups/longitudinal-reading/presentation/briefs/tb3-longitudinal-mri.md)<br>`tb3-longitudinal-mri` | tb3 / task | `longitudinal` / legacy |
| [Track CT lesions — Original image-only contract](../groups/longitudinal-reading/presentation/briefs/tb3-longitudinal-ct-original.md)<br>`tb3-longitudinal-ct-original` | tb3 / task | `longitudinal` / legacy |
| [Track CT lesions — Revised inclusion and instance contract](../groups/longitudinal-reading/presentation/briefs/tb3-longitudinal-ct-revised.md)<br>`tb3-longitudinal-ct-revised` | tb3 / task | `longitudinal` / legacy |
| [Track CT lesions — Comprehensive candidate contract](../groups/longitudinal-reading/presentation/briefs/tb3-longitudinal-ct-candidates.md)<br>`tb3-longitudinal-ct-candidates` | tb3 / task | `longitudinal` / legacy |
| [Compare two imaging studies over time](external-tasks/briefs/abra-longitudinal.md)<br>`abra-longitudinal` | abra / task | `longitudinal` / legacy |

<a id="annotation-review"></a>
### Audit and correct annotations — 5

| Candidate / source brief | Repository / role | Present recipe / state |
| --- | --- | --- |
| [Audit supplied anatomical labels](../groups/anatomy-audit/presentation/briefs/tb3-label-audit.md)<br>`tb3-label-audit` | tb3 / task | `anatomy_audit` / legacy |
| [Find foreign tissue inside a named mask](../groups/anatomy-audit/presentation/briefs/tb3-mixed-tissue-audit.md)<br>`tb3-mixed-tissue-audit` | tb3 / task | `anatomy_audit` / legacy |
| [Study geometric shortcuts in mask reasoning](../groups/anatomy-audit/presentation/briefs/tb3-mask-reasoning-study.md)<br>`tb3-mask-reasoning-study` | tb3 / source-study | `mask_shortcuts` / legacy |
| [Curate source anatomy and reference quality](../groups/anatomy-audit/presentation/briefs/tb3-anatomy-curation.md)<br>`tb3-anatomy-curation` | tb3 / source-study | `anatomy_curation` / legacy |
| [Correct an existing chest X-ray findings section](external-tasks/briefs/healthagentbench-cxr-correction.md)<br>`healthagentbench-cxr-correction` | healthagentbench / task | `report` / legacy |

<a id="localization"></a>
### Find and localize — 15

| Candidate / source brief | Repository / role | Present recipe / state |
| --- | --- | --- |
| [Locate named anatomy and detect unavailable targets](../groups/anatomical-landmarks/presentation/briefs/tb3-named-landmarks.md)<br>`tb3-named-landmarks` | tb3 / task | `landmark_point` / legacy |
| [Search for aneurysms and preserve negative cases](../groups/lesion-localization/presentation/briefs/tb3-aneurysm-localization.md)<br>`tb3-aneurysm-localization` | tb3 / task | `landmark_point` / legacy |
| [CAMELYON16 · 从全片找转移灶](../groups/lesion-localization/presentation/briefs/wsi-camelyon-search.md)<br>`wsi-camelyon-search` | tb3 / task | `—` / native views |
| [HiESD · 给每条胃组织建立病变地图](../groups/lesion-localization/presentation/briefs/wsi-hiesd-map.md)<br>`wsi-hiesd-map` | tb3 / task | `—` / native views |
| [Find tumor-bearing slide tiles](external-tasks/briefs/healthagentbench-tumor-tiles.md)<br>`healthagentbench-tumor-tiles` | healthagentbench / task | `tiles` / legacy |
| [Localize molecules in 3D from light-field views](external-tasks/briefs/imaging101-single-molecule-light-field.md)<br>`imaging101-single-molecule-light-field` | imaging101 / task | `molecules` / legacy |
| [Locate and label dental abnormalities](external-tasks/briefs/rexmle-dentex.md)<br>`rexmle-dentex` | rexmle / task | `detect` / legacy |
| [Locate and classify nuclei into three groups](external-tasks/briefs/rexmle-puma-track1-task2.md)<br>`rexmle-puma-track1-task2` | rexmle / task | `nuclei` / legacy |
| [Locate and classify ten nucleus types](external-tasks/briefs/rexmle-puma-track2-task2.md)<br>`rexmle-puma-track2-task2` | rexmle / task | `nuclei` / legacy |
| [Locate the Circle of Willis in a CT volume](external-tasks/briefs/rexmle-topcow-track1-task2.md)<br>`rexmle-topcow-track1-task2` | rexmle / task | `box3d` / legacy |
| [Locate the Circle of Willis in an MR volume](external-tasks/briefs/rexmle-topcow-track2-task2.md)<br>`rexmle-topcow-track2-task2` | rexmle / task | `box3d` / legacy |
| [Locate three blood-cell types in microscopy](external-tasks/briefs/automedbench-full-bccd-det-task.md)<br>`automedbench-full-bccd-det-task` | automedbench / task | `detect` / legacy |
| [Locate four dental disease categories](external-tasks/briefs/automedbench-full-dentex-det-task.md)<br>`automedbench-full-dentex-det-task` | automedbench / task | `detect` / legacy |
| [Locate pediatric wrist trauma findings](external-tasks/briefs/automedbench-full-grazpedwri-det-task.md)<br>`automedbench-full-grazpedwri-det-task` | automedbench / task | `detect` / legacy |
| [Draw boxes around chest X-ray abnormalities](external-tasks/briefs/automedbench-full-vindr-cxr-det-task.md)<br>`automedbench-full-vindr-cxr-det-task` | automedbench / task | `detect` / legacy |

<a id="segmentation"></a>
### Segment images — 35

| Candidate / source brief | Repository / role | Present recipe / state |
| --- | --- | --- |
| [Segment and name ten organs from CT](../groups/anatomy-audit/presentation/briefs/tb3-ct-organ-segmentation.md)<br>`tb3-ct-organ-segmentation` | tb3 / task | `segment` / legacy |
| [Segment dental anatomy — Original contract](../groups/anatomy-audit/presentation/briefs/tb3-dental-original.md)<br>`tb3-dental-original` | tb3 / task | `segment` / legacy |
| [Segment dental anatomy — F002 contract v2](../groups/anatomy-audit/presentation/briefs/tb3-dental-v2.md)<br>`tb3-dental-v2` | tb3 / task | `segment` / legacy |
| [Segment dental anatomy — F018 contract v3](../groups/anatomy-audit/presentation/briefs/tb3-dental-v3.md)<br>`tb3-dental-v3` | tb3 / task | `segment` / legacy |
| [Calibrate promptable segmenters on CT slices](../groups/anatomy-audit/presentation/briefs/tb3-segmentation-calibration.md)<br>`tb3-segmentation-calibration` | tb3 / tool-calibration | `segmenter_calibration` / legacy |
| [HuBMAP · 清点与测量肾小球](../groups/lesion-localization/presentation/briefs/wsi-hubmap-inventory.md)<br>`wsi-hubmap-inventory` | tb3 / task | `—` / native views |
| [TIGER · 在组织区室中计数免疫细胞](../groups/lesion-localization/presentation/briefs/wsi-tiger-context.md)<br>`wsi-tiger-context` | tb3 / task | `—` / native views |
| [Outline a lung nodule inside an imaging viewer](external-tasks/briefs/abra.md)<br>`abra` | abra / task | `nodule_outline` / legacy |
| [Build a kidney and tumor segmentation pipeline](external-tasks/briefs/automedbench.md)<br>`automedbench` | automedbench / task | `segment` / legacy |
| [Build a multi-organ CT segmentation pipeline](external-tasks/briefs/automedbench-tsg.md)<br>`automedbench-tsg` | automedbench / task | `segment` / legacy |
| [Learn to label the brain’s arterial ring in CTA](external-tasks/briefs/rexmle.md)<br>`rexmle` | rexmle / task | `segment` / legacy |
| [Segment brain tumor from four MRI sequences](external-tasks/briefs/bcer-short-segment-brain.md)<br>`bcer-short-segment-brain` | bcer / task | `segment` / legacy |
| [Segment ischemic stroke lesions](external-tasks/briefs/rexmle-isles22.md)<br>`rexmle-isles22` | rexmle / task | `segment` / legacy |
| [Separate individual cells in microscopy](external-tasks/briefs/rexmle-neurips-cellseg.md)<br>`rexmle-neurips-cellseg` | rexmle / task | `instances` / legacy |
| [Segment pancreatic tumor on diagnostic MRI](external-tasks/briefs/rexmle-panther-task1.md)<br>`rexmle-panther-task1` | rexmle / task | `segment` / legacy |
| [Segment pancreatic tumor on radiotherapy MRI](external-tasks/briefs/rexmle-panther-task2.md)<br>`rexmle-panther-task2` | rexmle / task | `segment` / legacy |
| [Label tissue types in melanoma histology](external-tasks/briefs/rexmle-puma-track1-task1.md)<br>`rexmle-puma-track1-task1` | rexmle / task | `segment` / legacy |
| [Segment the aorta and its branches](external-tasks/briefs/rexmle-seg-a.md)<br>`rexmle-seg-a` | rexmle / task | `segment` / legacy |
| [Label brain arteries on CT angiography](external-tasks/briefs/rexmle-topbrain-track1.md)<br>`rexmle-topbrain-track1` | rexmle / task | `segment` / legacy |
| [Label brain arteries on MR angiography](external-tasks/briefs/rexmle-topbrain-track2.md)<br>`rexmle-topbrain-track2` | rexmle / task | `segment` / legacy |
| [Label the Circle of Willis on MR angiography](external-tasks/briefs/rexmle-topcow-track2-task1.md)<br>`rexmle-topcow-track2-task1` | rexmle / task | `segment` / legacy |
| [Segment the lungs and airway tree](external-tasks/briefs/automedbench-full-aeropath-seg-task.md)<br>`automedbench-full-aeropath-seg-task` | automedbench / task | `segment` / legacy |
| [Segment primary colon cancer](external-tasks/briefs/automedbench-full-colon-seg-task.md)<br>`automedbench-full-colon-seg-task` | automedbench / task | `segment` / legacy |
| [Label seven fetal brain tissue types](external-tasks/briefs/automedbench-full-feta-seg-task.md)<br>`automedbench-full-feta-seg-task` | automedbench / task | `segment` / legacy |
| [Segment the left atrium in cardiac MRI](external-tasks/briefs/automedbench-full-heart-seg-task.md)<br>`automedbench-full-heart-seg-task` | automedbench / task | `segment` / legacy |
| [Segment liver vessels and tumors](external-tasks/briefs/automedbench-full-hepaticvessel-seg-task.md)<br>`automedbench-full-hepaticvessel-seg-task` | automedbench / task | `segment` / legacy |
| [Segment kidneys and kidney tumors](external-tasks/briefs/automedbench-full-kidney-seg-task.md)<br>`automedbench-full-kidney-seg-task` | automedbench / task | `segment` / legacy |
| [Segment liver and liver tumors](external-tasks/briefs/automedbench-full-liver-seg-task.md)<br>`automedbench-full-liver-seg-task` | automedbench / task | `segment` / legacy |
| [Label 21 structures around the pancreas](external-tasks/briefs/automedbench-full-pancreas-oar-seg-task.md)<br>`automedbench-full-pancreas-oar-seg-task` | automedbench / task | `segment` / legacy |
| [Segment pancreas and pancreatic tumors](external-tasks/briefs/automedbench-full-pancreas-seg-task.md)<br>`automedbench-full-pancreas-seg-task` | automedbench / task | `segment` / legacy |
| [Segment pancreas and tumor on arterial T1 MRI](external-tasks/briefs/automedbench-full-panther-t1-seg-task.md)<br>`automedbench-full-panther-t1-seg-task` | automedbench / task | `segment` / legacy |
| [Segment pancreas and tumor on MR-Linac T2 MRI](external-tasks/briefs/automedbench-full-panther-t2-seg-task.md)<br>`automedbench-full-panther-t2-seg-task` | automedbench / task | `segment` / legacy |
| [Label prostate zones on two-channel MRI](external-tasks/briefs/automedbench-full-prostate-seg-task.md)<br>`automedbench-full-prostate-seg-task` | automedbench / task | `segment` / legacy |
| [Segment the spleen in CT](external-tasks/briefs/automedbench-full-spleen-seg-task.md)<br>`automedbench-full-spleen-seg-task` | automedbench / task | `segment` / legacy |
| [Label 117 anatomical structures in CT](external-tasks/briefs/automedbench-full-tsg-multiorgan-seg-task.md)<br>`automedbench-full-tsg-multiorgan-seg-task` | automedbench / task | `segment` / legacy |

<a id="recognition"></a>
### Recognize and classify — 14

| Candidate / source brief | Repository / role | Present recipe / state |
| --- | --- | --- |
| [Name supplied anatomical objects](../groups/anatomy-audit/presentation/briefs/tb3-supplied-object-identity.md)<br>`tb3-supplied-object-identity` | tb3 / task | `object_identity` / legacy |
| [Assign identities to anonymous anatomical objects](../groups/anatomy-audit/presentation/briefs/tb3-unlabeled-anatomy-prototype.md)<br>`tb3-unlabeled-anatomy-prototype` | tb3 / task | `object_identity` / legacy |
| [HiESD · classify annotated gastric tissue patches](../groups/lesion-localization/presentation/briefs/wsi-hiesd-patches.md)<br>`wsi-hiesd-patches` | tb3 / task | `—` / native views |
| [Judge supplied CT candidates before linking them](../groups/longitudinal-reading/presentation/briefs/tb3-localized-candidate-recognition.md)<br>`tb3-localized-candidate-recognition` | tb3 / task | `candidate_judgment` / legacy |
| [Decide which findings are present in a chest CT](external-tasks/briefs/healthagentbench.md)<br>`healthagentbench` | healthagentbench / task | `multilabel` / legacy |
| [Predict glioma grade through a tool chain](external-tasks/briefs/bcer-medium-brain-grade-classify.md)<br>`bcer-medium-brain-grade-classify` | bcer / task | `classify` / legacy |
| [Recognize an image’s modality or display treatment](external-tasks/briefs/abra-vision-probe.md)<br>`abra-vision-probe` | abra / task | `classify` / legacy |
| [Classify arterial connections from CT angiography](external-tasks/briefs/rexmle-topcow-track1-task3.md)<br>`rexmle-topcow-track1-task3` | rexmle / task | `vesselgraph` / legacy |
| [Classify arterial connections from MR angiography](external-tasks/briefs/rexmle-topcow-track2-task3.md)<br>`rexmle-topcow-track2-task3` | rexmle / task | `vesselgraph` / legacy |
| [Classify brain MRI into four tumor categories](external-tasks/briefs/automedbench-full-braintumor-cls-task.md)<br>`automedbench-full-braintumor-cls-task` | automedbench / task | `classify` / legacy |
| [Classify pediatric X-rays as normal or pneumonia](external-tasks/briefs/automedbench-full-chest-xray-pneumonia-cls-task.md)<br>`automedbench-full-chest-xray-pneumonia-cls-task` | automedbench / task | `classify` / legacy |
| [Classify colorectal tissue into nine categories](external-tasks/briefs/automedbench-full-crc-histology-cls-task.md)<br>`automedbench-full-crc-histology-cls-task` | automedbench / task | `classify` / legacy |
| [Detect tumor in a histology tile’s center](external-tasks/briefs/automedbench-full-patchcamelyon-cls-task.md)<br>`automedbench-full-patchcamelyon-cls-task` | automedbench / task | `classify` / legacy |
| [Classify dermoscopy images into seven lesion types](external-tasks/briefs/automedbench-full-skin-lesion-cls-task.md)<br>`automedbench-full-skin-lesion-cls-task` | automedbench / task | `classify` / legacy |

<a id="image-reconstruction"></a>
### Reconstruct images — 46

| Candidate / source brief | Repository / role | Present recipe / state |
| --- | --- | --- |
| [Reconstruct an image from sparse CT projections](external-tasks/briefs/imaging101.md)<br>`imaging101` | imaging101 / task | `ct_phantom` / legacy |
| [Reconstruct accelerated cardiac MRI](external-tasks/briefs/bcer-short-recon-grappa.md)<br>`bcer-short-recon-grappa` | bcer / task | `mri` / legacy |
| [Reconstruct an object hidden around a corner](external-tasks/briefs/imaging101-confocal-nlos-fk.md)<br>`imaging101-confocal-nlos-fk` | imaging101 / task | `nlos` / legacy |
| [Recover a complex image from overlapping diffraction patterns](external-tasks/briefs/imaging101-conventional-ptychography.md)<br>`imaging101-conventional-ptychography` | imaging101 / task | `diffraction` / legacy |
| [Separate bone and soft tissue with dual-energy CT](external-tasks/briefs/imaging101-ct-dual-energy.md)<br>`imaging101-ct-dual-energy` | imaging101 / task | `dualct` / legacy |
| [Reconstruct a fan-beam CT slice](external-tasks/briefs/imaging101-ct-fan-beam.md)<br>`imaging101-ct-fan-beam` | imaging101 / task | `ct` / legacy |
| [Reconstruct CT from noisy photon counts](external-tasks/briefs/imaging101-ct-poisson-lowdose.md)<br>`imaging101-ct-poisson-lowdose` | imaging101 / task | `ct` / legacy |
| [Reconstruct a changing black-hole image](external-tasks/briefs/imaging101-eht-black-hole-dynamic.md)<br>`imaging101-eht-black-hole-dynamic` | imaging101 / task | `astro_dynamic` / legacy |
| [Reconstruct black-hole radio brightness](external-tasks/briefs/imaging101-eht-black-hole-original.md)<br>`imaging101-eht-black-hole-original` | imaging101 / task | `astronomy` / legacy |
| [Infer a 3D emission field near a black hole](external-tasks/briefs/imaging101-eht-black-hole-tomography.md)<br>`imaging101-eht-black-hole-tomography` | imaging101 / task | `astro_volume` / legacy |
| [Reconstruct conductivity from boundary voltages](external-tasks/briefs/imaging101-eit-conductivity-reconstruction.md)<br>`imaging101-eit-conductivity-reconstruction` | imaging101 / task | `conductivity` / legacy |
| [Recover a specimen from electron diffraction scans](external-tasks/briefs/imaging101-electron-ptychography.md)<br>`imaging101-electron-ptychography` | imaging101 / task | `diffraction` / legacy |
| [Reveal a planet in coronagraphic images](external-tasks/briefs/imaging101-exoplanet-imaging.md)<br>`imaging101-exoplanet-imaging` | imaging101 / task | `planet` / legacy |
| [Recover a high-resolution complex microscopy image](external-tasks/briefs/imaging101-fourier-ptychography.md)<br>`imaging101-fourier-ptychography` | imaging101 / task | `diffraction` / legacy |
| [Recover a 3D field from intensity-only microscopy](external-tasks/briefs/imaging101-fpm-inr-reconstruction.md)<br>`imaging101-fpm-inr-reconstruction` | imaging101 / task | `opticalvolume` / legacy |
| [Reconstruct a structured-illumination image sequence](external-tasks/briefs/imaging101-hessian-sim.md)<br>`imaging101-hessian-sim` | imaging101 / task | `image_sequence` / legacy |
| [Unwrap interferometric radar phase](external-tasks/briefs/imaging101-insar-phase-unwrapping.md)<br>`imaging101-insar-phase-unwrapping` | imaging101 / task | `phase` / legacy |
| [Reconstruct a scene from a diffuser-camera measurement](external-tasks/briefs/imaging101-lensless-imaging.md)<br>`imaging101-lensless-imaging` | imaging101 / task | `lensless` / legacy |
| [Recover a fluorescence volume from a light-field image](external-tasks/briefs/imaging101-light-field-microscope.md)<br>`imaging101-light-field-microscope` | imaging101 / task | `opticalvolume` / legacy |
| [Reconstruct a contrast-enhanced MRI time series](external-tasks/briefs/imaging101-mri-dynamic-dce.md)<br>`imaging101-mri-dynamic-dce` | imaging101 / task | `mri_dynamic` / legacy |
| [Reconstruct multi-coil MRI with GRAPPA](external-tasks/briefs/imaging101-mri-grappa.md)<br>`imaging101-mri-grappa` | imaging101 / task | `mri` / legacy |
| [Reconstruct MRI with a sparse wavelet prior](external-tasks/briefs/imaging101-mri-l1-wavelet.md)<br>`imaging101-mri-l1-wavelet` | imaging101 / task | `mri` / legacy |
| [Reconstruct MRI from a non-Cartesian trajectory](external-tasks/briefs/imaging101-mri-noncartesian-cs.md)<br>`imaging101-mri-noncartesian-cs` | imaging101 / task | `mri` / legacy |
| [Reconstruct brain MRI with a learned denoiser prior](external-tasks/briefs/imaging101-mri-pnp-admm.md)<br>`imaging101-mri-pnp-admm` | imaging101 / task | `mri` / legacy |
| [Reconstruct accelerated MRI with coil sensitivities](external-tasks/briefs/imaging101-mri-sense.md)<br>`imaging101-mri-sense` | imaging101 / task | `mri` / legacy |
| [Reconstruct knee MRI with total variation](external-tasks/briefs/imaging101-mri-tv.md)<br>`imaging101-mri-tv` | imaging101 / task | `mri` / legacy |
| [Reconstruct MRI with an unrolled variational network](external-tasks/briefs/imaging101-mri-varnet.md)<br>`imaging101-mri-varnet` | imaging101 / task | `mri` / legacy |
| [Reconstruct tracer activity from PET counts](external-tasks/briefs/imaging101-pet-mlem.md)<br>`imaging101-pet-mlem` | imaging101 / task | `pet` / legacy |
| [Reconstruct a photoacoustic pressure image](external-tasks/briefs/imaging101-photoacoustic-tomography.md)<br>`imaging101-photoacoustic-tomography` | imaging101 / task | `photoacoustic` / legacy |
| [Form an ultrasound image from plane-wave echoes](external-tasks/briefs/imaging101-plane-wave-ultrasound.md)<br>`imaging101-plane-wave-ultrasound` | imaging101 / task | `ultrasound` / legacy |
| [Reconstruct MRI with a self-similarity network prior](external-tasks/briefs/imaging101-pnp-mri-reconstruction.md)<br>`imaging101-pnp-mri-reconstruction` | imaging101 / task | `mri` / legacy |
| [Recover refractive index from reflected light](external-tasks/briefs/imaging101-reflection-odt.md)<br>`imaging101-reflection-odt` | imaging101 / task | `odt` / legacy |
| [Recover a volume from a detector-array microscope](external-tasks/briefs/imaging101-s2ism.md)<br>`imaging101-s2ism` | imaging101 / task | `opticalvolume` / legacy |
| [Infer subsurface velocity from waveforms](external-tasks/briefs/imaging101-seismic-fwi-original.md)<br>`imaging101-seismic-fwi-original` | imaging101 / task | `seismic` / legacy |
| [Recover subsurface reflectivity](external-tasks/briefs/imaging101-seismic-lsrtm-original.md)<br>`imaging101-seismic-lsrtm-original` | imaging101 / task | `seismic` / legacy |
| [Infer subsurface velocity from first arrivals](external-tasks/briefs/imaging101-seismic-traveltime-tomography.md)<br>`imaging101-seismic-traveltime-tomography` | imaging101 / task | `seismic` / legacy |
| [Recover an optical wavefront from spot shifts](external-tasks/briefs/imaging101-shack-hartmann.md)<br>`imaging101-shack-hartmann` | imaging101 / task | `wavefront` / legacy |
| [Recover a galaxy behind a gravitational lens](external-tasks/briefs/imaging101-shapelet-source-reconstruction.md)<br>`imaging101-shapelet-source-reconstruction` | imaging101 / task | `astronomy` / legacy |
| [Recover a spectral cube from one coded image](external-tasks/briefs/imaging101-spectral-snapshot-compressive-imaging.md)<br>`imaging101-spectral-snapshot-compressive-imaging` | imaging101 / task | `spectral_cube` / legacy |
| [Recover 3D refractive index from transmitted intensities](external-tasks/briefs/imaging101-ssnp-idt.md)<br>`imaging101-ssnp-idt` | imaging101 / task | `idt` / legacy |
| [Recover 3D refractive index from complex optical fields](external-tasks/briefs/imaging101-ssnp-odt.md)<br>`imaging101-ssnp-odt` | imaging101 / task | `odt` / legacy |
| [Map sound speed from ultrasound travel times](external-tasks/briefs/imaging101-ultrasound-sos-tomography.md)<br>`imaging101-ultrasound-sos-tomography` | imaging101 / task | `soundmap` / legacy |
| [Recover sound speed from full ultrasound wavefields](external-tasks/briefs/imaging101-usct-fwi.md)<br>`imaging101-usct-fwi` | imaging101 / task | `soundmap` / legacy |
| [Reconstruct a volume from tilted X-ray projections](external-tasks/briefs/imaging101-xray-laminography-tike.md)<br>`imaging101-xray-laminography-tike` | imaging101 / task | `ct` / legacy |
| [Reconstruct an X-ray specimen from diffraction scans](external-tasks/briefs/imaging101-xray-ptychography-tike.md)<br>`imaging101-xray-ptychography-tike` | imaging101 / task | `diffraction` / legacy |
| [Reconstruct a tooth from X-ray projections](external-tasks/briefs/imaging101-xray-tooth-gridrec.md)<br>`imaging101-xray-tooth-gridrec` | imaging101 / task | `ct` / legacy |

<a id="image-restoration"></a>
### Restore and synthesize images — 15

| Candidate / source brief | Repository / role | Present recipe / state |
| --- | --- | --- |
| [Denoise one MRI volume](external-tasks/briefs/bcer-short-denoise.md)<br>`bcer-short-denoise` | bcer / task | `denoise` / legacy |
| [Combine turbulent frames into a sharper lunar image](external-tasks/briefs/imaging101-lucky-imaging.md)<br>`imaging101-lucky-imaging` | imaging101 / task | `astronomy` / legacy |
| [Restore a noisy microscopy image](external-tasks/briefs/imaging101-microscope-denoising.md)<br>`imaging101-microscope-denoising` | imaging101 / task | `denoise` / legacy |
| [Enhance handheld ultrasound images](external-tasks/briefs/rexmle-usenhance.md)<br>`rexmle-usenhance` | rexmle / task | `denoise` / legacy |
| [Super-resolve contrast-enhanced brain-tumor MRI](external-tasks/briefs/automedbench-full-brats-t1c-sr-task.md)<br>`automedbench-full-brats-t1c-sr-task` | automedbench / task | `superres` / legacy |
| [Denoise DeepLesion CT slices](external-tasks/briefs/automedbench-full-deeplesion-denoising-task.md)<br>`automedbench-full-deeplesion-denoising-task` | automedbench / task | `denoise` / legacy |
| [Super-resolve T1 brain MRI from IXI](external-tasks/briefs/automedbench-full-ixi-t1-sr-task.md)<br>`automedbench-full-ixi-t1-sr-task` | automedbench / task | `superres` / legacy |
| [Denoise simulated low-dose CT slices](external-tasks/briefs/automedbench-full-ldct-denoising-task.md)<br>`automedbench-full-ldct-denoising-task` | automedbench / task | `denoise` / legacy |
| [Denoise LIDC-IDRI lung CT slices](external-tasks/briefs/automedbench-full-lidc-idri-denoising-task.md)<br>`automedbench-full-lidc-idri-denoising-task` | automedbench / task | `denoise` / legacy |
| [Double the resolution of an MRI slice](external-tasks/briefs/automedbench-full-mri-sr-task.md)<br>`automedbench-full-mri-sr-task` | automedbench / task | `superres` / legacy |
| [Super-resolve a chest X-ray image](external-tasks/briefs/automedbench-full-nih-cxr-sr-task.md)<br>`automedbench-full-nih-cxr-sr-task` | automedbench / task | `superres` / legacy |
| [Restore degraded CT-ORG volumes](external-tasks/briefs/automedbench-full-ctorg-ctsr-task.md)<br>`automedbench-full-ctorg-ctsr-task` | automedbench / task | `restore3d` / legacy |
| [Restore degraded pancreas CT volumes](external-tasks/briefs/automedbench-full-msd-pancreas-ctsr-task.md)<br>`automedbench-full-msd-pancreas-ctsr-task` | automedbench / task | `restore3d` / legacy |
| [Synthesize head-and-neck CT from MRI](external-tasks/briefs/automedbench-full-synthrad2025-mrct-task.md)<br>`automedbench-full-synthrad2025-mrct-task` | automedbench / task | `synthesis` / legacy |
| [Restore degraded TotalSegmentator CT volumes](external-tasks/briefs/automedbench-full-totalsegmentator-ctsr-task.md)<br>`automedbench-full-totalsegmentator-ctsr-task` | automedbench / task | `restore3d` / legacy |

<a id="quantification"></a>
### Estimate physical quantities — 7

| Candidate / source brief | Repository / role | Present recipe / state |
| --- | --- | --- |
| [Estimate gas temperature from Raman spectra](external-tasks/briefs/imaging101-cars-spectroscopy.md)<br>`imaging101-cars-spectroscopy` | imaging101 / task | `temperature` / legacy |
| [Estimate diffusion tensors from MRI](external-tasks/briefs/imaging101-diffusion-mri-dti.md)<br>`imaging101-diffusion-mri-dti` | imaging101 / task | `tensor` / legacy |
| [Estimate uncertainty in a black-hole image](external-tasks/briefs/imaging101-eht-black-hole-uq.md)<br>`imaging101-eht-black-hole-uq` | imaging101 / task | `astro_uncertainty` / legacy |
| [Infer evolving black-hole image features](external-tasks/briefs/imaging101-eht-black-hole-feature-extraction-dynamic.md)<br>`imaging101-eht-black-hole-feature-extraction-dynamic` | imaging101 / task | `astro_features` / legacy |
| [Separate chemical components in a spectral image](external-tasks/briefs/imaging101-mcr-hyperspectral.md)<br>`imaging101-mcr-hyperspectral` | imaging101 / task | `spectral` / legacy |
| [Estimate a quantitative T2 relaxation map](external-tasks/briefs/imaging101-mri-t2-mapping.md)<br>`imaging101-mri-t2-mapping` | imaging101 / task | `t2` / legacy |
| [Map chemical components inside cells](external-tasks/briefs/imaging101-raman-cell-phenotyping.md)<br>`imaging101-raman-cell-phenotyping` | imaging101 / task | `spectral` / legacy |

<a id="reporting"></a>
### Interpret and report — 22

| Candidate / source brief | Repository / role | Present recipe / state |
| --- | --- | --- |
| [Infer only clinical context supported by CT](../groups/longitudinal-reading/presentation/briefs/tb3-ct-context-inference.md)<br>`tb3-ct-context-inference` | tb3 / task | `report` / legacy |
| [Read imaging with supplied clinical reports](../groups/longitudinal-reading/presentation/briefs/tb3-report-backed-reading.md)<br>`tb3-report-backed-reading` | tb3 / task | `report` / legacy |
| [Complete a prostate MRI processing workflow](external-tasks/briefs/bcer.md)<br>`bcer` | bcer / task | `workflow` / legacy |
| [Write a chest CT report using specialist tools](external-tasks/briefs/radagent.md)<br>`radagent` | radagent / task | `report` / legacy |
| [Process cardiac cine MRI into a report](external-tasks/briefs/bcer-long-cardiac-full.md)<br>`bcer-long-cardiac-full` | bcer / task | `workflow` / legacy |
| [Process brain MRI into a tumor report](external-tasks/briefs/bcer-long-brain-full.md)<br>`bcer-long-brain-full` | bcer / task | `workflow` / legacy |
| [Produce a structured breast MRI assessment](external-tasks/briefs/abra-birads.md)<br>`abra-birads` | abra / task | `report` / legacy |
| [Answer a multiple-choice question about chest CT](external-tasks/briefs/radagent-vqa.md)<br>`radagent-vqa` | radagent / task | `vqa` / legacy |
| [Write a report for a frontal CheXpert Plus X-ray](external-tasks/briefs/automedbench-full-chexpert-plus-cxr-task.md)<br>`automedbench-full-chexpert-plus-cxr-task` | automedbench / task | `report` / legacy |
| [Write an IU/Open-i chest X-ray report](external-tasks/briefs/automedbench-full-iu-xray-report-task.md)<br>`automedbench-full-iu-xray-report-task` | automedbench / task | `report` / legacy |
| [Write chest X-ray findings from one or more views](external-tasks/briefs/automedbench-full-mimic-cxr-report-task.md)<br>`automedbench-full-mimic-cxr-report-task` | automedbench / task | `report` / legacy |
| [Caption histopathology images in the 100-case task](external-tasks/briefs/automedbench-full-pathology-caption-100-task.md)<br>`automedbench-full-pathology-caption-100-task` | automedbench / task | `caption` / legacy |
| [Caption histopathology images in the 500-case task](external-tasks/briefs/automedbench-full-pathology-caption-500-task.md)<br>`automedbench-full-pathology-caption-500-task` | automedbench / task | `caption` / legacy |
| [Answer medical questions using multiple image frames](external-tasks/briefs/automedbench-full-medframeqa-task.md)<br>`automedbench-full-medframeqa-task` | automedbench / task | `vqa` / legacy |
| [Answer expert-level multimodal medical questions](external-tasks/briefs/automedbench-full-medxpertqa-mm-task.md)<br>`automedbench-full-medxpertqa-mm-task` | automedbench / task | `vqa` / legacy |
| [Answer questions about pathology images](external-tasks/briefs/automedbench-full-pathvqa-task.md)<br>`automedbench-full-pathvqa-task` | automedbench / task | `vqa` / legacy |
| [Answer English radiology questions from SLAKE](external-tasks/briefs/automedbench-full-slake-task.md)<br>`automedbench-full-slake-task` | automedbench / task | `vqa` / legacy |
| [Answer questions about endoscopy images](external-tasks/briefs/automedbench-full-vqa-kvasir-task.md)<br>`automedbench-full-vqa-kvasir-task` | automedbench / task | `vqa` / legacy |
| [Answer medical-domain MMMU multiple-choice questions](external-tasks/briefs/automedbench-full-vqa-mmmu-medical-task.md)<br>`automedbench-full-vqa-mmmu-medical-task` | automedbench / task | `vqa` / legacy |
| [Answer medical image questions across authorized datasets](external-tasks/briefs/automedbench-full-vqa-omnimedvqa-task.md)<br>`automedbench-full-vqa-omnimedvqa-task` | automedbench / task | `vqa` / legacy |
| [Answer questions about biomedical publication figures](external-tasks/briefs/automedbench-full-vqa-pmc-vqa-task.md)<br>`automedbench-full-vqa-pmc-vqa-task` | automedbench / task | `vqa` / legacy |
| [Answer short questions about radiology images](external-tasks/briefs/automedbench-full-vqa-rad-task.md)<br>`automedbench-full-vqa-rad-task` | automedbench / task | `vqa` / legacy |

<a id="data-engineering"></a>
### Decode and transform data — 5

| Candidate / source brief | Repository / role | Present recipe / state |
| --- | --- | --- |
| [Reconstruct canonical MRI frame associations](../groups/anatomy-audit/presentation/briefs/tb3-mri-importer.md)<br>`tb3-mri-importer` | tb3 / task | `etl` / legacy |
| [Investigate historical task sources](../groups/anatomy-audit/presentation/briefs/tb3-history-sourcing.md)<br>`tb3-history-sourcing` | tb3 / source-study | `source_provenance` / legacy |
| [Convert EHR tables into MEDS events](external-tasks/briefs/healthagentbench-meds-etl.md)<br>`healthagentbench-meds-etl` | healthagentbench / task | `etl` / legacy |
| [Resample an MRI volume](external-tasks/briefs/bcer-short-superres.md)<br>`bcer-short-superres` | bcer / task | `superres` / legacy |
| [Answer questions about study metadata](external-tasks/briefs/abra-metadata-qa.md)<br>`abra-metadata-qa` | abra / task | `metadata` / legacy |

<a id="data-quality"></a>
### Check data quality — 5

| Candidate / source brief | Repository / role | Present recipe / state |
| --- | --- | --- |
| [Find mixed errors in EHR tables](external-tasks/briefs/healthagentbench-quality-combined.md)<br>`healthagentbench-quality-combined` | healthagentbench / task | `records` / legacy |
| [Find demographic contradictions](external-tasks/briefs/healthagentbench-quality-demographic-conflict.md)<br>`healthagentbench-quality-demographic-conflict` | healthagentbench / task | `records` / legacy |
| [Find impossible clinical values](external-tasks/briefs/healthagentbench-quality-impossible-value.md)<br>`healthagentbench-quality-impossible-value` | healthagentbench / task | `records` / legacy |
| [Find conflicting EHR observations](external-tasks/briefs/healthagentbench-quality-inconsistency.md)<br>`healthagentbench-quality-inconsistency` | healthagentbench / task | `records` / legacy |
| [Predict perceived low-dose CT image quality](external-tasks/briefs/rexmle-ldct-iqa.md)<br>`rexmle-ldct-iqa` | rexmle / task | `quality` / legacy |

<a id="prediction"></a>
### Predict outcomes — 8

| Candidate / source brief | Repository / role | Present recipe / state |
| --- | --- | --- |
| [Predict first diagnosis of acute myocardial infarction (heart attack)](external-tasks/briefs/healthagentbench-predict-acutemi.md)<br>`healthagentbench-predict-acutemi` | healthagentbench / task | `risk` / legacy |
| [Predict first diagnosis of celiac disease](external-tasks/briefs/healthagentbench-predict-celiac.md)<br>`healthagentbench-predict-celiac` | healthagentbench / task | `risk` / legacy |
| [Predict first diagnosis of hyperlipidemia (high blood lipids)](external-tasks/briefs/healthagentbench-predict-hyperlipidemia.md)<br>`healthagentbench-predict-hyperlipidemia` | healthagentbench / task | `risk` / legacy |
| [Predict first diagnosis of hypertension (high blood pressure)](external-tasks/briefs/healthagentbench-predict-hypertension.md)<br>`healthagentbench-predict-hypertension` | healthagentbench / task | `risk` / legacy |
| [Predict first diagnosis of systemic lupus erythematosus](external-tasks/briefs/healthagentbench-predict-lupus.md)<br>`healthagentbench-predict-lupus` | healthagentbench / task | `risk` / legacy |
| [Predict first diagnosis of pancreatic cancer](external-tasks/briefs/healthagentbench-predict-pancan.md)<br>`healthagentbench-predict-pancan` | healthagentbench / task | `risk` / legacy |
| [Forecast atmospheric fields from noisy history](external-tasks/briefs/imaging101-era5-tensorvar.md)<br>`imaging101-era5-tensorvar` | imaging101 / task | `geofield` / legacy |
| [Recover a future radar field from sparse observations](external-tasks/briefs/imaging101-weather-radar-data-assimilation.md)<br>`imaging101-weather-radar-data-assimilation` | imaging101 / task | `geofield` / legacy |

<a id="eligibility"></a>
### Apply eligibility criteria — 1

| Candidate / source brief | Repository / role | Present recipe / state |
| --- | --- | --- |
| [Match a patient to eligible trials](external-tasks/briefs/healthagentbench-trial-matching.md)<br>`healthagentbench-trial-matching` | healthagentbench / task | `trials` / legacy |

<a id="workflow-operation"></a>
### Operate an application — 1

| Candidate / source brief | Repository / role | Present recipe / state |
| --- | --- | --- |
| [Set the viewer to a requested state](external-tasks/briefs/abra-viewer-control.md)<br>`abra-viewer-control` | abra / task | `viewer` / legacy |
