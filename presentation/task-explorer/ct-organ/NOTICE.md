# CT organ segmentation reader pack

Source: TotalSegmentator v2.0.1 small dataset, s1233, Zenodo record 10047263.
Image data by the TotalSegmentator authors, CC BY 4.0; source label material,
Apache 2.0. Both exact retained notices accompany this derivative.
The source manifest and native receipt are in the anatomy-audit group.

This pack is a reader explanation, never a solver packet. It contains actual
windowed native CT pixels, submitted masks, saved prompt/candidate artifacts and
separately revealed private research references. All diagnostic view selection
occurred after submission. The initial centre section contains no masks.

Native shape 265 x 265 x 401, 1.5 mm isotropic, RAS positive directions. Axial
display columns increase i/right and rows decrease j/anterior; coronal rows
decrease k/superior. Pixel centres use half-pixel offsets. Source arrays are not
resampled. Gray window is [-160,240] HU. Contours trace the .5 level of padded
binary planes; masks remain separate, including the 57 reference overlaps.

The ten diagnostic views choose each reference's maximum-area axial section,
then a common crop covering reference and both medium predictions plus margin.
These are selected cross-sections, not a full 3D contour adjudication. The
displayed Dice values always score the full native 3D organ, not that crop.

Method views use k235-240. Baseline raw geometry is reconstructed from saved
stomach polygons and signed-distance interpolation; tool candidates are stored
small-batch masks, not fresh inference. Tool rectangles retain saved full-image
coordinates, transformed to the reader crop. The actual small-batch crop was
[75,60,225,210] in the 265px image, resized to 256px for learned inference.
Both explicit and interpolated boxes receive their own image-conditioned mask.
Later assembly unions candidates and applies filters/morphology. This numerical
comparison is not a chronological learning curve. The model's anatomical name
comes from the agent's job ID, not the box-only segmenter.

One public case and one attempt per condition; training overlap unknown. The
tool arm changes skill, instruction and runtime. Research labels are not a new
clinical adjudication. Original task and result bytes remain unchanged.

Rebuild with the existing imaging environment:
`python scripts/build_ct_organ_assets.py --root . --output FRESH_DIRECTORY`.
The manifest pins every input used and verifies PNG pixels and prompt mapping.
