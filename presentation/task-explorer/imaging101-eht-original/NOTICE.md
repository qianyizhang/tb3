# Static closure-imaging views

Benchmark commit dc2f668939b21e8312e22529615def610f8611df; asset revision
 a9de559b54849a25988a8a0d8a5e869063a5a7a3. The
[source audit](../../external-tasks/sources/imaging101-eht-original-audit.json)
retains hashes for 79 source files and all 40 released assets.

Rebuild with scripts/build_imaging101_eht_original_assets.py, --sources and a
fresh --output in the existing NumPy/Pillow environment. No source-module import,
random draw, simulation, optimization, model trial or runtime installation.

Input views retain all 421 measured rows, 21 station pairs and seven station
names. No conjugate samples are added. Both calibrated and corrupted observations
are supplied. Native closures retain all 269 phases and 233 log ratios; axes must
include the large corrupted log-amplitude outlier. Stored noisy-condition
comparisons are not a deterministic gain-only test.

Six fixed algebra controls select phase rows 0,134,268 and amplitude rows
0,116,232. Each leg is matched to its native UV row or conjugate within 0.001
wavelength. This preserves per-scan geometry, unlike the small first-occurrence
helper. Deterministic station gains have amplitudes 0.8..1.2 and phases
-0.5..0.7 radians. Individual baseline terms change; wrapped phase sums and log
ratios cancel to numerical precision. Amplitude control terms are direct logs
of matched visibilities, not a claim to reproduce every stored debias correction.
Station positions in the graph are schematic, not geographic.

Six saved images retain calibrated/corrupted conditions for visibility RML,
amplitude plus phase, and closure-only RML. Images are 64x64, 2 microarcsecond
pixels, 128 microarcsecond field. Row 0 is top and column 0 left; no celestial
bearing is asserted. Every display image is divided by its own stored sum for
morphology comparison, while original sums remain visible. One shared logarithmic
heat scale spans 1e-6..0.34 fraction of total flux per pixel; smaller values are
black. The 8-bit log quantization error and below-floor count are recorded in
each plane. No spatial interpolation, smoothing or crop is applied.

The stored prior is a reference workflow artifact, not a seeded L1 image file.
Any image-fitting flow diagram is conceptual. The player never fabricates
optimizer iterations or modifies source arrays. Supplied truth and score controls
live in reference.json and are gated to the reference/scoring chapters; truth
stays hidden until the reference chapter midpoint. All L1-L3 actually expose
data/ground_truth.npz, so this is reader ordering rather than solver privacy.

Published scores flux-normalize before range NRMSE. Live filesystem scoring uses
unscaled range NRMSE against a unit-sum reference; physical truth sums to 0.6 Jy.
The fallback/generator uses flux-normalized reference-RMS NRMSE. No pass boundaries
are supplied. Oracle physical-truth and zero controls disclose their roles and
are not new agent solutions. Single saved results do not establish robustness,
noise calibration, optimizer recovery or performance on sky observations.

The audit retains a ten-input/421-output fixture mismatch, a factor-of-two
visibility-loss convention, a TV-gradient sign defect, scan-grouping limitations
and stale notebook metrics. Main saved comparisons use entropy, not TV. No
corrected scientific outcome is inferred from these source observations.
