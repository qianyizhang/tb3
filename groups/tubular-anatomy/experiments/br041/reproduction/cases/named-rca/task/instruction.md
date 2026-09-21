Trace a named coronary vessel from a CTA image.

Input: `/app/data/image.nii.gz`, a coronary-region CTA crop with native HU intensities. Arrays are XYZ; the NIfTI affine maps zero-based voxel indices to RAS millimeters. No segmentation, route landmarks or centerline is provided.

Trace from the right coronary artery (RCA) ostium through the RCA into the right posterior descending artery (R-PDA), ending at its distal visible terminus. Follow the central contrast-filled lumen continuously, including bends; select R-PDA rather than the right posterolateral branch. Infer location from the image and anatomical name. This is an image geometry task, not diagnosis.

Write `/app/answer/centerline.npy`: finite floating-point N by 3 array in RAS mm, ordered proximal to distal, 100-2000 points, approximately 0.5 mm sampling (each step 0.05-0.75 mm). Also write `method.md` briefly describing your method, uncertainties and any external sources consulted. Optional segmentation and visualizations are welcome but not required. No CPR or mesh is required.

Evaluation uses a private annotation-derived route: 95th-percentile distance <=1 mm, reference coverage >=95% within 1 mm, each endpoint within 5 mm, and length within 15%. Endpoint tolerance accounts for distal extent ambiguity. A plausible rendering alone is insufficient.

NumPy, SciPy, nibabel, Pillow, scikit-image and trimesh are installed. You may inspect native images, write code and use ordinary tools or general methods. Do not obtain this case's reference annotations, masks or centerlines. Report any external assistance. See `/app/SOURCE_NOTICE.md`.
