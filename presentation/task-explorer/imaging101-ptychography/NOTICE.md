# Imaging101 conventional ptychography source views

Benchmark source: AI4ImagingLab/imaging-101-release at
`dc2f668939b21e8312e22529615def610f8611df`. Numeric data:
starpacker52/imaging-101 at `a9de559b54849a25988a8a0d8a5e869063a5a7a3`.
The [audit](../../external-tasks/sources/imaging101-ptychography-audit.json)
pins source, data, original licenses, failed/recovered fetch and diagnostics.
BENCHMARK-LICENSE.txt retains its MIT label. DATA-LICENSE.txt preserves the
original PtyLab Academic License Agreement for the attributed source algorithms.
No claim that benchmark MIT replaces those upstream terms is made.
Attribution: Loetgering et al., PtyLab.m/py/jl, Optics Express 31 (2023),
13763-13797; the upstream agreement also requests the 2021 PtyLab COSI citation.

This is one synthetic USAF pure-phase case, not a measured specimen. Three
128x128 diffraction frames use scan indices0,49,99 and a common log1p grayscale
range0..32966. Count values are neither rounded to integers nor regenerated.
Source generator adds a Poisson draw to its expectation;14-bit is not a cap.

All100 native positions and encoders are retained. Pixel upper-left corners are
round(encoder/dxp)+207. Probe/object pixels are3.4331597222 micrometers. Geometry
panels show rectangular extraction windows, not actual beam support. Every image
preserves source pixels with only labeled linear/log contrast and uint8 display
quantization. Object axes use pixel centers0..541; detector axes0..127. Physical
sampling is explicit. Images and outlines share the same coordinate mapping.

Projection diagnostics start from the exact source seed42 object/probe
initialization. They apply one detector intensity projection at each of three
selected scans. No object or probe update, inverse iteration, generation or agent
was executed. These pictures do not produce the saved reconstruction.

Saved amplitude and raw angle come from recon.hdf5. Phase images use the same
linear -pi..pi radian range as synthetic truth. Display does not subtract phase
means; the separately labeled native scores do. Stored error history has350
samples and is not an animation of intermediate object estimates.

Truth phase and amplitude live only in reference.json and require reader reveal.
This is a presentation boundary: releasedL1-L3 staging actually copies both truth
files. Generic scoring discards phase, giving the correct/erased/conjugated truth
identical NCC1/MSE0. Zero magnitude range produces infinite NRMSE, even for exact
truth. No pass boundaries are shipped. Native saved-phase scores replay the
original0.9757/0.0434 values without new reconstruction or historical rewriting.
