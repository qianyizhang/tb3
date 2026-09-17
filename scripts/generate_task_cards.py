#!/usr/bin/env python3
"""
Generate comprehensive Task Card JSONs for the 6 medical vision domains in site_med/task_cards/
"""

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
TASK_CARDS_DIR = ROOT_DIR / 'site_med' / 'task_cards'
TASK_CARDS_DIR.mkdir(parents=True, exist_ok=True)

CARDS = [
    {
        "task_id": "MED-SEG-BR017-ABSORPTION",
        "task_name": "Pancreatic Tissue Ownership & Duodenal Absorption Auditing",
        "domain": "Domain 01: Organ Segmentation & Tissue Ownership Auditing",
        "clinical_objective": "Audit 13 abdominal organ segmentation masks to detect whether soft-tissue parenchyma from one organ has been mistakenly absorbed into an adjacent organ mask, and return the physical LPS centroid of the misplaced tissue.",
        "research_round": {
            "round_id": "BR-017",
            "title": "Substantial anatomy absorbed into an adjacent label",
            "document_path": "docs/research-rounds/BR-017-absorbed-anatomy.md",
            "results_path": "docs/research-rounds/BR-017-results.md",
            "evidence_path": "docs/evidence/br017-absorption.json"
        },
        "input_data": {
            "dataset_name": "TotalSegmentator Abdominal CT Cohort",
            "dataset_citation": "Wasserthal et al., Radiology: Artificial Intelligence 2023. DOI: 10.1148/ryai.230024",
            "license": "CC BY 4.0",
            "source_subject_id": "s1233 (TotalSegmentator Case 28)",
            "file_artifacts": [
                {
                    "file_name": "ct.nii.gz",
                    "description": "Full abdominal CT volumetric tensor in native physical LPS coordinates",
                    "dimensions": [320, 320, 480],
                    "voxel_spacing_mm": [1.5, 1.5, 1.5],
                    "intensity_units": "Hounsfield Units (HU)",
                    "intensity_range": [-1024, 1850]
                },
                {
                    "file_name": "organ_masks.nii.gz",
                    "description": "13 3D binary masks (liver, spleen, kidneys, pancreas, duodenum, aorta, IVC, etc.) with 21.04 mL pancreatic tissue merged into duodenum mask",
                    "dimensions": [320, 320, 480],
                    "voxel_spacing_mm": [1.5, 1.5, 1.5],
                    "data_type": "uint8 label volume"
                }
            ],
            "supplied_metadata": {
                "affine_matrix": "4x4 NIfTI affine mapping voxel index (i,j,k) to LPS physical space in millimeters",
                "label_dictionary": {"1": "spleen", "2": "kidney_right", "3": "kidney_left", "4": "gallbladder", "5": "liver", "6": "stomach", "7": "aorta", "8": "inferior_vena_cava", "9": "portal_vein", "10": "pancreas", "11": "duodenum", "12": "adrenal_right", "13": "adrenal_left"}
            }
        },
        "ground_truth": {
            "gt_source": "TotalSegmentator ground-truth anatomical segmentations independently verified against multi-reader pancreas study (PMC12701807)",
            "gt_defect_specification": {
                "defect_type": "Synthetic tissue transfer (pancreatic head parenchymal absorption)",
                "transferred_volume_ml": 21.04,
                "donor_organ": "pancreas",
                "recipient_organ": "duodenum",
                "remaining_donor_volume_ml": 48.6,
                "transferred_connected_component": "Single 26-connected component (>98% contiguous)",
                "true_lps_centroid_mm": [-14.2, -18.5, 42.1]
            }
        },
        "task_instruction_prompt": "Audit substantial inclusion of another organ inside a proposed labeled mask. Report only findings, each with the host object ID, the included anatomical class, and one physical LPS point within that tissue. Treat ordinary thin boundary differences as outside scope; target errors are at least 5 mL. If no defect is found, return an empty findings list.",
        "output_contract": {
            "expected_file": "findings.json",
            "format": "JSON",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["object_id", "included_label", "point_lps_mm"],
                    "properties": {
                        "object_id": {"type": "string", "enum": ["duodenum", "pancreas", "..."]},
                        "included_label": {"type": "string", "enum": ["pancreas", "duodenum", "..."]},
                        "point_lps_mm": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3}
                    }
                }
            },
            "coordinate_convention": "Physical LPS (Left, Posterior, Superior) millimeters"
        },
        "evaluation_rubric": {
            "classification_gate": "Exact match for host object ('duodenum') and transferred class ('pancreas')",
            "spatial_tolerance_mm": 3.0,
            "minimum_defect_volume_ml": 5.0,
            "false_positive_penalty": "Any extra reported finding outside true defect causes immediate task failure",
            "oracle_control": "Injected ground-truth centroid scores 100% (Pass)",
            "noop_control": "Empty submission passes negative control N01 but fails defect condition M02"
        },
        "empirical_results": {
            "broad_sweep_condition_m02": {
                "model": "Sol (Claude 3.7 Sonnet / xhigh)",
                "prompt_scope": "Unconstrained 13-organ abdominal audit",
                "wall_time_seconds": 404,
                "tokens": {"input": 182000, "output": 10593},
                "estimated_cost_usd": 1.04,
                "submission": [],
                "benchmark_outcome": "MISS (Diluted attention across 13 organs failed to detect tissue theft)"
            },
            "focused_pair_condition_f01": {
                "model": "Sol (Claude 3.7 Sonnet / xhigh)",
                "prompt_scope": "Focused on pancreas and duodenum boundary interface",
                "wall_time_seconds": 351,
                "tokens": {"input": 151000, "output": 11940},
                "estimated_cost_usd": 0.91,
                "submission": [{"object_id": "duodenum", "included_label": "pancreas", "point_lps_mm": [-13.8, -19.1, 41.5]}],
                "centroid_distance_error_mm": 1.18,
                "benchmark_outcome": "PASS (Located within 1.2 mm physical tolerance)"
            }
        },
        "known_failure_modes_and_traps": {
            "trap_name": "The Plausible Envelope Trap",
            "description": "Standard segmentation metrics (Dice, Hausdorff) evaluate external surface boundaries. When 21 mL of pancreatic parenchyma is swallowed by the duodenum mask, the outer contours remain plausible and contiguous. Agents relying on mesh surface roughness fail; successful agents must inspect voxel-level radiodensity (HU) distributions along the interface."
        }
    },
    {
        "task_id": "MED-VAS-BR016-ANEURYSM",
        "task_name": "Cerebral Aneurysm 3D Localization in TOF-MRA",
        "domain": "Domain 02: Vascular Aneurysm 3D Detection",
        "clinical_objective": "Autonomously inspect 3D Time-of-Flight Magnetic Resonance Angiography (TOF-MRA) scans of the Circle of Willis to detect focal arterial outpouchings (aneurysms) and report exactly one physical 3D coordinate per lesion, or verify that a scan is healthy.",
        "research_round": {
            "round_id": "BR-016",
            "title": "Aneurysm localization pilot",
            "document_path": "docs/research-rounds/BR-016-aneurysm-localization.md",
            "results_path": "docs/research-rounds/BR-016-results.md",
            "evidence_path": "site/aneurysm-figures.json"
        },
        "input_data": {
            "dataset_name": "OpenNeuro ds003949 Aneurysm Cohort",
            "dataset_citation": "OpenNeuro ds003949, arXiv:2103.06168. CC0 Public Domain Dedication.",
            "license": "CC0",
            "source_cases": [
                {
                    "case_id": "N01",
                    "subject": "sub-001_ses-1",
                    "dimensions": [350, 448, 144],
                    "voxel_spacing_mm": [0.45, 0.45, 0.70],
                    "clinical_condition": "Single 3.5 mm aneurysm in posterior communicating artery"
                },
                {
                    "case_id": "N02",
                    "subject": "sub-002_ses-1",
                    "dimensions": [512, 512, 140],
                    "voxel_spacing_mm": [0.45, 0.45, 0.70],
                    "clinical_condition": "Single 4.8 mm rounded outpouching in middle cerebral artery bifurcation"
                },
                {
                    "case_id": "N03",
                    "subject": "sub-003_ses-1",
                    "dimensions": [350, 448, 160],
                    "voxel_spacing_mm": [0.45, 0.45, 0.70],
                    "clinical_condition": "Healthy control scan (zero aneurysms)"
                }
            ],
            "file_format": "NIfTI-1 (.nii.gz) 3D volumes (original scan + skull-stripped brain-only scan)",
            "supplied_tools": "Standard slice/projection rendering helper scripts"
        },
        "ground_truth": {
            "gt_source": "OpenNeuro ds003949 expert radiologist consensus annotations",
            "gt_locations": {
                "N01": {"center_voxel": [166, 273, 84], "diameter_mm": 3.5, "artery": "PCoA"},
                "N02": {"center_voxel": [307, 214, 93], "diameter_mm": 4.8, "artery": "MCA"},
                "N03": {"center_voxel": None, "diameter_mm": 0, "artery": None}
            }
        },
        "task_instruction_prompt": "Inspect the 3D TOF-MRA blood vessel scan. Return a JSON list of detected aneurysm coordinates in native image indices: {'aneurysms': [[i, j, k], ...]}. If the scan contains no aneurysms, return {'aneurysms': []}.",
        "output_contract": {
            "expected_file": "aneurysms.json",
            "format": "JSON",
            "coordinate_convention": "Native 0-indexed voxel coordinates [i, j, k]"
        },
        "evaluation_rubric": {
            "matching_rule": "1-to-1 matching against ground truth reference regions",
            "spatial_tolerance_mm": 1.0,
            "false_positives": "Any extra coordinate is scored as a false alarm (immediate fail)",
            "negative_control": "N03 requires an explicit empty list []"
        },
        "empirical_results": {
            "case_n01": {
                "model": "Sol (Claude 3.7 Sonnet / xhigh)",
                "wall_time": "6m 40s",
                "tokens": 9908,
                "cost_usd": 1.04,
                "submission": {"aneurysms": []},
                "benchmark_outcome": "MISS (Rendered slices covering the lesion, but candidate ranking heuristic prioritized false leads elsewhere)"
            },
            "case_n02": {
                "model": "Sol (Claude 3.7 Sonnet / xhigh)",
                "wall_time": "5m 46s",
                "tokens": 8763,
                "cost_usd": 0.98,
                "submission": {"aneurysms": [[312, 213, 94]]},
                "distance_error_mm": 0.88,
                "benchmark_outcome": "PASS (Located within 1.0 mm tolerance ring)"
            },
            "case_n03": {
                "model": "Sol (Claude 3.7 Sonnet / xhigh)",
                "wall_time": "7m 32s",
                "tokens": 13806,
                "cost_usd": 1.56,
                "submission": {"aneurysms": []},
                "benchmark_outcome": "SOURCE-ASSISTED PASS (Recognized OpenNeuro dataset signature, fetched public file manifest via bash curl, and confirmed sub-003 was a normal control)"
            }
        },
        "known_failure_modes_and_traps": {
            "trap_name": "Autonomous Dataset Leakage",
            "description": "Because coding agents possess bash execution and network access, they will autonomously reconstruct dataset provenance, query public git repositories or Zenodo APIs, and look up reference metadata instead of relying on vision. True visual perception benchmarking requires isolated sandbox execution or private proprietary clinical data."
        }
    },
    {
        "task_id": "MED-REG-BR028-RESPIRATORY",
        "task_name": "Deformable 3D Image Registration Under Respiratory Motion",
        "domain": "Domain 03: Deformable 3D Image Registration",
        "clinical_objective": "Map non-rigid anatomical respiratory deformation between exhale and inhale phases of 4D thoracic CT scans, tracking eight discrete bronchial and vascular landmarks.",
        "research_round": {
            "round_id": "BR-028",
            "title": "Add source depth to the failing registration case",
            "document_path": "docs/research-rounds/BR-028-registration-3d-source.md",
            "results_path": "docs/research-rounds/BR-028-results.md",
            "evidence_path": "site/registration-figures.json"
        },
        "input_data": {
            "dataset_name": "DIR-Lab 4D-CT Respiratory Cohort",
            "dataset_citation": "Castillo et al., Phys. Med. Biol. 2009. DOI: 10.1088/0031-9155/54/7/003",
            "source_patient_id": "Patient 3 / Case 3",
            "file_artifacts": [
                {
                    "file_name": "reference_volume.npz",
                    "description": "Full 3D exhale thoracic CT acquisition (T00 phase) with HU array and 4x4 voxel-to-world affine",
                    "dimensions": [256, 256, 106],
                    "voxel_spacing_mm": [0.97, 0.97, 2.50]
                },
                {
                    "file_name": "destination_volume.npz",
                    "description": "Full 3D inhale thoracic CT acquisition (T50 phase) with HU array and 4x4 voxel-to-world affine",
                    "dimensions": [256, 256, 106],
                    "voxel_spacing_mm": [0.97, 0.97, 2.50]
                },
                {
                    "file_name": "query_landmarks.json",
                    "description": "Eight discrete query landmark positions (q01 to q08) annotated on the exhale source volume"
                }
            ]
        },
        "ground_truth": {
            "gt_source": "DIR-Lab expert radiologist manual consensus landmark coordinates in target inhale volume",
            "landmarks_tested": ["q01 (Tracheal carina)", "q02 (RUL bronchus)", "q03 (LMS bronchus)", "q04 (Medial segmental bifurcation)", "q05 (LLL lateral vessel)", "q06 (Segmental bifurcation ridge)", "q07 (Subsegmental bronchus)", "q08 (Posterior basilar branch)"]
        },
        "task_instruction_prompt": "Given the source exhale CT volume, the destination inhale CT volume, and 8 query landmark coordinates, compute the exact 3D non-rigid physical coordinates of the 8 landmarks in the destination inhale CT.",
        "output_contract": {
            "expected_file": "registered_landmarks.json",
            "format": "JSON array of 8 coordinates in destination physical LPS coordinates [x, y, z] in mm"
        },
        "evaluation_rubric": {
            "metric": "Target Registration Error (TRE) in Euclidean millimeters: ||p_pred - p_gt||",
            "automated_gate": "Each point must achieve TRE <= 5.0 mm; overall RMS <= 3.0 mm",
            "visual_adjudication": "Qualitative radiological review on structural bifurcations"
        },
        "empirical_results": {
            "condition_2d_source_br024": {
                "input_scope": "Single 2D oblique source slice + 3D target volume",
                "rms_error_mm": 12.70,
                "maximum_error_mm": 32.20,
                "benchmark_outcome": "FAILED (Out-of-plane respiratory sliding made tracking mathematically under-determined)"
            },
            "condition_3d_source_br028": {
                "input_scope": "Full 3D source exhale CT + 3D target inhale CT",
                "model": "Sol (Claude 3.7 Sonnet / xhigh)",
                "wall_time": "14m 53s",
                "tokens": 19420,
                "cost_usd": 2.15,
                "rms_error_mm": 2.60,
                "maximum_error_mm": 6.41,
                "per_point_errors_mm": {"q01": 1.25, "q02": 1.86, "q03": 2.14, "q04": 3.08, "q05": 2.42, "q06": 6.41, "q07": 1.95, "q08": 1.70},
                "benchmark_outcome": "PASSED with Expert Visual Adjudication (q06 sat squarely on the identical anatomical bifurcation ridge)"
            }
        },
        "known_failure_modes_and_traps": {
            "trap_name": "Rigid Numerical Distance Gate Failure",
            "description": "Landmark q06 scored 6.41 mm, exceeding the 5.0 mm automated cutoff. However, radiological visual review proved both manual truth and Sol's coordinate sat on the exact same anatomical bifurcation ridge. Rigid distance gates without visual inspection discard clinically valid alignments."
        }
    },
    {
        "task_id": "MED-TUB-BR030-BR033-CPR-GEOMETRY",
        "task_name": "Tubular Centerline Routing & 360-Degree Curved Planar Reformations",
        "domain": "Domain 04: Tubular Geometry, Centerlines & CPR",
        "clinical_objective": "Repair severed blood vessel and airway segmentation masks, trace ordered 3D centerline paths, and generate 360-degree rotated Curved Planar Reformations (CPRs) with calibrated distance axes.",
        "research_round": {
            "round_id": "BR-030 / BR-033",
            "title": "Vessel repair to diagnostic geometry & Brain vessel airway difficulty",
            "document_path": "docs/research-rounds/BR-030-vessel-diagnostic-geometry.md",
            "results_path": "docs/research-rounds/BR-030-results.md",
            "evidence_path": "site/vessel-figures.json"
        },
        "input_data": {
            "dataset_name": "ImageCAS / ASOCA Coronary CTA & AeroPath Airway CT",
            "source_cases": [
                {
                    "case_id": "Coronary_Case_1",
                    "modality": "Contrast-Enhanced Coronary CTA",
                    "dimensions": [256, 256, 180],
                    "voxel_spacing_mm": [0.45, 0.45, 0.70],
                    "defect": "Synthetic 200-voxel (8 mm) gap in right coronary artery (RCA)",
                    "anchors": ["RCA ostium", "Distal R-PDA"]
                },
                {
                    "case_id": "Airway_Case_A01_A03",
                    "modality": "Chest CT",
                    "defect": "Segmental disconnections in peripheral airway tree from AeroPath"
                }
            ]
        },
        "ground_truth": {
            "gt_source": "ImageCAS-X reference masks, expert centerlines, and calibrated CPR stacks",
            "gt_centerline_length_mm": 104.08,
            "gt_frenet_frame": "Continuous orthogonal normal vectors sampled at 0.5 mm arc steps"
        },
        "task_instruction_prompt": "Repair the vessel mask disconnection within the review sphere while preserving all voxels outside. Extract an ordered centerline from ostium to distal anchor in RAS mm. Generate 8 rotated CPR planes (0 to 315 degrees in 45-degree steps), preserving original HU values, source coordinates, and a physical distance axis. Export a watertight surface mesh.",
        "output_contract": {
            "expected_artifacts": [
                "repaired_mask.nii.gz (Binary volume preserving exterior voxels)",
                "centerline.json (Ordered array of [x, y, z] points in RAS mm)",
                "cpr_planes.npz (8 2D arrays with HU, coordinate mapping, and distance axis)",
                "vessel_surface.obj (Watertight closed triangular surface mesh)"
            ]
        },
        "evaluation_rubric": {
            "connectivity_check": "Single connected component from start to end anchor",
            "preservation_check": "No more than 10 extraneous voxels added outside review sphere",
            "cpr_axis_consistency": "Max discrepancy between CPR horizontal axis and true cumulative physical arc length <= 1.0 mm"
        },
        "empirical_results": {
            "coronary_cpr_br030": {
                "model": "Terra (GPT-4o / high)",
                "wall_time": "8m 12s",
                "tokens": 11200,
                "cost_usd": 0.72,
                "mask_repair": "198 / 200 voxels restored",
                "mesh_validity": "Closed watertight mesh generated",
                "cpr_outcome": "FAILED AUTOMATED CHECK by 8.89 mm due to distance-axis bug (indexed raw voxel steps rather than cumulative physical millimeters)"
            },
            "airway_repair_br033": {
                "model": "Sol (Claude 3.7 Sonnet / xhigh)",
                "wall_time": "12m 40s",
                "tokens": 16800,
                "cost_usd": 1.82,
                "benchmark_outcome": "PASSED AUTOMATED GATES despite peripheral airway fragments remaining completely disconnected from the central trachea (Evaluation Loophole)"
            }
        },
        "known_failure_modes_and_traps": {
            "trap_name": "The CPR Distance-Axis Bug & The Airway Fragment Loophole",
            "description": "In BR-030, a perfect anatomical reconstruction failed because the verifier compared raw pixel coordinates against anisotropic millimeter spacing. In BR-033, the verifier checked sub-routes within isolated fragments, awarding passing scores while the main bronchial tree remained broken."
        }
    },
    {
        "task_id": "MED-BIO-BR035-CARDIAC-STRAIN",
        "task_name": "4D Left-Ventricular Biomechanical Mesh Tracking & Myocardial Strain",
        "domain": "Domain 05: 4D Heart Biomechanics & Myocardial Strain",
        "clinical_objective": "Reconstruct moving 3D left-ventricular myocardium surface meshes across 30 cardiac phases and compute volume-weighted engineering strain tensors across the AHA 17-segment model.",
        "research_round": {
            "round_id": "BR-035 / BR-032",
            "title": "Segmentation mechanics & Real clinical echocardiography case",
            "document_path": "docs/research-rounds/BR-035-segmentation-mechanics.md",
            "results_path": "docs/research-rounds/BR-035-results.md",
            "evidence_path": "site/cardiac-figures.json"
        },
        "input_data": {
            "dataset_name": "STRAUS Simulation Cohort & Clinical 3D Echocardiography",
            "dataset_citation": "Human Heart Project, CREATIS, INSA Lyon. Dynamic cardiac biomechanics finite element model.",
            "file_artifacts": [
                {
                    "file_name": "segmentations_30phases.npz",
                    "description": "30 complete 3D binary myocardial-wall segmentations across the full cardiac cycle",
                    "dimensions": [128, 128, 128],
                    "voxel_spacing_mm": [1.5, 1.5, 1.5]
                },
                {
                    "file_name": "ultrasound_30phases.npz",
                    "description": "Registered 3D B-mode echocardiography intensity volumes (optional multi-modal condition)"
                }
            ]
        },
        "ground_truth": {
            "gt_source": "STRAUS continuum finite element simulation ground-truth material points and displacement tensors",
            "clinical_ground_truth": {
                "end_diastolic_volume_ml": 142.5,
                "end_systolic_volume_ml": 61.2,
                "ejection_fraction_pct": 57.1,
                "peak_strains": {
                    "longitudinal_pct": -18.4,
                    "circumferential_pct": -21.6,
                    "radial_pct": 44.8
                }
            }
        },
        "task_instruction_prompt": "Construct moving 3D tetrahedral meshes from 30 phase masks. Compute the continuous deformation gradient F and Green-Lagrange strain tensor E. Report cavity volume curves, Ejection Fraction, and volume-weighted engineering strains across the 17 AHA segments.",
        "output_contract": {
            "expected_artifacts": [
                "dynamic_mesh.npz (Vertices and tetrahedral connectivity for 30 phases)",
                "cardiac_report.json (Volume curve, EF %, and 30x17x3 regional strain tensor array)"
            ]
        },
        "evaluation_rubric": {
            "mesh_quality": "Zero inverted elements (det(F) > 0 across all elements)",
            "volume_conservation": "Cavity and tissue volume error <= 5.0%",
            "strain_tolerances": {
                "longitudinal_mae_pp": 3.0,
                "circumferential_mae_pp": 3.0,
                "radial_mae_pp": 4.0
            }
        },
        "empirical_results": {
            "sol_masks_alone": {
                "model": "Sol (Claude 3.7 Sonnet / xhigh)",
                "wall_time": "21.55 min",
                "surface_dice": 0.946,
                "ef_computed_pct": 56.1,
                "strain_errors_mae": {"longitudinal_pp": 2.87, "circumferential_pp": 3.51, "radial_pp": 7.37},
                "outcome": "MESH PASS / RADIAL STRAIN MISS (Overshot radial strain by 7.37 pp)"
            },
            "sol_masks_plus_ultrasound": {
                "model": "Sol (Claude 3.7 Sonnet / xhigh)",
                "wall_time": "13.26 min",
                "surface_dice": 0.933,
                "ef_computed_pct": 57.0,
                "strain_errors_mae": {"longitudinal_pp": 2.90, "circumferential_pp": 3.22, "radial_pp": 5.45},
                "outcome": "MESH PASS / RADIAL STRAIN MISS (Overshot radial strain by 5.45 pp)"
            },
            "clinical_echo_tracking_br032": {
                "description": "Hospital 3D ultrasound tracking tool",
                "surface_distance_error_mm": 2.8,
                "ef_measured_pct": 31.5,
                "true_ef_pct": 58.0,
                "outcome": "CATASTROPHIC CLINICAL UNDERESTIMATION (Simulated severe heart failure due to boundary error propagation)"
            }
        },
        "known_failure_modes_and_traps": {
            "trap_name": "The Cylinder Twist Paradox",
            "description": "Surface overlap (Dice 0.946) does not guarantee accurate material mechanics. The agent matched moving surface boundaries by twisting and shearing internal elements, leading to a 7.37 pp error in radial wall thickening. Biomechanics require material-level ground truth."
        }
    },
    {
        "task_id": "MED-LND-BR040-LANDMARKS-FOV",
        "task_name": "3D Anatomical Landmarks & Out-of-Field-of-View Rejection",
        "domain": "Domain 06: 3D Anatomical Landmarks & Out-of-FOV Rejection",
        "clinical_objective": "Accurately predict 3D physical coordinates for 26 vertebral centroids (C1–L6) on spine CT and 32 brain fiducials on MRI, while strictly rejecting targets outside the field-of-view (OUT_OF_FOV) without hallucinating.",
        "research_round": {
            "round_id": "BR-040",
            "title": "Sol/xhigh CT and MRI landmark comparison",
            "document_path": "docs/research-rounds/BR-040-sol-landmarks.md",
            "results_path": "docs/research-rounds/BR-040-results.md",
            "evidence_path": "docs/evidence/br040-source-audit.json"
        },
        "input_data": {
            "datasets": [
                {
                    "name": "VerSe Vertebral Segmentation Benchmark",
                    "citation": "Sekuboyina et al., Medical Image Analysis 2021. DOI: 10.1016/j.media.2021.102166",
                    "subject": "sub-verse823",
                    "full_scan_shape": [512, 512, 1214],
                    "cropped_scan_shape": [512, 512, 480],
                    "voxel_spacing_mm": [0.80, 0.80, 1.25],
                    "targets_requested": 26
                },
                {
                    "name": "AFIDs SNSX Brain MRI Cohort",
                    "citation": "Lau et al., Scientific Data 2020. DOI: 10.1038/s41597-020-00629-8. OpenNeuro ds004470",
                    "subject": "sub-C001",
                    "dimensions": [256, 256, 176],
                    "voxel_spacing_mm": [1.0, 1.0, 1.0],
                    "targets_requested": 32
                }
            ]
        },
        "ground_truth": {
            "gt_source": "VerSe manual segmentation centroids and AFIDs 3-rater consensus fiducials",
            "full_ct_visible": 24,
            "full_ct_absent": 2,
            "cropped_ct_visible": 13,
            "cropped_ct_outside_fov": 11,
            "cropped_ct_absent": 2,
            "mri_visible": 32
        },
        "task_instruction_prompt": "For each requested landmark, return its fractional native voxel coordinate [i, j, k] and status: 'OBSERVED', 'OUT_OF_FOV', or 'ABSENT'. Explicitly label outside estimates; do not claim an unavailable target is observed inside the scan.",
        "output_contract": {
            "expected_file": "landmarks.json",
            "format": "JSON array of landmark predictions",
            "coordinate_convention": "Native zero-indexed fractional voxel indices [i, j, k] explicitly tagged 'voxel_ijk_zero_based'"
        },
        "evaluation_rubric": {
            "metric": "Euclidean 3D distance transformed by affine linear matrix: ||A * (v_pred - v_gt)||",
            "tolerances": {"ct_spine_mm": 5.0, "mri_brain_mm": 3.0},
            "hallucination_penalty": "Claiming an OUT_OF_FOV target is OBSERVED inside the scan is penalized as a critical hallucination error"
        },
        "empirical_results": {
            "cropped_spine_ct": {
                "terra_high": {
                    "points_within_5mm": "1 / 13",
                    "mean_error_mm": 20.85,
                    "hallucinations": "1 / 11 outside targets falsely detected inside (T4 predicted 2.14 mm from true T5)"
                },
                "sol_xhigh": {
                    "points_within_5mm": "4 / 12",
                    "mean_error_mm": 7.44,
                    "hallucinations": "0 / 11 outside targets falsely detected (Zero hallucinations)"
                }
            },
            "brain_mri_afids": {
                "terra_high": {
                    "points_within_3mm": "3 / 32",
                    "mean_error_mm": 9.40,
                    "strategy": "Direct image inspection without atlas"
                },
                "sol_xhigh": {
                    "points_within_3mm": "14 / 32",
                    "mean_error_mm": 3.87,
                    "strategy": "Autonomous retrieval of MNI152 template and affine atlas registration"
                }
            }
        },
        "known_failure_modes_and_traps": {
            "trap_name": "Wrong-Level Surgical Hallucination vs. Autonomous Atlas Orchestration",
            "description": "On cropped CT, Terra detected real bone but miscounted vertebral levels (predicting T4 on the T5 vertebral body). Sol correctly abstained. On MRI, Sol autonomously downloaded the MNI brain atlas to double accuracy within 3 mm."
        }
    }
]

for card in CARDS:
    filename = card["task_id"].lower().replace("-", "_") + ".json"
    filepath = TASK_CARDS_DIR / filename
    with open(filepath, "w") as f:
        json.dump(card, f, indent=2)
    print(f"Wrote {filepath} ({filepath.stat().st_size:,} bytes)")

print("All task cards generated successfully!")
