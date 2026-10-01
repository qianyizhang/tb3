> **Matching Full BraTS T1c input and private target unavailable; symbolic geometry only. [Official BraTS acquisition](https://www.synapse.org/Synapse:syn51156910/wiki/).**

# Trace T1c 2× geometry without inventing a high-resolution MRI

Source-pinned Full contract, symbolic pixel mechanics and private-evaluator boundaries. No patient input, reconstruction or clinical outcome.

## Given

### Original data

Full package brats-t1c-sr-task, MRI_T1c / BraTS 2023 GLI. Per-case public input.npy, declared normalized float32 (128, 128), 16,384 pixels; target (256, 256), 65,536 pixels, 2× length / 4× cells. Harness dataset.included=false /data_status not_included /split unresolved. Retained official Synapse entity request returned PROJECT metadata, 317 bytes, not a matching case. A fresh bounded unauthenticated file-child listing returned HTTP 200 and an empty page (11 bytes), not a native file. This covers direct file children only, not nested folders, controlled contents or all BraTS availability. Exact Full case membership and LR/HR mapping remain unrecovered; no account, access terms or credentials used. Case folders called patient IDs by common prompts; whole-patient versus 2D slice multiplicity unknown. No contrast dose, scanner sequence, voxel spacing, FOV, anatomical findings or private target established.

### Supplied helpers

Configuration, task/model info and planning/setup/validation/inference/submission prompts. Full Lite prescribes public caidas/swin2SR-classical-sr-x2-64; grayscale→model-compatible channels→grayscale mapping remains operator responsibility, not a supplied exact preprocessing. Standard compares at least 3 inference-only methods including at least 2 pretrained neural, one bicubic/Lanczos baseline allowed. Public pilot case required but not bundled. No model files/runtime assets. Requirements NumPy/SciPy/skimage/torch/Pillow/transformers minimum versions; LPIPS package absent although scorer requires it. GPU/DNN evaluation mode mandated, no weight updates/train/optimizer/backward or private reference access. These are task instructions, not runtime verification here.

### Callable tools

No task/model/tool/evaluator executed or installed. Authoring SVG shows symbolic 2 × 2 normalized cells [.1,.4;.3,.8] beside 4 × 4 unknown output sockets; these are NOT MRI, real voxels, bicubic outputs, reference or submitted arrays. Shapes reduced for illustration only; exact declared 128²→256² counts separately shown. Pixel color legend: teal authored low-resolution values; outlined high-resolution cells unknown. No MRI derivative/native pixel parity claim; deterministic pack/fixture byte equality only.

### Reference-only material

/data/private/<case_id>/reference.npy and private ground_truth.csv:data_range belong to evaluation, never participants or the explainer. No private file acquired or displayed. Public pretrained checkpoint and source contract are helpers, not target evidence. Late reader reveal teaches private reference/metric rules; exit/backward/reset covers before paint. Actual target, enhanced.npy and metrics always absent.

## Task specification

Declared normalized 128×128 T1c input from bicubic downsampling with scale 2; output 256×256 [0,1]. Harness includes NO degradation/preprocessing implementation, source slice selection, normalization min/max or clipping, cubic kernel parameter, coordinate convention, antialias setting, border mode, downsample library/version, voxel geometry or exact data split. Do not infer nearest/bilinear, z-axis super-resolution, synthesized noise, retained high-res texture or restored clinical edges. Mathematical 2× shape expansion changes cell counts, not known information; high-resolution values remain unknown. No resized clinical image or method outcome.

Full Lite and Standard are assistance tiers of this harness. Related gallery/branch/Lite package conditions preserved below but equivalence not established. Named Swin2SR baseline is a public model selection, not evidence that it loads, fits T1c domain or preserves pathology. No inference/training/performance. Prompt same shape as input in common preamble conflicts task-specific 128→256 config and tier validation; task-specific geometry explains intended output, generic checker derives shape from private reference. Task-specific Lite validation uses agent_outputs singular while task.json/S5 establish agents_outputs plural; retain discrepancy, intended declared output root plural.

## Expected output

{output_dir}/agents_outputs/<case_id>/enhanced.npy, one 2D normalized float32 finite 256×256 per case. Optional agents_decision.csv not scored. Actual output empty. Formatchecker checks 2D, expected private-reference shape, floating dtype and finite values; accepts float64, does NOT enforce float32, [0,1], nonconstant or quality. A format-valid fixture would not be a conformant medical result. No new sourcechecker/evaluator execution; pure authored predicates only.

## Evaluation

Config primary mean_ssim, diagnostic PSNR/LPIPS; runner always computes all 3 aligned and cyclic shuffled, requires LPIPS even if diagnostic. Source SSIM skimage structural_similarity(data_range,Gaussian weights=True,use_sample_covariance=False), default sigma/window depend on installed skimage and are not pinned. PSNR float32 squared-error mean, if MSE<=1e−12 return 99.0; otherwise 10 log10(range²/MSE). Data_range from private CSV per case, fallback reference max−min, no protection from invalid/zero CSV range. LPIPS Alex weights/runtime absent: each input independently minmax normalizes to [-1,1], constant span<1e−9→zeros, grayscale repeats 3channels, no_grad; this loses absolute offset/scale differences and is not MRI/clinical validation. No metric computed.

Effective TASK brats-t1c-sr-task absent TASK_NORM and RATING_THRESHOLDS. Without unresolved baseline_bands, code uses generic named clinical composite: equal one-third weights for clipped(PSNR−20)/30, SSIM,1−LPIPS. No BraTS-specific PSNR 20–35 or LPIPS max .5 windows/rating imported from mri-sr-task. Valid unknown-task rating C vs hard fail F (invalid/abort/no PSNR/completion<.5); no outcome/rating asserted. Datasetbands missing => pass_rate omitted, cannot infer classical SSIM threshold or pass rate. Config evaluator_status blocked_metric_assets remains unresolved. Named clinical is code field, not clinical validation.

Number of cases and unique patients unknown. Scorer means independently drop NaN metrics, n_valid based only non-NaN PSNR; differs format n_valid. Missing predictions append NaNs; total n_patients counts all evaluator-supplied PATIENT_IDS rows, including missing predictions; that variable name does not establish unique-patient versus slice/case multiplicity. Runner if any format-valid scores all IDs without filtering invalid, so malformed/nonfinite cases may raise/propagate instead of clean partial penalty. Completion format-valid /max(1,total). If baseline bands available pass rate denominator all per_patient rows, missing outputs retained. Shuffle maps next ID modulo N; with N=1 unchanged reference, no independent negative control. No case/pixel metric/clinical performance.

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

## Difficulty

Reconcile the model’s preprocessing with the source image scale and required output. An apparently reasonable image or text can still violate the task contract.

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/enhancement/brats-t1c-sr-task.tar.gz)
- [Official BraTS acquisition](https://www.synapse.org/Synapse:syn51156910/wiki/)
- [Resolution receipt](../sources/automedbench-full-brats-t1c-sr-task-resolution.json)

## Limits and attribution

Controlled BraTS access/rights, exact Full split/native case, degradation geometry, weights/runtime/LPIPS and baseline bands remain unresolved. No source patient image, fabricated high-resolution truth, clinical edge preservation or model performance. Local symbolic LicenseRef is authoring restriction, not dataset permission. Reopen with authorized matching input lineage, coherent geometry/output, independently private reference/evaluator assets and intended tier conditions. No publication, model or evaluator execution.

The task.json declared staging_manifest_sha256 refers to an unrecovered distinct staging manifest; it differs from the outer MANIFEST.sha256 byte hash. Outer manifest’s 26 file hashes and all 27 archive members verify independently; this distinction does not establish archive corruption. The declared authority ref is not a verified per-file upstream Git blob identity.
