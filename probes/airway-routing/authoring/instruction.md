# Restore an airway route and produce source-mapped CPR views

Three small CT regions are under `/app/data/A01`, `A02`, and `A03`. Each contains
`image.nii.gz` (CT Hounsfield units), `proposed_mask.nii.gz` (binary airway
segmentation), `editable_region.nii.gz`, and `request.json` with two ordered
anchors in NIfTI RAS millimetres. Arrays use the voxel axes of their NIfTI affine.

For each request, make the smallest image-supported repair needed to restore
the airway lumen between the anchors. Follow the actual airway rather than
cutting through a neighboring wall or choosing a shorter connection to another
branch. Some requested routes are already intact: preserve those masks exactly.
Other branches and unrelated imperfections are outside the task. Do not delete
existing foreground, refine existing boundaries, or change any voxel outside
the editable region. Restoring a one-voxel wire through a wider missing lumen
is insufficient: restore the visible lumen core. Do not expand into lung tissue.

Save these files in `/app/answer/<case_id>/`:

1. `corrected_mask.nii.gz`: binary mask on exactly the input grid and affine.
2. `centerline.npy`: ordered N×3 array of RAS-mm coordinates from the start
   anchor to the end anchor, following the repaired airway centrally. Use
   consecutive steps between 0.05 and 0.75 mm and endpoints within 1 mm of the
   supplied anchors. The route must be contained in the repaired segmentation.
3. `cpr.npz`: eight rotated curved planar reformations of the original CT.
   Required arrays: `hu` of shape (8,N,65), `source_ras_mm` of shape (8,N,65,3),
   `angles_deg` = [0,45,90,135,180,225,270,315], `offsets_mm` = -8 through +8
   in steps of 0.25, and `arc_mm` of length N.

For reproducible CPR orientation, compute unit tangents using `np.gradient`
on the saved centerline. Initialize the normal by projecting the Cartesian
RAS basis axis least aligned with the first tangent onto its normal plane.
Transport the normal by the minimal rotation between consecutive tangents,
then project and normalize it again. The binormal is tangent cross normal.
At angle θ and offset u, sample at
`centerline + u*(cos(θ)*normal + sin(θ)*binormal)`.
Use trilinear interpolation of the source CT in its physical coordinate system;
use -1024 outside the image. `arc_mm` must be cumulative Euclidean distance along
the saved centerline, starting at zero. Do not synthesize image intensities.

Anatomical repair/routing and CPR integrity are scored separately. The full
result requires both. Anatomical checks include connectivity along the correct
branch, at least 80% coverage of the reference lumen core in the reviewed route,
preservation, and at most 1 mm³ of newly added tissue farther than 0.8 mm from
the reference airway. Route tolerance is 1.2 mm at the 95th percentile, with
at least 90% reference-route coverage at that distance and length within 20%.
CPR coordinates must agree within 0.02 mm, intensities within 0.2 HU at the 99th
percentile, and arc coordinates within 0.1 mm.

This is an engineering reconstruction task. It does not ask for a disease
diagnosis or claim physical bronchoscope reachability. Optional explanatory
notes or meshes may be saved alongside the required files.
