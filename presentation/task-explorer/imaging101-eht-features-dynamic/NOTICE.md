# Dynamic crescent feature views

Benchmark `dc2f668939b21e8312e22529615def610f8611df`; data revision
`a9de559b54849a25988a8a0d8a5e869063a5a7a3`. The
[source audit](../../external-tasks/sources/imaging101-eht-features-dynamic-audit.json)
pins 74 source files and all 9 assets, original scores and staging evidence.

Rebuild with scripts/build_imaging101_eht_features_dynamic_assets.py using
--sources and a fresh --output directory in the existing NumPy/Pillow runtime.
No source-module initialization, random sampling, solver, training or installation.

All 10 native 64x64 frames and original 10000 weights per epoch are retained through
full-support weighted histograms. Observations run 0..7.2 hours at 0.8-hour steps;
playback time is separate. This synthetic crescent is not real Sgr A* data.

Images retain the full grid without cropping or spatial resampling. Row 0 is at
the top and column 0 at the left: explicit array coordinates, not celestial axes.
Pixel size 1.875 microarcseconds, full field 120 microarcseconds. The source's
angle formula uses atan2(grid_y,grid_x); no independent E-of-N calibration is
claimed. Ring diameter means twice the Gaussian radial center, width means sigma.

Saved and truth images share 0..0.0022 fraction-of-total-flux per pixel. They sum
to approximately 1, although metadata's visibility generator uses 0.6 Jy. Absolute
error uses a separate labeled bound rounded upward to 0.00001. Eight fixed model
examples use a separate 0..0.0045 scale. Quantization is 8-bit with explicit RGB
interpolation and maximum errors in each plane record. No image smoothing.

Input views use 28 native UV samples and both complex visibility components.
The 6 fixed closure controls choose stations [0,4,7] for phases and[0,3,4,7] for
amplitudes at frames 0, 4, 9. Station gains are deterministic audit controls:
amplitudes linearly 0.8..1.2 and phases -0.5..0.7 radians. They change individual
visibilities but cancel in wrapped phases and log ratios. No noise is redrawn.
Source 56 phase combinations have linear rank 21; 70 amplitude combinations rank 19.
These are correlated expressions, not 126 independent observations.

Model examples use fixed values unrelated to truth: diameter 30/70, width 4/20,
asymmetry 0/0.9 and angle -135/-45; other parameters are fixed and recorded.
They illustrate the supplied formula, not a fit or measured intermediate state.
Each actual source frame initializes an independent flow; there is no temporal
coupling. Flow/training diagrams remain conceptual.

Each parameter uses 60 fixed bins covering every saved sample and its original
normalized weight. Ridge height is normalized independently for legibility;
bin width is shown. No KDE, trimming, new samples or posterior fitting. Weighted
means and standard deviations preserve original precision within float32
roundoff. ESS is 1/sum(w^2), not a count of independent experimental cases.

Truth, errors, parameter biases, scoring values and oracle examples live in
reference.json and appear only in explicit reference/diagnostics/scoring scenes.
The reference scene stays hidden until its midpoint. Actual L1-L3 expose both
ground_truth.npz and answer-bearing meta_data: this is reading order, not privacy.

Native angle error is 6.08 degrees; generic image NCC/NRMSE is 0.996218/0.022811.
Generic dispatch rejects the native posterior shape and has no pass boundaries.
Oracle point distributions use answers; zero bias with zero spread does not
validate uncertainty. The fixed [-179,179] wrap example is not present in the saved
angle range. Ten snapshots do not establish uncertainty calibration.

The pinned source weights likelihood 70 times more during training than importance
reweighting, relative to its log-density term. Latents/checkpoints are missing;
do not infer corrected outcomes. Source design mentions UVFITS but release uses
NPZ. The no-filesystem fallback requires an absent NPY reference. No new agent
pass, NUFFT equivalence, runtime recovery or population claim is established.
