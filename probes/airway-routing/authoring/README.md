# BR-033 airway development experiment

This directory owns source acquisition, curation, fixed controls, the frozen
task builder and the local viewer. It does not replace the workshop's submitted
tasks. [Execution record](../../../docs/research-rounds/BR-033-results.md).

Runtime files remain under `runs/br033-airway-routing/`; source downloads are
under `runs/br033-brain-routing/airway-access/`. Do not overwrite freezes or
completed runs. Inspect those manifests before rerunning anything.

Source inference uses Python 3.12, `raidionicsseg==1.5.2`,
`onnxruntime==1.22.1`, `numpy==2.2.6`, `scipy==1.15.3`, `nibabel==5.3.2`,
`SimpleITK==2.4.1`. Geometry additionally uses `scikit-image==0.25.2`,
`trimesh==4.11.3` and `pillow==11.3.0`; it reuses the BR-030 geometry helpers.
The prepared Dockerfiles independently pin verifier and agent dependencies.

The ordered workflow is:

1. `fetch_cases.py`: pinned author-mirror files, LFS SHA-256 verification.
2. `run_source_model.py`: official lung model, then airway model using that
   predicted lung mask. The initial backend compatibility failure is retained.
3. `screen_prediction.py`, `compare_local_routes.py`: reference-assisted
   candidate selection and the fixed CT/mask route contrast.
4. `build_cases.py`: unchanged prediction crops and independent references.
5. `solve_baseline.py`: reference-assisted oracle or public-input development
   solvers. Initial and revised baseline outputs are separate retained folders.
6. `validate_and_package.py`: admit A01/A02/A03, validate positive and negative
   controls, then freeze file hashes. A04 is retained but excluded.
7. `run_trials.py`: hash checks, Docker oracle, Docker no-op, one Terra/high run,
   no automatic retries. Requires the already-configured local model access.
8. `build_viewer.py`: standalone local HTML from actual CT and saved outputs.

`geometric_controls.py` adds straight-anchor and nearest-component methods
after the trial was dispatched, without changing the frozen cases or criteria.
Those timing and development exposures are part of the interpretation.

The source masks, source models, benchmark package and trial outputs are local
artifacts. Source licenses and notices accompany the prepared environment.
One retained error is not a claim of general difficulty or clinical utility.
