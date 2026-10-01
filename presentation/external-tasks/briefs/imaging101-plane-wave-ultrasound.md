> **Phantom RF only; no participant B-mode. Baseline and generic binding unresolved. [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/plane_wave_ultrasound).**

# Trace plane-wave RF without inventing a focused image

Actual physical-phantom ADC inputs, public steering/compounding mechanics and empty participant output.

## Given

### Original data

Source describes SonixRP physical nylon-fiber and circular-cyst phantoms; no patient. RF_fibers float32 (1,2688,128,7) and RF_cysts (1,1536,128,7): batch, receive-time, element, steering angle. Values are native integer ADC codes 0..255, not calibrated acoustic pressure or demodulated complex IQ. 128 elements, pitch 298 µm, sound speed 1540 m/s, sampling 20 MHz (50 ns), seven angles −1.5° to +1.5° in 0.5° steps; solver uses radians. No RF carrier, wavelength, TGC, receive impulse response, acquisition-noise distribution or attenuation model independently established.

Fibers t0=0, last native sample 134.35 µs; cysts t0=50 µs, last absolute sample 126.75 µs (relative last 76.75 µs). These are distinct acquisitions/windows, not frames of one patient. Raw cells 2,408,448 fibers /1,376,256 cysts; output pixels 344,064 /196,608. Input element/time sheet is not a tissue-depth image, ultrasound envelope or migrated B-mode.

### Supplied helpers

Metadata for c/fs/pitch/angles/t0. Preprocessing casts float64 and subtracts one global mean across all times, elements and angles PER phantom: fibers 127.5505213315795, cysts 121.45401364281064. Not a per-trace mean, ADC value 128, envelope or IQ conversion. Display here shows untouched RF; gray line is the global source mean, not a subtraction outcome. No noise sampling or DC preprocessing executed through source tools.

### Callable tools

Pinned fkmig and coherent_compound inspected only. Two native input PNGs select angle index 3 (0°), every eighth time row, all 128 elements; fibers 336 × 128 / cysts 192 × 128. Direct integer count→gray RGB(value,value,value), fixed 0..255, no mean subtraction/interpolation/envelope/beamforming. Time stride 8 is explicitly a display subset (400 ns), not a changed acquisition rate or antialias filter. Three exact full element 63 traces: fibers angle indices 0/3 (−1.5°/0°), cysts index 3. All 2,688/2,688/1,536 cells preserved; time origin explicit. Teal untouched ADC, gray global mean. No B-mode displayed.

### Reference-only material

No ground_truth.npz. data/baseline_reference.npz contains source-visible bmode_fibers (1,2688,128), bmode_cysts (1,1536,128), float32 arbitrary display units, not anatomical truth. Runner stages entire data directory. Saved evaluation B-mode arrays differ by maximum absolute 24.5727902321358 fibers /5.1292611982279475 cysts from data baselines; retained-array equality check only, not a scored reconstruction. No baseline or saved B-mode image bundled. Later reader rules cover before paint on exit/backward/reset.

## Task specification

Source Stolt f-k migration, not delay-and-sum or a computed speedup comparison. Element coordinates x=(e−63.5)×298µm (−18.923..18.923 mm). z[n]=n×c/(2fs), spacing 38.5 µm, relative depth 0..103.4495 mm fibers /0..59.0975 mm cysts; this code axis does not add cyst t0×c/2=38.5 mm. t0 is compensated by phase and crop; distinguish reported relative depth from absolute two-way time convention. Phase delay sinθ×((127 if θ<0 else 0)−e)×pitch/c+t0. Positive θ means element 0 fires first by declared convention; compensation sign retained, not independently calibrated. The source declares positive angle means element0 fires first, while the steering-delay expression sin(theta)*(reference-e)*pitch/c+t0 numerically decreases with element for positive theta. This expression is used for phase compensation; mapping to measured hardware emission times is not independently established. Preserve expression and declared convention without inferring calibration.

Time pad ntFFT=4nt+ntshift, ntshift=2ceil(t0fs/2)=0/1000; fibers 10752 / cysts 7144, lateral nxFFT 192. Retains positive time frequencies, applies exp(−2πi f delay), spatial FFT, removes |f|/(|kx|+spacing)<c, then linear Stolt interpolation separately on real/imaginary channels; no sinc implemented. Queries above penultimate frequency row set 0; helper lacks negative-query guard, source mapping nonnegative. kx cycles/m and f Hz. ERM v=c/sqrt(1+cosθ+sin²θ); at 0 v=c/sqrt2, contrary to README narrative c/2. beta=(1+cosθ)^1.5/(1+cosθ+sin²θ); normal-incidence kx 0 mapping yields |f|. Describe implemented formula, not an independently verified exact forward model.

Obliquity f/(fkz+spacing), DC zero; conjugate mirroring, axial IFFT, lateral steering phase and lateral IFFT. Crop time indices n+ntshift and first 128 spatial columns. Coherent compounding averages seven complex migrated images BEFORE envelope. Envelope abs(Hilbert(real(compound),axis 0)) then power gamma 0.7 fibers/.5 cysts; imaginary part discarded before Hilbert. No per-image max normalization, log compression or dB conversion. Authored +1 and−1 average 0 coherently versus mean magnitudes 1: phase cancellation fixture only, no measured image/outcome. No migration/FFT/Hilbert run.

## Expected output

Generic one real output/reconstruction.npy. Shape 2688×128 selects fibers baseline ; 1536×128 selects cysts. No one array represents both conditions or aggregate verdict. Source main separately saves compound, B-mode and x/z arrays for both phantoms under evaluation/reference_outputs. Participant B-mode, resolution/CNR, metrics and outcome empty; saved arrays never substituted.

## Evaluation

Source main NCC subtracts means (Pearson); generic NCC cosine without mean subtraction. Both range NRMSE but source adds 1e−12 to range. Generic squeeze/complex→magnitude/float64, no mean removal, flux or max normalization. Reference discovery selects baseline_reference.npz by output shape; saved bmode_*.npy names are not reconstruction/reference candidate names. Pixel denominator 344,064 or 196,608, no two-phantom averaging, ROI mask or phase metric.

Main thresholds ncc_fibers_boundary=.9/nrmse_fibers_boundary=.1 and cysts equivalent; generic requires ncc_boundary AND nrmse_boundary. Those keys absent in source schema, so generic passed=None if this metrics schema is installed; no pass/fail or current score inferred. Baseline-versus-saved mismatch and selected live metrics/reference must be resolved.

Filesystem generic reference discovery uses data/baseline_reference.npz, whose two (1,Nt,128) arrays squeeze only because ndim>2. Output (2688,128) selects fibers and (1536,128) selects cysts; neither is private anatomical truth. Saved bmode_*.npy filenames lack accepted ground_truth/reference/reconstruction/recon/gt tokens and do not replace that baseline. No-filesystem scorer instead requires generic ground_truth.npy, absent in the pinned tree. Installed phantom-specific metrics keys are not generic ncc_boundary/nrmse_boundary; without both generic keys, passed=None, not a success or failure.

FWHM source uses gamma 0.7 display, nearest rows at 8 approximate target depths 10..80 mm, first argmax, discrete lateral half-max crossings, no interpolation. CNR uses linear envelope, not gamma 0.5 B-mode: scripted 2 mm disk and 3–5 mm shell, absolute mean difference/population standard deviation outside (not pooled variance or dB). Two approximate phantom ROIs in relative cyst depth. Neither FWHM nor CNR is a generic full-array score or clinical performance; none computed here.

## Visual explanation

### Workflow

- Actual raw RF sheets and persistent phantom/no-result/acquisition warning.
- Canonical time/steering units, three full native traces, phase-before-envelope mechanics.
- Empty participant output and late source-baseline/scorer-binding rules; immediate reset/exit/backward cover.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| L1 · README | README, data description and method hints. | Choose and implement a workable algorithm. |
| L2 · + approach | A proposed algorithmic approach is added. | Design the software and implement the method. |
| L3 · + design | Approach and software design are added. | Implement the specified design and numerical details. |

## Sources

- [Pinned README](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/plane_wave_ultrasound/README.md)
- [Pinned physics](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/plane_wave_ultrasound/src/physics_model.py)
- [Pinned migration](https://github.com/AI4ImagingLab/imaging-101-release/blob/dc2f668939b21e8312e22529615def610f8611df/tasks/plane_wave_ultrasound/src/solvers.py)
- [Official acquisition](https://huggingface.co/datasets/starpacker52/imaging-101/tree/a9de559b54849a25988a8a0d8a5e869063a5a7a3/tasks/plane_wave_ultrasound)
- [Resolution receipt](../sources/imaging101-plane-wave-ultrasound-resolution.json)

## Limits and attribution

Imaging101 code/HF card declares MIT; original PICMUS/Garcia phantom acquisition rights not independently verified. LicenseRef-Ultrasound-phantom-local-teaching covers local packet restriction, not a granted redistribution license. No publication or patient claim. Reopen with selected condition/reference, coherent threshold schema, original-data rights and participant lineage. No beamforming, evaluation or runtime execution.
