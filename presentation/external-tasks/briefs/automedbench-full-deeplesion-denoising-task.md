> **Matching Full DeepLesion input / private target absent; symbolic normalized-noise rules only. [Official DeepLesion acquisition](https://nihcc.app.box.com/v/DeepLesion).**

# Trace normalized CT noise without inventing a clean lesion image

Source-pinned Full denoising contract; authored noisy cells and unknown clean/output values, not patient CT or denoising evidence.

## Given

### Original data

Full package deeplesion-denoising-task, NIH DeepLesion CT. Declared public input.npy per case, normalized float32 (512, 512), 262,144 pixels. Same output geometry. Full harness declares data not included and split unresolved. Retained bounded NIH Box acquisition returned HTTP 200 partial HTML and stopped at its 64 KiB cap (curl 56); no matching Full input or exact degradation lineage was recovered. Fresh retained-byte/header validation is not a new GET. A bounded page truncation is neither proof of official byte absence nor a dataset access refusal; original archive contains no native cases and provides no Full case mapping. Case folders called patient IDs by prompts; unique-patient/slice mapping and number of cases unknown. No CT image, HU transform, dose/scanner acquisition, voxel spacing, native noise or clinical findings.

### Supplied helpers

Task/model config and five-stage guidance. Full Lite prescribes public pretrained DRUNet, checkpoint source chosen/documented by operator. Standard ≥3 inference-only methods including ≥2 public pretrained neural; BM3D one possible classical baseline, DnCNN/Restormer/SwinIR candidates. Public-input pilot, no training/finetuning/optimizer/backward/private reference. Requirements and GPU-eval instructions do not establish installed runtime/checkpoint/domain suitability. No weights/runtime assets bundled; LPIPS not requirements despite evaluator dependency. Related Lite/gallery equivalence not assumed; original Conditions preserved.

### Callable tools

No task, model, scorer/checker or evaluator executed/installed. Author SVG noisy 2 × 2 values [.25,.5;.6,.8] beside 2 × 2 unknown clean/output sockets, same geometry. Teal authored normalized observations; outline unknown values. These are not CT, private targets, actual Gaussian draws, denoised results or submitted arrays. Exact 512² counts separately shown. Native pixel parity not applicable because native assets unavailable; deterministic fixture/pack byte equality only.

### Reference-only material

/data/private/<case_id>/reference.npy and private ground_truth.csv:data_range evaluator-only; never acquired/displayed. Public model/checkpoint names are helper context, not clean targets. Late reader reveal covers only code/reference/metric rules, never private target pixels. Backward/exit/reset cover before paint; all target/output/score fields remain null.

## Task specification

Declared degradation additive_gaussian sigma 0.05 in normalized_intensity, variance 0.0025. This is not 0.05 HU, dose fraction, photon count or real clinical low-dose CT noise. No actual degradation implementation, normalization/minmax/window/HU conversion, random seed, zero-mean declaration, spatial independence/correlation, clipping/quantization/order or split/case mapping recovered. Do not infer a physical Poisson transmission pipeline. Default Gaussian symmetry/zero mean is conventional illustration only, not native condition proof. Gaussian support unbounded: authored normalized 0.98 +0.05=1.03; source [0,1] requirement does not establish clipping rule, and clipping would change distribution.

Authored y = .45 can be formed by (x, ε) = (.40, .05), (.45, 0), or (.50, −.05). Multiple clean/noise pairs teach uncertainty; none is a denoised result or patient truth. No random generator draws, synthetic native CT creation, denoiser execution or reconstructed lesion detail. Same 512×512 output preserves geometry, not image information or lesion boundaries. No copied source patient image from unrelated CT used.

Full Lite DRUNet checkpoint/noise conditioning/preprocessing remains to provision; published sigma .05 is normalized domain, not assumed DRUNet argument convention or estimator. Standard comparisons are assistance, not evidence that candidate methods execute or preserve anatomy. Prompt validation forbids exact copy/constant, asks finite float32 normalized moderate change and lesion boundary preservation; these checks are not diagnostic performance evidence. S4 forbids heuristic histogram/tone postprocessing and mandates DNN GPU/no_grad/eval, no weight updates.

## Expected output

{output_dir}/agents_outputs/<case_id>/enhanced.npy, normalized finite float32 (512, 512), 262,144 values per case. Optional agents_decision.csv not scored. Task.json/S5 plural agents_outputs conflicts singular agent_outputs in task Lite validation, preserve discrepancy. Actual array empty. Checker expected shape from private reference, floating dtype+finite 2D only; accepts float64, lacks [0,1], constant, exact copy/moderate difference and quality checks. Format-valid is not protocol/medical success. No source checker execution; pure authored predicates only.

## Evaluation

Config mean_ssim diagnostics PSNR/LPIPS, but runner requires all 3 aligned and cyclic shuffled. Private CSV data_range or reference max−min; invalid/zero range guard absent. PSNR float32 MSE≤1e−12→99, else 10 log10(range²/MSE). SSIM skimage Gaussian weights True/population covariance False; actual installed defaults/runtime not pinned. LPIPS Alex model independently minmax each input to [-1,1], constant span<1e−9→zeros, repeats gray 3 channels/no_grad; offset/scale differences can disappear. Package/weights absent/unverified, no metric computed.

Declared TASK deeplesion-denoising-task absent TASK_NORM/RATING_THRESHOLDS; do not inherit ldct-denoising-task PSNR 30–45 /LPIPS max .30 or its A/B bands. Without dataset bands, generic named clinical equal one-third clip((PSNR−20)/30), clip SSIM, clip(1−LPIPS); unknown-task rating C for otherwise valid versus hard fail F invalid/abort/no PSNR/completion<.5. This “clinical” field is a code composite, not clinical validation. Missing baseline bands => pass rate not emitted, configured blocked_metric_assets unresolved. No outcome/rating/pass rate claimed.

Scorer non-NaN means independently per metric; score n_valid checks PSNR only, differs format n_valid. Missing predictions append NaNs but all evaluator-supplied PATIENT_IDS rows remain in total n_patients. This variable name does not establish unique patients rather than slices/cases. Runner if any format-valid scores all IDs unfiltered; bad shape/nonfinite can raise/propagate rather than clean penalty. Completion valid/max(1,total). If bands known, pass rate denominator all per_patient rows includes missing outputs. One case cyclic shuffle maps itself, not independent negative control. Case count/valid denominators unknown, no metrics evaluated.

## Visual explanation

### Workflow

- Persistent missing matching Full input/target warning and official acquisition route.
- Canonical normalized noise, Full Lite/Standard/format selectors, same geometry unknown clean/output values.
- Empty enhanced.npy, late evaluator/private-reference rules, reset/exit/backward covers.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: DRUNet pretrained denoiser. | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Difficulty

Suppress noise while preserving structure and the required intensity units. Synthetic degradation differs from unknown real scanner noise.

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/enhancement/deeplesion-denoising-task.tar.gz)
- [Official DeepLesion acquisition](https://nihcc.app.box.com/v/DeepLesion)
- [Resolution receipt](../sources/automedbench-full-deeplesion-denoising-task-resolution.json)

## Limits and attribution

Exact Full split / native case / degradation, original NIH data reuse rights, private clean / evaluator bands / checkpoint / runtime unavailable. Original DeepLesion source is not a matched Full denoising sample. Local symbolic LicenseRef conveys no dataset rights. Reopen with authorized matching input lineage, documented normalized noise/geometry, intended output root / private evaluator and assets. No clinical findings, native/model denoising or publication.

Task.json staging_manifest_sha256 refers to an unrecovered distinct staging manifest, not the outer MANIFEST.sha256. Outer 26 file hashes and all 27 archive members verify independently; no corruption inferred. Authority ref is declared source metadata, not per-file upstream Git proof.
