# Dynamic EHT source views

Benchmark `dc2f668939b21e8312e22529615def610f8611df`; asset revision
`a9de559b54849a25988a8a0d8a5e869063a5a7a3`. The
[source audit](../../external-tasks/sources/imaging101-eht-dynamic-audit.json)
records all 73 source and 18 asset hashes, fixture replay and scoring controls.

Rebuild with scripts/build_imaging101_eht_dynamic_assets.py using --sources
and a fresh --output destination in the existing NumPy/Pillow environment.
No source module import, simulation, solver, EM optimization or install runs.

All twelve native 30x30 frames remain in original order, with epoch times from
0 to 6 hours. Display time is an explanatory clock, not observation duration or
EM iteration. This is a synthetic crescent with an EHT-inspired array; the
source generator retains all 28 station pairs without an elevation cut.

Full grids use source origin=lower: PNG rows are flipped vertically, with
array row zero at the bottom and column zero at the left. The source DFT l and m
both decrease with array index. Use array coordinates; do not copy RA/Dec labels
from another task. Pixel size is 3.4 microarcseconds; full field is 102 microarcseconds.
Brightness-direction moments use atan2(row-center,column-center), describing
array brightness direction rather than celestial position angle or warp parameters.

Brightness images share 0..0.075 Jy/pixel. Absolute error uses a separately
labeled full-range upper bound rounded upward to 0.001 Jy/pixel. DFT kernel real
and imaginary weights share -1..1. Explicit interpolated RGB palettes and 8-bit
quantization have recorded maximum error; no crop, smoothing or spatial resampling.

Input plots use exactly 28 stored u/v points and complex visibilities per epoch.
No conjugate copies are counted. Component bars use sigma/sqrt(2), following the
generator's complex-RMS convention. The source inference helper uses sigma squared
per real/imaginary component, twice the nominal generator variance; retain this
source discrepancy. Kernel witnesses are fixed baseline rows 0,8,16,27 at epoch 0.
They evaluate the source DFT formula only, with no reference image or inversion.

The prior is the source's 50 microarcsecond FWHM, power-six super-Gaussian with
5-percent floor, normalized to 2 Jy. The temporal diagram is conceptual; highlight
passes are not measured trajectories or EM states. Source defaults to a four-
parameter affine warp without translation and process covariance 1e-7 times identity.

Saved static and StarWarps arrays are historical outputs. Native metrics average
twelve per-frame centered correlations and range-normalized errors. The legacy
task recipe flattens the video; local generic dispatch uses cosine correlation
and global-range error. No current pass boundaries exist. The older no-workspace
fallback requires 2D; local replay does not establish Docker equivalence.

Truth images, errors, truth diagnostics and answer-based controls live in
reference.json. They mount only in explicit reference/diagnostics/scoring chapters;
reference chapter's first half remains hidden. A repeat of truth's time mean or
first frame and reversed truth are oracle scoring controls, not reconstructions.
Actual L1-L3 expose ground_truth.npz, so reader reveal is not evaluator privacy.

Native image scores improve for saved StarWarps, but its descriptive brightness
direction advances 57.88 degrees versus 90 in truth and 88.61 in static. Supplemental
adjacent-difference error also differs from total-image error. Do not generalize
from one saved synthetic video, claim a calibrated motion estimate, or rewrite
scores. Pinned main.py has a SyntaxError; no fresh solver execution is established.
