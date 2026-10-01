**Full CT-ORG pair absent — symbolic protocol.** [Official CT-ORG acquisition](https://www.cancerimagingarchive.net/collection/ct-org/). No exact degraded volume, private HR or selected Full list acquired.

# Restore CT-ORG through-plane detail under the Full contract

Explain the pinned Full task contract and its input-to-output operation. This is a symbolic protocol view; no Full case, participant prediction or score is available.

## Value

Through-plane restoration seeks information lost by degradation while retaining the native grid and HU convention. Sharper appearance, identical shape or proxy score does not establish anatomical recovery or clinical accuracy.

## Given

### Original data

Config calls the public ct.nii.gz a same-grid x4 z-axis trilinear-degraded CT volume, with public and hidden HR shapes equal. No exact degradation code, interpolation conventions, phase/antialiasing, original voxel dimensions, affine, physical-axis mapping, spacing, orientation or selected case is retained. Same-grid shape does not prove HR signal recovery. Fourfold degradation is through-plane, not x4 enlargement in all dimensions. CTORG_CT_SR20 and Standard S3 all 20 are declared task intent, not recovered IDs/count. task.json case and evaluator patient naming do not establish a join or patient-independent split.

Official upstream CT-ORG describes native NIfTI HU volumes and CC BY 3.0 attribution; its historical Wiki warns of left-right flips. Upstream segmentation train/test and organ labels are not this Full restoration selection or private HR. No upstream volume, label or derivative is embedded. An independently acquired helper would need affine/pixel/rights proof and a separate later reader role.

### Supplied helpers

Lite prescribes ISBI2023 PlainCNN_trilinear_interpolation_x4.pth from Roldbach/autoencoder_ct_3d_super_resolution; same-grid degraded CT, inverse normalization and preserving shape/affine/header remain task work. Standard S1 asks comparison of all 5 named checkpoint variants: PlainCNN, AE_Maxpool and UNet trilinear x4; PlainCNN/AE_Maxpool same-insertion x4. No immutable weight/source revision/hash is pinned or acquired. Named availability/compatibility claims are guidance, not performance or current validated suitability. CUDA0 setup and GPU guidance are declared; no runtime/model installed or executed. Tier config requires plan.md for both, plan.png only Standard; no postprocessing requirement.

### Callable tools

The source specifies plan, setup, validation, inference and submission stages with a terminal, task-specific libraries and tier guidance. No tool or model was executed for this explanation.

### Reference-only material

The matching high-resolution or CT target is held under the Full evaluator's private mount. It is absent here and never shown as a solver input. 

## Task specification

Estimate through-plane detail while preserving x-y placement, native 3D grid and HU scale. The output is not fourfold larger in every dimension. Follow the selected Lite or Standard stage guidance and preserve the Full split. The harness has `dataset.included=false`; an upstream image would not by itself establish Full case membership.

## Expected output

Write agents_outputs/<case_id>/sct.nii.gz; evaluator --agent-dir receives case directories, without an extra internal root. Required same public/privateHR grid and HU scale. Checker loads NIfTI as float32 and requires finite 3D; no strict on-disk floating dtype or affine/header/spacing equality guard. Shape is checked against private target if it exists; absent reference skips shape check. HU min<-2500/max>5000 and constants warn, not fail. Missing predictions do not invalidate present-output format; scorer/aggregate handle incompleteness. No submitted artifact.

## Evaluation

Effective backend is source/run_eval.py synthetic, not LDCT/MRI-SR enhancement v2/v3 bands. Config is loaded by exact task ID/alias ctorg-ctsr; load failure silently falls back to generic MR/mask defaults and .90/.75 thresholds. Correct configured thresholds are mean SSIM≥.98 good/tier2, ≥.95 okay/tier1, else tier0. No baseline_bands, LPIPS, PSNR normalization window or LDCT rating is bound here.

No mask_filename is configured: HU MAE/RMSE use the full volume without clipping. PSNR uses fixed range 4095 HU (-1024..3071), identical MSE→infinity; only finite PSNR values enter mean, so a perfect case may be omitted from mean PSNR. SSIM clips arrays to[-1024,3071], computes slice means along array axis2 regardless of physical affine, skips small planes/errors, and is None without scikit-image. When a mask is configured in another route, MAE uses mask>.5 with empty ROI→full volume, while SSIM skips low-mask slices but still scores full retained planes; this is not the configured CT-ORG route.

Scorer checks equal array shapes and finite prediction; no affine/header/GT finiteness guard or registration proof. Missing prediction/GT/load/shape failures are unscored. Means are over valid scored outputs, with separate SSIM and finite PSNR denominators; evaluator-supplied patient-ID rows remain completion denominator and are not deduplicated in metric lists. Repeated IDs collapse the keyed per_patient diagnostic dictionary while repeated loop iterations still enter metric/completion counts; no unique patient denominator is proven. Empty IDs yield completion 0; report coerces n_patients to 1. No actual count or score.

Clinical-named proxy is finite clipped mean SSIM 0–1 multiplied by n_predicted/allIDs, rounded 4 decimals. S4=.5completion+.5format; S5=.5(anyvalid and positiveproxy)+.5format. S1–S3 remain None→0 in this entrypoint, even though optional judge is attached afterwards without recomputing steps; weights .25/.15/.35/.15/.10 retain full denominator1. Overall=.5workflow+.5proxy. Rating isA/B/C from SSIM medal when format valid and n_predicted>0, else F; partial inference can retain A/B while losing proxy credit. Progress rate counts completion≥.9 and format over 2 gates. These are source mechanics, not clinical accuracy or observed performance. No evaluator executed.

## Visual explanation

### Workflow

Absent same-grid CT → declared x4 z degradation audit → checkpoint and normalization/restoration contract → empty NIfTI output → source/evaluator limits. No public mask is configured.

### Input

**Symbolic contract; no native pixels.** Config calls the public ct.nii.gz a same-grid x4 z-axis trilinear-degraded CT volume, with public and hidden HR shapes equal. No exact degradation code, interpolation conventions, phase/antialiasing, original voxel dimensions, affine, physical-axis mapping, spacing, orientation or selected case is retained. Same-grid shape does not prove HR signal recovery. Fourfold degradation is through-plane, not x4 enlargement in all dimensions. CTORG_CT_SR20 and Standard S3 all 20 are declared task intent, not recovered IDs/count. task.json case and evaluator patient naming do not establish a join or patient-independent split.

Official upstream CT-ORG describes native NIfTI HU volumes and CC BY 3.0 attribution; its historical Wiki warns of left-right flips. Upstream segmentation train/test and organ labels are not this Full restoration selection or private HR. No upstream volume, label or derivative is embedded. An independently acquired helper would need affine/pixel/rights proof and a separate later reader role.

### Supplied helpers

**Visible task guidance.** Lite prescribes ISBI2023 PlainCNN_trilinear_interpolation_x4.pth from Roldbach/autoencoder_ct_3d_super_resolution; same-grid degraded CT, inverse normalization and preserving shape/affine/header remain task work. Standard S1 asks comparison of all 5 named checkpoint variants: PlainCNN, AE_Maxpool and UNet trilinear x4; PlainCNN/AE_Maxpool same-insertion x4. No immutable weight/source revision/hash is pinned or acquired. Named availability/compatibility claims are guidance, not performance or current validated suitability. CUDA0 setup and GPU guidance are declared; no runtime/model installed or executed. Tier config requires plan.md for both, plan.png only Standard; no postprocessing requirement.

### Reference or output

**Empty output schema.** `agents_outputs/{case_id}/sct.nii.gz`, finite 3D NIfTI on the public/target grid, in HU. Private reference remains absent.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: ISBI 2023 3D CT SISR PlainCNN x4. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

The spaced axial planes are a sampling schematic, not CT voxels or a restoration result. The task-specific input, geometry and target roles must be retained before any quality claim.

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/synthetic/ctorg-ctsr-task.tar.gz)
- [Official upstream route](https://www.cancerimagingarchive.net/collection/ct-org/)
- [Source resolution receipt](../sources/automedbench-full-ctorg-ctsr-task-resolution.json)

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

## Gaps

Dated landing reachability retained; current fetch500 and readable historical primary metadata do not establish an access denial. No small matching Full degraded/private pair or membership recovered. This symbolic explanation has no model result, clinical claim or score. Generic stage prompts still describe cyst segmentation and organ/lesion masks, contradicting the task-specific config, checker and scorer requirement for `sct.nii.gz`; this unexecuted source conflict remains open.
