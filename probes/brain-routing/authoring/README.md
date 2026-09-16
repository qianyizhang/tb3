# TopBrain development screen

The current outcome and limitations are in
[`BR-033-brain-resumption.md`](../../../docs/research-rounds/BR-033-brain-resumption.md).
There is no frozen brain task or coding-agent trial in this directory.

Runtime files live under `runs/br033-brain-routing/`. Acquisition preserves
archive members and verifies their hashes; inference preserves untouched
predictions. The local execution used Python 3.12, the existing `.venv-br030`
scientific environment, and Apple MPS. Exact package versions and checkpoint
hashes accompany the predictions. This is not a clean-container reproduction
of the original CUDA ensemble.

Relevant entry points:

- `fetch_model_layer.py`: resume and hash-check the official model/source layer.
- `fetch_variant_images.py`: acquire the selected original TopCoW scans and
  match their sizes/CRCs to retained TopBrain metadata.
- `infer_source.py --cases 004 007 012`: source-only inference; refuses to
  overwrite an existing prediction. The later run used `--cases 006 011`.
- `screen_predictions.py`, `find_review_regions.py`, `audit_parents.py`:
  reference comparisons for curation, not automatic error admission.
- `gap_calibration.py`: one simple same-label nearest-point bridge and its
  centerline, rotated CPR and mesh. Refuses to overwrite an existing run.
- `build_calibration_viewer.py`, `render_calibration.py`: actual-array viewer
  and static preview. Displays the residual reference disagreement explicitly.
- `validate_calibration.py`: independent source sampling, parent connectivity,
  preserved-volume, native-grid rounding, mesh, asset and syntax checks.

Raw predictions, intermediate exports and failed authoring checks are retained.
The viewer is a geometry calibration, not an accepted difficult benchmark.
