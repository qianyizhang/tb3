**Full MSD Pancreas pair absent — symbolic protocol.** [Official MSD Pancreas acquisition](https://medicaldecathlon.com/). No exact degraded volume, private HR or selected Full list acquired.

# Restore MSD Pancreas through-plane detail under the Full contract

Explain the pinned Full task contract and its input-to-output operation. This is a symbolic protocol view; no Full case, participant prediction or score is available.

## Value

Through-plane restoration seeks information lost by degradation while retaining the native grid and HU convention. Sharper appearance, identical shape or proxy score does not establish anatomical recovery or clinical accuracy.

## Given

### Original data

Config calls the public ct.nii.gz a same-grid x4 z-axis trilinear-degraded CT volume, with public and hidden HR shapes equal. No exact degradation code, interpolation conventions, phase/antialiasing, original voxel dimensions, affine, physical-axis mapping, spacing, orientation or selected case is retained. Same-grid shape does not prove HR signal recovery. Fourfold degradation is through-plane, not x4 enlargement in all dimensions. MSD_Pancreas_CT_SR20 and Standard S3 all 20 are declared task intent, not recovered IDs/count. task.json case and evaluator patient naming do not establish a join or patient-independent split.

Official registry lists CC BY-SA 4.0 and an anonymously accessible MSD archive. A bounded 64 KiB range yielded complete upstream dataset.json (release 1.0 04/05/2018): CT, 3D, 281 training/139 test paths. These are upstream segmentation counts, not Full 20 restoration IDs or a demonstrated overlap/independence relation. Labels in upstream metadata describe a segmentation family; no label map/patient annotation is displayed as an answer here. First listed test image is 28,239,655 B and incomplete in the prefix; no complete image, HU pixel distribution, affine or derivative was decoded. No native image/helper is embedded. Matching Full membership and degraded/privateHR join cannot be inferred from anatomy resemblance or filenames.

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

Effective backend is source/run_eval.py synthetic, not LDCT/MRI-SR enhancement v2/v3 bands. Config is loaded by exact task ID msd-pancreas-ctsr-task / aliases msd-pancreas, msd-pancreas-ctsr, pancreas-ctsr; load failure silently falls back to generic MR/mask defaults and .90/.75 thresholds. Correct configured thresholds are mean SSIM≥.98 good/tier2, ≥.95 okay/tier1, else tier0. No baseline_bands, LPIPS, PSNR normalization window or LDCT rating is bound here.

No mask_filename is configured: HU MAE/RMSE use the full volume without clipping. PSNR uses fixed range 4095 HU (-1024..3071), identical MSE→infinity; only finite PSNR values enter mean, so a perfect case may be omitted from mean PSNR. SSIM clips arrays to[-1024,3071], computes slice means along array axis2 regardless of physical affine, skips small planes/errors, and is None without scikit-image. When a mask is configured in another route, MAE uses mask>.5 with empty ROI→full volume, while SSIM skips low-mask slices but still scores full retained planes; this is not the configured MSD Pancreas route.

Scorer checks equal array shapes and finite prediction; no affine/header/GT finiteness guard or registration proof. Missing prediction/GT/load/shape failures are unscored. Means are over valid scored outputs, with separate SSIM and finite PSNR denominators; evaluator-supplied patient-ID rows remain completion denominator and are not deduplicated in metric lists. Repeated IDs collapse the keyed per_patient diagnostics while repeated loop iterations still enter metric/completion counts; no unique patient denominator is proven. Empty IDs yield completion 0; report coerces n_patients to 1. No actual count or score.

Clinical-named proxy is finite clipped mean SSIM 0–1 multiplied by n_predicted/allIDs, rounded 4 decimals. S4=.5completion+.5format; S5=.5(anyvalid and positiveproxy)+.5format. S1–S3 remain None→0 in this entrypoint, even though optional judge is attached afterwards without recomputing steps; weights .25/.15/.35/.15/.10 retain full denominator1. Overall=.5workflow+.5proxy. Rating isA/B/C from SSIM medal when format valid and n_predicted>0, else F; partial inference can retain A/B while losing proxy credit. Progress rate counts completion≥.9 and format over 2 gates. These are source mechanics, not clinical accuracy or observed performance. No evaluator executed.

## Visual explanation

### Workflow

Absent same-grid CT → declared x4 z degradation audit → checkpoint and normalization/restoration contract → empty NIfTI output → source/evaluator limits. No public mask is configured.

### Input

**Symbolic contract; no native pixels.** Config calls the public ct.nii.gz a same-grid x4 z-axis trilinear-degraded CT volume, with public and hidden HR shapes equal. No exact degradation code, interpolation conventions, phase/antialiasing, original voxel dimensions, affine, physical-axis mapping, spacing, orientation or selected case is retained. Same-grid shape does not prove HR signal recovery. Fourfold degradation is through-plane, not x4 enlargement in all dimensions. MSD_Pancreas_CT_SR20 and Standard S3 all 20 are declared task intent, not recovered IDs/count. task.json case and evaluator patient naming do not establish a join or patient-independent split.

Official registry lists CC BY-SA 4.0 and an anonymously accessible MSD archive. A bounded 64 KiB range yielded complete upstream dataset.json (release 1.0 04/05/2018): CT, 3D, 281 training/139 test paths. These are upstream segmentation counts, not Full 20 restoration IDs or a demonstrated overlap/independence relation. Labels in upstream metadata describe a segmentation family; no label map/patient annotation is displayed as an answer here. First listed test image is 28,239,655 B and incomplete in the prefix; no complete image, HU pixel distribution, affine or derivative was decoded. No native image/helper is embedded. Matching Full membership and degraded/privateHR join cannot be inferred from anatomy resemblance or filenames.

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

- [Official MSD AWS registry/rights](https://registry.opendata.aws/msd/) and [organizer AWS download route](https://medicaldecathlon.com/dataaws/).

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/synthetic/msd-pancreas-ctsr-task.tar.gz)
- [Official upstream route](https://medicaldecathlon.com/)
- [Source resolution receipt](../sources/automedbench-full-msd-pancreas-ctsr-task-resolution.json)

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

## Gaps

Dated original attempts retained; current official homepage/dataaws timeouts and successful AWSlisting/prefix reads do not establish an access barrier. The 12,289,971,712 B archive is accessible, but only 64 KiB metadata/header were acquired; no complete matching Full pair or membership was recovered. This symbolic explanation has no model result, clinical claim or score. Generic stage prompts still describe cyst segmentation and organ/lesion masks, contradicting the task-specific config, checker and scorer requirement for `sct.nii.gz`; this unexecuted source conflict remains open.

Full 12,289,971,712 B archive hash remains unverified. The retained 64 KiB TAR prefix contains complete dataset.json with 281 training / 139 test paths and only an incomplete first 28,239,655 B image; these are upstream segmentation paths, not Full restoration pairs.
