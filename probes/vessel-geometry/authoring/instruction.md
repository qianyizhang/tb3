Build a coronary vessel review package from a CTA and a proposed lumen mask.

The reviewer wants the route from the right coronary artery (RCA) ostium to the
distal right posterior descending artery (R-PDA). A small region needs review
for possible connectivity errors. Use the CTA evidence to repair the mask there,
preserve the surrounding vessels, trace the requested route, and generate rotated
curved planar reformations (CPR) and a surface mesh. This is an engineering
geometry task; do not diagnose disease or infer stenosis grades.

Inputs in `/app/data`:
- `image.nii.gz`: native CTA intensities in HU, stored as XYZ arrays.
- `proposed_mask.nii.gz`: binary output from a published segmentation model.
- `editable_region.nii.gz`: the only region in which mask edits are allowed.
- `request.json`: route name, start and end landmarks, review marker, and CPR grid.

All coordinates below are **RAS millimeters**, using the NIfTI affine. Preserve
the input mask's shape and affine exactly. A reference may differ slightly in
boundary placement; evaluation tolerates that. Do not change any mask voxel
outside the editable region. Nearby branches must retain their identity; joining
the distal vessel to the wrong neighboring branch does not repair this route.

Write these four artifacts to `/app/answer`:

1. `corrected_mask.nii.gz`: the repaired binary mask.
2. `centerline.npy`: a finite N×3 floating-point array, ordered from the start
   landmark to the end landmark. Trace the center of the intended lumen. Sample
   at approximately 0.5 mm arc length (each step between 0.05 and 0.75 mm; 100–2000
   points). Do not reverse the route, skip a bend, take another branch or insert
   disconnected point fragments.
3. `cpr.npz`: a NumPy archive with:
   - `hu`: float array [8,N,65] of linearly interpolated source CTA intensities;
   - `source_ras_mm`: float array [8,N,65,3], the source location of each pixel;
   - `angles_deg`: [0,45,90,135,180,225,270,315];
   - `offsets_mm`: 65 positions from -8 to +8 mm in 0.25 mm steps;
   - `arc_mm`: cumulative Euclidean length along your centerline, starting at 0.

   For reproducible orientation, use a parallel-transport frame. Tangents are
   normalized `numpy.gradient(centerline, axis=0)` vectors. For the first normal,
   pick the positive RAS unit axis least aligned with the first tangent
   (`argmin(abs(tangent))`, X/Y/Z tie order); project it onto the normal plane and
   normalize. For every next normal, apply the minimal rotation taking the previous
   tangent to the new tangent, reproject onto the new normal plane and normalize.
   The binormal is `cross(tangent, normal)`. Pixel location at angle θ and offset u
   is `centerline + u*(cos(θ)*normal + sin(θ)*binormal)`. Use trilinear sampling;
   locations outside the input volume have HU -1024. CPR is a sampled curved plane,
   not a maximum-intensity projection or a thick slab. Preserve HU in the archive;
   windowing is only for optional previews.
4. `vessels.ply`: a triangle mesh of the complete corrected mask in RAS mm. Include
   both coronary trees for spatial context, including the repaired segment. Meshes
   must be closed with consistent outward winding; cap segmentation termini and
   any crop faces. Modest surface smoothing is allowed if it preserves geometry.

Evaluation reports repair, trace, CPR and mesh separately; all must pass for
end-to-end success. Repair needs local Dice and recall ≥0.80, the intended local
connection, zero changes outside the review region, and ≤1.5 mm³ of additions
farther than 0.75 mm from the reference. Centerline checks require endpoints within
1 mm, length within 10%, reference coverage ≥95% within 0.8 mm, 95th-percentile
distance ≤0.8 mm, and ≥99% of points within 0.5 mm of the corrected mask. CPR
coordinates must match your centerline/frame within 0.02 mm and the 99th-percentile
HU sampling error must be ≤0.2 HU. Mesh surface agreement is checked against your
corrected mask (95th percentile ≤0.65 mm, both globally and within the review
region), along with closure, winding and volume
within 10% of voxel volume. A plausible-looking rendering alone is insufficient.

NumPy, SciPy, nibabel, Pillow, scikit-image and trimesh are installed. Other
libraries and optional visual previews are permitted. You can inspect native
images, write code and use ordinary tools. See `/app/SOURCE_NOTICE.md` for data
provenance. Do not use reference annotations as a substitute for solving the
image-and-mask task; report any external source material you consult.
