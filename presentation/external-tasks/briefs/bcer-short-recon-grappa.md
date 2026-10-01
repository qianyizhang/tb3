> **Matching cardiac H5, reconstruction and clean GT absent; mask and modes are symbolic. Acquire through [official CMRxRecon2025](https://cmrxrecon.github.io/2025/Join-the-Challenge.html); verify selected data terms and BCER-compatible format.**

# Distinguish GRAPPA, skip, image passthrough and zero-filled fallback

Bind complex cardiac measurements to explicit axes, coils, calibration and physical metadata. Teach the source-defined mode decisions without inventing measured k-space, reconstructed images or quality results.

## Given

### Original data

The short registry accepts cardiac `h5` or `raw_kspace`; the tool requires `h5_path`. **0 matching H5 files, 0 reconstructions and 0 clean image references** are retained. The diagram is an authored **8 kx × 32 ky × 2 coil** sampling layout, with frequency indices and Boolean inclusion, not image pixels, physical distances or measured amplitudes. An unrelated prostate MRI cannot establish matching cardiac raw input.

Retained official join and FAQ pages are 29,369 and 64,612 bytes. They route acquisition through Synapse; no anonymous small matching BCER-compatible H5 was established. The original acquisition objects are historical, without invented UTC timestamps. Current attempts revalidate retained bytes only; no new GET, account, terms acceptance or data download.

### Supplied helpers

Case manifest, runtime state and registered tool references. Optional dataset/calibration keys, `coil_axis`, `nonspatial_order` and pixel spacing need actual H5 verification. Source auto-ACS defaults to **24 central ky lines** and kernel **[5,5]**; official FAQ describes central **16 lines or 16×16**. These separate statements do not resolve any selected file adapter. Explicit calibration failure falls back to auto-ACS. Auto-ACS checks summed energy, not that every central line was fully acquired.

### Callable tools

`reconstruct_grappa` uses h5py/NumPy and pygrappa for complex mode, with a SimpleITK/nibabel image writer. No dependency installation, source runtime import or operator execution is part of this explanation. Spacing comes from an argument, H5 attributes, or placeholder **[1,1,1] mm**. Placeholder spacing is not measured patient geometry; explicit frame order does not establish slice or cardiac-phase timing.

### Reference-only material

No pristine/fully sampled/private cardiac image is bundled. A later explicit reader button exposes public mode/grader rules only; backward seek, exit and reset cover them before paint. Optional `zerofilled_nifti` is a control derived from the same retrospectively decimated measurements, not pristine truth; none is retained.

## Task specification

Executable axis inference assumes the last two axes are kx/ky, then selects the last remaining dimension ≤64 as coils, or the last remaining dimension if none qualifies. The docstring's “smallest” description differs; do not transfer that wording. Explicit coil hints must not collide with kx/ky. Each frame becomes `(kx,ky,coils)`; nonspatial slice/phase order is separately validated.

The source counts ky lines with nonzero summed absolute energy. A fraction **<0.90** triggers GRAPPA; this is not an authenticated acquisition mask. Explicit or central ACS supplies pygrappa with `coil_axis=-1`. Successful, fully sampled skipped and failed frames have separate counts. On pygrappa failure the acquired/zero-filled frame remains; real image datasets can pass through, including dependency fallback, without demonstrating GRAPPA.

The source describes `ifftshift → ifft2(axes 0,1) → ifftshift → sqrt(sum |coil image|²)` and float32 magnitude output. Complex phase is not retained in RSS magnitude. This formula is explained only; **no FFT or reconstruction is calculated**.

Optional retrospective decimation is off by default. Symbolic R2 sampling plus central ACS24 retains **28/32 ky lines = 0.875**, with effective line ratio **32/28**, not net 2× acceleration. Full sampling retains32/32 and skips GRAPPA; the failure branch is hypothetical, not observed. No acquired amplitudes, calibration coefficients or computed coil image appear.

Readout crop requires an explicit request. Center crop shifts origin by discarded sample offset × spacing; millimetre requests reject placeholder spacing. NIfTI output uses declared/default spacing and writer geometry, not independently validated patient orientation or time calibration. The short grader does not test affine equality.

## Expected output

Registry key **`reconstructed_nifti`**, default path `artifacts/grappa/reconstructed_<h5stem>.nii.gz`. Tool response retains mode, source key, output shape, spacing/source, crop and elapsed time; complex mode also reports coils, ACS/kernel, frame counts, nonspatial order and optional decimation/control artifact. Here actual path, image, mode, counts, elapsed and quality remain **null**. Authored mode rules are not telemetry.

## Evaluation

The short registry requires stage/tool success, `path_exists` and `nifti_nonempty`. The runner checks **nonzero voxel count**; read failure can fall back to positive file size, which does not prove readable image content. No GRAPPA-applied, correct axes/calibration, affine/phase fidelity, PSNR/SSIM or independent image-reference invariant is specified. A successful artifact may be passthrough, skipped reconstruction or include failed zero-filled frames. Artifact checks are not cardiac accuracy or clinical/model performance.

## Visual explanation

### Workflow

- Symbolic frequency mask: blue sampled outside ACS, teal central ACS, gray missing; shared across two illustrative coils.
- Canonical steps inspect axes, calibration and apply/skip/failure predicates; output stays empty.
- Later public rule is explicitly reader-controlled; backward/exit/reset cover it, without revealing private truth.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Source condition | A case manifest, runtime state, typed artifact references and registered specialist tools. Fault/recovery variants may alter paths, arguments or available modalities. | Raw measurement dimensions and calibration must reach the correct tool in the correct form. |

## Sources

- [Pinned GRAPPA tool](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/tools/reconstruct_grappa.py)
- [Pinned registry](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/configs/tasks_registry.json)
- [Pinned grader](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/benchmark/benchmark_runner.py)
- [Official acquisition](https://cmrxrecon.github.io/2025/Join-the-Challenge.html)
- [Official FAQ](https://cmrxrecon.github.io/2025/FAQ.html)
- [Resolution receipt](../sources/bcer-short-recon-grappa-resolution.json)

## Gaps and attribution

No selected H5 format, actual ACS, physical frame calibration, reconstruction or reference has been recovered. Reopen after an authorized matching H5/adapter and its terms are verified. BCER MIT code attribution is retained separately from authored symbolic diagrams; no patient-image license or redistribution permission is inferred from public pages.
