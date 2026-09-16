# Vessel geometry experiment — BR-030

Real coronary segmentation error → local repair → named vessel trace → rotated
CPR with source mapping → closed world-space mesh. See the
[results](../../docs/research-rounds/BR-030-results.md) and
[predeclared scope](../../docs/research-rounds/BR-030-vessel-diagnostic-geometry.md).

The local run is `runs/br030-vessel-geometry`. It contains source hashes, the
unedited predictions, three linked offline viewers, a frozen task and retained
trial evidence. Public task inputs never include the reference mask or route.

## Sources and dependencies

- Original CTA: ImageCAS case 1, fetched from the bounded prefix of its official
  Kaggle multi-volume archive; inner ZIP CRC and SHA-256 checked.
- New reference: ImageCAS-X Zenodo record 21887809, selected mask, named VTK
  centerlines, surface, descriptors and split files. Case 1 is training data.
- Coronary prediction: ImageCAS-X source commit
  `dbc7343187adf45ca9306dc3460eebc70f92b204`, released `cas_net.pt`.
- MRA screen: CLAIM source commit
  `e7ae1d33cbae407b6ab42cd1063b55f4ff0f82a5`, fold 0 final checkpoint, public
  CoW ROI plus halo. This is not the full challenge ensemble.
- Local environment `.venv-br030`: Python 3.12.13, NumPy 2.2.6, SciPy 1.15.3,
  nibabel 5.3.2, scikit-image 0.25.2, trimesh 4.11.3, Pillow 11.3.0,
  Torch 2.10.0, SimpleITK 2.5.6, VTK 9.5.2 and openpyxl 3.1.5. The custom
  CLAIM nnUNet package and dynamic-network-architectures 0.3.1 are only needed
  for MRA inference. Matplotlib is used for the paired-image review panel.

Source manifests are collected in `docs/evidence/br030-sources.json`. The
original CTA listing declares Apache 2.0, the ImageCAS-X record CC BY 4.0 and
the implementation MIT. Attribution and license declarations are copied into
the frozen task. These are recorded upstream declarations, not a legal opinion.

## Commands

Run from the repository root. Frozen preparation scripts intentionally refuse
to overwrite an existing task or prediction. **Do not rerun trial/preparation
commands against this completed round.** Use a separately authorized new round
and output directory for another experiment.

```sh
# Source acquisition (record/container metadata is retained in the runtime root)
.venv-br030/bin/python probes/vessel-geometry/authoring/fetch_coronary.py refs
.venv-br030/bin/python probes/vessel-geometry/authoring/fetch_coronary.py original
.venv-br030/bin/python probes/vessel-geometry/authoring/fetch_coronary.py weights

# Full coronary inference; on Apple Silicon the pooling operation needs fallback
PYTORCH_ENABLE_MPS_FALLBACK=1 .venv-br030/bin/python probes/vessel-geometry/authoring/infer_coronary.py

# Reference-assisted author preparation and validation, before freezing
.venv-br030/bin/python probes/vessel-geometry/authoring/build_geometry.py
.venv-br030/bin/python probes/vessel-geometry/authoring/validate_geometry.py
.venv-br030/bin/python probes/vessel-geometry/authoring/package_task.py

# One oracle, one no-op, then one Terra/high attempt
.venv-br030/bin/python probes/vessel-geometry/authoring/run_trials.py

# Local public-input algorithm and its matched upstream intensity ablation
.venv-br030/bin/python probes/vessel-geometry/authoring/image_baseline.py
.venv-br030/bin/python probes/vessel-geometry/authoring/image_baseline.py --mask-only

# Build self-contained local previews (safe to regenerate; no frozen file edits)
.venv-br030/bin/python probes/vessel-geometry/authoring/build_viewer.py
.venv-br030/bin/python probes/vessel-geometry/authoring/build_viewer.py image-baseline
.venv-br030/bin/python probes/vessel-geometry/authoring/build_viewer.py terra-arc-correction
```

`score_geometry.py ANSWER_DIR REFERENCE_NPZ` grades local outputs without
changing them. Its exact frozen copy is in the task's separate verifier image.
`closeout.py` replays the model artifact, checks current and previous freezes,
and refreshes concise evidence receipts. Raw outputs remain local.

The three viewers are standalone HTML files. For browser download links and
local inspection, a loopback-only server can serve the runtime root:

```sh
.venv-br030/bin/python -m http.server 8790 --bind 127.0.0.1 --directory runs/br030-vessel-geometry
```

Open `http://127.0.0.1:8790/viewer-terra-arc-correction/` or the local HTML file.
The server is only a convenience; it is not a publication or hosted service.

## Important distinctions

The real CAS-Net gap is approximately 5 mm, despite 94.14% whole-mask Dice.
The author oracle repairs it from the reference. The fixed image method and
the Terra attempt solve from public inputs; author development was not blind.
Terra's original output fails only because `arc_mm` describes the pre-resampling
skeleton instead of the saved centerline. Its separate author-corrected copy
changes that field alone and passes. Never replace the original failure with
the corrected result in a model ledger.

CPR is a thin sampled curved plane, not MIP, a thick slab, a stenosis diagnosis
or a blood-flow simulation. Mesh caps close the segmentation geometry; they do
not establish physiological inlet/outlet boundary conditions. The old MRA
disagreement remains clinically unadjudicated, with a paired-image review packet.
