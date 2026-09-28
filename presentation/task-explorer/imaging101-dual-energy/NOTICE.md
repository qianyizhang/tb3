# Imaging101 dual-energy CT source views

Benchmark source: AI4ImagingLab/imaging-101-release at
`dc2f668939b21e8312e22529615def610f8611df`. Numeric release:
starpacker52/imaging-101 at `a9de559b54849a25988a8a0d8a5e869063a5a7a3`.
The [audit](../../external-tasks/sources/imaging101-dual-energy-audit.json)
pins source, data, licenses, download failures and numerical replay.
BENCHMARK-LICENSE.txt retains the benchmark MIT notice; DATA-LICENSE.txt retains
Giavanna Jadick's MIT notice for the cited dex-ct-sim source. Its Siddon/fan-beam
geometry is different from this benchmark's parallel-beam adaptation.

One synthetic 128x128 phantom, not a patient scan. Native images preserve every
pixel with labeled linear contrast and uint8 quantization, with zero clipping.
Count sinograms have 128 detector rows and 180 angle columns (0..179 degrees).
They share a 0..1600000 count scale. Material sinograms share 0..11 g/cm2;
saved and truth density maps share 0..1.6 g/cm3. Native centers are indexed
0..127; 1 mm spacing means a 128 mm field edge to edge. No laterality or clinical
orientation is implied. Selected-ray circles use pixel centers, never edges.

Exact supplied spectra and attenuation coefficients have 131 bins, 20..150 keV.
Plots retain every numerical sample. Spectra are photons per 1 keV bin. The
mass attenuation curves are cm2/g; the released approximate values are preserved,
not replaced by selected official NIST values. Green labels tissue material or
low-energy spectrum according to the explicit legend; orange labels bone or
high energy. Material and spectral quantities never share an unlabeled plot.

Three saved material ray estimates feed the source polychromatic forward model.
The charts illustrate exp(-a_t mu_t - a_b mu_b), then spectral weighting and
energy summation. They are forward diagnostics at a saved state, not iterations
that generated the reconstruction. Native saved sinograms divided by 0.1 cm and
ramp filtered backprojected, with negative values clipped to zero, reproduce the
stored maps exactly in scikit-image 0.25.2. No material optimization was run.

Truth maps live only in reference.json and are mounted only after reader reveal
in the reference chapter. Dashed purple frames label reference panels. This
presentation boundary is not solver privacy: actual L1-L3 file seeding exposes
both maps and both material sinograms in data/ground_truth.npz.

Native two-material metrics use the 8797/16384 pixel truth body mask, cosine NCC
and range-normalized RMSE. Generic scoring selects a single truth key by shape,
compares whole arrays and does not validate both materials. Control scores are
new saved-array/constructed-control replays, not historical outcomes. No metrics
file or pass thresholds are shipped. The unavailable tiny inverse fixture remains
explicitly unverified. This pack establishes no agent or clinical performance.
