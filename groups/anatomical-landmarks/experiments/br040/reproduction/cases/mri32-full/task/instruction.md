Localize all 32 named anatomical points from the COMPLETE T1 MRI volume. This task is volume -> 3D landmark coordinates, not screenshot -> image pixels.

Input: `/app/volume.npy` is the full intensity array with shape (224, 342, 342); access it as volume[i,j,k]. `/app/volume.nii.gz` is the identical array with spatial metadata. `/app/landmarks.json` defines the target points. All requested reference points are contained in this full volume. MRI numeric keys refer to definitions in that file.

Output `/app/answer/landmarks.json` with exactly this structure:
{"space":"voxel_ijk_zero_based","landmarks":{"<each requested key>":[i,j,k]}}
Return native array indices, zero-based; fractional values are allowed. They are 3D VOXEL coordinates, NOT screenshot pixels, NOT physical millimetres, NOT MNI or AC-PC coordinates. Do not reorder axes or flip sides. Index [0,0,0] is the array's first voxel, not an anatomical landmark. Patient RAS [0,0,0] is not necessarily AC. The volume has not been registered to an anatomical template for this task.

Run `python /app/volume_tools.py check` to verify the input contract. `/app/geometry.json` supplies shape, axis directions, affine and arbitrary NONANATOMICAL conversion examples. The supplied viewer avoids manual display-coordinate conversion:
`python /app/volume_tools.py view 112 171 171 --out /app/overview.png`
Inspect the resulting image with your image tool. To zoom, add `--radius-mm 30`; change any i,j,k centre to inspect other slices. Axis ticks are original voxel indices. Cyan lines only indicate the centre you requested, not a detected point. You can build other views/tools as desired. `convert i j k` reports world RAS for debugging only; submit voxel indices.

The verifier alone converts voxel differences into physical distances, using the image geometry. Acceptance stays <= 3 mm per landmark. No coordinate convention needs to be guessed. Inspect and refine image evidence for the actual subject; do not substitute nominal atlas positions. Record briefly how you identified the points. General anatomical references/software are allowed; source-subject labels, prior solutions and case-specific annotation retrieval are not. No earlier model answers are supplied.
