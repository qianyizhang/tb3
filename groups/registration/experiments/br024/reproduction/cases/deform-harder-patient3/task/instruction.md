# Find corresponding anatomy across respiratory phases

The supplied images come from the same patient in exhale and inhale phases.
Breathing changes anatomical shape, so a global rigid or affine transform may
not adequately describe the correspondence. Locate the anatomical points
specified in queries.json in the inhale CT /app/data/volume.npz.

Write /app/answer/points.json as
{"query_ids": ["q01", "q02", ...], "points_world_mm": [[x,y,z], ...]}.
Use the exact query order and IDs from queries.json. Coordinates must be
finite numbers in the supplied dataset-world millimetres.

Each volume NPZ contains hu[i,j,k] (float32 HU) and voxel_to_world (4x4).
The latter maps zero-based voxel centres [i,j,k,1] to homogeneous dataset-world
millimetres. The challenge volumes were cropped, resampled and affine
prealigned; matching array indices are only a nominal spatial initialization.
Do not assume a scanner LPS or RAS convention from the array order. Expiration
coverage is incomplete. Every requested corresponding point is visible in
the supplied inhale volume.

Inputs in /app/data:
- volume.npz: the inhale volume to search.
- view.npy: float32 HU [row,column] sampled from one thin oblique exhale plane.
- view.png: a preview, round(255*clip((HU+1000)/1200,0,1)).
- view.json: shape, spacing_xy_mm and slice_to_world (4x4).
- queries.json: query_ids and pixels_uv, specifying source landmarks by
  fractional pixel column u and row v in the exhale view.

The acquisition frame is supplied: slice_to_world maps [u*sx,v*sy,0,1] to
exhale dataset-world millimetres, where (sx,sy)=spacing_xy_mm and (0,0) is
the top-left pixel centre. This is a nominal source geometry, NOT the mapping
of anatomy into inhale. The full exhale volume is not supplied. Find where
the specified structures in this single view moved in the inhale volume.
The source landmarks are localized to this view within 0.35 mm through-plane.
The view is a trilinear thin section, not an X-ray projection or thick slab.

Acceptance: root-mean-square Euclidean error <=3 mm AND maximum error <=5 mm
against independently supplied manual corresponding landmarks. The comparison
is in world millimetres, not voxels, and only the eight submitted positions are
graded. Pixel similarity alone is not acceptance. No dense-field accuracy is
claimed between the queried points.

Python, NumPy, SciPy, Pillow and SimpleITK are installed. You may use suitable
registration algorithms, other software and public method documentation.
Reference landmark annotation files and evaluation answer keys are not solver
inputs; recover correspondences from the supplied images.

You have 1800 seconds to complete the task.
