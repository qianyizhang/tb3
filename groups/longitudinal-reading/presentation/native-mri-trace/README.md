# BR-037 P03 neutral native MRI evidence package

Recover one retained Terra/high attempt, `attempt-6c8ee6d062c12e5b435afa42`, from
the [committed mapping](canonical-mapping.md). The recipe reads source bytes and
builds bounded reader previews. It does not execute historical preparation,
the solver's `analyze_mri.py`, the supplied viewer, scorer or a new model trial.
Canonical binding and visual acceptance remain separate.

## Fresh recovery

```sh
.venv-br019/bin/python groups/longitudinal-reading/presentation/native-mri-trace/prepare_trace.py \
  --output .local/anatomy-pose/mri/FRESH-RUN
```

Use the existing NumPy/Pillow/nibabel runtime. The destination must not exist and
must be under `.local/anatomy-pose/mri`; overwrite is refused. The output contains
`data.json`, three exact delivered PNGs, license/notice/instructions, derivation
`receipt.json` and a local `manifest.json`. Add
`--manifest groups/longitudinal-reading/presentation/native-mri-trace/native-trace.json`
only to update the owned tracked manifest after extraction checks pass.

The recipe validates mapping pins, all **134 frozen task files** and all
**122 supplied NIfTI files** against the freeze and existing source audit. Raw
volumes, workbooks, saved figures and executable method/scorer files are provenance
pins; the player bundles only display data, exact delivered images and small notices.

## Display geometry and roles

- **Whole input:** 122 neutral series across V1 day 0 and V2 day 34. The complete
  inventory retains per-series native affine, shape and file phase count. Scouts
  remain individual planes. Only sixteen selected dynamic grids get image previews;
  a preview subset does not establish exhaustive examination review.
- **Previews:** V1 128×128×53, V2 128×128×50, nearest native integer indices from
  rounded `linspace(0, shape−1, count)`. Explicit index arrays include all endpoints:
  i/j 0..511; k 0..105 for V1 and 0..99 for V2. uint8 bytes are rounded/clipped,
  C-order, gzip `mtime=0`, base64 encoded. No interpolation of source voxels occurs.
- **Window:** per visit, compute sampled 1st/99.8th percentiles for each of its
  eight dynamic grids; choose minimum lower and maximum upper endpoint. Apply
  that one fixed window to all eight grids. Receipt records every percentile and
  byte digest. The two visit windows are independent display scales, not MR signal
  calibration or evidence of biological signal change.
- **Input posters:** whole first-post preview coronal MIP over j; i increases
  horizontally toward R and k upward toward S. No target selection or solver/
  reference marks. Sixteen separate 3D files have dynamic ordinals 0..7 but file
  citation **phase=0**. No elapsed contrast timing is fabricated.
- **Native states:** actual logged planes, MIP slabs, focus windows, computational
  ROIs and saved bbox spans. Bounds are half-open array-cell endpoints; physical
  box edges use `affine(bounds−0.5)`. Full-precision selected NIfTI affine owns world
  positions; inventory preserves rounded supplied manifest metadata. Grids are
  explicitly unregistered. Inspection centres and saved citations retain their
  one-voxel differences.
- **Observed versus saved:** exact embedded PNGs at steps 15/18/22 are delivery.
  Final saved PNGs have different hashes/dimensions; they are separate provenance.
  Step 18's incorrect side labels were corrected in code at step 20; no later
  corrected projection delivery is recorded. Keep the delivered image and caveat.
  Red crosses in focus panels are solver-selected points, not ground truth.
- **Measurements:** preserve saved rounded component `bbox_mm` and numeric maximum,
  plus assessment's reported values separately. Bbox extrema are inclusive native
  indices. Method: sigma=1 voxel first-post subtraction, 30% local peak threshold,
  connected component containing local peak, largest voxel-edge axis span. A bbox
  span is not an adjudicated clinical longest diameter or tumor contour.
- **Reader reference:** frozen mechanical contract/reward, source FTV/diameter/pCR
  and earlier reproduction precision are a separate `reference` object. Source
  identity/VOIs/future outcomes are excluded from input/observed fields. Previous
  source-selected teaching crops and cue-method results are not intermediate states
  of this neutral attempt.

## Terms and remaining limits

Copy the retained I-SPY2 CC BY 4.0 notice in `DATA-LICENSE.txt` unchanged; the new
`SOURCE_NOTICE.txt` adds collection DOI, attribution and transformation disclosures.
The original collection/terms snapshot stays pinned. No endorsement is implied.
Generated image arrays/PNGs and reports stay ignored and local.

Mechanical `contract_pass=true`, reward 1 validates format/citation bounds only;
clinical accuracy was not scored. Source workbook diameter units remain unresolved.
Existing audit full-precision diameters are 21.25119972229004→20.0 mm (−5.887666%).
This recipe does not repeat the historical measurement. The forecast's confidence
0.43 remains its saved conditional claim; an always-smaller baseline also matches
all three neutral source directions. No clinical or population result is added.

Intermediate on-disk script/PNG revisions and calibrated injection/phase timing are
not retained; exact tool patches/observations are. A later `git: command not found`
shell tail does not erase the printed measurement output. No source registration,
clinical adjudication, new trial, browser review or publication occurs.

[Story](../stories/br037-native-trace.story.md): seven discrete 168-frame chapters
at 24 fps, **1,176 frames / 49 s**. Reading time differs from agent elapsed time.
Native geometry, reference hiding, controls, fallback and independent visual review
remain required before acceptance.
