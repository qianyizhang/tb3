# Master Evidence, Provenance & Reference Index
## Medical Vision in the Agent Era

> This document indexes all primary research rounds, machine-readable Task Card specifications, explicit Input Data & Ground Truth (GT) definitions, retained evidence JSON ledgers, clinical datasets, and academic literature supporting the showcase stack.

---

## 1. Complete Research Round Index (BR-001 – BR-040)

The empirical conclusions in this showcase derive from 40 controlled research rounds executed in September 2026:

| Round ID | Domain & Focus | Primary Model | Key Deliverable / Finding | Document Reference |
| :--- | :--- | :--- | :--- | :--- |
| **BR-001–003** | Multi-organ CT Scaffolding | Sol / Astra | Initial DICOM ingestion, voxel affine checks | [`BR-002-results.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-002-results.md) · [`BR-003`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-003-work-history.md) |
| **BR-004** | Single-Patient Annotation | Sol / xhigh | DICOM segmentation and boundary testing | [`BR-004-results`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-004-sol-followup.md) |
| **BR-005–009** | Scaffolding & Budget Tools | Sol / Terra | Scaffolding re-tests, tool execution limits | [`BR-005-results.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-005-results.md) · [`BR-008`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-008-results.md) |
| **BR-010–012** | Mask-Only Anatomical Curation | Sol / Terra | Tested organ naming without CT radiodensity | [`BR-010-mask-only.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-010-mask-only-anatomy.md) |
| **BR-013–015** | Abdominal Direction & Evidence | Sol / Terra | Adding HU density and vascular anchors | [`BR-013-results.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-013-results.md) · [`BR-015`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-015-results.md) |
| **BR-016** | **Aneurysm 3D Localization** | Sol / xhigh | 3 cases evaluated; detected dataset leakage | [`BR-016-aneurysm.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-016-aneurysm-localization.md) · [`BR-016 Results`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-016-results.md) |
| **BR-017** | **Tissue Ownership Auditing** | Sol / xhigh | Duodenum-pancreas 21 mL absorption audit | [`BR-017-absorbed.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-017-absorbed-anatomy.md) · [`BR-017 Results`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-017-results.md) |
| **BR-018** | Report-Backed Diagnosis | Sol / Terra | Longitudinal chest CT lesion comparison | [`BR-018-diagnosis.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-018-report-backed-diagnosis.md) |
| **BR-019–022** | 2D/3D Slice Registration | Terra / high | Non-rigid alignment, optimization traps | [`BR-021-deformation.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-021-anatomical-deformation.md) · [`BR-022`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-022-results.md) |
| **BR-023–024** | Challenging Registration Setup | Sol / xhigh | 2D source slice failure (12.7 mm RMS) | [`BR-024-harder-reg.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-024-harder-registration.md) · [`BR-024 Results`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-024-results.md) |
| **BR-025–026** | Vessel Repair & Connectivity | Terra / high | MRA gap repair; 198/200 voxels restored | [`BR-025-connectivity.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-025-vessel-connectivity.md) · [`BR-026 Results`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-026-results.md) |
| **BR-027** | Cardiac Difficulty Grading | Terra / high | Cine-MRI motion and contrast analysis | [`BR-027-cardiac.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-027-cardiac-video-difficulty.md) |
| **BR-028** | **Full 3D Source Registration** | Sol / xhigh | 3D depth dropped RMS error to 2.60 mm | [`BR-028-3d-source.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-028-registration-3d-source.md) · [`BR-028 Results`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-028-results.md) |
| **BR-029** | Dynamic Heart Modeling | Sol / Terra | Left-ventricular volume and tracking setup | [`BR-029-modeling.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-029-dynamic-heart-modeling.md) · [`BR-029 Results`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-029-dynamic-heart-results.md) |
| **BR-030** | **Coronary CPR Diagnostic Geometry** | Terra / high | Uncovered 8.89 mm distance-axis bug | [`BR-030-geometry.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-030-vessel-diagnostic-geometry.md) · [`BR-030 Results`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-030-results.md) |
| **BR-031** | Cardiac Agent Levels | Sol / Terra | Evaluated prompt difficulty and meshes | [`BR-031-results.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-031-cardiac-agent-results.md) |
| **BR-032** | Real Clinical Echocardiography | Sol / Terra | Underestimated EF (58% -> 28-35%) | [`BR-032-real-echo.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-032-real-echo-case.md) · [`BR-032 Results`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-032-real-echo-results.md) |
| **BR-033** | **Brain & Airway Difficulty** | Sol / xhigh | Exposed airway fragment loophole | [`BR-033-difficulty.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-033-brain-vessel-airway-difficulty.md) · [`BR-033 Results`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-033-results.md) |
| **BR-034** | Pathological Echo Simulation | Sol / Terra | Assessed regional wall motion defects | [`BR-034-echo.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-034-pathological-echo.md) · [`BR-034 Results`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-034-results.md) |
| **BR-035** | **Segmentation Biomechanics** | Sol / xhigh | Dice 0.946 hid 7.37 pp radial strain error | [`BR-035-mechanics.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-035-segmentation-mechanics.md) · [`BR-035 Results`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-035-results.md) |
| **BR-036** | Semantic Landmarks Initial | Terra / high | 4 CT / 8 MRI points; identified FOV issues | [`BR-036-landmarks.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-036-semantic-landmarks.md) · [`BR-036 Results`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-036-results.md) |
| **BR-037** | Longitudinal Reading | Sol / xhigh | Multi-timepoint lesion progression audit | [`BR-037-reading.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-037-longitudinal-reading.md) · [`BR-037 Results`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-037-results.md) |
| **BR-038** | Volume Coordinate Contract Audit | Sol / Terra | Established explicit voxel coordinate tags | [`BR-038-volume.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-038-volume-landmarks.md) · [`BR-038 Results`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-038-results.md) |
| **BR-039** | CT Spine Landmark Expansion | Terra / high | 26 vertebral targets (C1–L6) on VerSe | [`BR-039-landmarks.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-039-ct-landmarks.md) · [`BR-039 Results`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-039-results.md) |
| **BR-040** | **Final Landmark Comparison** | Sol / xhigh | 0 false FOV on CT; Atlas doubled MRI score | [`BR-040-landmarks.md`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-040-sol-landmarks.md) · [`BR-040 Results`](file:///Users/zhangqy/pkgs/tb3/docs/research-rounds/BR-040-results.md) |

---

## 2. Explicit Input Data & Ground Truth (GT) Specifications

Every benchmark task in this showcase is grounded in an explicit, machine-readable **Task Card JSON** located in [`site_med/task_cards/`](task_cards/). These cards define the exact input files, matrix dimensions, voxel resolutions, coordinate systems, reference ground truths, and quantitative acceptance thresholds.

### 2.0 Task Specification Summary Matrix

| Domain & Task ID | Task Card JSON | Clinical Cohort & Modality | Exact Subject & Dimensions | Clinical Target / Injected Defect | Ground Truth Provenance | Passing Criteria & Gate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **01. Segmentation**<br>`MED-SEG-BR017-ABSORPTION` | [`med_seg_br017_absorption.json`](task_cards/med_seg_br017_absorption.json) | Abdominal CT<br>(TotalSegmentator) | Case `s1233` (Case 28)<br>320×320×480, 1.5mm iso | 21.04 mL pancreatic head tissue absorbed into duodenum mask | TotalSegmentator consensus (PMC12701807); true LPS centroid `[-14.2, -18.5, 42.1] mm` | Flag defect $\ge 5.0	ext{ mL}$;<br>LPS centroid error $\le 3.0	ext{ mm}$ |
| **02. Aneurysms**<br>`MED-VAS-BR016-ANEURYSM` | [`med_vas_br016_aneurysm.json`](task_cards/med_vas_br016_aneurysm.json) | Brain TOF-MRA<br>(OpenNeuro ds003949) | `sub-001`, `sub-002`, `sub-003`<br>0.45×0.45×0.70 mm | Focal arterial outpouchings (3–5 mm) at Circle of Willis bifurcations | Expert neuroradiologist multi-reader consensus; N01 PCoA, N02 MCA, N03 Healthy `[]` | Distance $\le 1.0	ext{ mm}$;<br>Zero false positives on N03 |
| **03. Registration**<br>`MED-REG-BR028-RESPIRATORY` | [`med_reg_br028_respiratory.json`](task_cards/med_reg_br028_respiratory.json) | 4D Thoracic CT<br>(DIR-Lab) | Patient 3 (T00 exhale to T50 inhale)<br>256×256×106, 0.97×0.97×2.5mm | 8 anatomical landmarks (q01–q08) under non-rigid respiratory deformation | DIR-Lab expert radiologist landmark consensus in T50 inhale volume | TRE $\le 5.0	ext{ mm}$ per landmark;<br>Overall RMS $\le 3.0	ext{ mm}$ |
| **04. Vessel CPR**<br>`MED-TUB-BR030-BR033-CPR-GEOMETRY` | [`med_tub_br030_br033_cpr_geometry.json`](task_cards/med_tub_br030_br033_cpr_geometry.json) | Coronary CTA (ImageCAS) & Chest CT (AeroPath) | `Coronary_Case_1` (256×256×180)<br>& `Airway_Case_A01_A03` | 200-voxel (8 mm) gap in RCA; segmental disconnections in bronchial tree | ImageCAS-X manual reference mask, true centerline length 104.08 mm, Frenet normal frame | $\le 10$ extra voxels outside sphere;<br>CPR distance-axis error $\le 1.0	ext{ mm}$ |
| **05. Cardiac Strain**<br>`MED-BIO-BR035-CARDIAC-STRAIN` | [`med_bio_br035_cardiac_strain.json`](task_cards/med_bio_br035_cardiac_strain.json) | Dynamic 4D Ultrasound<br>(STRAUS Simulation) | 30 phases across full cycle<br>128×128×128, 1.5mm iso | Reconstruct moving 3D LV mesh; compute 17 AHA segment strain tensors | Continuum finite-element material displacement points (EDV 142.5 mL, EF 57.1%) | $\det(F) > 0$; Volume err $\le 5\%$;<br>Strain MAE $\le 3	ext{ pp}$ (L/C), $\le 4	ext{ pp}$ (R) |
| **06. 3D Landmarks**<br>`MED-LND-BR040-LANDMARKS-FOV` | [`med_lnd_br040_landmarks_fov.json`](task_cards/med_lnd_br040_landmarks_fov.json) | Spine CT (VerSe) & Brain MRI (AFIDs ds004470) | `sub-verse823` (512×512×1214 / 480)<br>& `sub-C001` (256×256×176, 1.0mm) | 26 vertebral centroids (C1–L6) & 32 brain fiducials; crop rejection | VerSe manual segmentation centroids & AFIDs 3-rater consensus fiducials | CT error $\le 5.0	ext{ mm}$, MRI $\le 3.0	ext{ mm}$;<br>Zero false presence on `OUT_OF_FOV` |

---

### 2.1 Domain 01: Organ Segmentation & Tissue Ownership Auditing
- **Task Identifier:** `MED-SEG-BR017-ABSORPTION`
- **Machine-Readable Card:** [`site_med/task_cards/med_seg_br017_absorption.json`](task_cards/med_seg_br017_absorption.json)
- **Clinical Objective:** Audit 13 abdominal organ segmentation masks to detect whether soft-tissue parenchyma from one organ has been mistakenly absorbed into an adjacent organ mask, and return the physical LPS centroid of the misplaced tissue.
- **Input Data Specifications:**
  - **Dataset:** TotalSegmentator Abdominal CT Cohort (Wasserthal et al., *Radiology: AI* 2023; CC BY 4.0).
  - **Subject ID:** `s1233` (TotalSegmentator Case 28).
  - **Image Volume:** `ct.nii.gz`, 3D NIfTI volume, dimensions $320 	imes 320 	imes 480$ voxels, isotropic voxel spacing $1.5 	imes 1.5 	imes 1.5	ext{ mm}$, intensity in Hounsfield Units $[-1024, 1850	ext{ HU}]$.
  - **Supplied Masks:** `organ_masks.nii.gz`, uint8 label volume containing 13 organs (1: spleen, 2: kidney_right, 3: kidney_left, 4: gallbladder, 5: liver, 6: stomach, 7: aorta, 8: inferior_vena_cava, 9: portal_vein, 10: pancreas, 11: duodenum, 12: adrenal_right, 13: adrenal_left).
  - **Coordinate Space:** LPS (Left-Posterior-Superior) physical space via standard $4 	imes 4$ affine matrix.
- **Ground Truth & Defect Synthesis:**
  - **Ground Truth Provenance:** TotalSegmentator expert consensus segmentation cross-verified against multi-reader pancreas morphology studies (PMC12701807).
  - **Defect Injection:** Exactly 21.04 mL ($6,234$ voxels) of authentic pancreatic head parenchyma was digitally carved from label 10 (`pancreas`) and merged into label 11 (`duodenum`).
  - **Morphology:** The transferred voxels form a single 26-connected contiguous component (>98% contiguous) along the shared duodenal C-loop interface.
  - **True LPS Centroid:** $[-14.2, -18.5, 42.1]	ext{ mm}$. Remaining true pancreas volume: $48.6	ext{ mL}$.
- **Evaluation Contract & Acceptance Gates:**
  - **Deliverable:** `findings.json` reporting `object_id`, `included_label`, and `point_lps_mm`.
  - **Automated Gate:** Detect tissue absorption $\ge 5.0	ext{ mL}$; predicted physical LPS point within $\le 3.0	ext{ mm}$ Euclidean distance of true centroid.

---

### 2.2 Domain 02: Vascular Aneurysm 3D Localization
- **Task Identifier:** `MED-VAS-BR016-ANEURYSM`
- **Machine-Readable Card:** [`site_med/task_cards/med_vas_br016_aneurysm.json`](task_cards/med_vas_br016_aneurysm.json)
- **Clinical Objective:** Autonomously inspect 3D Time-of-Flight Magnetic Resonance Angiography (TOF-MRA) scans of the Circle of Willis to detect focal arterial outpouchings (aneurysms) and report exactly one physical 3D coordinate per lesion, or verify that a scan is healthy.
- **Input Data Specifications:**
  - **Dataset:** OpenNeuro `ds003949` Aneurysm Cohort (CC0 Public Domain).
  - **Cases Evaluated:**
    - `N01` (`sub-001_ses-1`): $350 	imes 448 	imes 144$ voxels, spacing $0.45 	imes 0.45 	imes 0.70	ext{ mm}$. Full TOF-MRA + skull-stripped brain volume.
    - `N02` (`sub-002_ses-1`): $512 	imes 512 	imes 140$ voxels, spacing $0.45 	imes 0.45 	imes 0.70	ext{ mm}$. Full TOF-MRA + skull-stripped brain volume.
    - `N03` (`sub-003_ses-1`): $350 	imes 448 	imes 160$ voxels, spacing $0.45 	imes 0.45 	imes 0.70	ext{ mm}$. Full TOF-MRA + skull-stripped brain volume.
- **Ground Truth & Clinical Status:**
  - **Ground Truth Provenance:** Independent consensus annotations from three board-certified neuroradiologists.
  - **Case N01:** Single saccular aneurysm ($3.5	ext{ mm}$ diameter) in Posterior Communicating Artery (PCoA), center voxel $[166, 273, 84]$.
  - **Case N02:** Single saccular outpouching ($4.8	ext{ mm}$ diameter) at Middle Cerebral Artery (MCA) bifurcation, center voxel $[307, 214, 93]$.
  - **Case N03:** Healthy control scan (verified zero aneurysms, Ground Truth = `[]`).
- **Evaluation Contract & Acceptance Gates:**
  - **Deliverable:** `aneurysm_detections.json` returning predicted 3D coordinates.
  - **Automated Gate:** Euclidean distance $\le 1.0	ext{ mm}$ from reference ground truth. Strict zero-tolerance for false positives on healthy scans (Case N03).
  - **Audit Finding:** Documented agent terminal trajectory querying open-web manifest to confirm Case N03 was healthy, establishing the necessity of network sandboxing in medical AI benchmarks.

---

### 2.3 Domain 03: Deformable 3D Image Registration Under Respiratory Motion
- **Task Identifier:** `MED-REG-BR028-RESPIRATORY`
- **Machine-Readable Card:** [`site_med/task_cards/med_reg_br028_respiratory.json`](task_cards/med_reg_br028_respiratory.json)
- **Clinical Objective:** Map non-rigid anatomical respiratory deformation between exhale and inhale phases of 4D thoracic CT scans, tracking eight discrete bronchial and vascular landmarks.
- **Input Data Specifications:**
  - **Dataset:** DIR-Lab 4D-CT Respiratory Cohort (Castillo et al., *Phys. Med. Biol.* 2009).
  - **Subject ID:** Patient 3 (Case 3).
  - **Image Volumes:**
    - `reference_volume.npz`: Exhale phase acquisition (T00), $256 	imes 256 	imes 106$ voxels, spacing $0.97 	imes 0.97 	imes 2.50	ext{ mm}$, HU array + $4 	imes 4$ affine matrix.
    - `destination_volume.npz`: Inhale phase acquisition (T50), $256 	imes 256 	imes 106$ voxels, spacing $0.97 	imes 0.97 	imes 2.50	ext{ mm}$, HU array + $4 	imes 4$ affine matrix.
    - `query_landmarks.json`: 8 discrete query landmark positions (q01 to q08) annotated on T00 exhale volume.
- **Ground Truth & Target Landmarks:**
  - **Ground Truth Provenance:** DIR-Lab expert thoracic radiologist manual consensus landmark coordinates in target inhale volume (T50).
  - **Landmarks Tracked:** q01 (Tracheal carina), q02 (RUL bronchus), q03 (LMS bronchus), q04 (Medial segmental bifurcation), q05 (LLL lateral vessel), q06 (Segmental bifurcation ridge), q07 (Subsegmental bronchus), q08 (Posterior basilar branch).
- **Evaluation Contract & Acceptance Gates:**
  - **Deliverable:** `registered_landmarks.json` (array of 8 [x, y, z] LPS coordinates in inhale physical space).
  - **Automated Gate:** Target Registration Error (TRE) $\le 5.0	ext{ mm}$ per landmark; Root Mean Square (RMS) $\le 3.0	ext{ mm}$ across all 8 landmarks.
  - **Qualitative Adjudication Protocol:** Visual radiological adjudication on anatomical bifurcation ridges (adjudicated q06 $6.41	ext{ mm}$ error as structurally correct on the identical anatomical bifurcation).

---

### 2.4 Domain 04: Tubular Centerline Routing & 360° Curved Planar Reformations
- **Task Identifier:** `MED-TUB-BR030-BR033-CPR-GEOMETRY`
- **Machine-Readable Card:** [`site_med/task_cards/med_tub_br030_br033_cpr_geometry.json`](task_cards/med_tub_br030_br033_cpr_geometry.json)
- **Clinical Objective:** Repair severed blood vessel and airway segmentation masks, trace ordered 3D centerline paths, and generate 360-degree rotated Curved Planar Reformations (CPRs) with calibrated distance axes.
- **Input Data Specifications:**
  - **Coronary CTA Cohort:** ImageCAS / ASOCA (MICCAI 2020; CC BY-SA 4.0).
    - Case: `Coronary_Case_1`, crop dimensions $256 	imes 256 	imes 180$ voxels, spacing $0.45 	imes 0.45 	imes 0.70	ext{ mm}$.
    - Injected Defect: Synthetic 200-voxel ($8	ext{ mm}$) disruption in Right Coronary Artery (RCA) within a $15	ext{ mm}$ review sphere.
    - Anchors: RCA ostium (start) and distal Posterior Descending Artery (R-PDA).
  - **Airway CT Cohort:** AeroPath Thoracic CT (`Airway_Case_A01_A03`).
    - Injected Defect: Segmental disconnections in peripheral airway tree.
- **Ground Truth & Calibrated Deliverables:**
  - **Ground Truth Provenance:** ImageCAS-X expert manual lumen segmentations and continuous centerline curve.
  - **Ground Truth Centerline:** Arc length $104.08	ext{ mm}$; Frenet-Serret normal frame sampled at $0.5	ext{ mm}$ arc steps.
- **Evaluation Contract & Acceptance Gates:**
  - **Deliverables:** `repaired_mask.nii.gz` ($\le 10$ extra voxels outside review sphere), `centerline.json` (ordered RAS mm coordinates), `cpr_planes.npz` (8 planar reformations from $0^\circ$ to $315^\circ$ in $45^\circ$ steps), `vessel_surface.obj` (watertight closed triangular mesh).
  - **Automated Gate:** Single connected component from ostium to distal anchor; CPR horizontal distance axis discrepancy $\le 1.0	ext{ mm}$ against true cumulative physical arc length.
  - **Post-Mortem Traps:** Exposed the 8.89 mm CPR distance-axis indexing bug in BR-030 (raw pixel indices vs. anisotropic millimeters) and the airway tree loophole in BR-033 (passing local routes within detached pieces without full-tree connection).

---

### 2.5 Domain 05: 4D Heart Biomechanics & Myocardial Strain
- **Task Identifier:** `MED-BIO-BR035-CARDIAC-STRAIN`
- **Machine-Readable Card:** [`site_med/task_cards/med_bio_br035_cardiac_strain.json`](task_cards/med_bio_br035_cardiac_strain.json)
- **Clinical Objective:** Reconstruct moving 3D left-ventricular myocardium surface meshes across 30 cardiac phases and compute volume-weighted engineering strain tensors across the AHA 17-segment model.
- **Input Data Specifications:**
  - **Dataset:** STRAUS Continuum Simulation Cohort (Human Heart Project, CREATIS, INSA Lyon) & Clinical 3D Echocardiography.
  - **Input Artifacts:**
    - `segmentations_30phases.npz`: 30 3D binary masks of the left-ventricular myocardium across full cardiac cycle, $128 	imes 128 	imes 128$ voxels, $1.5	ext{ mm}$ isotropic.
    - `ultrasound_30phases.npz`: Matched 3D B-mode echocardiography intensity volumes.
- **Ground Truth & Biomechanical Parameters:**
  - **Ground Truth Provenance:** Continuum finite-element biomechanical simulation tracking material points and displacement gradients.
  - **Hemodynamic Ground Truth:** End-Diastolic Volume ($	ext{EDV}$) $= 142.5	ext{ mL}$, End-Systolic Volume ($	ext{ESV}$) $= 61.2	ext{ mL}$, Ejection Fraction ($	ext{EF}$) $= 57.1\%$.
  - **Strain Ground Truth:** Peak longitudinal strain $arepsilon_{LL} = -18.4\%$, peak circumferential strain $arepsilon_{CC} = -21.6\%$, peak radial strain $arepsilon_{RR} = +44.8\%$.
- **Evaluation Contract & Acceptance Gates:**
  - **Deliverables:** `dynamic_mesh.npz` (moving 3D tetrahedral mesh across 30 phases), `cardiac_report.json` (volume curve, EF %, and $30 	imes 17 	imes 3$ engineering strain tensor array across AHA 17-segment model).
  - **Automated Gate:** Zero inverted elements ($\det(F) > 0$ across all elements); cavity volume conservation error $\le 5.0\%$; strain MAE $\le 3.0	ext{ pp}$ (longitudinal/circumferential) and $\le 4.0	ext{ pp}$ (radial).
  - **The Cylinder-Twist Paradox:** Sol scored high surface Dice ($0.946$) and accurate EF ($56.1\%$), but missed radial strain by $+7.37	ext{ pp}$ due to superficial boundary matching failing to track internal myocardial shearing. Real clinical ultrasound tracking (BR-032) failed drastically (underestimating EF by $23$–$30	ext{ pp}$).

---

### 2.6 Domain 06: 3D Anatomical Landmarks & Out-of-FOV Rejection
- **Task Identifier:** `MED-LND-BR040-LANDMARKS-FOV`
- **Machine-Readable Card:** [`site_med/task_cards/med_lnd_br040_landmarks_fov.json`](task_cards/med_lnd_br040_landmarks_fov.json)
- **Clinical Objective:** Accurately predict 3D physical coordinates for 26 vertebral centroids (C1–L6) on spine CT and 32 brain fiducials on MRI, while strictly rejecting targets outside the field-of-view (`OUT_OF_FOV`) without hallucinating.
- **Input Data Specifications:**
  - **Dataset 1:** VerSe Spine CT Benchmark (`sub-verse823`, Sekuboyina et al., *MedIA* 2021; CC BY-SA 4.0).
    - Full CT: $512 	imes 512 	imes 1214$ voxels, spacing $0.80 	imes 0.80 	imes 1.25	ext{ mm}$.
    - Cropped CT: $512 	imes 512 	imes 480$ voxels (thoracic-only crop).
    - Target List: 26 vertebral centroids (C1 through L6).
  - **Dataset 2:** AFIDs SNSX Brain T1 MRI (`sub-C001`, OpenNeuro `ds004470`, Lau et al., *Sci Data* 2020; CC BY 4.0).
    - Matrix: $256 	imes 256 	imes 176$ voxels, $1.0	ext{ mm}$ isotropic.
    - Target List: 32 brain fiducial landmarks (AC, PC, Pineal, etc.).
- **Ground Truth & FOV Status:**
  - **Ground Truth Provenance:** VerSe expert manual vertebral centroids and AFIDs 3-rater consensus fiducials.
  - **VerSe Full Scan:** 24 visible vertebrae, 2 absent.
  - **VerSe Cropped Scan:** 13 visible vertebrae (T1–T12, L1), 11 outside FOV (C1–C7, L2–L5), 2 absent (L6).
  - **AFIDs Brain MRI:** 32 visible brain landmarks.
- **Evaluation Contract & Acceptance Gates:**
  - **Deliverable:** `landmarks.json` reporting native zero-indexed fractional voxel coordinates `[i, j, k]` (`voxel_ijk_zero_based`) and status (`OBSERVED`, `OUT_OF_FOV`, or `ABSENT`).
  - **Automated Gate:** Euclidean distance via affine matrix $\le 5.0	ext{ mm}$ for spine CT and $\le 3.0	ext{ mm}$ for brain MRI.
  - **Strict Anti-Hallucination Gate:** Zero tolerance for predicting an `OUT_OF_FOV` target as `OBSERVED`. Sol achieved 0/11 hallucinations on cropped CT; autonomous MNI template registration boosted brain MRI landmark accuracy from 3/32 to 14/32 within 3 mm.

---

## 3. Clinical Datasets & Imaging Cohorts

| Dataset Name | Imaging Modality | Anatomical Scope | Public Source & License | Primary Benchmark Task |
| :--- | :--- | :--- | :--- | :--- |
| **TotalSegmentator** | Whole-body CT | 117 anatomical structures | [Radiology: AI 2023](https://doi.org/10.1148/ryai.230024) · CC BY 4.0 | Domain 01: Tissue ownership auditing |
| **OpenNeuro ds003949** | Brain 3D TOF-MRA | Circle of Willis aneurysms | [OpenNeuro ds003949](https://openneuro.org/datasets/ds003949) · CC0 | Domain 02: Aneurysm 3D detection |
| **DIR-Lab 4D-CT** | 4D Thoracic CT | Exhale/Inhale lung pairs | [Phys. Med. Biol. 2009](https://doi.org/10.1088/0031-9155/54/7/003) | Domain 03: Deformable registration |
| **ASOCA & AeroPath** | Coronary CTA / Chest CT | Arterial & bronchial trees | [ASOCA MICCAI 2020](https://asoca.grand-challenge.org/) · CC BY-SA 4.0 | Domain 04: Tubular routing & CPR |
| **4D Echocardiography** | Dynamic 3D Ultrasound | Left ventricle (30 phases) | Synthetic & clinical ultrasound | Domain 05: Biomechanical strain |
| **VerSe Benchmark** | Spine CT | 26 Vertebrae (C1–L6) | [MedIA 2021](https://doi.org/10.1016/j.media.2021.102166) · CC BY-SA 4.0 | Domain 06: Vertebral centroid tracking |
| **AFIDs SNSX (ds004470)** | Brain T1 MRI | 32 anatomical fiducials | [Sci Data 2020](https://doi.org/10.1038/s41597-020-00629-8) · CC BY 4.0 | Domain 06: Brain fiducial localization |

---

## 4. Retained Evidence Ledgers & Verification Receipts

All raw trial outputs, trajectory checksums, and scoring receipts are permanently preserved in the repository:

- [`site_med/task_cards/`](task_cards/) · Complete stack of machine-readable task card JSON specifications.
- [`docs/evidence/br037-freeze.json`](file:///Users/zhangqy/pkgs/tb3/docs/evidence/br037-freeze.json) · Scoring rubric and task hashes for longitudinal reading.
- [`docs/evidence/br037-results.json`](file:///Users/zhangqy/pkgs/tb3/docs/evidence/br037-results.json) · Model execution transcripts and metrics.
- [`docs/evidence/br040-source-audit.json`](file:///Users/zhangqy/pkgs/tb3/docs/evidence/br040-source-audit.json) · Atlas assistance and URL access audit for landmark localization.
- [`site/provenance.json`](file:///Users/zhangqy/pkgs/tb3/site/provenance.json) · Cryptographic SHA-256 hashes of all generated figures and slice images.
- [`site/landmark-provenance.json`](file:///Users/zhangqy/pkgs/tb3/site/landmark-provenance.json) · Exact coordinate conversion verification across nibabel and SimpleITK.

---

## 5. Academic Literature Citations

1. **Wasserthal, J., et al. (2023).** TotalSegmentator: Robust Segmentation of 117 Cognitive Structures in CT Scans. *Radiology: Artificial Intelligence*, 5(5), e230024.
2. **Castillo, R., et al. (2009).** A framework for evaluation of deformable image registration using 4D computed tomography. *Physics in Medicine & Biology*, 54(7), 1871.
3. **Sekuboyina, A., et al. (2021).** VerSe: A Large-scale Benchmark for Multi-vertebra Segmentation and Identification. *Medical Image Analysis*, 73, 102166.
4. **Lau, J. C., et al. (2020).** Automated open-access anatomical fiducial detection in human brain MRI. *Scientific Data*, 7, 396.
5. **Cerqueira, M. D., et al. (2002).** Standardized Myocardial Segmentation and Nomenclature for Tomographic Imaging of the Heart. *Circulation*, 105(4), 539–542.

---

## Stack Navigation

- [← Master Executive Overview](README.md)
- [01. Organ Segmentation & Tissue Auditing](01-segmentation.md)
- [02. Vascular Aneurysm 3D Detection](02-aneurysms.md)
- [03. Deformable 3D Image Registration](03-registration.md)
- [04. Tubular Geometry, Centerlines & CPR](04-vessels-cpr.md)
- [05. 4D Heart Biomechanics & Strain](05-cardiac-mechanics.md)
- [06. 3D Landmarks & Out-of-FOV Rejection](06-landmarks.md)
