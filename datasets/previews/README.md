# Dataset sample and reference snapshots

Every dataset page has a source-specific frozen snapshot or an explicit
acquisition gap. The snapshot appears before the optional conceptual diagram.
Images open in a zoomable viewer; ground truth and other source references require
an explicit reveal. A page reload closes that reveal.

The current collection contains 32 documented examples: 27 sample/reference
pairs, two image-only examples (PI-CAI and EchoSlicer), one reference-only example
(the generic AFIDs atlas), and two metadata-only source screens (CT-RATE and
ACRIN brain). There are 56 pinned PNG panels and four text panels. **Paired means
both artifacts are shown, not that every annotation is valid ground truth.**
The STS-3D mirror masks and MedPelvis3D landmark mapping remain disputed. NLST
shows a paired reconstruction; I-SPY2 includes clinical/functional measurements;
STRAUS shows simulator material identity. These are different reference contracts.

## Inspectable provenance

- [recipes.json](recipes.json) fixes the selected sample, source fingerprints,
  rendering method, scope and reference qualifications.
- [catalog.json](catalog.json) pins each frozen image and records source paths,
  derivation, captions and the renderer fingerprint. Native data are not embedded
  in this tracked manifest.
- [render.py](../../presentation/dataset-snapshots/render.py) reads only declared
  retained inputs. It checks their SHA-256 values before rendering and refuses
  to overwrite an existing snapshot file. It never imports historical authoring
  modules, changes a task freeze, downloads data, or runs a model.
- Generated PNGs live under `presentation/tours/data/dataset-snapshots/` and stay
  local. The standalone Task Explorer embeds the pinned PNG bytes, so its viewer
  does not require native scans or a medical runtime.

Masks are shown on matched image grids. Point coordinates are transformed through
source affines. RAS-oriented voxel views retain physical pixel aspect. EchoSlicer
uses its retained calibrated Cartesian planes; its raw polar axes must not be
treated as Cartesian millimetres. Crops, reference-selected slices, display
windows, collapsed classes and phase choices remain beside each image. Colored
reference marks have matching legends. Source predictions are not substituted for
ground truth; published reconstruction outputs remain separately labeled.

## Build and verify

The ordinary explorer build reads the small manifests and frozen PNGs, never the
native source volumes. A changed PNG fails its fingerprint check. An absent PNG
produces an explicit missing-snapshot notice and is listed by `med brief check`.
Native data absence does not prevent an available frozen snapshot from rendering.
The root catalogue requires every dataset to have a preview record, including
explicit unacquired or reference-only cases.

To deliberately regenerate local previews with an already installed imaging
environment, choose a **fresh** output directory:

```sh
.venv-br030/bin/python presentation/dataset-snapshots/render.py \
  --output presentation/tours/data/dataset-snapshots/new-review
# Inspect the images and captions before promoting the resulting manifest.json
# to datasets/previews/catalog.json. Retain the old frozen output directory.
uv run med brief build --output .local/dataset-explorer/index.html
```

The rendering environment used here already contained NumPy, Pillow, nibabel,
SciPy and Matplotlib. Rendering is an explicit preparation operation, not a side
effect of `med check` or page navigation. No new model or acquisition was run.
