Localize the 26 requested vertebral landmarks from the supplied CT volume and identify targets that cannot be localized. Use this patient's anatomy, not an assumed fixed count. Some requests may be outside the field of view or represent a genuinely absent extra vertebra. A missing annotation is not proof of absence. Do not force a coordinate for every requested name.

Input `/app/volume.npy` is the entire supplied 3D CT array, shape (512, 512, 920), access volume[i,j,k]. `/app/volume.nii.gz` contains identical intensities and spatial metadata. This partial CT volume can be inspected at any slice and zoom. `/app/landmarks.json` gives the requested semantic definitions. You are not given reference segmentations or coordinates. Standard nomenclature: C1-C7; thoracic levels are rib-bearing; lumbar levels precede the sacrum. T13/L6 are possible additional levels, not required placeholders.

Write `/app/answer/landmarks.json` exactly as:
{"space":"voxel_ijk_zero_based","landmarks":{"<each requested key>":{"status":"observed|out_of_fov|absent|uncertain","ijk":[i,j,k] or null}}}
- observed: target exists and its centre is within the supplied scan; provide a native zero-based voxel triple.
- out_of_fov: target's centre lies outside this scan; use null, or optionally give an explicitly extrapolated out-of-bounds voxel triple. Such an estimate is not an observed detection.
- absent: evidence supports that this patient does not have that anatomical level; use null. Do not equate outside coverage with absence.
- uncertain: insufficient evidence to decide/localize; use null.
All keys are required. Fractional indices are allowed. Coordinates are array ijk, NOT screenshot pixels, NOT RAS/LPS millimetres. Do not reorder or flip indices. The scanner origin is not an anatomical anchor.

Run `python /app/volume_tools.py check`. View with `python /app/volume_tools.py view 256 220 460 --out /app/overview.png` and inspect the resulting image using your image tool. Change the centre to explore the volume; add `--radius-mm 40` to zoom. Axis ticks show native voxel indices. Cyan crosshairs indicate only your chosen inspection centre. Geometry and nonanatomical conversion examples are in `/app/geometry.json`. You may build other views or image-processing tools.

Localization is measured in physical millimetres from native voxel coordinates at 5/10/20 mm thresholds. False observed detections on unavailable requests, missed visible points, correct visibility/absence classification, and uncertain abstentions are measured separately. General anatomy references and software are allowed; case-specific source annotations, prior answers, or reference masks must not be retrieved. Briefly document image evidence and your identification method.
