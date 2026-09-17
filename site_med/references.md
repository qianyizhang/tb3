# Master Evidence, Provenance & Reference Index
## Medical Vision in the Agent Era

> This document indexes all primary research rounds, retained evidence JSON ledgers, clinical datasets, and academic literature supporting the showcase stack.

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

## 2. Clinical Datasets & Imaging Cohorts

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

## 3. Retained Evidence Ledgers & Verification Receipts

All raw trial outputs, trajectory checksums, and scoring receipts are permanently preserved in the repository:

- [`docs/evidence/br037-freeze.json`](file:///Users/zhangqy/pkgs/tb3/docs/evidence/br037-freeze.json) · Scoring rubric and task hashes for longitudinal reading.
- [`docs/evidence/br037-results.json`](file:///Users/zhangqy/pkgs/tb3/docs/evidence/br037-results.json) · Model execution transcripts and metrics.
- [`docs/evidence/br040-source-audit.json`](file:///Users/zhangqy/pkgs/tb3/docs/evidence/br040-source-audit.json) · Atlas assistance and URL access audit for landmark localization.
- [`site/provenance.json`](file:///Users/zhangqy/pkgs/tb3/site/provenance.json) · Cryptographic SHA-256 hashes of all generated figures and slice images.
- [`site/landmark-provenance.json`](file:///Users/zhangqy/pkgs/tb3/site/landmark-provenance.json) · Exact coordinate conversion verification across nibabel and SimpleITK.

---

## 4. Academic Literature Citations

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
