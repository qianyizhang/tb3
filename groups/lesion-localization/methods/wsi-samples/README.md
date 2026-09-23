# Four-route WSI teaching samples

This method supports the [WSI idea](../../ideas/wsi-ground-truth-task-landscape.md).
It performs explicit acquisition and source-derived rendering, never a model run.
All native payloads and generated media are local under `.local/wsi-ground-truth/`.
The pinned [receipt](../../../../datasets/receipts/wsi-teaching-samples.json) owns
source URLs, local paths, checksums, geometry and acquisition qualifications.

- `http_zip.py` is a bounded HTTP-range reader; it refuses servers that do not
  return the requested exact range. It never falls back to the 33.6 GB archive.
- `acquire_selected.py` downloads the explicitly selected source files, or with
  `--hubmap` extracts only the specified ZIP members with CRC verification. Its
  local selection metadata is retained in `source-metadata/`; raw URLs and the
  selected-member identities are recoverable from the pinned receipt. Existing
  files are size-checked; use the receipt SHA-256 audit before trusting a resume.
- `render.py` reads retained TIFF tiles with the existing `.venv-br030` runtime,
  overlays supplied XML/JSON/masks and writes source-derived images/measurements.
  It does not install dependencies or import historical probes. Renderer outputs
  are preparation artifacts, not immutable task freezes; use a new output root
  before preparing a revised study.
- `build_tour.py` reuses the normal brief-section parser and Markdown renderer,
  embeds the local images in the group-owned HTML teaching template, and builds
  `.local/wsi-ground-truth/explainer/index.html`. The four Markdown briefs are
  canonical task descriptions; normal `med brief build` also consumes them.

```sh
.venv-br030/bin/python groups/lesion-localization/methods/wsi-samples/render.py
uv run python groups/lesion-localization/methods/wsi-samples/build_tour.py
uv run med brief check
```

The local `check-viewer.cjs` uses the repository disposable-browser harness.
On this Mac, browser launching requires approved execution outside the restricted
sandbox. Retained `explainer/qa.json` reports ten views, GT default/reveal states,
TIGER layer controls, mobile page bounds and browser errors. This is presentation
QA, not clinical adjudication, exhaustive source annotation validation or model
performance. The TIGER native-vs-ROI comparison is exactly pixelwise; the other
source overlays were reviewed visually on their documented coordinate grids.
