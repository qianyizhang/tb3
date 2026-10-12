# Retained BR-039 native landmark trace

This recipe recovers one source-pinned Terra/high partial-CT attempt,
`attempt-824eaf2afb12f840a722b998`, on VerSe sub-verse823. It reads retained
bytes and derives a bounded display payload. The canonical manuscript selects this one condition; its separate renderer review
records visual verification. The original story and historical acceptance remain retained.

## Recover into a fresh directory

Use the existing local runtime with NumPy and Pillow, for example:

```sh
.venv-br019/bin/python groups/anatomical-landmarks/presentation/native-landmark-trace/prepare_trace.py \
  --output .local/anatomy-pose/landmarks/FRESH-RUN
```

The destination must not exist and must be inside `.local/anatomy-pose/landmarks`.
The recipe refuses overwrite. `manifest.json` and `receipt.json` are written into
that fresh output. Only an explicit
`--manifest groups/anatomical-landmarks/presentation/native-landmark-trace/native-trace.json`
updates the owned tracked manifest after extraction checks pass. It does not run
the historical authoring recipe, supplied helper, scorer, model or any installation.

- **Recover first:** exact task files under `runs/br039-ct-landmarks/tasks/ct-partial`
  and exact attempt files under
  `runs/br039-ct-partial-terra-high-v1-20260917/ct-partial__DeU639y`. The recipe
  checks the SHA-256 pins from [the mapping](canonical-mapping.md) before writing.
  Source code is read as text; raw volumes remain local and never enter the bundle.
- **Retained output:** original answer/status JSON and submitted evidence account;
  original `verifier/details.json` supplies frozen endpoints. `metrics.json` is
  absent. Reproduction `expected.json` is a separate replay artifact.
- **Exact delivery:** ten embedded PNGs from trajectory steps
  11, 15, 17, 20, 22, 24, 27, 29, 30 and 33. Each original decoded byte hash is
  checked; no regeneration substitutes for delivery. Original work PNG files and
  `inspect_spine.py` were not retained separately.

## Coordinate and role boundaries

The supplied crop is 512×512×920, zero-based `volume[i,j,k]`; its native axes
increase L/A/S. The supplied affine maps native centres to RAS mm. All selected
planes, slab endpoints, axial k lists, requested helper centres and intensity-weighted
centres come from actual logged calls/observations. No interpolated search trajectory
or corrected vertebral numbering is created.

- **Preview:** 128×128×230 samples, nearest native integer indices from rounded
  `linspace(0, shape-1, count)` on each axis. Explicit `preview_indices` retain the
  actual sampling locations, including all three endpoint pairs (0/511, 0/511,
  0/919). Fixed supplied window −200..1400 HU maps to rounded uint8; C-order bytes
  are gzip compressed with `mtime=0`, then base64 encoded in flat `volume`.
  This is a coarse context display, not native-resolution localization evidence.
- **Input poster:** a coronal maximum-intensity projection of that preview over j,
  with i horizontal toward L and k upward toward S. It contains no solver or
  reference marks. Its image is derived from the supplied crop only.
- **Half-open bounds:** integer plane/slab/ROI slicing endpoints use [lo,hi).
  Helper display limits originally use centre coordinates clipped to
  [−0.5, shape−0.5]; store them plus 0.5 as half-open array-cell endpoints. Physical
  box edges use `affine(bounds−0.5)`. Requested `center_ijk` remains a native centre
  coordinate. Radius 0 means complete orthogonal planes, not a zero-sized ROI.
- **Points:** logged 2D/3D weighted centres are solver cross-checks with solver
  level names; threshold >100 HU and weights `clip(HU,100,600)−100`. Their ROIs
  and rounded logged centres are retained. Requested cyan helper crosshairs are
  separate `center_ijk` fields, never detections. The `saved` state is step 40's
  exact answer, including all 26 statuses; step 41 validates only the contract.
- **Reader reference:** private source points and frozen errors are separate
  `reference_points`, `frozen` and `wrong_level` keys. Reference-centred review
  images and excluded full-CT cranial intensities are not bundled. True T4 is
  outside the supplied crop; submitted “T4” lies 2.142412 mm from source T5.
  This interpretation does not rewrite the frozen result or prove clinical truth.

## Sources, terms and limits

Exact `SOURCE_NOTICE.md`, the retained CC BY-SA 4.0 legal text and
[source terms](../sources/named-landmark-source-terms.json) accompany the payload.
`DERIVATIVES.txt` attributes Sekuboyina et al. 2021 and Liebl et al. 2021 and
discloses crop, preview and poster transformations. VerSe data/derived images are
CC BY-SA 4.0; its repository code's MIT license is separate. Preserve attribution,
license links, transformation disclosures and ShareAlike in downstream packaging.

The manifest pins raw evidence, source notice, legal terms, curation, recipe and
recovery mapping. The canonical compiler separately pins the manuscript and README
through its source dependencies, so presentation timing does not alter data lineage. It bundles only the compact payload, exact delivered images and
small disclosure/receipt files. Original evaluator code and large NPY/NIfTI are
provenance pins; they are never executed or embedded as player assets.

The selected observations include step 9's missing-image error and step 31's
syntax error. These are execution boundaries, not model medical failures. The
solver's saved account claims the visible column begins at T4; retain that as a
claim beside the reference interpretation. Frozen visible-target counts are
1/13 ≤5 mm, 2/13 ≤10 mm, 5/13 ≤20 mm; outside false-observed 1/11, outside correct
rejections 10/11; absent false-observed 0/2, absent correct rejections 2/2.

No private reasoning, continuous recording, new evaluation, clinical adjudication,
trial, visual acceptance or cross-condition performance claim is provided. The
[seven-chapter manuscript](../stories/br039-native-trace.story.md) uses discrete 168-frame
holds at 24 fps (49 seconds total); reading time is independent of recorded agent elapsed time.
