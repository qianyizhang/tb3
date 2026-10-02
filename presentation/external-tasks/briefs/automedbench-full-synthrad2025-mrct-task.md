> **Matching Full MR/mask/CT pair absent; symbolic roles only. [Official SynthRAD acquisition](https://zenodo.org/records/15373853).**

# Synthesize head-and-neck CT from MRI

Produce a synthetic CT volume in the declared HU domain from each supplied MRI and outline mask, preserving the source task’s case grid and output contract. Matching Full inputs, private CT and participant output remain absent.

## Value

MR→CT synthesis predicts a different intensity domain; it is not super-resolution. No generated sCT, numerical quality or clinical outcome is shown.

## Given

### Original data

Per case, public `mr.nii.gz` is MRI; its exact arbitrary-intensity normalization, shape, affine, orientation, voxel spacing and FOV are unstaged. Task config names `SynthRAD2025_MRCT_HN20`; Standard guidance says 20 patients, but supplied IDs determine evaluator denominators and no 20-count enforcement is found. Official training record provides preprocessed `.mha` MR/CT/mask, not the Full selected NIfTI cases. Conversion, registration and partition mapping remain unverified.

### Supplied helpers

Public `mask.nii.gz` is a binary dilated body-outline ROI, not target CT or segmentation output. Lite prescribes VBoussot SynthRAD2025 Task 1 HN five-fold CV_0–CV_4 plus Prediction.yml, 2.5D U-Net++/ResNet34 KonfAI per source. Standard compares HN VBoussot and aehrc Dataset262 with AB-TH fallback. Source model Apache-2.0 claims are unverified; no checkpoint, runtime or availability proven. Benchmark is inference-only; no training or fine-tuning.

### Callable tools

The source expects terminal/library/GPU inference and `submit_results`; no task tool/model/solver/evaluator is executed here.

### Reference-only material

Private paired `ct.nii.gz` in HU is evaluation-only and absent. No private CT truth is bundled. A late reader-only upstream training MR 1HNC117 display is included; membership in Full HN20 and paired mask/CT are unverified. Late reader reveal exposes rules only; reset, backward seek and scene exit clear it before paint.

## Task specification

Map MR plus outline mask to synthetic CT in HU; preserve source geometry and invert model normalization as applicable. Do not treat MR arbitrary units as HU or invent a 2× resize. Source-specific output is `sct.nii.gz`. Generic common/S4/S5 templates name Dice, organ/lesion masks and filenames that conflict with the specific config and model guidance; that conflict is retained, not silently resolved by importing segmentation or SR defaults.

## Expected output

Write `agents_outputs/{case_id}/sct.nii.gz`. This plural task path is distinct from CLI's arbitrary `--agent-dir`; no mounted execution is established. Checker loads float32, checks 3D/finiteness, compares shape with public MR by default only if it exists; no affine/spacing/orientation equality check. Missing files do not fail format by themselves; extreme HU below −2500/above5000 and constant volumes warn, not error. These checks do not prove plausible synthesis, registration or medical utility. Actual output remains empty.

## Evaluation

Task source `run_eval.py` calls `synth_scorer.py`, `medal_tier.py` and `aggregate.py`; no generic SR/LDCT PSNR/LPIPS norms or bands apply. No LPIPS backend appears. Private CT, public mask and output shapes must match; nonfinite prediction fails. Mask >0.5 sets voxel ROI, empty mask falls back to whole volume. MAE/RMSE HU use unclipped differences; PSNR dB uses range4095 HU (3071−(−1024)) and perfect infinity is excluded from aggregate finite-PSNR cases. SSIM separately clips both CT arrays to [−1024,3071], uses full x-y axial slices along array axis2 (anatomical orientation unverified), skips mask slice sum<16/min plane dimension<7; optional scikit-image import/operation failure yields None. It is not voxel-mask SSIM.

Prediction finiteness is checked; reference CT and mask finiteness are not explicitly checked. Repeated supplied IDs are not deduplicated: per-case dictionaries overwrite the key while metric lists and supplied-ID counts retain repeated entries. Valid cases form MAE/RMSE denominators. Available slices form each SSIM and available cases form mean SSIM; finite PSNR has its own denominator. `n_predicted/n_patients` uses supplied IDs; IDs and private targets absent. Good SSIM≥.90/okay≥.75 inclusive maps medal2/1 and valid, nonzero-scored results to A/B; C otherwise, F for invalid format/no scored output. Completion≥.9 contributes progress, not an A/B rating gate. No rating observed.

Offline workflow weights .25/.15/.35/.15/.10 keep S1–S3 None as zero under all weights. S4=.5completion+.5format; S5=.5has_valid_results+.5format, where has_valid_results needs positive clipped SSIM. Code named clinical_score is clipped meanSSIM times completion, overall half workflow/half clinical; neither term establishes clinical performance. CLI default `synthrad2025_hn_mrct` is not an alias; config-load exception falls back filenames, medal defaults still .90/.75. Exact invocation remains unknown.

## Visual explanation

### Workflow

Four canonical steps: MR/mask roles → same-grid HU output contract → Lite/Standard and format → source metric/denominator distinctions. Symbolic unknown cells, no resampling or synthesis.

### Input

Teal MR-role cells are authored unknowns; no patient intensities. Outline represents output socket, not reconstructed CT; gray private reference remains absent. Physical geometry is unverified.

### Supplied helpers

Tier selector changes source guidance only; format and metric selectors inspect rules, never execute a model or scorer.

### Reference or output

Later reader-only rules contain no CT truth, performance or private answer. Actual output is always absent.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: VBoussot SynthRAD2025 Task 1 HN ensemble. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

Match MR preprocessing, inverse CT normalization and registration without assuming shape means geometric alignment. Missing native pairs and checkpoints limit this packet to task interpretation.

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/synthetic/synthrad2025-mrct-task.tar.gz)
- [Official training record / CC BY-NC 4.0](https://zenodo.org/records/15373853)
- [Resolution receipt](../sources/automedbench-full-synthrad2025-mrct-task-resolution.json)

## Gaps

No exact Full MR/mask/private CT pair, Full geometry, selected IDs/partition, MHA-to-NIfTI lineage, model weights or metric execution. Upstream MR-only native cell parity is verified separately; it does not close those gaps.

### Upstream MR helper: late reader display only

Official open CC BY-NC 4.0 training ZIP member `Task1/HN/1HNC117/mr.mha` was recovered by 206 byte ranges without downloading the 14.85 GB archive. Whole-archive SHA is unknown; advertised MD5 is metadata only. Exact local member CRC, decompressed MHA SHA/header and signed16 303×302×41 payload are checked. Header ElementSpacing=1,1,3; identity TransformMatrix, Offset=−174,−130.19999694824219,297.33999633789062; RAI header and original NIfTI srows retained without reinterpretation. Header xyzt_units2 records mm.

Display is native k20, native i/j0,3,…,300, no flip/reorientation: 101×101 cells. Plane-local min/max maps each cell by floor(255*(value−min)/(max−min)); this is display treatment, not model normalization. At native i=j=0,k20, MHA coordinate formula Offset+direction×spacing×index gives z357.33999633789062 in recorded units. MR intensity is arbitrary, no HU conversion. No paired CT/mask acquired; no registration, fitting, synthesis or score. Reader must reveal the helper later; backward seek/exit/reset removes it before paint.

Attribution: Thummerer, van der Bijl, Galapon Jr., Kamp and Maspero, *SynthRAD2025 Grand Challenge dataset: Training*, DOI10.5281/zenodo.15373853, [CC BY-NC4.0](https://creativecommons.org/licenses/by-nc/4.0/).
