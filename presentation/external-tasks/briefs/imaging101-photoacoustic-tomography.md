> **Synthetic pressure signals only; no tissue scan, participant reconstruction or score. [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/photoacoustic_tomography).**

# Trace photoacoustic time of flight without inventing a reconstructed image

Native synthetic acoustic input and authored geometric mechanics; no reconstruction or metric execution.

## Given

### Original data

One four-sphere synthetic condition. Native signals float64 (1, 1301, 31, 31): batch, time, detector x, detector y. 1,301 time samples × 961 detectors = 1,250,261 signed pressure samples. Time 0–65 microseconds inclusive, spacing 50 ns, sampling frequency 20 MHz. Detector centres span −10 to +10 mm in both planar axes, pitch 2/3 mm; z=0. Sound speed 1,484 m/s, target plane z=15 mm. Coordinates metres and time seconds in native data. No patient, tissue specimen or vessel observation.

Forward sphere signal H(radius−|R−ct|) × (R−ct)/(2R), H at zero=.5. It is bipolar signed relative amplitude, not photon counts or calibrated Pa. Finite 2 mm square aperture averages 25 sub-elements, 5×5 offsets −.8, −.4, 0, .4, .8 mm; pitch 2/3 mm means nominal square apertures overlap. Four sphere contributions add linearly. No fluence, optical absorption, wavelength, Gruneisen coefficient, tissue attenuation, detector impulse response, additive noise or stochastic seed in generator. Do not infer absorption, oxygenation or clinical uptake from initial-pressure language.

### Supplied helpers

Detector x/y coordinates, time vector and metadata sound speed/geometry/depth. Generator defines three 0.75 mm-radius spheres and one 2.5 mm-radius sphere at z=15 mm. Native ground truth is binary projected support, not physically calibrated initial pressure or optical absorption. No modelled laser-energy/fluence variation or conversion between initial pressure and absorbed-energy density. Binary support and peak-normalized reconstruction cannot establish that physical relationship.

### Callable tools

Pinned source universal_back_projection. Native measurement visualization alone here: center detector-y index15 slice, every time sample and all 31 detector-x indices. PNG 1301 columns ×31 rows, no interpolation or decimation. Signed amplitude p mapped u=min(|p|/.1,1); RGB floors255×(1−u) for neutral channels, positive red=(255,neutral,neutral), negative blue=(neutral,neutral,255); zero white. Fixed ±.1 arbitrary-unit range covers native data. Three full 1,301-cell traces at detector indices (15,15),(0,15),(15,0), teal p, gray zero, x time0–65µs. Selected traces follow pinned source plot_signals choices. No FFT, signal filtering, solver or evaluator called.

### Reference-only material

Source ground_truth_image float64 (1,41,41), image_x/y (1,41); generic ndim>2 rule reduces the image to (41,41) but leaves the coordinate arrays ndim2 at (1,41). Matching array shape is not reference identity. grid −10..10 mm, .5mm spacing, 1,681 pixels and 101 positive binary support pixels. Runner stages all data, so synthetic truth is solver-visible; no separate private target established. Source saved reconstruction.npz retained for provenance only; image not bundled. Later reader card exposes rules only and covers synchronously on backward, exit and reset.

## Task specification

Source main uses universal backprojection, resolution 500 µm, nfft 2048, detector area (2 mm)² and z=15 mm. Output grid 41 × 41 with x first/y second, plotted transpose only in source visualization. Frequency vector is signed f, k=2πf/c; pf=IFFT(−i k FFT(p,nfft)). This is a signed derivative filter, not simply an absolute-frequency ramp. b=2p−2tc pf; time-of-flight index round(distance×fs/c), nearest sample with NumPy rounding, no fractional-delay interpolation or t0 correction. Native time starts0; indexing formula assumes that origin. No FFT/filter/backprojection computed here.

Weight omega=(detector_area/distance²)×z/distance; sum omega×sample divided by sum omega. Then pgmax selects all complex pg entries attaining maximum absolute magnitude, pg/pgmax followed by real(). This removes absolute amplitude and can retain signed values; not abs-image/positivity/fluence normalization. No zero-max or tie-shape guard: multiple equal maxima may yield a vector/broadcast mismatch. No iterative algorithm, regularization, OSEM/MLEM/FBP or learned reconstruction variant in this main. Exact dependency/runtime and tie handling not verified by saved artifacts.

Authored geometric distance 15 mm / 1,484 m/s ≈ 10.108 µs, sample index 202 at 20 MHz; it is a units/time-of-flight fixture, not a native target or reconstructed pixel. Geometry public rules separate from later source truth. Maximum native grid-to-detector distance gives rounded index 431, within 1,301 samples; this is bounds inspection only, no reconstruction.

## Expected output

Generic participant output/reconstruction.npy, intended 41 × 41 initial-pressure image at z=15 mm. Source main saves evaluation/reference_outputs/reconstruction.npz: reconstruction(1,41,41), image_x/y(1,41), plus signals.npz and figures; never substitute a saved source result. Participant image, calibrated pressure, tissue finding, metric and outcome remain absent.

## Evaluation

Source metrics operate on real signed arrays (no magnitude transform): NCC returns0 for exactly zero norm product, range NRMSE returns infinity for exactly constant reference. Generic filesystem transforms complex arrays to magnitude, adds1e-30 to NCC denominator and uses full-array/global SSIM without scale normalization. The no-filesystem backend instead requires strict2D NPY truth, flux-normalizes output and uses relativeL2 NRMSE. No scorer/helper invoked.


Source evaluates centre_crop(fraction=.8): int(41×.1)=4 each side =>33×33=1,089 pixels, not32×32 or80% of pixels. All101 positive support pixels remain, but background denominator differs from full41 × 41 = 1,681. Binary truth range1. Source NCC is cosine, not centered Pearson; NRMSE RMS error divided by reference range. Source thresholds 0.9 × NCC / 1.1 × NRMSE from cropped normalized baseline. Generic shape selector chooses sole matching2D ground_truth_image (coordinate arrays stay (1,41) and do not match the intended (41,41) image); compares full image, no crop, positivity or scale normalization. Generic squeezes/float64 and complex-to-magnitude if applicable; source real signed reconstruction differs from its dB abs display. Generic metrics include MSE/PSNR/globalSSIM; installed thresholds/reference lineage not a retained current verdict. Cropped baseline does not silently qualify full-image comparison. No score computed or clinical/model performance inferred.

## Visual explanation

### Workflow

- Native signed-pressure slice with persistent synthetic/no-result warning and official route.
- Canonical geometry, three exact native traces, source filter/weight/normalization rules.
- Empty participant image; late binary-support/evaluator-rule reveal, covered before paint on reset/backward/exit.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Sources

- [Pinned README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/photoacoustic_tomography/README.md)
- [Pinned physics](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/photoacoustic_tomography/src/physics_model.py)
- [Pinned solver](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/photoacoustic_tomography/src/solvers.py)
- [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/photoacoustic_tomography)
- [Resolution receipt](../sources/imaging101-photoacoustic-tomography-resolution.json)

## Limits and attribution

Imaging101 code/HF card MIT. Synthetic sphere acoustics only; no measured tissue, calibrated initial pressure, fluence/absorption inference, reconstruction or numerical outcome. Reopen with coherent runtime/normalization, matched reference/threshold lineage and participant output. Exact input display is evidence of native source bytes, not clinical validity.
