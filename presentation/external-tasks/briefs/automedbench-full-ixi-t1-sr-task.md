> **Matching Full IXI input / private target absent; upstream T1 example is reader-only. [Official IXI acquisition](https://brain-development.org/ixi-dataset/).**

# Trace T1 2× geometry without inventing a high-resolution MRI

Source-pinned Full contract, symbolic pixel mechanics and private-evaluator boundaries. No matching Full input, reconstruction or clinical outcome.

## Given

### Original data

Full package ixi-t1-sr-task, MRI_T1w / IXI T1. Per-case public input.npy, declared normalized float32 (128, 128), 16,384 pixels; target (256, 256), 65,536 pixels, 2× length / 4× cells. Harness dataset.included=false /data_status not_included /split unresolved. Official range recovery retained one upstream IXI T1 whole-volume NIfTI, not an exact Full case/slice/degradation mapping. Case folders called patient IDs by common prompts; whole-patient versus 2D slice multiplicity unknown. No Full scanner sequence, physical grid/FOV, anatomical findings or private target established; upstream source-example geometry is separate.

### Supplied helpers

Configuration, task/model info and planning/setup/validation/inference/submission prompts. Full Lite prescribes public caidas/swin2SR-classical-sr-x2-64; grayscale→model-compatible channels→grayscale mapping remains operator responsibility, not a supplied exact preprocessing. Standard compares at least 3 inference-only methods including at least 2 pretrained neural, one bicubic/Lanczos baseline allowed. Public pilot case required but not bundled. No model files/runtime assets. Requirements NumPy/SciPy/skimage/torch/Pillow/transformers minimum versions; LPIPS package absent although scorer requires it. GPU/DNN evaluation mode mandated, no weight updates/train/optimizer/backward or private reference access. These are task instructions, not runtime verification here.

### Callable tools

No task/model/tool/evaluator executed or installed. Authoring SVG shows symbolic 2 × 2 normalized cells [.1,.4;.3,.8] beside 4 × 4 unknown output sockets; these are NOT MRI, real voxels, bicubic outputs, reference or submitted arrays. Shapes reduced for illustration only; exact declared 128²→256² counts separately shown. Pixel color legend: teal authored low-resolution values; outlined high-resolution cells unknown. An upstream whole-volume source-example display is available only in the later reader reveal; exact native pixel parity is verified, but it is not a Full input or private target.

### Reference-only material

/data/private/<case_id>/reference.npy and private ground_truth.csv:data_range belong to evaluation, never participants or the explainer. No private file acquired or displayed. Public pretrained checkpoint and source contract are helpers, not target evidence. Late reader reveal teaches upstream source provenance and private reference/metric rules; exit/backward/reset covers before paint. Actual target, enhanced.npy and metrics always absent.

## Task specification

Declared normalized 128×128 T1 input from bicubic downsampling with scale 2; output 256×256 [0,1]. Harness includes NO degradation/preprocessing implementation, source slice selection, normalization min/max or clipping, cubic kernel parameter, coordinate convention, antialias setting, border mode, downsample library/version, voxel geometry or exact data split. Do not infer nearest/bilinear, z-axis super-resolution, synthesized noise, retained high-res texture or restored clinical edges. Mathematical 2× shape expansion changes cell counts, not known information; high-resolution values remain unknown. No resized clinical image or method outcome.

Full Lite and Standard are assistance tiers of this harness. Related gallery/branch/Lite package conditions preserved below but equivalence not established. Named Swin2SR baseline is a public model selection, not evidence that it loads, fits T1 domain or preserves pathology. No inference/training/performance. Prompt same shape as input in common preamble conflicts task-specific 128→256 config and tier validation; task-specific geometry explains intended output, generic checker derives shape from private reference. Task-specific Lite validation uses agent_outputs singular while task.json/S5 establish agents_outputs plural; retain discrepancy, intended declared output root plural.

## Expected output

{output_dir}/agents_outputs/<case_id>/enhanced.npy, one 2D normalized float32 finite 256×256 per case. Optional agents_decision.csv not scored. Actual output empty. Format checker checks 2D, expected private-reference shape, floating dtype and finite values; accepts float64, does NOT enforce float32, [0,1], nonconstant or quality. A format-valid fixture would not be a conformant medical result. No new source checker/evaluator execution; pure authored predicates only.

## Evaluation

Config primary mean_ssim, diagnostic PSNR/LPIPS; runner always computes all 3 aligned and cyclic shuffled, requires LPIPS even if diagnostic. Source SSIM skimage structural_similarity(data_range,Gaussian weights=True,use_sample_covariance=False), default sigma/window depend on installed skimage and are not pinned. PSNR float32 squared-error mean, if MSE<=1e−12 return 99.0; otherwise 10log10(range²/MSE). Data_range from private CSV per case, fallback reference max−min, no protection from invalid/zero CSV range. LPIPS Alex weights/runtime absent: each input independently min-max normalizes [-1,1], constant span < 1e−9→zeros, grayscale repeats 3 channels, no_grad; this loses absolute offset/scale differences and is not MRI/clinical validation. No metric computed.

Effective TASK ixi-t1-sr-task absent TASK_NORM and RATING_THRESHOLDS. Without unresolved baseline_bands, code uses generic named clinical composite: equal one-third weights for clipped(PSNR−20)/30, SSIM,1−LPIPS. No IXI-specific PSNR 20–35 or LPIPS max .5 windows/rating imported from mri-sr-task. Valid unknown-task rating C vs hard fail F (invalid/abort/noPSNR/completion<.5); no outcome/rating asserted. Dataset bands missing => pass_rate omitted, cannot infer classical SSIM threshold or pass rate. Config evaluator_status blocked_metric_assets remains unresolved. Named clinical is code field, not clinical validation.

Number of cases and unique patients unknown. Scorer means independently drop NaN metrics, n_valid based only non-NaN PSNR; differs format n_valid. Missing predictions append NaNs; total n_patients still requested IDs. Runner if any format-valid scores all IDs without filtering invalid, so malformed/nonfinite cases may raise/propagate instead of clean partial penalty. Completion format-valid /max(1,total). If baseline bands available pass rate denominator all per_patient rows, missing outputs retained. Shuffle maps next ID modulo N; with N=1 unchanged reference, no independent negative control. No case/pixel metric/clinical performance.

## Visual explanation

### Workflow

- Missing exact native Full input/target warning and official acquisition route.
- Canonical 128→256 geometry, Lite/Standard/format selectors and unknown output cells.
- Empty participant array, late evaluator/private-reference rules, backward/exit/reset covers.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: Swin2SR x2 public pretrained checkpoint. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/enhancement/ixi-t1-sr-task.tar.gz)
- [Official IXI acquisition](https://brain-development.org/ixi-dataset/)
- [Resolution receipt](../sources/automedbench-full-ixi-t1-sr-task-resolution.json)

## Limits and attribution

IXI CC BY-SA 3.0 source attribution and separate Full mapping, exact Full split/native case, degradation geometry, weights/runtime/LPIPS and baseline bands remain unresolved. No matching Full source image, fabricated high-resolution truth, clinical edge preservation or model performance. Local symbolic LicenseRef is authoring restriction, not dataset permission. Reopen with authorized matching input lineage, coherent geometry/output, independently private reference/evaluator assets and intended tier conditions. No publication, model or evaluator execution.

The task.json declared staging_manifest_sha256 refers to an unrecovered distinct staging manifest; it differs from the outer MANIFEST.sha256 byte hash. Outer manifest’s 26 file hashes and all 27 archive members verify independently; this distinction does not establish archive corruption. The declared authority ref is not a verified per-file upstream Git blob identity.

### Upstream source-example display, not Full task data

Official IXI TAR byte range 0–6,944,035 recovered exactly one member, IXI002-Guys-0828-T1.nii.gz (6,943,524 bytes). Only the first 6,944,036 of 4,840,816,640 archive bytes were acquired; no whole-TAR SHA claim. HTTP 206 ETag and Content-Range, first-probe parity, TAR header checksum, gzip CRC and retained member SHA establish local transport/byte provenance, not independently published volume SHA or Full selected-case membership. Original whole NIfTI is little-endian signed int16, (256,256,150), offset 352, slope 1 / intercept 0, voxel spacing (0.9375,0.9375,1.1999969482421875) mm, spatial units mm/time seconds, qform/sform code 1. Stored T1 signal has arbitrary units, not task [0,1] normalization. Native oblique sform and quaternion/offset/qfac are retained in the receipt; no radiological orientation, registration or calibration inferred.

Reader-only display selects native k=75 zero-based, samples i/j=0,2,…254, and maps stored values using integer floor(255*(v-plane_min)/(plane_max-plane_min)); extrema come from all 256×256 cells of that plane. PNG 128×128 is a stride-sampled display, not a 128² Full low-resolution input, bicubic downsample, anatomical reconstruction, target or model result. No interpolation, NIfTI reslicing, SR, inverse, fitting or evaluation. Native affine coordinates remain distinct from unknown Full slice coordinates. Exact cells/PNG parity verified independently. Display remains covered before the late reference scene, backward/exit/reset hides before paint.

Attribution: IXI – Information eXtraction from Images (EPSRC GR/S21533/02), [IXI dataset website](https://brain-development.org/ixi-dataset/), [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/). Changes: one native slice, integer-stride sampling and declared grayscale display mapping; no registration or clinical interpretation. Derived PNG is CC BY-SA 3.0; symbolic mechanics remain separately authored. Full private target, selected cases and normalized preprocessing remain absent.
