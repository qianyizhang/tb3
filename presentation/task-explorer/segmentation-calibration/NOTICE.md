# Retained segmentation-tool calibration layers

Source: TotalSegmentator v2.0.1, public CT case s1233, originally selected from
[Zenodo record 10047263](https://zenodo.org/records/10047263).
CT image data: CC-BY-4.0. Source labels: Apache-2.0. Exact license copies are retained.
Credit: Jakob Wasserthal and the TotalSegmentator contributors, *TotalSegmentator:
Robust Segmentation of 104 Anatomic Structures in CT Images* (2023),
[doi:10.1148/ryai.230024](https://doi.org/10.1148/ryai.230024).

The 2026-09-21 direct SAM 2.1 Small / LiteMedSAM calibration used official pinned
checkpoints on an Apple M5 Pro, 64 GiB unified memory, PyTorch 2.10 FP32, four CPU
threads. This asset builder replays saved bytes; it does not run those models.
Upstream SAM2 and LiteMedSAM code licenses are Apache-2.0. Model checkpoints are
not distributed in this pack. Provenance remains in the linked source audit.

All 18 native 265 by 265 RGB inputs have identical grayscale channels. Lossless
PNG retains that grayscale exactly. Display x=i and y=j increases down, fixed
native slice k; no radiological flip. Window [-160,240] HU was applied before
inference. The source volume is 265 by 265 by 401, with 1.5 mm isotropic spacing.
The affine and per-view k indices retain the connection to source coordinates.
Pixel centres are at (i+.5,j+.5) in SVG, corresponding to voxel index (i,j,k).

Source masks selected the 25th, 50th and 75th percentiles of nonempty slice
indices, using nearest-even rounding. Tight/wide boxes expand the reference
bounding rectangle by 2/10 native pixels (3/15 mm) per side, clipped to image
bounds. Native boxes are half-open xyxy. Both models receive the same full slice
and box, not the organ name or dense reference mask. Localization is privileged.

The pack includes all 116 saved masks: 72 primary MPS predictions, 8 prespecified
CPU checks and 36 additional SAM2 CPU predictions after the backend discrepancy.
Mask contours are traced at level .5; XOR rasterization at native pixel centres
reconstructs every mask exactly, including holes. A detail view always encloses
all saved CPU/MPS predictions, GT and both boxes for that sample. Crops are
reader aids derived after inference and may reveal target location. Full native
images remain available, and inference never used these crops.

Separate files preserve inputs, outputs/timing and reference/measurements. A
reader reference reveal is explanatory, not solver access. The supplied boxes
are already reference-derived. Inspecting a selected section does not establish
full-volume quality. Six middle slices are prespecified display examples; the
worst backend pair is explicitly selected after observing disagreement.

HD95 is the 95th percentile of concatenated bidirectional 2D surface distances
after 4-connected erosion, using 1.5 mm sampling. It is not the maximum of two
directional percentiles. Dice, precision and recall have their ordinary binary
pixel definitions. Backend mask-to-mask Dice is distinct from agreement with GT.
Model quality-head scores are not used as measured accuracy or calibrated confidence.

Timing separates one full-image encode from two cached box decodes. Denominators
are 18 unique encodes and 36 decodes per complete run, 2 and 4 per CPU subset.
Measured encode includes preprocessing; decode includes CPU mask return. Model
load, warmup and disk input are excluded. Memory counters are not additive and
do not establish total peak unified memory. CPU expansion is a diagnostic, not
an independent medical replication. Original masks and scores remain unchanged.

One known public CT, correlated slices, uncertain training overlap and privileged
localization do not establish autonomous localization, semantic naming, clinical
accuracy, 3D propagation or population generalization. Reference intent has not
been clinically adjudicated. No new trial or revised prompt is implied.

Rebuild: `python scripts/build_segmentation_calibration_assets.py --root . --output FRESH_DIRECTORY`.
