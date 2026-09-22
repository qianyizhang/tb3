# Baseline instance convention needs review

2026-09-22 · recorded during the first image-only attempt; no task edits or feedback.

The three abdominal source labels (1, 2, 4) form one 6-connected foreground
component. Minimum distances between their labeled voxel centers are 0.822 mm
(1/2), 0.822 mm (1/4), and 3 mm (2/4). The distant label 3 is a separate component.
See [the retained calculation](longitudinal-ct-instance-boundary-review.json).

This does **not** establish radiologic confluence or invalidate the source labels.
It raises a specific question for our authored instruction, “A confluent region
is one instance.” That wording may encourage coarser instances than the expert
reference, so an exact merge-group failure cannot by itself isolate temporal
reasoning from baseline instance separation. This is an authoring limitation to
review, not an adjudicated reference error or a reason to alter scores.

The [dataset paper](https://www.nature.com/articles/s41597-026-07466-y) describes
expert manual volumetric segmentation followed by consensus review. Correspondence
and merging were judged using anatomy, proximity and visual continuity. Subvoxel
contours were voxelized, so raster connectivity alone is insufficient to reconstruct
the expert's distinction. The authors aimed for exhaustive malignant-lesion
annotations, with no minimum size cutoff. No independent clinical adjudication was
performed in this exploratory study.

Local static figure: `.local/longitudinal-ct-image-only-v1/reference-boundaries.png`.
Selected native axial slices show the labeled boundaries; they do not replace
full-volume expert review. No numerical score, source mask, source event or frozen
solver instruction has been changed. Both model attempts retain the same task.

Next-task recommendation: retain image-only inputs, define distinguishable touching
nodules as separate instances where supported by the images, and allow explicit
uncertainty about instance partitioning. Have an appropriate reviewer assess the
chosen pairs before treating exact merge events as an isolated reasoning endpoint.
