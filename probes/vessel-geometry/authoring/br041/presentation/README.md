# Interactive BR-041 CPR review

Reuses BR-030 `geometry.py` sampling/frames and `build_viewer.py` surface simplification. The new interface compares unchanged Terra/high, Sol/xhigh and Astra/xhigh lines with both retained coronary references. Native axial/coronal/sagittal panels use the original CTA, with adjustable window, field of view and slices. CPR position, source RAS, orthogonal sections, distance plot and 3D selected point are linked.

From the repository root:

```sh
.venv-br030/bin/python probes/vessel-geometry/authoring/br041/presentation/build.py
.venv-br030/bin/python probes/vessel-geometry/authoring/br041/presentation/tour.py
.venv-br030/bin/python probes/vessel-geometry/authoring/br041/presentation/validate.py
.venv-br030/bin/python probes/vessel-geometry/authoring/br041/presentation/launch.py
```

`build.py` requires the completed BR-041 receipts and local BR-030 source assets. It verifies frozen task bytes and copies submitted lines byte-for-byte. Generated assets (about 126 MB) stay under ignored `runs/br041-image-only-centerline/presentation/`. `launch.py` starts a loopback-only server on port 8794 when needed and opens the viewer; `Open review.command` is generated there for reopening. No remote services, deployment or new trials.

## Interpretation

Select a model and use **Review discrepancy**, **Nearest reference endpoint**, or **Submitted endpoint**. Click either CPR or the distance graph to navigate; rotate the sampled plane and adjust windowing. Use **Faint distal signal** for Astra's extension, then inspect native CT with route overlays off/on. Drag the 3D surface, use standard view buttons, or click the selected route. Reference and model positions match spatially, not by percentage along their lines. Each route's perpendicular frames differ; native views share anatomical orientation.

The simplified mesh is reference-assisted context, not a model segmentation. These CPRs are author-generated visualizations from model centerlines, not model CPR submissions. The full source CT, exact line copies and numerical review CPR/HU/source-coordinate archives are downloadable. Frozen failures remain recorded; this viewer does not adjudicate distal anatomy or change scoring.

## Validation

Five routes: independent source-coordinate/HU sample checks, CPR/section center agreement, exact model-file digests, binary shapes and true cumulative arc axes. The browser's trilinear sampler is executed independently in Node against 304 points including volume boundaries and compared with SciPy (zero HU difference on the retained build). The browser UI was exercised on all five routes, including endpoint jumps, CPR rotation, window presets, slice controls and recentering. Local validation receipts are `validation.json` and `numeric-validation.json` in the generated presentation.

## Narrated guided tour

`tour.py` renders a 2:12 local H.264/AAC video at 1280 × 720, with six seekable chapters in the viewer. It uses the unchanged submitted geometry and the source-derived CPR/cross-section arrays from `build.py`; no illustrative anatomy is synthesized. Narration uses macOS `say` (Samantha), and encoding uses local `ffmpeg`/`ffprobe`. The Python environment needs NumPy and Pillow. macOS speech synthesis must be available; an empty speech file must not be interpreted as a successful narration.

The tour distinguishes Terra's localization mismatch, Sol's accurate R-PLA tracing instead of the requested R-PDA, and Astra's close R-PDA tracing with an unresolved distal extension. A plausible continuous distal lumen could justify preferring Astra's longer extent; the reference-distance penalty cannot adjudicate that question. This is a review interpretation, not a revised benchmark pass or an independent clinical adjudication. Frozen scores remain in a collapsed secondary section.

Generated outputs: `guided-tour.mp4`, `tour-chapters.json`, `tour-transcript.md`, `tour-validation.json`, and local `tour/` narration/render intermediates. The receipt records video/manifest hashes and stream metadata. The viewer loads the small video into a local Blob so chapter seeking also works with Python's basic HTTP server.
