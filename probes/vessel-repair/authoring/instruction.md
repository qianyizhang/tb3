# Repair vessel connectivity in an MRA region

Inspect the angiographic image and proposed binary vessel segmentation in
`/app/data`. Correct a broken or unsupported vessel connection if present.
The segmentation may already be correct; in that case return it unchanged.
Small or absent communicating arteries are valid anatomy: a complete or
symmetric Circle of Willis is not required. Preserve other vessels.

Write `/app/answer/corrected_mask.nii.gz`, a binary 0/1 NIfTI on exactly the
same voxel grid and affine as the input. The inputs are:

- `image.nii.gz`: native-resolution MRA intensities, unchanged from the source.
- `proposed_mask.nii.gz`: proposed binary vessel mask on that image grid.
- `editable_region.nii.gz`: broad review region; do not change mask voxels
  outside its nonzero region. The image includes an additional context halo.

Use the NIfTI affine and physical spacing rather than assuming array indices
are millimetres. A bright projection overlap alone does not establish a 3-D
connection. Preserve the native image geometry in your output.

Acceptance checks the reference communicating-vessel routes locally, not
whole-volume connectedness. Reference-absent communicating routes must remain
absent. For present vessels, the appropriate attachments must connect, at least
95% of the reference centerline must lie within 0.45 mm of your mask, and at
least 80% of each reference communicating-vessel mask must be preserved.
Where repair is necessary, local Dice and vessel recall must each be at least
0.75. Boundary voxels need not exactly reproduce the manual reference.
Outside the true local repair neighborhood, additions and deletions must each
be no more than 2 mm³. Additions more than 0.6 mm from reference foreground
must total no more than 1 mm³. All mask voxels outside the supplied editable
region must be unchanged. A thin connector, excessive dilation, or deleting
a valid branch can fail even with high whole-mask Dice. Vessel paths use
26-neighbor foreground connectivity.

Python, NumPy, SciPy, scikit-image, nibabel and Pillow are installed. You may use scripts,
viewers, other packages, pretrained tools or public resources as appropriate.
Only the corrected mask is required; no clinical report is requested.

You have 1800 seconds to complete the task.
