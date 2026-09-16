# Dynamic Heart Lab

Owner: [BR-029](../../../../docs/research-rounds/BR-029-dynamic-heart-modeling.md).
Contract: [Dynamic heart modeling](TASK.md).

This is a local research workbench with real volumetric mesh calculations:
11,370 material vertices, 47,186 tetrahedra, two STRAUS simulated scenarios,
three directional strain components, source AHA regional curves, material
rotation and cutaway rendering. It separates reference playback, image-driven
fits and privileged controls. It is not a four-chamber patient digital twin or
a force-balanced electromechanical simulation.

## Data and dependencies

The author run downloaded the healthy case's 30 ultrasound volumes/meshes and
the LBBB case's 30 meshes, plus RefMeshP1 anatomical axes. Native files, per-file
hashes and API metadata remain under `runs/br029-dynamic-heart/source/`.
The initial patient-item inventories came from the earlier source curation and
were checked against live public file metadata before downloading. The first
LBBB download manifest accidentally retained a generic patient01 source label;
its file IDs/URLs identify patient04 correctly. The final integrity receipt
records this provenance correction without changing downloaded bytes.

Python 3.12.13; NumPy 2.2.6; SciPy 1.15.3; Pillow 11.3.0; meshio 5.3.5;
opencv-python-headless 4.12.0.88. Matplotlib 3.10.6 is used only for the summary
figure. The isolated local environment is `.venv-dynamic-heart`.

The workbench uses native WebGL 2 and local data assets, with no external JS,
fonts or image requests. Open it through a localhost server, not `file://`.

## Reproduce the retained corrected screen

Use fresh output paths; preparation, fitting and evaluation refuse to overwrite
their output directories. Data acquisition is in `fetch_straus.py`; it needs
the exact source item inventories retained in the source folder.

```sh
.venv-dynamic-heart/bin/python probes/cardiac-reconstruction/authoring/dynamic_heart/prepare_video.py \
  --source runs/br029-dynamic-heart/source/patient01_healthy \
  --reference runs/br029-dynamic-heart/source/RefMeshP1.vtk \
  --output runs/br029-dynamic-heart/public-video

.venv-dynamic-heart/bin/python probes/cardiac-reconstruction/authoring/dynamic_heart/fit_video.py \
  --input runs/br029-dynamic-heart/public-video \
  --output runs/br029-dynamic-heart/video-fit-v1

.venv-dynamic-heart/bin/python probes/cardiac-reconstruction/authoring/dynamic_heart/fit_tissue.py \
  --input runs/br029-dynamic-heart/public-video \
  --affine runs/br029-dynamic-heart/video-fit-v1/prediction.npz \
  --output runs/br029-dynamic-heart/tissue-fit-v2 --max-cg 2000

.venv-dynamic-heart/bin/python probes/cardiac-reconstruction/authoring/dynamic_heart/analyze.py \
  --source runs/br029-dynamic-heart/source \
  --public runs/br029-dynamic-heart/public-video \
  --prediction runs/br029-dynamic-heart/video-fit-v1/prediction.npz \
  --output runs/br029-dynamic-heart/analysis-v2

.venv-dynamic-heart/bin/python probes/cardiac-reconstruction/authoring/dynamic_heart/evaluate_tissue.py \
  --reference runs/br029-dynamic-heart/analysis-v2 \
  --prediction runs/br029-dynamic-heart/tissue-fit-v2/prediction.npz \
  --output runs/br029-dynamic-heart/tissue-analysis-v3

.venv-dynamic-heart/bin/python probes/cardiac-reconstruction/authoring/dynamic_heart/build_workbench.py \
  --analysis runs/br029-dynamic-heart/analysis-v2 \
  --public runs/br029-dynamic-heart/public-video \
  --tissue runs/br029-dynamic-heart/tissue-analysis-v3 \
  --output runs/br029-dynamic-heart/workbench
```

Serve `runs/br029-dynamic-heart/workbench/` on localhost (the author used port
8768). The `*.bin` viewer files are little-endian float32 with shape
(30,11370,10): x/y/z, three nodal engineering strains, three nodal Green–Lagrange
components and J. Author NPZ files retain full element-level fields; playback
uses volume-weighted nodal interpolation and does not replace those arrays.

## Interpretation and retained corrections

`prepare_video.py` uses only first-frame geometry to establish pose and four
plane definitions. `fit_video.py` and `fit_tissue.py` read the public package
and permitted prior output. Future source meshes are read only by evaluation.
This is reviewed code separation, not an OS-isolated or blind provider trial.

`mechanics.py` implements finite deformation, engineering/Green–Lagrange strain,
Jacobian ratios and independent analytic checks. Source axes are averaged into
elements and orthonormalized. AHA 0 and three positive-label cells without a
complete basis are excluded from directional statistics; they remain in all
geometry/Jacobian checks. Source frame-zero strain is asserted to vanish on
supported directions. The corrected evaluator reports coverage explicitly.

The first tissue run used CG max 300 and did not fully converge. Its prediction
and executed source remain in `tissue-fit-v1/`. Increasing only the numerical
iteration allowance to 2000 made all 87 linear solves converge; no image,
regularization or acceptance parameter was changed. Three Gauss-Newton steps
are a fixed approximation, not proof of full nonlinear stationarity.

The first evaluation included undefined positive-AHA directions. It is retained
as `analysis-v1/` and `tissue-analysis-v2/`, with executed source snapshots.
Corrected results live in `analysis-v2/` and `tissue-analysis-v3/`. Predictions
were not changed for this evaluator correction. Final evidence names these
versions explicitly.

No cavity/valve-plane partition is validated in STRAUS here. Tissue volume is
not cavity volume, and EF/flow are not supplied for this source. The atlas's
reference axes lack direction fields for much of the RV. Regional twist is an
exploratory apical-minus-basal in-plane material rotation, not clinical torsion.
