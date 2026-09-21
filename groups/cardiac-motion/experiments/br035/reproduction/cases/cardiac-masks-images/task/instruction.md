Build a consistent deforming volumetric mesh from a complete cardiac segmentation sequence, and calculate its finite strain.

Registered ultrasound images.npy is present and may be used together with the masks.

Inputs under /app/data:
- masks.npz key masks: boolean (T,Z,Y,X), sampled at voxel centers. The current case contains 30 phases of biventricular myocardial WALL, including inner and outer boundaries. They are binary per-phase segmentations, with no material identities, initial mesh, AHA labels or tracked points.
- geometry.json: origin_xyz_mm, spacing_xyz_mm, shape_tzyx, reference_frame=0, mask_semantics, phase and timestamps_s. World point=origin+spacing*[x,y,z]. All arrays are on this grid. Synthetic phase duration is unknown; do not invent strain rates in seconds.
- Where present, images.npy contains float32 ultrasound (T,Z,Y,X) on exactly this grid. It is image intensity, not blood velocity or reference deformation. Segmentation is already supplied for all frames.

Construct your OWN reference tetrahedral mesh from the first mask, then infer positions through the cycle on that fixed connectivity. Choose a usable resolution and explain it. Ordinary numpy/scipy/scikit-image/meshio/OpenCV/Pillow are installed; other ordinary meshing libraries are permitted. Your reference mesh need not match any hidden source mesh. Every vertex keeps a consistent hypothesized material identity, but consistent indices alone do not establish true tissue correspondence.

Write /app/answer/solve.py with CLI `python solve.py --input DIRECTORY --output DIRECTORY`, run it on the supplied case, and save prediction.npz containing:
- points: (T,N,3) world mm; points[0] is the reference configuration;
- tetra: integer (M,4), fixed connectivity, no duplicate or degenerate cells;
- F and E: (T,M,3,3), deformation gradients and full Green–Lagrange tensors;
- J: (T,M), signed current/reference volume ratios.
F maps reference COLUMN vectors to current column vectors; E=(F.T@F-I)/2. All numerical fields must be finite. Negative J is an inversion even if a renderer hides it. Use fractional strain, not percent. Arrays may use float32 if accurate enough. Include method.md describing geometry, motion assumptions, uncertainty, validations and the distinction between a plausible deformation and measured material motion. Also write assessment.json with mask_semantics, myocardial_strain_supported (boolean), limitations (list), and a short finding. For this synthetic wall, this boolean concerns whether the domain supports a myocardial strain model, not whether its recovered motion is validated.

The executable will be replayed on a second segmentation sequence with different dimensions/frame count and optional images. It may have mask_semantics=lv_cavity: then mesh/deform the cavity for geometric volume/EF checks, but explicitly set myocardial_strain_supported=false and do NOT interpret that mathematical deformation as myocardial strain. No epicardium or tissue tracking is supplied for a cavity. Do not hardcode the current patient's geometry or number of frames. Replay allowance: five minutes, 4 CPUs/8 GB.

The main construction checks are mean full-volume mask Dice>=0.90, mean relative domain-volume error<=5%, zero inverted cells, and F/E/J agreement with independent recomputation within absolute 1e-4. A static or independently remeshed sequence is insufficient. Cell topology must be shared through time. No per-frame realignment is performed by the evaluator.

Material motion and directional strain are separately assessed at independent reference locations using your piecewise affine map, NOT by matching your vertex IDs to the source. Coverage is reported. Research diagnostic targets are >=95% reference-volume coverage, material RMSE<=2 mm, each longitudinal/circumferential/radial strain and regional peak MAE<=5 percentage points, regional peak timing error<=2 frames. These are similarity targets to one simulator; especially without image texture, the input may not identify a unique material map. Material diagnostics do not enter the construction reward. Report unobservable motion and sensitivity rather than presenting smooth strain colors as verified physiology. No etiologic diagnosis or active-force equilibrium is requested.

Source: already curated public STRAUS simulation; the transfer case is clinical EchoXFlow. Public-source training exposure is unknown. All permitted observations are in /app/data. Do not retrieve original moving meshes, reference strain, prior solutions or other workbench outputs. There is no score feedback. Use your time to deliver and validate a runnable artifact; independent geometry and mechanics matter more than polished rendering.
