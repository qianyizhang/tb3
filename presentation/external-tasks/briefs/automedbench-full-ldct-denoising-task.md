**Full CT pair absent — symbolic protocol.** [Official AAPM acquisition](https://www.aapm.org/grandchallenge/lowdosect/). Exact simulated noisy–clean arrays and selected Full case IDs are missing.

# Denoise simulated low-dose CT

Explain the pinned AutoMedBench Full restoration contract using source records and symbolic geometry. No case or participant result is available.

## Value

Denoising aims to reduce noise while retaining structure and the declared HU scale. Artifact validity and image-proxy metrics do not establish lesion preservation or clinical accuracy.

## Given

### Original data

Config declares 512×512 float32 CT input.npy in HU. Prose range −1300..+3200 differs from field −1024..3000 and helper normalization window −1024..3072; these are source declarations, not observed pixel extrema. No spacing, orientation, kernel, slice thickness, anatomical registration or dose ratio is recovered for Full. task.json unit is case; config/evaluator say patient, without a recovered patient join or independence proof. dataset.included=false.

Full says simulated low-dose chest/abdominal slices, dataset LDCT_SimNICT. model_info calls LDCT_High I0 = 10³; exact noise operator/seed and severity mapping are absent. The official upstream acquisition route does not establish this Full simulation or case count. The prior ReX LDCT-IQA normalized 512×512 training TIFF is not this task's HU noisy-clean pair and is excluded.

### Supplied helpers

Pinned config and method guidance. Lite names DRUNet via deepinv, GPU inference-only with noisy tensor and sigma, HU → [0,1] mapping then inverse. Sigma prior/estimator/air region and normalization are participant choices; no checkpoint version/hash is pinned or acquired. Model performance prose is an unreproduced source claim. BM3D fallback is allowed. Standard compares at least 3 inference-only candidates, at least 2 DNN-based; model_info names BM3D/DnCNN/Restormer and replacement DNNs. S1 example includes 2 classical + 1 DNN, conflicting with that requirement; record this ambiguity rather than silently treating the example as compliance. No training/fine-tuning on benchmark data.

### Callable tools

A terminal and task-specific libraries/model loaders are available in the task setting; none are executed here.

### Reference-only material

Private `reference.npy` under `/data/private/{case_id}` and any private case scoring data are evaluator-only and absent from this explainer.

## Task specification

The pinned config describes simulated low-dose noise but does not specify a seed or exact noise/sparse-view operator. Full package ID: `ldct-denoising-task`. The case/split mapping to AAPM Low Dose CT Grand Challenge is unresolved. The diagram has no patient pixels.

## Expected output

Submit agents_outputs/<case_id>/enhanced.npy per selected case; evaluator mount reads /agent_outputs/<pid>/enhanced.npy. Declared output is same-grid 512 × 512 float32 in HU. Actual checker uses the private reference shape and accepts any floating dtype, 2D, finite; it does not enforce float32 or plausible HU bounds. It rejects missing/unreadable/nonfloat/nonfinite/wrong shape. Actual output remains null, with no authored medical pixels.

## Evaluation

Private reference.npy is required and absent. Aligned scoring is by evaluator-supplied PATIENT_IDS (including repeated IDs if supplied); no recovered count or patient split. PSNR (dB) and SSIM use per-ID data_range from private ground_truth.csv else reference max−min, with no positive/finite range guard. Both arrays cast float32; MSE ≤ 1e−12 yields PSNR 99. SSIM uses Gaussian weights and population covariance; values can be negative. LPIPS AlexNet independently min-max maps each array to [-1,1], constant arrays to 0, repeats grayscale into 3 channels. This hides absolute offsets/scales from LPIPS and is not clinical calibration. No LPIPS model loaded.

Means omit NaN separately per metric, retain infinities; missing predictions have NaNs and remain in n_patients. n_valid means non-NaN PSNR. Wrong-shape predictions may pass to scorer when some files valid because wrapper proceeds despite global format failure; runtime/broadcast error remains possible, not a demonstrated result. All-format-valid is required for a non-F rating; completion < .5/aborted/no PSNR also fail. Empty case list produces no valid output and F.

Present baseline_bands.json supplies v3 thresholds: A PSNR ≥ 42.798 dB AND SSIM ≥ .9863; B 40.798/.9463; C 38.798/.9163, else F. LPIPS is reported, not gated here. There is no finite-score guard: NaN less-than-threshold comparisons are false and can bypass v3 checks. Nonpositive/nonfinite data_range, constant references and metric errors require independent validation; threshold passage alone is not qualified quality. These are source-prescribed thresholds and retained baseline claims, not newly measured method performance. Older fallback v2 AND includes LPIPS, but is not effective with bands present. Normalized source field named clinical uses clipped (PSNR−30)/15, clipped SSIM and clipped (1−LPIPS/.30), average rounded 4 decimals, 0–1; its name does not establish clinical accuracy. Pass fraction uses SSIM ≥ .9663058295715962−.02 over all per-ID records, including missing predictions, not only valid metrics. Shuffled control rotates reference IDs by one, including corresponding range; with one ID it equals aligned mapping. No grader/control/metric result was executed. The bands path is task-ID-dependent: these effective v3 statements require TASK=ldct-denoising-task and matching /eval deployment; the absent launcher/environment is not recovered. Source threshold values are not independently validated measurements.

## Visual explanation

### Workflow

- Symbolic HU input socket; no CT anatomy or simulated pixels.
- Canonical normalization, denoising, inverse-HU and submission stages with tier guidance.
- Empty output; explicit later format/metric-rule inspection, reset on backward/exit before paint. Private reference remains absent.

## Difficulty

Scale inversion, sigma selection and structural preservation must be checked independently. Missing exact simulation/staging and source checkpoint pins prevent matching-native demonstration. Metric agreement does not prove diagnostic fidelity.

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/enhancement/ldct-denoising-task.tar.gz)
- [Official AAPM Low Dose CT Grand Challenge route](https://www.aapm.org/grandchallenge/lowdosect/)

## Source limit

No task-matched Full low-dose CT array is staged; only the HU and output contracts are shown. AAPM source acquisition, permission for local use, simulated Full case construction, exact degradation, and split mapping remain unresolved.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: DRUNet (deep residual UNet denoiser). | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

