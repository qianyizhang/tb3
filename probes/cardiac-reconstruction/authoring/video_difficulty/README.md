# Cardiac video difficulty screen

Owner: [BR-027](../../../../docs/research-rounds/BR-027-cardiac-video-difficulty.md).
The old all-frame-contour pilot is preserved in the parent directory. This
screen removes target-frame contours while retaining four calibrated videos.
It is author development tooling, not an admitted or provider-tested TB3 task.

Use Python 3.12 with NumPy 2.2.6, SciPy 1.15.3, Pillow 11.3.0 and
opencv-python-headless 4.12.0.88. The isolated local environment is
`.venv-cardiac-hard`. Commands below assume the repository root. Use new output
directories for reruns: preparation, solving and evaluation refuse to overwrite
their directories. Native source acquisition is documented in the parent README.

```sh
.venv-cardiac-hard/bin/python probes/cardiac-reconstruction/authoring/video_difficulty/prepare.py \
  --source runs/br025-cardiac/source/native/Patient001 \
  --output runs/br027-cardiac/public

.venv-cardiac-hard/bin/python probes/cardiac-reconstruction/authoring/video_difficulty/solve.py \
  --input runs/br027-cardiac/public/one_anchor \
  --output runs/br027-cardiac/one-anchor-v1
.venv-cardiac-hard/bin/python probes/cardiac-reconstruction/authoring/video_difficulty/solve.py \
  --input runs/br027-cardiac/public/two_anchors \
  --output runs/br027-cardiac/two-anchors-v1

.venv-cardiac-hard/bin/python probes/cardiac-reconstruction/authoring/video_difficulty/evaluate.py \
  --source runs/br025-cardiac/source/native/Patient001 \
  --run runs/br027-cardiac --output runs/br027-cardiac/evaluation-v1

.venv-cardiac-hard/bin/python probes/cardiac-reconstruction/authoring/video_difficulty/refine.py \
  --input runs/br027-cardiac/public/one_anchor \
  --prediction runs/br027-cardiac/one-anchor-v1/dis-mesh.npz \
  --output runs/br027-cardiac/one-anchor-refined-v1

.venv-cardiac-hard/bin/python probes/cardiac-reconstruction/authoring/video_difficulty/evaluate.py \
  --source runs/br025-cardiac/source/native/Patient001 --run runs/br027-cardiac \
  --extra runs/br027-cardiac/one-anchor-refined-v1/refined-mesh.npz \
  --output runs/br027-cardiac/evaluation-v2
.venv-cardiac-hard/bin/python probes/cardiac-reconstruction/authoring/video_difficulty/build_viewer.py \
  --source runs/br025-cardiac/source/native/Patient001 --run runs/br027-cardiac \
  --evaluation runs/br027-cardiac/evaluation-v2
```

`solve.py` reads only the selected public input, verifies its manifest, and
serializes predictions before private evaluation. `refine.py` reads that input
and the frozen tracking prediction. It was developed after seeing the first
screen and is not a blind-method claim. `evaluate.py` reads withheld source
masks and computes the clean-contour control and derived 36-plane comparator.
`build_viewer.py` also reads private references. Never provide either the source
tree, this author tooling directory, evaluation files or the review viewer to a
tested agent. A future trial needs its own process/filesystem separation.

The solver NPZ contains `vertices` (30,V,3) in mm, fixed `faces` (F,3),
`volume_ml` (30), `radius_px` (30,72,65) and `input_view_masks` (4,30,H,W).
Mesh vertices are centered on the supplied rotation axis/origin; the geometry
file describes orientation. Cavity volume is signed tetrahedral volume /1000.
Fixed indices are a surface parameterization, not material motion or strain.

The four initial masks are sufficient to identify the intended cavity but
the one-anchor author methods do not yet achieve a complete pass. Two-anchor
DIS passes the same gates. GrabCut recovers EF/volume yet fails shape, making
the separate shape and measurement gates consequential. This screen does not
qualify exact 3D anatomy, flow, disease or model difficulty.
