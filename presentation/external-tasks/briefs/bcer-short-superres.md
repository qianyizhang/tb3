> **Representative PI-CAI input; no matched BCER output or high-resolution truth. [Official acquisition](https://zenodo.org/records/6624726).**

# Resample MRI onto a caller-defined physical grid

Produce an MRI volume on a supplied physical sampling grid with `resample_image`. Interpolation changes sampling; it does not acquire new anatomical measurements or estimate alignment.

## Value

A common physical grid lets later processing consume compatible arrays. Artifact completion and reconstruction fidelity require separate evidence.

## Given

### Original data

The registry permits any prostate T2w, ADC or DWI_highb, or any brain T1, T1c, T2 or FLAIR. The displayed PI-CAI 10001_1000001 T2w is a **representative upstream helper**, not the selected BCER short case, a degraded/clean pair or high-resolution truth. Its 640×640×21 unsigned-16-bit voxels have arbitrary MRI intensity units, not HU.

Original MHA and prepared NIfTI voxel bytes are equal. The prepared NIfTI spacing is 0.30000001192092896×0.30000001192092896×3.6000001430511475 mm; the original MHA z-spacing differs by about 6.5×10⁻⁸ mm after header conversion. Source origin/direction are LPS; the NIfTI sform uses RAS. The display is native index k=10, whole-volume 1–99.5 percentile window 15–829, rounded to uint8. The 640² PNG then becomes a 320² bilinear JPEG quality-70 preview. This display derivative is not a participant resampling output or an ordered clinical viewer.

### Supplied helpers

A case manifest, runtime state, typed artifact references and the registered `resample_image` tool. The caller supplies a reference NIfTI grid or target spacing. No matching target grid or output is retained. A reference grid is a geometry helper; it does not establish clean truth or anatomical correspondence. Fault variants may alter paths, arguments or modalities.

### Callable tools

`input_nifti` is required. The schema describes reference and spacing routes as mutually exclusive, but executable code chooses the reference when both are supplied. Linear is the default; nearest and B-spline are alternatives. Unknown interpolation names raise. Outside-input values default to zero, and the output retains the input pixel type, so integer interpolation can quantize values. This packet never invokes the tool.

### Reference-only material

No independent high-resolution target or matched resampled image is retained. A later explicit reader reveal shows grader rules only. Exiting, seeking backward or resetting covers that card before paint. The representative input never becomes gold truth.

## Task specification

The reference route adopts its size, spacing, origin and direction. The explicit-spacing route computes **ceil(Nᵢ×sᵢ/tᵢ)**, retains input origin/direction and pads a short spacing list from the input. This uses N×spacing, not the center-to-center extent (N−1)×spacing. The physical transform is the 3D identity; no registration is estimated.

Pure calculations from the prepared header give 640×640×21 for exactly the same spacing, 640×640×42 for half z-spacing, and 1280×1280×42 for half all spacing. Supplying rounded literals [0.3, 0.3, 3.6] instead gives **641×641×22**, because tiny positive float differences cross `ceil` boundaries. That is 9,039,382 versus 8,601,600 grid slots: +437,782 (+5.09%). These are illustrative counts, not measured output voxels, new detail or a quality result. No operator ran. The tool has no explicit positive/finite-spacing guard beyond downstream behavior.

## Expected output

The tool returns `ok`, `data.resampled_nifti`, input/output size and spacing, interpolation, elapsed seconds and artifact references. The default path is `<artifacts_dir>/resample/resampled_<input_stem>.nii.gz`; callers can override it. Actual output path, image, elapsed time and quality remain null here.

## Evaluation

The pinned registry requires `resample_image` stage success, an existing `resampled_nifti` path and a nonempty NIfTI. The runner counts nonzero voxels; on image-read failure it can fall back to positive file size. No target-spacing, affine or image-quality invariant is configured for `short_superres`, despite a space-mismatch fault variant. These are artifact validity checks with no independent quality denominator, PSNR/SSIM or clinical-performance claim.

## Visual explanation

### Workflow

- Inspect representative native input geometry and the display derivative.
- Seek three canonical contract steps; select an illustrative spacing grid and interpolation rule.
- Keep actual output empty; explicitly reveal late grader mechanics, then reset or leave to cover them.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | A case manifest, runtime state, typed artifact references and registered specialist tools. Fault/recovery variants may alter paths, arguments or available modalities. | Interpolation changes the grid but does not by itself recover newly measured anatomical detail. |

## Difficulty

Source geometry, target conventions, floating-point rounding and input pixel type can change array shape or values. A denser grid alone does not recover acquired resolution.

## Sources

- [Pinned tool](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/tools/resample_image.py)
- [Pinned registry](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/configs/tasks_registry.json)
- [Pinned runner](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/benchmark/benchmark_runner.py)
- [Official PI-CAI acquisition](https://zenodo.org/records/6624726)
- [Resolution receipt](../sources/bcer-short-superres-resolution.json)

## Coverage

This is one registry definition, not an enumeration of external cases or a fresh task run. Code rules are source-derived; grid examples are authored symbolic calculations; the displayed MRI is a representative public helper.

## Gaps and attribution

No matched BCER target/output or independent high-resolution truth is retained. Reopen with a source-pinned selected input and caller target, actual output and an independently defined fidelity reference. PI-CAI dataset authors, public training/development release Zenodo 6624726, CC BY-NC 4.0; preview derivation is stated. BCER code is MIT, separate from image rights. No publication, clinical finding, model run, operator or evaluator execution is implied.
