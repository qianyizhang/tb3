# EHT uncertainty source views

Benchmark `dc2f668939b21e8312e22529615def610f8611df`, asset revision
`a9de559b54849a25988a8a0d8a5e869063a5a7a3`, upstream DPI
`1bf3f02a92796af737bd6fe6233d1d0dd778ffd5`. The
[source audit](../../external-tasks/sources/imaging101-eht-uq-audit.json) records
identities, source defects, arithmetic controls and evaluator boundaries.

Rebuild with the existing NumPy/Pillow environment and the builder's --sources
and fresh --output paths. No dependency installation, learned-network sampling,
training, NUFFT forward model or new scientific trial runs in the builder/player.

All image panels keep the complete 32x32 grid at 5 microarcseconds per pixel.
PNG rows are flipped vertically to reproduce source origin=lower; relative RA
falls from +80 to -80 left-to-right and Dec rises from -80 to +80 bottom-to-top.
There is no horizontal array flip, crop or spatial resampling. Images are colored
from 8-bit quantized values; each record stores its range and error bound. The
heat and spread palettes are explicitly interpolated RGB colors, not scientific
measurements. Sample, mean, reference and helper images share one scale covering
all displayed values. Standard deviation and error each use their labeled full
range rounded upward to 0.001 Jy/pixel. No values are clipped.

Eight saved samples are original rows 0..7 in posterior_samples.npy. All 1024
rows produce the retained mean/std exactly. The alternative file ending _1024
contains different samples and is never substituted. The pixel trace uses all
1024 values at fixed row15,column20 and population std, without a normality
assumption, score-based selection, latent values or new sample generation.

Native u/v data use G wavelengths and one common axis scale. Orange conjugate
points are derived symmetry, not extra measurements. The first closure row of
each kind determines the triangle/quadrangle witnesses. Their node positions
are schematic, not geographic. Edges are conjugated into the stated direction.
Gain control g(t)=abs(g)^t exp(i*t*arg(g)) is a deterministic arithmetic example
with Vab(t)=ga(t)*conj(gb(t))*Vab. It preserves closure quantities while changing
individual visibilities; it does not remove thermal noise. Log-amplitude pairing
follows source indices V12*V34/(V14*V23), unlike the README's denominator order.

Current Gaussian prior uses the all-baseline median flux, 0.2738309775 Jy.
Retained prior uses APEX-ALMA, 2.0444813540 Jy; keep both labeled. The flow diagram
explains the source procedure only, not a retained latent-to-sample correspondence.

Truth, absolute error, containment and the pixel reference value live in
reference.json and mount only after the explicit reader reveal. Actual L1-L3
seed both truth files, so this reveal is not solver privacy. Neither generic
single-image scoring nor the task-native mean score measures uncertainty.
Spatial containment for this one reference does not prove calibration. Native
and generic metric definitions differ and no current pass thresholds are supplied.

The real-2015-observation claim is unresolved; call this the bundled DPI example.
The source main.py syntax error, obsolete obs object and changed prior prevent
using saved outputs as proof of source reproducibility. Preserve original scores.
