# Explainer scope and priority ledger

**154 core entries: 48 reviewed, 106 unfinished.** Keep 13 related candidates separate; exclude 38 reference, non-imaging, nonmedical and historical entries from automatic completion. All 205 records and prior reviews remain retained.

Audit date: **2026-09-29**. This is a local catalogue/brief scope survey, not a fresh upstream audit, clinical qualification or source-asset verification. Priority is an assistant judgment implementing the user’s request.

## Authority and resumption

- [Scope ledger](EXPLAINER-SCOPE.json) owns membership and group priority. [Review ledger](EXPLAINER-LEDGER.json) owns live review status, blockers and receipts. Join on `entry_id`.
- Statuses and the queue below are a dated snapshot; refresh them from the review ledger before starting work. The JSON pins the audited ledger hash and each brief hash.
- The later user clarification routes unfinished entries through source resolution first, then sound symbolic illustrations with a top reason/acquisition warning where actual data remains unavailable. See the current [workflow](EXPLAINER-WORKFLOW.md); historical blocker labels below do not imply proven external barriers.
- Only `automatic_completion=true` enters the queue. Sort by group order, then review-ledger order; skip already reviewed entries. Unclassified new entries require a scope review. A source blocker remains unfinished.
- This scope gate supersedes the old all-205 completion sequence. The active black-hole-original entry is excluded; preserve its unfinished files and any later receipts, and do not schedule more nonmedical work.
- The other chat was actively reviewing that entry during this audit. This file does not interrupt a running chat or enforce a runtime scheduler; it must reread the [completion plan](EXPLAINER-CANDIDATES.md) before its next selection. No message or stop command was sent.

## Group priorities

| Priority | Group | Total | Reviewed | Unfinished | Queue treatment |
| --- | --- | ---: | ---: | ---: | --- |
| P0 | Existing TB3 imaging questions and supporting research | 45 | 39 | 6 | core |
| P1 | Clinical image localization, segmentation, topology and correspondence | 41 | 3 | 38 | core |
| P1 | Image interpretation, reporting and imaging workflow support | 31 | 1 | 30 | core |
| P2 | Medical image formation, restoration and quantitative maps | 37 | 5 | 32 | core |
| P3 | Biomedical microscopy methods | 11 | 0 | 11 | candidate |
| P3 | Broader biomedical visual questions | 2 | 0 | 2 | candidate |
| — | Generic imaging and optical methods | 8 | 1 | 7 | reference-only |
| — | Healthcare without imaging | 12 | 0 | 12 | excluded-nonimaging |
| — | Explicitly nonmedical applications | 17 | 6 | 11 | excluded-nonmedical |
| — | Closed mixed investigation | 1 | 1 | 0 | historical |

Reviewed means recorded assistant visual/engineering review, not medical validity, task readiness or user acceptance. The full catalogue has 56 reviewed entries: 48 core and 8 outside core. Exclusion does not erase those reviews.

## Next work and limits

**P0: six internal entries remain.** Resolve the five cardiac source contracts, then the report-backed reading input gap. These are source-resolution priorities, not instructions to launch trials.

- `tb3-cardiac-contour-feasibility` — blocked-source-contract.
- `tb3-cardiac-anchor-feasibility` — blocked-source-contract.
- `tb3-cardiac-material-feasibility` — blocked-source-contract.
- `tb3-real-echo-reconstruction` — blocked-source-contract.
- `tb3-mask-to-mechanics` — blocked-source-contract.
- `tb3-report-backed-reading` — blocked-source-input.

**P1:** clinical structure and reading/workflow support. **P2:** reconstruction, restoration and quantitative imaging. Within each group use the existing ledger order; skip a genuine external dependency only after recording the exact gap and next action. No task is promoted merely because a sibling explainer is finished.

**Reopening:** candidates need a specific biomedical question and image/specimen plus output/reference contract; generic methods need a concrete medical application. Exclusions need a changed scope decision, with actor and source recorded. Historical records remain closed.

**Boundary checks:** EIT conductivity, photoacoustic tomography and ultrasound full-waveform inversion remain in the supplied audit’s medical-modality support group, but their briefs do not establish a clinical specimen. Verify that connection before authoring; move to candidates if it cannot be established. Pathology/cell segmentation remains relevant biomedical CV; microscopy acquisition alone does not establish the same question.

## Source reconciliation

| Source | Core | Candidates | Outside automatic completion, excluding candidates | Total |
| --- | ---: | ---: | ---: | ---: |
| tb3 | 45 | 0 | 1 | 46 |
| healthagentbench | 3 | 0 | 12 | 15 |
| abra | 6 | 0 | 0 | 6 |
| bcer | 9 | 0 | 0 | 9 |
| automedbench | 48 | 2 | 0 | 50 |
| imaging101 | 22 | 11 | 25 | 58 |
| radagent | 2 | 0 | 0 | 2 |
| rexmle | 19 | 0 | 0 | 19 |

## Entry register

Each entry appears exactly once. Titles link to the source brief; exact input/output excerpts, hashes and machine-readable queue eligibility are in the companion JSON. Status abbreviations: **reviewed** = recorded planar/spatial review; **contract gap** = blocked-source-contract; **input gap** = blocked-source-input; **pending review** = pending-operation-review.

### P0 · Existing TB3 imaging questions and supporting research

Resolve the six unfinished internal entries first; preserve reviewed variants and scientific limits.

| Entry / source brief | Status at audit |
| --- | --- |
| [tb3-named-landmarks](../groups/anatomical-landmarks/presentation/briefs/tb3-named-landmarks.md) — Locate named anatomy and detect unavailable targets | reviewed |
| [tb3-label-audit](../groups/anatomy-audit/presentation/briefs/tb3-label-audit.md) — Audit supplied anatomical labels | reviewed |
| [tb3-mixed-tissue-audit](../groups/anatomy-audit/presentation/briefs/tb3-mixed-tissue-audit.md) — Find foreign tissue inside a named mask | reviewed |
| [tb3-supplied-object-identity](../groups/anatomy-audit/presentation/briefs/tb3-supplied-object-identity.md) — Name supplied anatomical objects | reviewed |
| [tb3-unlabeled-anatomy-prototype](../groups/anatomy-audit/presentation/briefs/tb3-unlabeled-anatomy-prototype.md) — Assign identities to anonymous anatomical objects | reviewed |
| [tb3-ct-organ-segmentation](../groups/anatomy-audit/presentation/briefs/tb3-ct-organ-segmentation.md) — Segment and name ten organs from CT | reviewed |
| [tb3-dental-original](../groups/anatomy-audit/presentation/briefs/tb3-dental-original.md) — Segment dental anatomy — Original contract | reviewed |
| [tb3-dental-v2](../groups/anatomy-audit/presentation/briefs/tb3-dental-v2.md) — Segment dental anatomy — F002 contract v2 | reviewed |
| [tb3-dental-v3](../groups/anatomy-audit/presentation/briefs/tb3-dental-v3.md) — Segment dental anatomy — F018 contract v3 | reviewed |
| [tb3-mri-importer](../groups/anatomy-audit/presentation/briefs/tb3-mri-importer.md) — Reconstruct canonical MRI frame associations | reviewed |
| [tb3-segmentation-calibration](../groups/anatomy-audit/presentation/briefs/tb3-segmentation-calibration.md) — Calibrate promptable segmenters on CT slices | reviewed |
| [tb3-mask-reasoning-study](../groups/anatomy-audit/presentation/briefs/tb3-mask-reasoning-study.md) — Study geometric shortcuts in mask reasoning | reviewed |
| [tb3-anatomy-curation](../groups/anatomy-audit/presentation/briefs/tb3-anatomy-curation.md) — Curate source anatomy and reference quality | reviewed |
| [tb3-cardiac-contour-feasibility](../groups/cardiac-motion/presentation/briefs/tb3-cardiac-contour-feasibility.md) — Study cardiac reconstruction with supplied contours | contract gap |
| [tb3-cardiac-anchor-feasibility](../groups/cardiac-motion/presentation/briefs/tb3-cardiac-anchor-feasibility.md) — Study motion recovery from sparse contour anchors | contract gap |
| [tb3-cardiac-material-feasibility](../groups/cardiac-motion/presentation/briefs/tb3-cardiac-material-feasibility.md) — Study dynamic myocardial models and reference mechanics | contract gap |
| [tb3-cardiac-material-motion](../groups/cardiac-motion/presentation/briefs/tb3-cardiac-material-motion.md) — Recover cardiac material motion and compute mechanics | reviewed |
| [tb3-real-echo-reconstruction](../groups/cardiac-motion/presentation/briefs/tb3-real-echo-reconstruction.md) — Recover a dynamic cavity from real ultrasound | contract gap |
| [tb3-clinical-cavity-adaptation](../groups/cardiac-motion/presentation/briefs/tb3-clinical-cavity-adaptation.md) — Adapt a cavity model and measure contraction | reviewed |
| [tb3-mask-to-mechanics](../groups/cardiac-motion/presentation/briefs/tb3-mask-to-mechanics.md) — Construct deforming meshes from supplied masks | contract gap |
| [tb3-aneurysm-localization](../groups/lesion-localization/presentation/briefs/tb3-aneurysm-localization.md) — Search for aneurysms and preserve negative cases | reviewed |
| [wsi-camelyon-search](../groups/lesion-localization/presentation/briefs/wsi-camelyon-search.md) — CAMELYON16 · 从全片找转移灶 | reviewed |
| [wsi-hiesd-map](../groups/lesion-localization/presentation/briefs/wsi-hiesd-map.md) — HiESD · 给每条胃组织建立病变地图 | reviewed |
| [wsi-hiesd-patches](../groups/lesion-localization/presentation/briefs/wsi-hiesd-patches.md) — HiESD · classify annotated gastric tissue patches | reviewed |
| [wsi-hubmap-inventory](../groups/lesion-localization/presentation/briefs/wsi-hubmap-inventory.md) — HuBMAP · 清点与测量肾小球 | reviewed |
| [wsi-tiger-context](../groups/lesion-localization/presentation/briefs/wsi-tiger-context.md) — TIGER · 在组织区室中计数免疫细胞 | reviewed |
| [tb3-longitudinal-mri](../groups/longitudinal-reading/presentation/briefs/tb3-longitudinal-mri.md) — Compare lesion extent and interpretation across MRI visits | reviewed |
| [tb3-longitudinal-ct-original](../groups/longitudinal-reading/presentation/briefs/tb3-longitudinal-ct-original.md) — Track CT lesions — Original image-only contract | reviewed |
| [tb3-longitudinal-ct-revised](../groups/longitudinal-reading/presentation/briefs/tb3-longitudinal-ct-revised.md) — Track CT lesions — Revised inclusion and instance contract | reviewed |
| [tb3-longitudinal-ct-candidates](../groups/longitudinal-reading/presentation/briefs/tb3-longitudinal-ct-candidates.md) — Track CT lesions — Comprehensive candidate contract | reviewed |
| [tb3-localized-candidate-recognition](../groups/longitudinal-reading/presentation/briefs/tb3-localized-candidate-recognition.md) — Judge supplied CT candidates before linking them | reviewed |
| [tb3-ct-context-inference](../groups/longitudinal-reading/presentation/briefs/tb3-ct-context-inference.md) — Infer only clinical context supported by CT | reviewed |
| [tb3-report-backed-reading](../groups/longitudinal-reading/presentation/briefs/tb3-report-backed-reading.md) — Read imaging against private clinical reports | input gap |
| [tb3-oblique-pose](../groups/registration/presentation/briefs/tb3-oblique-pose.md) — Recover the pose of an oblique CT section | reviewed |
| [tb3-respiratory-correspondence](../groups/registration/presentation/briefs/tb3-respiratory-correspondence.md) — Transfer landmarks across respiratory deformation | reviewed |
| [tb3-registration-analysis](../groups/registration/presentation/briefs/tb3-registration-analysis.md) — Analyze a single-view registration failure | reviewed |
| [resect-mri-us-correspondence](../groups/registration/presentation/briefs/resect-mri-us-correspondence.md) — Audit MRI-to-intraoperative-ultrasound correspondences | reviewed |
| [tb3-resect-point-pilot](../groups/registration/presentation/briefs/tb3-resect-point-pilot.md) — Correct two MRI-to-ultrasound point correspondences | reviewed |
| [tb3-vessel-source-screen](../groups/tubular-anatomy/presentation/briefs/tb3-vessel-source-screen.md) — Curate vessel connectivity tasks | reviewed |
| [tb3-vessel-connection-repair](../groups/tubular-anatomy/presentation/briefs/tb3-vessel-connection-repair.md) — Repair a vessel connection without damaging anatomy | reviewed |
| [ours](../groups/tubular-anatomy/presentation/briefs/br030.md) — Repair a vessel gap and unfold the route | reviewed |
| [tb3-airway-repair](../groups/tubular-anatomy/presentation/briefs/tb3-airway-repair.md) — Repair an airway route while preserving supplied fragments | reviewed |
| [tb3-topbrain-screen](../groups/tubular-anatomy/presentation/briefs/tb3-topbrain-screen.md) — Screen TopBrain predictions for a repair task | reviewed |
| [tb3-named-coronary](../groups/tubular-anatomy/presentation/briefs/tb3-named-coronary.md) — Trace a named coronary artery | reviewed |
| [tb3-coronary-inventory](../groups/tubular-anatomy/presentation/briefs/tb3-coronary-inventory.md) — Discover and name coronary branches | reviewed |

### P1 · Clinical image localization, segmentation, topology and correspondence

Direct image-to-anatomy work, including pathology and cell delineation; prioritize capability coverage over duplicate dataset variants.

| Entry / source brief | Status at audit |
| --- | --- |
| [abra](../presentation/external-tasks/briefs/abra.md) — Outline a lung nodule inside an imaging viewer | reviewed |
| [automedbench](../presentation/external-tasks/briefs/automedbench.md) — Build a kidney and tumor segmentation pipeline | input gap |
| [automedbench-tsg](../presentation/external-tasks/briefs/automedbench-tsg.md) — Build a multi-organ CT segmentation pipeline | reviewed |
| [rexmle](../presentation/external-tasks/briefs/rexmle.md) — Learn to label the brain’s arterial ring in CTA | reviewed |
| [bcer-short-segment-brain](../presentation/external-tasks/briefs/bcer-short-segment-brain.md) — Segment brain tumor from four MRI sequences | contract gap |
| [bcer-medium-register-prostate](../presentation/external-tasks/briefs/bcer-medium-register-prostate.md) — Align prostate MRI sequences | contract gap |
| [abra-longitudinal](../presentation/external-tasks/briefs/abra-longitudinal.md) — Compare two imaging studies over time | contract gap |
| [rexmle-dentex](../presentation/external-tasks/briefs/rexmle-dentex.md) — Locate and label dental abnormalities | contract gap |
| [rexmle-isles22](../presentation/external-tasks/briefs/rexmle-isles22.md) — Segment ischemic stroke lesions | contract gap |
| [rexmle-neurips-cellseg](../presentation/external-tasks/briefs/rexmle-neurips-cellseg.md) — Separate individual cells in microscopy | contract gap |
| [rexmle-panther-task1](../presentation/external-tasks/briefs/rexmle-panther-task1.md) — Segment pancreatic tumor on diagnostic MRI | contract gap |
| [rexmle-panther-task2](../presentation/external-tasks/briefs/rexmle-panther-task2.md) — Segment pancreatic tumor on radiotherapy MRI | contract gap |
| [rexmle-puma-track1-task1](../presentation/external-tasks/briefs/rexmle-puma-track1-task1.md) — Label tissue types in melanoma histology | contract gap |
| [rexmle-puma-track1-task2](../presentation/external-tasks/briefs/rexmle-puma-track1-task2.md) — Locate and classify nuclei into three groups | contract gap |
| [rexmle-puma-track2-task2](../presentation/external-tasks/briefs/rexmle-puma-track2-task2.md) — Locate and classify ten nucleus types | contract gap |
| [rexmle-seg-a](../presentation/external-tasks/briefs/rexmle-seg-a.md) — Segment the aorta and its branches | contract gap |
| [rexmle-topbrain-track1](../presentation/external-tasks/briefs/rexmle-topbrain-track1.md) — Label brain arteries on CT angiography | contract gap |
| [rexmle-topbrain-track2](../presentation/external-tasks/briefs/rexmle-topbrain-track2.md) — Label brain arteries on MR angiography | contract gap |
| [rexmle-topcow-track2-task1](../presentation/external-tasks/briefs/rexmle-topcow-track2-task1.md) — Label the Circle of Willis on MR angiography | contract gap |
| [rexmle-topcow-track1-task2](../presentation/external-tasks/briefs/rexmle-topcow-track1-task2.md) — Locate the Circle of Willis in a CT volume | contract gap |
| [rexmle-topcow-track2-task2](../presentation/external-tasks/briefs/rexmle-topcow-track2-task2.md) — Locate the Circle of Willis in an MR volume | contract gap |
| [rexmle-topcow-track1-task3](../presentation/external-tasks/briefs/rexmle-topcow-track1-task3.md) — Classify arterial connections from CT angiography | contract gap |
| [rexmle-topcow-track2-task3](../presentation/external-tasks/briefs/rexmle-topcow-track2-task3.md) — Classify arterial connections from MR angiography | contract gap |
| [automedbench-full-bccd-det-task](../presentation/external-tasks/briefs/automedbench-full-bccd-det-task.md) — Locate three blood-cell types in microscopy | input gap |
| [automedbench-full-dentex-det-task](../presentation/external-tasks/briefs/automedbench-full-dentex-det-task.md) — Locate four dental disease categories | input gap |
| [automedbench-full-grazpedwri-det-task](../presentation/external-tasks/briefs/automedbench-full-grazpedwri-det-task.md) — Locate pediatric wrist trauma findings | input gap |
| [automedbench-full-vindr-cxr-det-task](../presentation/external-tasks/briefs/automedbench-full-vindr-cxr-det-task.md) — Draw boxes around chest X-ray abnormalities | input gap |
| [automedbench-full-aeropath-seg-task](../presentation/external-tasks/briefs/automedbench-full-aeropath-seg-task.md) — Segment the lungs and airway tree | input gap |
| [automedbench-full-colon-seg-task](../presentation/external-tasks/briefs/automedbench-full-colon-seg-task.md) — Segment primary colon cancer | input gap |
| [automedbench-full-feta-seg-task](../presentation/external-tasks/briefs/automedbench-full-feta-seg-task.md) — Label seven fetal brain tissue types | input gap |
| [automedbench-full-heart-seg-task](../presentation/external-tasks/briefs/automedbench-full-heart-seg-task.md) — Segment the left atrium in cardiac MRI | input gap |
| [automedbench-full-hepaticvessel-seg-task](../presentation/external-tasks/briefs/automedbench-full-hepaticvessel-seg-task.md) — Segment liver vessels and tumors | input gap |
| [automedbench-full-kidney-seg-task](../presentation/external-tasks/briefs/automedbench-full-kidney-seg-task.md) — Segment kidneys and kidney tumors | input gap |
| [automedbench-full-liver-seg-task](../presentation/external-tasks/briefs/automedbench-full-liver-seg-task.md) — Segment liver and liver tumors | input gap |
| [automedbench-full-pancreas-oar-seg-task](../presentation/external-tasks/briefs/automedbench-full-pancreas-oar-seg-task.md) — Label 21 structures around the pancreas | input gap |
| [automedbench-full-pancreas-seg-task](../presentation/external-tasks/briefs/automedbench-full-pancreas-seg-task.md) — Segment pancreas and pancreatic tumors | input gap |
| [automedbench-full-panther-t1-seg-task](../presentation/external-tasks/briefs/automedbench-full-panther-t1-seg-task.md) — Segment pancreas and tumor on arterial T1 MRI | input gap |
| [automedbench-full-panther-t2-seg-task](../presentation/external-tasks/briefs/automedbench-full-panther-t2-seg-task.md) — Segment pancreas and tumor on MR-Linac T2 MRI | input gap |
| [automedbench-full-prostate-seg-task](../presentation/external-tasks/briefs/automedbench-full-prostate-seg-task.md) — Label prostate zones on two-channel MRI | input gap |
| [automedbench-full-spleen-seg-task](../presentation/external-tasks/briefs/automedbench-full-spleen-seg-task.md) — Segment the spleen in CT | input gap |
| [automedbench-full-tsg-multiorgan-seg-task](../presentation/external-tasks/briefs/automedbench-full-tsg-multiorgan-seg-task.md) — Label 117 anatomical structures in CT | input gap |

### P1 · Image interpretation, reporting and imaging workflow support

Image-grounded diagnosis, reporting, VQA, viewer control and metadata support; qualify metadata/tool tasks as workflow support.

| Entry / source brief | Status at audit |
| --- | --- |
| [healthagentbench](../presentation/external-tasks/briefs/healthagentbench.md) — Decide which findings are present in a chest CT | input gap |
| [bcer](../presentation/external-tasks/briefs/bcer.md) — Complete a prostate MRI processing workflow | reviewed |
| [radagent](../presentation/external-tasks/briefs/radagent.md) — Write a chest CT report using specialist tools | input gap |
| [healthagentbench-tumor-tiles](../presentation/external-tasks/briefs/healthagentbench-tumor-tiles.md) — Find tumor-bearing slide tiles | contract gap |
| [healthagentbench-cxr-correction](../presentation/external-tasks/briefs/healthagentbench-cxr-correction.md) — Correct an existing chest X-ray findings section | contract gap |
| [bcer-medium-brain-grade-classify](../presentation/external-tasks/briefs/bcer-medium-brain-grade-classify.md) — Predict glioma grade through a tool chain | contract gap |
| [bcer-long-cardiac-full](../presentation/external-tasks/briefs/bcer-long-cardiac-full.md) — Process cardiac cine MRI into a report | contract gap |
| [bcer-long-brain-full](../presentation/external-tasks/briefs/bcer-long-brain-full.md) — Process brain MRI into a tumor report | contract gap |
| [abra-viewer-control](../presentation/external-tasks/briefs/abra-viewer-control.md) — Set the viewer to a requested state | contract gap |
| [abra-metadata-qa](../presentation/external-tasks/briefs/abra-metadata-qa.md) — Answer questions about study metadata | contract gap |
| [abra-vision-probe](../presentation/external-tasks/briefs/abra-vision-probe.md) — Recognize an image’s modality or display treatment | contract gap |
| [abra-birads](../presentation/external-tasks/briefs/abra-birads.md) — Produce a structured breast MRI assessment | contract gap |
| [radagent-vqa](../presentation/external-tasks/briefs/radagent-vqa.md) — Answer a multiple-choice question about chest CT | contract gap |
| [rexmle-ldct-iqa](../presentation/external-tasks/briefs/rexmle-ldct-iqa.md) — Predict perceived low-dose CT image quality | contract gap |
| [automedbench-full-braintumor-cls-task](../presentation/external-tasks/briefs/automedbench-full-braintumor-cls-task.md) — Classify brain MRI into four tumor categories | input gap |
| [automedbench-full-chest-xray-pneumonia-cls-task](../presentation/external-tasks/briefs/automedbench-full-chest-xray-pneumonia-cls-task.md) — Classify pediatric X-rays as normal or pneumonia | input gap |
| [automedbench-full-crc-histology-cls-task](../presentation/external-tasks/briefs/automedbench-full-crc-histology-cls-task.md) — Classify colorectal tissue into nine categories | input gap |
| [automedbench-full-patchcamelyon-cls-task](../presentation/external-tasks/briefs/automedbench-full-patchcamelyon-cls-task.md) — Detect tumor in a histology tile’s center | input gap |
| [automedbench-full-skin-lesion-cls-task](../presentation/external-tasks/briefs/automedbench-full-skin-lesion-cls-task.md) — Classify dermoscopy images into seven lesion types | input gap |
| [automedbench-full-chexpert-plus-cxr-task](../presentation/external-tasks/briefs/automedbench-full-chexpert-plus-cxr-task.md) — Write a report for a frontal CheXpert Plus X-ray | input gap |
| [automedbench-full-iu-xray-report-task](../presentation/external-tasks/briefs/automedbench-full-iu-xray-report-task.md) — Write an IU/Open-i chest X-ray report | input gap |
| [automedbench-full-mimic-cxr-report-task](../presentation/external-tasks/briefs/automedbench-full-mimic-cxr-report-task.md) — Write chest X-ray findings from one or more views | input gap |
| [automedbench-full-pathology-caption-100-task](../presentation/external-tasks/briefs/automedbench-full-pathology-caption-100-task.md) — Caption histopathology images in the 100-case task | input gap |
| [automedbench-full-pathology-caption-500-task](../presentation/external-tasks/briefs/automedbench-full-pathology-caption-500-task.md) — Caption histopathology images in the 500-case task | input gap |
| [automedbench-full-medframeqa-task](../presentation/external-tasks/briefs/automedbench-full-medframeqa-task.md) — Answer medical questions using multiple image frames | input gap |
| [automedbench-full-medxpertqa-mm-task](../presentation/external-tasks/briefs/automedbench-full-medxpertqa-mm-task.md) — Answer expert-level multimodal medical questions | input gap |
| [automedbench-full-pathvqa-task](../presentation/external-tasks/briefs/automedbench-full-pathvqa-task.md) — Answer questions about pathology images | input gap |
| [automedbench-full-slake-task](../presentation/external-tasks/briefs/automedbench-full-slake-task.md) — Answer English radiology questions from SLAKE | input gap |
| [automedbench-full-vqa-kvasir-task](../presentation/external-tasks/briefs/automedbench-full-vqa-kvasir-task.md) — Answer questions about endoscopy images | input gap |
| [automedbench-full-vqa-omnimedvqa-task](../presentation/external-tasks/briefs/automedbench-full-vqa-omnimedvqa-task.md) — Answer medical image questions across authorized datasets | input gap |
| [automedbench-full-vqa-rad-task](../presentation/external-tasks/briefs/automedbench-full-vqa-rad-task.md) — Answer short questions about radiology images | input gap |

### P2 · Medical image formation, restoration and quantitative maps

Lower priority than clinical image understanding; source and medical-use checks precede authoring.

| Entry / source brief | Status at audit |
| --- | --- |
| [imaging101](../presentation/external-tasks/briefs/imaging101.md) — Reconstruct an image from sparse CT projections | reviewed |
| [bcer-short-denoise](../presentation/external-tasks/briefs/bcer-short-denoise.md) — Denoise one MRI volume | contract gap |
| [bcer-short-superres](../presentation/external-tasks/briefs/bcer-short-superres.md) — Resample an MRI volume | contract gap |
| [bcer-short-recon-grappa](../presentation/external-tasks/briefs/bcer-short-recon-grappa.md) — Reconstruct accelerated cardiac MRI | contract gap |
| [imaging101-ct-dual-energy](../presentation/external-tasks/briefs/imaging101-ct-dual-energy.md) — Separate bone and soft tissue with dual-energy CT | reviewed |
| [imaging101-ct-fan-beam](../presentation/external-tasks/briefs/imaging101-ct-fan-beam.md) — Reconstruct a fan-beam CT slice | reviewed |
| [imaging101-ct-poisson-lowdose](../presentation/external-tasks/briefs/imaging101-ct-poisson-lowdose.md) — Reconstruct CT from noisy photon counts | input gap |
| [imaging101-diffusion-mri-dti](../presentation/external-tasks/briefs/imaging101-diffusion-mri-dti.md) — Estimate diffusion tensors from MRI | reviewed |
| [imaging101-eit-conductivity-reconstruction](../presentation/external-tasks/briefs/imaging101-eit-conductivity-reconstruction.md) — Reconstruct conductivity from boundary voltages | contract gap |
| [imaging101-mri-dynamic-dce](../presentation/external-tasks/briefs/imaging101-mri-dynamic-dce.md) — Reconstruct a contrast-enhanced MRI time series | contract gap |
| [imaging101-mri-grappa](../presentation/external-tasks/briefs/imaging101-mri-grappa.md) — Reconstruct multi-coil MRI with GRAPPA | contract gap |
| [imaging101-mri-l1-wavelet](../presentation/external-tasks/briefs/imaging101-mri-l1-wavelet.md) — Reconstruct MRI with a sparse wavelet prior | contract gap |
| [imaging101-mri-noncartesian-cs](../presentation/external-tasks/briefs/imaging101-mri-noncartesian-cs.md) — Reconstruct MRI from a non-Cartesian trajectory | contract gap |
| [imaging101-mri-pnp-admm](../presentation/external-tasks/briefs/imaging101-mri-pnp-admm.md) — Reconstruct brain MRI with a learned denoiser prior | contract gap |
| [imaging101-mri-sense](../presentation/external-tasks/briefs/imaging101-mri-sense.md) — Reconstruct accelerated MRI with coil sensitivities | contract gap |
| [imaging101-mri-t2-mapping](../presentation/external-tasks/briefs/imaging101-mri-t2-mapping.md) — Estimate a quantitative T2 relaxation map | contract gap |
| [imaging101-mri-tv](../presentation/external-tasks/briefs/imaging101-mri-tv.md) — Reconstruct knee MRI with total variation | reviewed |
| [imaging101-mri-varnet](../presentation/external-tasks/briefs/imaging101-mri-varnet.md) — Reconstruct MRI with an unrolled variational network | contract gap |
| [imaging101-pet-mlem](../presentation/external-tasks/briefs/imaging101-pet-mlem.md) — Reconstruct tracer activity from PET counts | contract gap |
| [imaging101-photoacoustic-tomography](../presentation/external-tasks/briefs/imaging101-photoacoustic-tomography.md) — Reconstruct a photoacoustic pressure image | contract gap |
| [imaging101-plane-wave-ultrasound](../presentation/external-tasks/briefs/imaging101-plane-wave-ultrasound.md) — Form an ultrasound image from plane-wave echoes | contract gap |
| [imaging101-pnp-mri-reconstruction](../presentation/external-tasks/briefs/imaging101-pnp-mri-reconstruction.md) — Reconstruct MRI with a self-similarity network prior | contract gap |
| [imaging101-ultrasound-sos-tomography](../presentation/external-tasks/briefs/imaging101-ultrasound-sos-tomography.md) — Map sound speed from ultrasound travel times | contract gap |
| [imaging101-usct-fwi](../presentation/external-tasks/briefs/imaging101-usct-fwi.md) — Recover sound speed from full ultrasound wavefields | contract gap |
| [imaging101-xray-tooth-gridrec](../presentation/external-tasks/briefs/imaging101-xray-tooth-gridrec.md) — Reconstruct a tooth from X-ray projections | contract gap |
| [rexmle-usenhance](../presentation/external-tasks/briefs/rexmle-usenhance.md) — Enhance handheld ultrasound images | contract gap |
| [automedbench-full-brats-t1c-sr-task](../presentation/external-tasks/briefs/automedbench-full-brats-t1c-sr-task.md) — Super-resolve contrast-enhanced brain-tumor MRI | input gap |
| [automedbench-full-deeplesion-denoising-task](../presentation/external-tasks/briefs/automedbench-full-deeplesion-denoising-task.md) — Denoise DeepLesion CT slices | input gap |
| [automedbench-full-ixi-t1-sr-task](../presentation/external-tasks/briefs/automedbench-full-ixi-t1-sr-task.md) — Super-resolve T1 brain MRI from IXI | input gap |
| [automedbench-full-ldct-denoising-task](../presentation/external-tasks/briefs/automedbench-full-ldct-denoising-task.md) — Denoise simulated low-dose CT slices | input gap |
| [automedbench-full-lidc-idri-denoising-task](../presentation/external-tasks/briefs/automedbench-full-lidc-idri-denoising-task.md) — Denoise LIDC-IDRI lung CT slices | input gap |
| [automedbench-full-mri-sr-task](../presentation/external-tasks/briefs/automedbench-full-mri-sr-task.md) — Double the resolution of an MRI slice | input gap |
| [automedbench-full-nih-cxr-sr-task](../presentation/external-tasks/briefs/automedbench-full-nih-cxr-sr-task.md) — Super-resolve a chest X-ray image | input gap |
| [automedbench-full-ctorg-ctsr-task](../presentation/external-tasks/briefs/automedbench-full-ctorg-ctsr-task.md) — Restore degraded CT-ORG volumes | input gap |
| [automedbench-full-msd-pancreas-ctsr-task](../presentation/external-tasks/briefs/automedbench-full-msd-pancreas-ctsr-task.md) — Restore degraded pancreas CT volumes | input gap |
| [automedbench-full-synthrad2025-mrct-task](../presentation/external-tasks/briefs/automedbench-full-synthrad2025-mrct-task.md) — Synthesize head-and-neck CT from MRI | input gap |
| [automedbench-full-totalsegmentator-ctsr-task](../presentation/external-tasks/briefs/automedbench-full-totalsegmentator-ctsr-task.md) — Restore degraded TotalSegmentator CT volumes | input gap |

### P3 · Biomedical microscopy methods

Hold outside automatic completion until a concrete biomedical research question, specimen and evaluation contract are recorded.

| Entry / source brief | Status at audit |
| --- | --- |
| [imaging101-fourier-ptychography](../presentation/external-tasks/briefs/imaging101-fourier-ptychography.md) — Recover a high-resolution complex microscopy image | contract gap |
| [imaging101-fpm-inr-reconstruction](../presentation/external-tasks/briefs/imaging101-fpm-inr-reconstruction.md) — Recover a 3D field from intensity-only microscopy | contract gap |
| [imaging101-hessian-sim](../presentation/external-tasks/briefs/imaging101-hessian-sim.md) — Reconstruct a structured-illumination image sequence | contract gap |
| [imaging101-light-field-microscope](../presentation/external-tasks/briefs/imaging101-light-field-microscope.md) — Recover a fluorescence volume from a light-field image | contract gap |
| [imaging101-microscope-denoising](../presentation/external-tasks/briefs/imaging101-microscope-denoising.md) — Restore a noisy microscopy image | contract gap |
| [imaging101-raman-cell-phenotyping](../presentation/external-tasks/briefs/imaging101-raman-cell-phenotyping.md) — Map chemical components inside cells | contract gap |
| [imaging101-reflection-odt](../presentation/external-tasks/briefs/imaging101-reflection-odt.md) — Recover refractive index from reflected light | contract gap |
| [imaging101-s2ism](../presentation/external-tasks/briefs/imaging101-s2ism.md) — Recover a volume from a detector-array microscope | contract gap |
| [imaging101-single-molecule-light-field](../presentation/external-tasks/briefs/imaging101-single-molecule-light-field.md) — Localize molecules in 3D from light-field views | contract gap |
| [imaging101-ssnp-idt](../presentation/external-tasks/briefs/imaging101-ssnp-idt.md) — Recover 3D refractive index from transmitted intensities | contract gap |
| [imaging101-ssnp-odt](../presentation/external-tasks/briefs/imaging101-ssnp-odt.md) — Recover 3D refractive index from complex optical fields | contract gap |

### P3 · Broader biomedical visual questions

Hold outside automatic completion until an image-grounded clinical subset and its research value are established.

| Entry / source brief | Status at audit |
| --- | --- |
| [automedbench-full-vqa-mmmu-medical-task](../presentation/external-tasks/briefs/automedbench-full-vqa-mmmu-medical-task.md) — Answer medical-domain MMMU multiple-choice questions | input gap |
| [automedbench-full-vqa-pmc-vqa-task](../presentation/external-tasks/briefs/automedbench-full-vqa-pmc-vqa-task.md) — Answer questions about biomedical publication figures | input gap |

### Outside queue · Generic imaging and optical methods

Retain as method references; require a concrete medical task and source/GT link before promotion.

| Entry / source brief | Status at audit |
| --- | --- |
| [imaging101-conventional-ptychography](../presentation/external-tasks/briefs/imaging101-conventional-ptychography.md) — Recover a complex image from overlapping diffraction patterns | reviewed |
| [imaging101-electron-ptychography](../presentation/external-tasks/briefs/imaging101-electron-ptychography.md) — Recover a specimen from electron diffraction scans | contract gap |
| [imaging101-lensless-imaging](../presentation/external-tasks/briefs/imaging101-lensless-imaging.md) — Reconstruct a scene from a diffuser-camera measurement | contract gap |
| [imaging101-mcr-hyperspectral](../presentation/external-tasks/briefs/imaging101-mcr-hyperspectral.md) — Separate chemical components in a spectral image | contract gap |
| [imaging101-shack-hartmann](../presentation/external-tasks/briefs/imaging101-shack-hartmann.md) — Recover an optical wavefront from spot shifts | contract gap |
| [imaging101-spectral-snapshot-compressive-imaging](../presentation/external-tasks/briefs/imaging101-spectral-snapshot-compressive-imaging.md) — Recover a spectral cube from one coded image | contract gap |
| [imaging101-xray-laminography-tike](../presentation/external-tasks/briefs/imaging101-xray-laminography-tike.md) — Reconstruct a volume from tilted X-ray projections | contract gap |
| [imaging101-xray-ptychography-tike](../presentation/external-tasks/briefs/imaging101-xray-ptychography-tike.md) — Reconstruct an X-ray specimen from diffraction scans | contract gap |

### Outside queue · Healthcare without imaging

Exclude from the imaging completion queue; a separate non-imaging program would require explicit scope.

| Entry / source brief | Status at audit |
| --- | --- |
| [healthagentbench-trial-matching](../presentation/external-tasks/briefs/healthagentbench-trial-matching.md) — Match a patient to eligible trials | contract gap |
| [healthagentbench-quality-combined](../presentation/external-tasks/briefs/healthagentbench-quality-combined.md) — Find mixed errors in EHR tables | contract gap |
| [healthagentbench-quality-demographic-conflict](../presentation/external-tasks/briefs/healthagentbench-quality-demographic-conflict.md) — Find demographic contradictions | contract gap |
| [healthagentbench-quality-impossible-value](../presentation/external-tasks/briefs/healthagentbench-quality-impossible-value.md) — Find impossible clinical values | contract gap |
| [healthagentbench-quality-inconsistency](../presentation/external-tasks/briefs/healthagentbench-quality-inconsistency.md) — Find conflicting EHR observations | contract gap |
| [healthagentbench-predict-acutemi](../presentation/external-tasks/briefs/healthagentbench-predict-acutemi.md) — Predict first diagnosis of acute myocardial infarction (heart attack) | contract gap |
| [healthagentbench-predict-celiac](../presentation/external-tasks/briefs/healthagentbench-predict-celiac.md) — Predict first diagnosis of celiac disease | contract gap |
| [healthagentbench-predict-hyperlipidemia](../presentation/external-tasks/briefs/healthagentbench-predict-hyperlipidemia.md) — Predict first diagnosis of hyperlipidemia (high blood lipids) | contract gap |
| [healthagentbench-predict-hypertension](../presentation/external-tasks/briefs/healthagentbench-predict-hypertension.md) — Predict first diagnosis of hypertension (high blood pressure) | contract gap |
| [healthagentbench-predict-lupus](../presentation/external-tasks/briefs/healthagentbench-predict-lupus.md) — Predict first diagnosis of systemic lupus erythematosus | contract gap |
| [healthagentbench-predict-pancan](../presentation/external-tasks/briefs/healthagentbench-predict-pancan.md) — Predict first diagnosis of pancreatic cancer | contract gap |
| [healthagentbench-meds-etl](../presentation/external-tasks/briefs/healthagentbench-meds-etl.md) — Convert EHR tables into MEDS events | contract gap |

### Outside queue · Explicitly nonmedical applications

Exclude from active medical work; mathematical similarity alone does not establish relevance.

| Entry / source brief | Status at audit |
| --- | --- |
| [imaging101-cars-spectroscopy](../presentation/external-tasks/briefs/imaging101-cars-spectroscopy.md) — Estimate gas temperature from Raman spectra | reviewed |
| [imaging101-confocal-nlos-fk](../presentation/external-tasks/briefs/imaging101-confocal-nlos-fk.md) — Reconstruct an object hidden around a corner | reviewed |
| [imaging101-differentiable-deflectometry](../presentation/external-tasks/briefs/imaging101-differentiable-deflectometry.md) — Recover lens geometry from refracted fringe patterns | reviewed |
| [imaging101-eht-black-hole-uq](../presentation/external-tasks/briefs/imaging101-eht-black-hole-uq.md) — Estimate uncertainty in a black-hole image | reviewed |
| [imaging101-eht-black-hole-dynamic](../presentation/external-tasks/briefs/imaging101-eht-black-hole-dynamic.md) — Reconstruct a changing black-hole image | reviewed |
| [imaging101-eht-black-hole-feature-extraction-dynamic](../presentation/external-tasks/briefs/imaging101-eht-black-hole-feature-extraction-dynamic.md) — Infer evolving black-hole image features | reviewed |
| [imaging101-eht-black-hole-original](../presentation/external-tasks/briefs/imaging101-eht-black-hole-original.md) — Reconstruct black-hole radio brightness | pending review |
| [imaging101-eht-black-hole-tomography](../presentation/external-tasks/briefs/imaging101-eht-black-hole-tomography.md) — Infer a 3D emission field near a black hole | contract gap |
| [imaging101-era5-tensorvar](../presentation/external-tasks/briefs/imaging101-era5-tensorvar.md) — Forecast atmospheric fields from noisy history | contract gap |
| [imaging101-exoplanet-imaging](../presentation/external-tasks/briefs/imaging101-exoplanet-imaging.md) — Reveal a planet in coronagraphic images | contract gap |
| [imaging101-insar-phase-unwrapping](../presentation/external-tasks/briefs/imaging101-insar-phase-unwrapping.md) — Unwrap interferometric radar phase | contract gap |
| [imaging101-lucky-imaging](../presentation/external-tasks/briefs/imaging101-lucky-imaging.md) — Combine turbulent frames into a sharper lunar image | contract gap |
| [imaging101-seismic-fwi-original](../presentation/external-tasks/briefs/imaging101-seismic-fwi-original.md) — Infer subsurface velocity from waveforms | contract gap |
| [imaging101-seismic-lsrtm-original](../presentation/external-tasks/briefs/imaging101-seismic-lsrtm-original.md) — Recover subsurface reflectivity | contract gap |
| [imaging101-seismic-traveltime-tomography](../presentation/external-tasks/briefs/imaging101-seismic-traveltime-tomography.md) — Infer subsurface velocity from first arrivals | contract gap |
| [imaging101-shapelet-source-reconstruction](../presentation/external-tasks/briefs/imaging101-shapelet-source-reconstruction.md) — Recover a galaxy behind a gravitational lens | contract gap |
| [imaging101-weather-radar-data-assimilation](../presentation/external-tasks/briefs/imaging101-weather-radar-data-assimilation.md) — Recover a future radar field from sparse observations | contract gap |

### Outside queue · Closed mixed investigation

Preserve provenance and reviews; do not reopen the closed investigation as new work.

| Entry / source brief | Status at audit |
| --- | --- |
| [tb3-history-sourcing](../groups/anatomy-audit/presentation/briefs/tb3-history-sourcing.md) — Investigate historical task sources | reviewed |
