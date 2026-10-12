# BR-030 coronary native trace package

Recover the original Terra/high `attempt-1fd0ceae7bf0308d3f0a2562` from
[mapped source pins](canonical-mapping.md). This reader recipe extracts retained
bytes and builds bounded context displays. It never executes historical preparation,
`build_review_package.py`, the supplied scorer, CAS-Net inference or a model trial.
Canonical binding and independent visual review remain separate.

## Fresh recovery

```sh
.venv-br019/bin/python groups/tubular-anatomy/presentation/native-coronary-trace/prepare_trace.py \
  --output .local/anatomy-pose/coronary/FRESH-RUN
```

The destination must not exist and must be under `.local/anatomy-pose/coronary`.
Overwrite is refused. Existing NumPy/nibabel/Pillow/SciPy suffice; the exact saved
binary PLY layout has a read-only parser, so no trimesh installation is needed.
Output includes `data.json`, three exact delivery PNGs, notices/licenses/instructions,
`receipt.json` and a local `manifest.json`. Only an explicit
`--manifest groups/tubular-anatomy/presentation/native-coronary-trace/native-trace.json`
updates the owned tracked manifest after checks pass.

Mapping pins and all 18 original frozen task files are checked before derivation.
Raw sources, original artifacts and intervention records remain local provenance;
only display payload, exact deliveries and small disclosure files enter the player
asset bundle. Mapping/recipe are raw provenance; README/draft are pinned separately
by the canonical compiler, allowing timing edits or draft relocation.

## Native geometry and byte formats

- **Input:** whole supplied 366×319×205 CTA crop, affine/spacing, unchanged mask,
  exact binary editable region and supplied start/end/review RAS coordinates.
  Positive native axes are L/A/S; zero-based native centres map through the affine
  to RAS mm. This crop is source i=82:448, j=162:481, k=0:205; excluded full-CTA
  regions are provenance, not additional solver input.
- **Preview:** 128×112×103, nearest native integer samples from rounded
  `linspace(0,shape−1,count)`, with explicit endpoint-inclusive indices. Window
  −200..700 HU maps to rounded/clipped uint8. Bytes are C-order, gzip `mtime=0`,
  base64 encoded. Input poster is a whole preview coronal MIP over j, unmarked;
  i increases toward L horizontally, k upward toward S. This coarse display is
  context, not native-resolution repair evidence.
- **Masks and edits:** sorted native C-flat integer indices,
  `flat=((i*shape[1])+j)*shape[2]+k`. Input mask/editable indices are supplied data;
  observed added/removed lists come only from the original saved mask comparison.
  No intermediate repair mask is invented. The binary region, not its enclosing
  box or an analytic sphere illustration, determines edit permission.
- **Bounds:** half-open native array-cell endpoints `[lo,hi)`; physical edges map
  via `affine(index−0.5)`. Plane levels/ROI support and requested centres are actual
  logged selections. Inspection bounds do not become clinical segmentations.
- **Route:** original float64 `[371,3]` RAS coordinates as JSON numbers; eventual
  fourteen-point native ridge recovered as text from the step-38 patch. That ridge
  is a discrete later choice after alternatives, never an early search trajectory.
- **CPR:** original shape `[angle,route,offset]=[8,371,65]`; `hu` is float32 LE,
  `source_ras_mm` float32 LE `[8,371,65,3]`, C-order gzip/base64. Angles are
  0,45,…315 degrees and offsets −8..8 mm at 0.25 mm. Original `arc_mm` is retained
  verbatim. Source coordinates link each reader-selected sample through the inverse
  affine; reader navigation is not an observed solver screen recording.
- **Mesh:** original PLY vertex order and face order, positions float32 LE `[V,3]`,
  triangular indices uint32 LE `[F,3]`, both C-order gzip/base64. The exact saved
  layout is binary little-endian float XYZ and uchar-count/int face indices. No
  smoothing, simplification, coordinate replacement or face reordering occurs.

## Delivered images, choices and visible roles

The three exact embedded PNGs are step 17 axial, step 18 coronal and step 19
sagittal montages. Every decoded PNG SHA matches its committed mapping. Original
on-disk montage/script files are absent; authoring patches and delivered bytes
are retained. Step 14's missing `montage` command precedes the successful Pillow
implementation. No CPR or mesh screenshot was delivered to the solver.

The original overlays use **red** for supplied proposed mask and **green tint**
for editable-region pixels outside that mask, over grayscale CT at −200..500 HU.
Their transposes and 3× tile resize remain exact delivered pixels. Native reader
overlays need their own matching legend; supplied helpers, observed additions,
eventual chosen bridge and private reference must have distinct labels.

`contacts` is step 38's eventual chosen ridge after earlier printed alternatives.
Its chapter includes step 38 explicitly. Bridge geometry must not appear in
input/search; observed added voxels appear from saved repair/route onward. Exact
montage alternatives remain selectable as separate axial/coronal/sagittal states.

## Reference and derivation QA

Input/observed objects exclude evaluator results and corrected distance metadata.
The reference object retains original reward/stages and scalar numeric metrics,
plus the separately retained author-corrected arc and correction stages. Original
non-scalar/boolean metric values remain in the pinned complete verifier file.

The original frozen result passes repair, trace and mesh, while CPR distance-axis
consistency fails: reported arc ends 184.80925341171147 mm; cumulative saved-line
distance ends 175.91775513587936 mm. The post-outcome author package changes only
`arc_mm`. Other CPR arrays are equal and mask/line/mesh are byte-identical. Its
separate retained score passes; the original reward remains 0. No scorer was rerun.
These outcomes belong to the final reader-reference reveal.

Independent read-only QA checks centre-offset source RAS against saved route,
physical offset distances, and trilinear CTA sampling at the original stored
source coordinates using SciPy `order=1`, `prefilter=False`, constant −1024 HU
outside the native grid. Receipt reports errors/outside count and tolerances:
central/offset positions <0.00005 mm and HU p99 <0.05 HU. This validates byte/
source links, not a new grade. Mesh QA checks counts, index/physical bounds,
two-face closed edges, consistent winding and positive volume.

## Terms and limits

Exact task source notice/terms accompany the package, with retained Apache 2.0
legal text and new transformation disclosure. ImageCAS CTA listing declares
Apache 2.0; ImageCAS-X annotations/geometry CC BY 4.0; source code MIT. Preserve
separate attributions and source links. No endorsement or publication is implied.

Case 1 is a training-split development fixture. References derive from corrected
masks and are related geometry evidence, not independent clinical votes. Supplied
mask/sphere/endpoints remove much search; author image-guided and geometry-only
baselines are separate calibration. No lesion-specific stenosis/plaque truth,
clinical accuracy, population difficulty or new trial is established.

[Story](../stories/br030-native-trace.story.md): seven 168-frame holds at 24 fps,
1,176 frames / 49 s. Reading time differs from logged agent elapsed time.
Native geometry/asset closure checks do not establish visual acceptance; reference
hiding, controls, narrow layout, fallback and independent review remain required.

The reader also retains a **70×70×55 native-resolution CT detail** at crop origin
`[108,95,15]`: the union of all three logged montage supports plus ten voxels on
each side. It uses the same display window and no spatial downsampling. This is
a reader-generated local view, not an additional solver delivery. Whole-crop
context remains visible alongside it; raw HU/source-coordinate checks use the
original CTA, not display bytes.
