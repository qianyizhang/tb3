> **Matching Full noisy / clean pair absent; upstream LIDC CT is reader-only. [Official LIDC-IDRI acquisition](https://www.cancerimagingarchive.net/collection/lidc-idri/).**

# Trace normalized CT noise without inventing a clean lesion image

Source-pinned Full denoising contract; authored noisy cells and unknown clean/output values, not patient CT or denoising evidence.

## Given

### Original data

Full package lidc-idri-denoising-task, LIDC-IDRI CT. Declared public input.npy per case, normalized float32 (512, 512), 262,144 pixels. Same output geometry. Full harness declares data not included and split unresolved. Bounded official TCIA collection returned HTTP 200 partial HTML, capped 64KiB/curl 63; no selected Full noisy-clean pair or exact degradation lineage. Retained upstream DICOM exists separately, reader-only. Case folders called patient IDs by prompts; unique-patient/slice mapping and number of cases unknown. No matched Full CT array, HU normalization, dose/noise calibration or findings. Upstream DICOM geometry/rescale exists separately from unspecified Full preprocessing.

### Supplied helpers

Task/model config and five-stage guidance. Full Lite prescribes public pretrained DRUNet, checkpoint source chosen/documented by operator. Standard ≥3 inference-only methods including ≥2 public pretrained neural; BM3D one possible classical baseline, DnCNN/Restormer/SwinIR candidates. Public-input pilot, no training/finetuning/optimizer/backward/private reference. Requirements and GPU-eval instructions do not establish installed runtime/checkpoint/domain suitability. No weights/runtime assets bundled; LPIPS not requirements despite evaluator dependency. Related Lite/gallery equivalence not assumed; original Conditions preserved.

### Callable tools

No task, model, scorer/checker or evaluator executed/installed. Author SVG noisy 2 × 2 values [.25,.5;.6,.8] beside 2 × 2 unknown clean/output sockets, same geometry. Teal authored normalized observations; outline unknown values. These are not CT, private targets, actual Gaussian draws, denoised results or submitted arrays. Exact 512² counts separately shown. Separate late upstream display has exact native cell/pixel parity; default normalized cells remain symbolic, not a Full pair.

### Reference-only material

/data/private/<case_id>/reference.npy and private ground_truth.csv:data_range evaluator-only; never acquired/displayed. Public model/checkpoint names are helper context, not clean targets. Late reader reveal covers only code/reference/metric rules, never private target pixels. Backward/exit/reset cover before paint; all target/output/score fields remain null.

## Task specification

Declared degradation additive_gaussian sigma 0.05 in normalized_intensity, variance 0.0025. This is not 0.05 HU, dose fraction, photon count or real clinical low-dose CT noise. No actual degradation implementation, normalization/minmax/window/HU conversion, random seed, zero-mean declaration, spatial independence/correlation, clipping/quantization/order or split/case mapping recovered. Do not infer a physical Poisson transmission pipeline. Default Gaussian symmetry/zero mean is conventional illustration only, not native condition proof. Gaussian support unbounded: authored normalized 0.98 +0.05=1.03; source [0,1] requirement does not establish clipping rule, and clipping would change distribution.

Authored y = .45 can be formed by (x, ε) = (.40, .05), (.45, 0), or (.50, −.05). Multiple clean/noise pairs teach uncertainty; none is a denoised result or patient truth. No random generator draws, synthetic native CT creation, denoiser execution or reconstructed lesion detail. Same 512×512 output preserves geometry, not image information or lesion boundaries. The later public source helper is not used as a Full noisy-clean pair.

Full Lite DRUNet checkpoint/noise conditioning/preprocessing remains to provision; published sigma .05 is normalized domain, not assumed DRUNet argument convention or estimator. Standard comparisons are assistance, not evidence that candidate methods execute or preserve anatomy. Prompt validation forbids exact copy/constant, asks finite float32 normalized moderate change and absence of severe over-smoothing; these checks are not diagnostic performance evidence. S4 forbids heuristic histogram/tone postprocessing and mandates DNN GPU/no_grad/eval, no weight updates.

## Expected output

{output_dir}/agents_outputs/<case_id>/enhanced.npy, normalized finite float32 (512, 512), 262,144 values per case. Optional agents_decision.csv not scored. Task.json/S5 plural agents_outputs conflicts singular agent_outputs in task Lite validation, preserve discrepancy. Actual array empty. Checker expected shape from private reference, floating dtype+finite 2D only; accepts float64, lacks [0,1], constant, exact copy/moderate difference and quality checks. Format-valid is not protocol/medical success. No source checker execution; pure authored predicates only.

## Evaluation

Config mean_ssim diagnostics PSNR/LPIPS, but runner requires all 3 aligned and cyclic shuffled. Private CSV data_range or reference max−min; invalid/zero range guard absent. PSNR float32 MSE≤1e−12→99, else 10log10(range²/MSE). SSIM skimage Gaussian weights=True and use_sample_covariance=False (population covariance); actual installed defaults/runtime not pinned. LPIPS Alex model independently minmax each input[-1,1], constant span < 1e−9→zeros, repeats gray 3 channels/no_grad; offset/scale differences can disappear. Package/weights absent/unverified, no metric computed.

Declared TASK lidc-idri-denoising-task absent TASK_NORM/RATING_THRESHOLDS; do not inherit ldct-denoising-task PSNR 30–45 /LPIPS max .30 or its A/B bands. Without dataset bands, generic named clinical equal one-third clip((PSNR−20)/30), clip SSIM, clip(1−LPIPS); unknown-task rating C for otherwise valid versus hard fail F invalid/abort/no PSNR/completion<.5. This “clinical” field is a code composite, not clinical validation. Missing baseline bands => pass rate not emitted, configured blocked_metric_assets unresolved. No outcome/rating/pass rate claimed.

Scorer non-NaN means independently per metric; score n_valid checks PSNR only, differs format n_valid. Missing preds append NaNs but total requested IDs retained. Runner if any format-valid scores all IDs unfiltered; bad shape/nonfinite can raise/propagate rather than clean penalty. Completion valid/max(1,total). If bands known, pass rate denominator all per_patient rows includes missing outputs. One case cyclic shuffle maps itself, not independent negative control. Case count/valid denominators unknown, no metrics evaluated.

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

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/enhancement/lidc-idri-denoising-task.tar.gz)
- [Official LIDC-IDRI acquisition](https://nihcc.app.box.com/v/LIDC-IDRI)
- [Resolution receipt](../sources/automedbench-full-lidc-idri-denoising-task-resolution.json)

## Limits and attribution

Exact Full split / native case / degradation, Full-derived data provenance, private clean / evaluator bands / checkpoint / runtime unavailable. Original LIDC-IDRI source is not a matched Full denoising sample. Local symbolic LicenseRef conveys no dataset rights. Reopen with authorized matching input lineage, documented normalized noise/geometry, intended output root / private evaluator and assets. No clinical findings, native/model denoising or publication.

Task.json staging_manifest_sha256 refers to an unrecovered distinct staging manifest, not the outer MANIFEST.sha256. Outer 26 file hashes and all 27 archive members verify independently; no corruption inferred. Authority ref is declared source metadata, not per-file upstream Git proof.

### Upstream source helper, not a Full noisy-clean pair

Retained LIDC-IDRI-0003 archive ct.zip has 140 DICOMs in one study/series, all member CRCs verified. Selected member 00000001.dcm is InstanceNumber 80, native 512×512 signed-int16, uncompressed explicit-VR little-endian; numeric slope 1 / intercept -1024 rescale (selected header has no RescaleType tag), spacing 0.820312mm in both in-plane axes, IPP[−228.800003,−210,−229]mm and IOP retained in receipt. Member name, InstanceNumber and unverified Full slice/case index are distinct. Dataset native signal is a public acquired CT example, not synthetic Gaussian-noised Full input, pristine clean truth, private reference or clinical noise evidence. LIDC annotations/lesion IDs, partition and selected-slice membership not used or inferred.

Late reader-only PNG 128² takes row/column indices 0,4,…508 directly and applies an authored display window C40/W400 rescaled source units: floor(255*(clip(rescaled,-160,240)+160)/400). This is a declared integer grayscale transfer, not DICOM VOI convention, Full normalization or noise preprocessing. DICOM native orientation/geometry remains; no flip/reslicing/registration/interpolation, Gaussian draw, denoising, reconstruction/model or metric. Native pixel/cell parity independently verified; size reduction is display sampling, not benchmark degradation. Default story uses authored normalized 2² values and unknown same-size clean/output sockets. Helper reveal late; backward/exit/reset covers before paint.

CC BY 3.0 full LIDC-IDRI citation, TCIA/NCI/FNIH acknowledgement and original archive LICENSE retained verbatim in SOURCE-LICENSE. Dataset citation: Armato III et al. (2015), Data From LIDC-IDRI, TCIA, https://doi.org/10.7937/K9/TCIA.2015.LO9QL9SX. Changes: native slice selection, stride 4 and declared grayscale window only, no lesion annotation or clinical interpretation. Private target rights/availability and task-specific case/noise lineage separate.
