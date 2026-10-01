> **Representative PI-CAI helper only; matched BM3D input/output and clean GT absent. [Official PI-CAI acquisition](https://zenodo.org/records/6624726).**

# Denoise an MRI volume while preserving its physical geometry

The task resolves a NIfTI path, calls `denoise_image_bm3d` and retains `denoised_nifti`. This explanation shows source-defined mechanics without running the operator or inventing an output. The retained representative MRI is an upstream helper, not an established BM3D input or noise-free target.

## Given

### Original data

Registry prostate cases require any T2w/ADC/DWI_highb; brain cases require any T1/T1c/T2/FLAIR. The public representative PI-CAI `10001_1000001` T2w volume has **640×640×21 uint16 voxels** and **0.300×0.300×3.600 mm** spacing. Original MHA geometry is LPS with an oblique direction matrix; prepared NIfTI qform/sform use RAS x/y sign conversion and retain identical voxel bytes. No canonical reorientation, patient-axis overlay or BM3D input match is established.

The native array slice **k=10, zero-based among 21 slices**, uses a whole-volume 1st/99.5th percentile display window **15–829 arbitrary intensity units**. Its 640² grayscale PNG pixels are verified. The compact 320² JPEG is bilinear/quality70 display conditioning, not a denoised or resampled participant volume; JPEG appearance does not measure patient noise. **One upstream volume/slice; zero matching BCER inputs or task outputs.**

### Supplied helpers

Case manifest/runtime state, typed artifact references and the registered specialist tool are source workflow helpers. Fault/recovery variants can change paths/tokens, omit input_nifti, remove modalities or violate scope; those faults do not define image-quality ground truth. Preserve input/output path bindings. No clean target, measured noise distribution or injected-noise realization is specified.

### Callable tools

`denoise_image_bm3d` requires `input_nifti`. `sigma_psd` defaults to **0.08 estimated standard deviation in normalized [0,1] units**, guidance 0.03–0.15, and must be positive. It is not injected or measured noise. Optional output_nifti selects an explicit path; output_subdir defaults to denoise. The default path is artifacts_dir/denoise/denoised_<input_stem>.nii.gz. NumPy, SimpleITK and BM3D dependencies are source requirements, not installed or invoked here.

### Reference-only material

No pristine/private image or clean/noisy ground truth is retained for this short task. The later explicit reader reveal shows only public validator criteria, never a pristine or denoised comparison. The representative MRI is not noise-free truth. Noise distribution and seed are unspecified; sigma does not establish Gaussian patient noise.

## Task specification

The pinned implementation casts working values to float32, computes finite min/max over the whole volume and normalizes/clips to [0,1]; nonfinite entries become zero. All-nonfinite arrays return zeros with range 0–1. A range ≤1e-12 normalizes to zeros; the complete tool skips BM3D for constant range and retains its original float32 values.

Last two array dimensions define independent 2-D slices, with leading dimensions flattened. BM3D profile=np is requested; filtered values are clipped to [0,1], and the ≥3-D branch checks returned slice shape. Intensities are restored to the original range. Floating input dtype is retained where possible; otherwise float32. Input spacing/origin/direction and metadata are copied. No source operator, normalization function, denoising or output writer is executed in this preparation.

Independent authored toy values [10,20,30,50] map to [0,.25,.5,1]. Sigma estimates .03/.08/.15 correspond to 1.2/3.2/6.0 units of that toy range40; these are parameter-unit mechanics, not MRI noise estimates or results.

## Expected output

The tool response includes denoised_nifti, input_nifti, sigma_psd, original_min, original_max and elapsed_seconds, plus a generated NIfTI artifact reference. The registry consumes **denoised_nifti**. Actual path/image/elapsed/quality remain null here. No answer JSON, prediction label or clinical finding is provided.

## Evaluation

The short registry requires stage/tool success, path_exists, nifti_nonempty and nifti_affine_match. Runner nonempty checks **nonzero voxel count** (`np.count_nonzero(arr) > 0`); on image-read failure a positive file-size fallback may pass, which does not prove a readable NIfTI. Geometry compares exact size plus spacing/origin/direction with **1e-3 floating tolerance**; it is not anatomical registration or quality measurement. No PSNR, SSIM, clean target, measured noise variance or image-quality denominator is specified. Artifact validity cannot establish noise suppression, detail preservation or clinical performance.

## Visual explanation

### Workflow

- Inspect the labelled representative upstream helper and native/display geometry boundaries.
- Select canonical normalization, estimated sigma units and slice/geometry mechanics using authored toy values.
- Keep actual output empty; explicitly reveal public validator criteria later, with backward/exit/reset coverage and no clean image.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | A case manifest, runtime state, typed artifact references and registered specialist tools. Fault/recovery variants may alter paths, arguments or available modalities. | Noise suppression can also erase real detail; the contract checks file/geometry validity, not that trade-off. |

## Difficulty

Noise suppression can also erase real detail; the contract checks file/geometry validity, not that trade-off.

## Sources

- [Pinned BM3D tool](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/tools/bm3d_denoising.py)
- [Pinned registry](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/configs/tasks_registry.json)
- [Pinned evaluator](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/benchmark/benchmark_runner.py)
- [Official PI-CAI acquisition](https://zenodo.org/records/6624726)
- [Resolution receipt](../sources/bcer-short-denoise-resolution.json)

## Gaps and attribution

Matching BM3D task input, actual denoised NIfTI, noise basis/seed and clean ground truth remain absent. PI-CAI public training/development release Zenodo6624726 has CC BY-NC4.0 terms with the full retained license and dataset authors' attribution. Native MHA/NIfTI helper roles and lossy display conditioning are explicit. BCER's MIT code license is separate and is not an image license grant. Local noncommercial explanation; no publication, tool execution or clinical claim.

## Retained metadata qualification

The inherited metadata digest `162f71ef…72ac` has no located file in the bounded retained lookup and is preserved only as a historical claim. The active retained metadata is `038-assets-v1/inputs.json`, SHA256 `7ea306dcc3876a1bf2387eba1b72a269285ccf24ea5df2a60efe1f729cf5e14b` (347,437 bytes). Native MHA z spacing is **3.6000000778884846 mm**; prepared NIfTI float32 header z spacing is **3.6000001430511475 mm**. This encoding precision difference does not establish resampling; the voxel arrays agree byte-for-byte. Exact native/header and display parity is independently revalidated, not inferred from the historical metadata digest.
