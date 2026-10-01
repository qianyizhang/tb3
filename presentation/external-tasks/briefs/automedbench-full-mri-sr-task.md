**Full MRI LR/HR pair absent — symbolic protocol.** [Official fastMRI acquisition](https://fastmri.med.nyu.edu/). No exact degraded slice/private HR or selected Full case list acquired.

# Double MRI slice resolution

Explain the pinned AutoMedBench Full restoration contract using source records and symbolic geometry. No case or participant result is available.

## Value

Super-resolution aims to map a lower-resolution slice to a denser grid while preserving anatomy. More samples, format validity or image-proxy agreement do not establish recovered detail or clinical accuracy.

## Given

### Original data

Config declares MRI input.npy 360×256 float32, roughly normalized [0,1], target 720×512: twofold per axis, fourfold sample count. These are grid sizes, not measured spatial resolution, spacing or recovered frequencies. No actual magnitude/k-space conversion, normalization, contrast, anatomical region, selected slice, coil combination, patient/volume join, FOV, orientation or HR/LR alignment is recovered. task.json unit is case; config/evaluator say patient without a patient join or independence proof. dataset.included=false.

Official fastMRI provides raw k-space in several anatomical/contrast groups and requires application and agreement; that upstream description does not identify this Full image-space subset. No raw k-space/mask/ACS/coil data or exact degraded slice is acquired. Any upstream authorized helper would need an independently verified join and LR-generation recipe; it cannot become a private Full HR reference.

### Supplied helpers

Lite names Swin2SR caidas/swin2SR-classical-sr-x2-64, GPU inference-only, no training. It prescribes normalized grayscale→uint8→PIL RGB, mean across output channels, then resize to expected 720×512. Quantization, RGB replication/channel reduction and final grid adjustment are adaptations, not proven anatomical reconstruction. Checkpoint name is source guidance, without immutable weight revision/hash or acquisition. Bicubic fallback allowed. Standard compares at least 3 inference-only candidates, at least 2 DNNs; bicubic/Lanczos/SwinIR/Restormer named. S1 example 2 classical + 1 DNN conflicts with that method requirement. Source performance/clinical-transfer assertions and retained baseline claims are unverified, not recommendations or measured results. No benchmark training/fine-tuning. Standard labels SwinIR but gives a Swin2SR checkpoint example; these architecture names are not interchangeable evidence. Lite says bicubic falls below a DNN baseline, while retained bands show the named DNN baseline weaker than classical bicubic; this source disagreement is not resolved by performing a trial.

### Callable tools

A terminal and task-specific libraries/model loaders are available in the task setting; none are executed here.

### Reference-only material

Private `reference.npy` under `/data/private/{case_id}` and any private case scoring data are evaluator-only and absent from this explainer.

## Task specification

Produce the task-specific x2 HR grid, while selecting/preparing/inferencing/submitting a method under the tier conditions. Exact Full LR-generation kernel, antialiasing, spatial-frequency sampling and seed are not pinned. The generic S3 prompt demands the input shape and direct input-output difference, conflicting with config/liteS3 x2 output; this is a source contract conflict, not an observed runtime failure. Lite S3 demonstrates bicubic 2x with align_corners=False and clipping to [0,1]; Standard S3 uses x2 output and relaxed range [-0.1,1.1]. These are method-validation examples, not a recovered LR-generation operator. No interpolation, degradation or model was executed. Private HR stays evaluator-only. No diagram depicts anatomy, acquired pixels or method performance.

## Expected output

Submit agents_outputs/<case_id>/enhanced.npy; evaluator mount /agent_outputs/<pid>/enhanced.npy. Declared 720×512 float32 normalized roughly [0,1]. Actual checker accepts any finite floating 2D array matching private reference shape; it does not enforce float32 width, [0,1] or agreement with input shape. Missing/unreadable/nonfloat/nonfinite/wrongshape fail. Output and measured shape remain unset.

## Evaluation

Private reference.npy is required and absent. Aligned scoring is by evaluator-supplied PATIENT_IDS (including repeated IDs if supplied); no recovered count or patient split. PSNR (dB) and SSIM use per-ID data_range from private ground_truth.csv else reference max−min, with no positive/finite range guard. Both arrays cast float32; MSE ≤ 1e−12 yields PSNR 99. SSIM uses Gaussian weights=True and use_sample_covariance=False (population covariance); values can be negative. LPIPS AlexNet independently min-max maps each array to [-1,1], constant arrays to 0, repeats grayscale into 3 channels. This hides absolute offsets/scales from LPIPS and is not clinical calibration. No LPIPS model loaded.

Means omit NaN separately per metric, retain infinities; missing predictions have NaNs and remain in n_patients. n_valid means non-NaN PSNR. Wrong-shape predictions may pass to scorer when some files valid because wrapper proceeds despite global format failure; runtime/broadcast error remains possible, not a demonstrated result. All-format-valid is required for a non-F rating; completion < .5/aborted/no PSNR also fail. Empty case list produces no valid output and F.

Present baseline_bands.json supplies v3 thresholds: A PSNR ≥ 25.599 dB AND SSIM ≥ .6332; B 23.599/.5932; C 21.599/.5632, else F. LPIPS is reported, not gated here. There is no finite-score guard: NaN less-than-threshold comparisons are false and can bypass v3 checks. Nonpositive/nonfinite data_range, constant references and metric errors require independent validation; threshold passage alone is not qualified quality. These are source-prescribed thresholds and retained baseline claims, not newly measured method performance. Older fallback v2 AND includes LPIPS, but is not effective with bands present. Normalized source field named clinical uses clipped (PSNR−20)/15, clipped SSIM and clipped (1−LPIPS/.50), average rounded 4 decimals, 0–1; its name does not establish clinical accuracy. Pass fraction uses SSIM ≥ .6131783537940364−.02 over all per-ID records, including missing predictions, not only valid metrics. Shuffled control rotates reference IDs by one, including corresponding range; with one ID it equals aligned mapping. No grader/control/metric result was executed. The bands path is task-ID-dependent: these effective v3 statements require TASK=mri-sr-task and matching /eval deployment; the absent launcher/environment is not recovered. Source threshold values are not independently validated measurements.

## Visual explanation

### Workflow

- Distinct 360×256 LR and 720×512 HR sockets, no medical pixels.
- Canonical input/model-channel/x2-grid/submission controls.
- Empty output, later declared-vs-checker and metric-rule reveal; private HR remains absent and controls reset before paint/backward/exit.

## Difficulty

The missing degradation and geometry mapping limit any claim of recovery. Source model adaptation and generic same-shape conflict require explicit validation. Metrics and increased sample count do not establish preserved pathology.

## Sources

- [Pinned Full harness](https://huggingface.co/datasets/MitakaKuma/AutoMedBench-Full-release/resolve/f894057807cc334421784e702ead2c1883583e1b/tasks/enhancement/mri-sr-task.tar.gz)
- [Official fastMRI route](https://fastmri.med.nyu.edu/)

## Source limit

No task-matched Full fastMRI-derived slice is staged; only abstract array geometry is shown. fastMRI application/agreement, authorized local source, Full slice selection, downsampling provenance and split mapping remain unresolved.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Full · Lite | Task-specific Lite guidance: Swin2SR (HuggingFace `caidas/swin2SR-classical-sr-x2-64`). | Provision the prescribed method, validate its input/output mapping and submit predictions. |
| Full · Standard | Candidate methods and task-specific comparison requirements. | Research, choose, configure, validate and run a suitable pipeline. |
| Related source listing | The gallery, branch or Lite-package entry describes the same target family; release equivalence is not established. | Use this brief to understand the task’s nature; follow that entry’s exact source for its executable conditions. |

## Coverage

Full-release definition with Lite and Standard conditions. Related gallery/branch/Lite listings may point here for task meaning, but remain separately identified; their datasets and exact recipes are not claimed identical.

