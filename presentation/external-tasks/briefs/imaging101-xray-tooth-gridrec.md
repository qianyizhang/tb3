> **Native tooth counts; calibrated attenuation, independent truth and participant output absent. [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/xray_tooth_gridrec).**

# Trace tooth projection counts without inventing a reconstructed cross-section

Native experimental count rows and source-pinned correction/centre rules; participant reconstruction empty.

## Given

### Original data

Pinned task xray_tooth_gridrec. Source README identifies a real APS beamline 2-BM/32-ID tooth specimen experiment; no patient linkage or anatomical/clinical finding established. raw_data.npz:projections float32 (1,181,2,640), axes batch/angle/sinogram row/detector. 231,680 raw count cells. theta float64 (1,181), radians 0 to 3.124235788100347, step π/181, endpoint π excluded. Two axial detector rows, not a 640-slice volume. Native counts may be fractional; no calibrated photon count, Poisson noise model, dose, beam energy, detector pitch or voxel spacing supplied.

### Supplied helpers

flat_field and dark_field float32 each (1,10,2,640): 10 frames / 12,800 cells per stack. Source float64 averages over calibration frames; first-frame reader profiles below are explicitly not means. Metadata only array dimensions, angular interval and x-ray_transmission_ct label. Parallel-beam assumptions are declared by source, not verified scan geometry. TomoPy gridrec baseline reconstruction float32 (1,2,640,640), solver-visible data helper, no independent ground-truth scan. Source saved reconstruction.npy (2,640,640) equals baseline native cells exactly. Saved rot_center.npy=[296.34375] detector pixels is prior provenance, not a centre newly estimated here. All three original Conditions preserved.

### Callable tools

No task/tool/evaluator source imported or executed. Native PNGs display raw projections row 0 / row 1, select angle indices 0, 2,…180 and detector indices 0, 4,…636 (91×160 cells), common full-projection minmax 3921.25..33891.5 counts, floor 255×float64(v−min)/(max−min), no resize/interpolation/filter/log/reconstruction. Gray low→high raw counts, angle rows/detector columns, not an attenuation image or source saved sinogram. First flat/dark frame row 0 full 640-cell profiles retained/displayed with teal/gray line legend, detector index units. Raw input/calibration cell and PNG pixel parity checked. No native preprocessing or inverse calculation.

### Reference-only material

No ground_truth.npz. End-to-end visible paths README.md/data/requirements.txt stage the whole data directory, including baseline_reference.npz; evaluation/source trees are not in that default list. The baseline it is solver-visible TomoPy reconstruction, not hidden truth. Generic first evaluation/reference_outputs/reconstruction.npy equals supplied baseline exactly, but its source-derived origin is not current participant success. Saved reconstructions remain audit-only, no tooth cross-section display or inferred pathology. Late reader reveal teaches reference identity and denominator, exit/backward/reset hides rules before paint; actual output remains empty.

## Task specification

Source flat/dark correction T=(I−mean(D))/(mean(F)−mean(D)) in float64. Exact zero denominator replaced by 1 rather than rejecting invalid calibration. minus_log clips lower bound 1e−12 only, then −ln(T); no upper clipping, so T>1 produces negative line integrals. Fractional counts and log values do not establish calibrated photons or attenuation per mm. Authored I=500,F=1000,D=100 gives T=4/9; native correction/log not run. Symbolic explanation labels counts versus dimensionless transmission versus line integral; no new sinogram or inverse outcome.

Source main implements ramp-filtered pixel-driven FBP, NOT a TomoPy/Gridrec function call. Ramp abs(fftfreq) in cycles/detector-index units; 640 detectors zero-padded FFT length 2048, real IFFT cropped first 640. No filter/window control or inverse executed. Image centre and detector midpoint 319.5, row 0 positive y, t=xcosθ+ysinθ+319.5. np.interp default endpoint-hold outside detector range (not zero extension); final factor π/181. forward projector uses map_coordinates zero extension and opposite y-row convention; no adjoint identity proof or numerical-equivalence-to-gridrec claim. No voxel spacing or calibrated attenuation unit.

Rotation centre: correlate first projection with reversed last (last angle π−π/181, not exact opposing π); peak integer shift gives 319.5+shift/2. Refine candidate±5 detector pixels, 0.5 step: 20 repeated FBP trials, minimise−variance (maximise reconstructed variance), not independent accuracy truth. init 290 argument is only checked/defaulted and is not used in correlation or refinement, so not an active centre prior. tol 0.5 is search step, not convergence bound. _shift_sinogram uses scipy.ndimage.shift negative(center−319.5), default cubic interpolation, constant zero edge. No centre estimation or trial reconstruction here. Saved centre 296.34375 would imply shift −23.15625 pixels; provenance only, no fitted output.

Source circular mask radius 0.95×640/2=304 detector-index pixels, centre 319.5; output outside circle zero. This does not remove those pixels from generic metric denominator. Source reconstruction uses both rows; no patient tooth tissue, clinical resolution or performance claim. Runtime/SciPy versions and source-gridrec equivalence unverified.

## Expected output

Single real output/reconstruction.npy intended (2,640,640), 819,200 values in source pixel-scaled arbitrary reconstruction units, not calibrated attenuation coefficient/mm. Source main also saves output/metrics.json and results.png; no current files produced. Saved sinogram/rot_center/reconstruction provenance never substituted for participant outputs. Actual image, reconstruction_npy, quality score and clean reference remain null.

## Evaluation

Source compute_metrics on recon_volume[0],ref_recon[0]:first slice, 409,600 pixels only, NRMSE=RMSE/reference range and cosine NCC (no mean subtraction; zero norm→0). Filesystem generic first selects the existing saved reconstruction.npy before checking target shape; its ndim>2 squeeze leaves a (2,640,640) array because neither slice axis is singleton. Generic scores both slices, 819,200 values, after complex→magnitude/float64; same range-normalized NRMSE and cosine NCC, no output flux/max/minmax normalization. References equal, but denominators/scope differ. Circular-zero background included. Generic MSE/PSNR/global SSIM not clinical image quality. Source output/metrics.json nested fbp_vs_ref is not generic evaluation/metrics.json ncc_boundary/nrmse_boundary; Neither evaluation/metrics.json nor evaluation/reference_outputs/metrics.json is listed in the pinned official tree; without such a file the filesystem scorer adds no boundary/verdict. No-filesystem scoring requires ground_truth.npy in evaluation/reference_outputs or data, both absent in that tree, so it errors before comparison rather than substituting the baseline. Its fallback also requires strictly 2D output and would flux-rescale/use norm-relative NRMSE if separately supplied truth existed, unlike the filesystem shape/formula. These backend contracts are not interchangeable. No metric or participant performance computed.

## Visual explanation

### Workflow

- Exact native raw projection count display, calibration gaps and official acquisition warning.
- Canonical correction boundaries, two detector rows / calibration profile selectors, and symbolic centre/filter geometry.
- Empty output; later solver-visible reference identity/metric scope reveal; backward/exit/reset covers.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Difficulty

Normalize detector response and find the rotation center; small errors produce obvious rings or doubled edges.

## Sources

- [Pinned README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/xray_tooth_gridrec/README.md)
- [Pinned preprocessing](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/xray_tooth_gridrec/src/preprocessing.py)
- [Pinned source physics](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/xray_tooth_gridrec/src/physics_model.py)
- [Pinned metric definition](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/xray_tooth_gridrec/src/visualization.py)
- [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/xray_tooth_gridrec)
- [Resolution receipt](../sources/imaging101-xray-tooth-gridrec-resolution.json)

## Limits and attribution

Source code MIT; original APS/TomoPy specimen acquisition, reuse rights and calibration not independently resolved. Local LicenseRef restriction is not redistribution permission. No reconstructed anatomy or clinical findings. Reopen with exact instrument/geometry/calibration/rights, centre/FBP implementation evidence, coherent reference/threshold and participant lineage. No new reconstruction or evaluation.
