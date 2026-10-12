# Named landmarks: retained partial-CT trace mapping

**Selected on 2026-10-12:** BR-039 Terra/high partial CT,
`attempt-824eaf2afb12f840a722b998`, run `ct-partial__DeU639y`. Native CT, geometry,
42-step trajectory, ten delivered images, saved coordinates/statuses and frozen
verifier details are available. This investigation reads and hashes retained bytes;
it does not execute a trial, scorer, image recipe or new visual acceptance review.

## Existing story and selected condition

Entry `tb3-named-landmarks` belongs to **anatomical-landmarks**, although campaign
inventory groups it under `tb3-research` / P0. Its current
[story](../stories/named-landmarks.story.md) uses `named-landmarks-v1` and
`retained-named-landmarks-v1`. It already has real source sections, saved outputs,
coordinate conversion, reference reveals and multiple conditions. Its search
chapter explicitly labels k=857..917 navigation as teaching navigation, not an
agent trajectory. That distinction should remain; the retained trace below adds
observed operations and their source-volume extent.

Use the [brief](../briefs/tb3-named-landmarks.md),
[source audit](../sources/named-landmark-audit.json),
[terms](../sources/named-landmark-source-terms.json),
[finding](../../findings/landmarks-availability-and-localization.json) and
[variant idea](../../ideas/variant-vertebral-numbering.md) as dependencies. Their
existing all-visible-target denominators, wrong-level interpretation, correlated
full/crop subjects and reference limits remain authoritative.

This attempt is a useful process witness because the solver built native sagittal,
coronal and axial inspections, computed image-based centres, and submitted an
in-FOV point with the wrong level name. It is **one cropped VerSe sub-verse823
condition**, not a replacement for the entry's other ten model attempts.

## Source identity and roles

`T = runs/br039-ct-landmarks/tasks/ct-partial/`

`R = runs/br039-ct-partial-terra-high-v1-20260917/ct-partial__DeU639y/`

All paths in this table use those exact repository-relative roots. SHA-256 and
sizes were recomputed from current local bytes, including the large volumes.

| Role | Relative path | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Native input array | T `environment/volume.npy` | 482,345,088 | `9d800b5afb3dda6d2b6b4d7ebafd5f91bacb0fcc9b351982232df362df55c1d5` |
| Native image/affine | T `environment/volume.nii.gz` | 332,820,651 | `d0820fce2984ab65448fed1fea8b41b88b739468fe46677ee9147f05de680439` |
| Supplied geometry | T `environment/geometry.json` | 1,004 | `8aa4dfd5e420440b2c74f34672bdf7e72b27a6d21cf169c5d25488fc6780b62c` |
| Supplied inspection helper | T `environment/volume_tools.py` | 3,121 | `9e45612aae89c572509492807b4323ee8027201c69b3a3336faff4ff18a0f058` |
| Names/definitions | T `environment/landmarks.json` | 4,040 | `c01dd5b1366b3b6d5c16b997c4549ccf8a8610c60da357ab0d3fd4301404167a` |
| Frozen instructions | T `instruction.md` | 2,757 | `48d4dfa2accae7922cbc54a9f7d9b5dc9d266bb1028cd5fb98544197d267d830` |
| Actual observations | R `agent/trajectory.json` | 10,514,360 | `d2c5338c2eac8ffa249a193aac09ba6a4aaa0bc5224340190f6cf9bd9b6837d4` |
| Saved coordinates/statuses | R `artifacts/app/answer/landmarks.json` | 1,265 | `3e7ab43535874c35152d1830af7b55dedb73ebfc52d7726de5331f3a5636cdfe` |
| Saved solver account | R `artifacts/app/answer/evidence.md` | 725 | `fa8bc02a6b5f35df4c6db6c978d6103883076be9e372b1bb09d0911398aab991` |
| Private reference | T `tests/truth.json` | 4,681 | `3de07e775860f7cbf10f11a66666cda62dfc0b5e26f4186f402f651f22de585e` |
| Private evaluator | T `tests/score.py` | 3,248 | `10dd7d5417180e95d8f98f677904a0136a772dbee5f14d4b34e9d2fc3c1b9ef4` |
| Frozen result | R `verifier/details.json` | 5,455 | `2fbb5abae1bf6add106a90ec030d74e4cdc7c8302b774d644f4e3651d7a62a47` |
| Attribution/terms notice | T `environment/SOURCE_NOTICE.md` | 408 | `91188f8f2a43b8bf02b5e02914c44d7b47d8afdb17e8d5e1b0a9a1769ed4ddd1` |

The separately retained BR-040 reproduction copy of this earlier attempt has
`.local/inputs/reproduction/anatomical-landmarks-br040/saved/attempt-824eaf2afb12f840a722b998/expected.json`
(5,456 B; SHA-256 `2b99324b6fd48aafc0a1efda77adfb6980d77b7d7ca362b52c1e33424b86800d`).
It is a replay expectation, not another model attempt or the original result file.
The original result is `details.json`; **`verifier/metrics.json` is absent**.

## Delivered image closure

Images are present as base64 PNGs in trajectory observations; original work PNGs
and `inspect_spine.py` are not in the retained `artifacts/app` tree. Extract exact
embedded bytes for packaging; do not regenerate them and call the result delivered.
Every image below is `steps[step_id].observation.results[0]`, decoded content item
**1** (`input_image`). The locator is by `step_id`, not list position.

| Step | Actual requested view | Decoded bytes | PNG SHA-256 |
| --- | --- | ---: | --- |
| 11 | `overview.png`, centre (256,220,460) | 859,926 | `e3e1b8a262d565d0a942cedc904dce9434ac6219771c7aca65f97fcdf31b617e` |
| 15 | `spine_mid.png`, (256,85,650), radius 180 mm | 933,290 | `9c6100c1cc8531e4fab1bdd105924bfd26c6ce4caaa300582c84f26dc08c4062` |
| 17 | `spine_body.png`, (256,135,650), radius 180 mm, window 0..1800 | 790,918 | `c5de0b2aea26a27fb283d89a379a44e6d6f7ee49f4a9b572dc20af676706c2a5` |
| 20 | Sagittal native i=246,256,266; j<260; k=380:920 | 960,688 | `8ee89b99a0c85bce139179c700097544ac9dc90326a617dab162e664e3f85646` |
| 22 | Coronal bone MIP through j=70:180, k=380:920 | 660,164 | `ddcec1f064436d3ba688b476015d9b099939e1cb03170b4374d318cadae27fa8` |
| 24 | Sagittal MIP through i=242:270, j<230, k=380:920 | 335,433 | `750f198d5fdf1cafca909fd7ab9f536aeec71cd9ca34a356efecad2ce0d11487` |
| 27 | Axial montage at fourteen candidate body levels | 2,367,142 | `e522c56394cae209285122d28810bdcc16c1b743b09c68c697ce60360089d6e1` |
| 29 | L5 check, (248,220,450), radius 45 mm | 236,678 | `0dcffc9fe6a0513d5f1ab40205e6392661b97eb5e4551653d6053ed0203db289` |
| 30 | T4-labelled check, (262,155,910), radius 35 mm | 154,297 | `a9b68f40a41c6929ca9e741c01b5dc47222a356031cdd2a0a594586d4f078493` |
| 33 | Lower axial k=639,603,565,526,487,450,415 | 524,637 | `04469bf244fc90be00dc19ba2e3a8b079ec20bb32b2bd0335ee02ca7c3f4ae67` |

Step 9's initial view-and-open failed because its image was not yet available;
steps 10–11 succeeded. Step 31's inline centre calculation had a Python syntax
error; steps 34–37 supplied a functioning script. Neither event is a failed
medical trial or a new result. Retain these boundaries if those calls are excerpted.

## Native whole-volume link

Supplied crop shape is **512×512×920**; array access is `volume[i,j,k]` with zero
base. The NPY/NIfTI intensity identity was verified by the existing source audit.
Geometry maps indices to RAS mm:

```text
x = 181.640625 − 0.71875 i
y = −7.140625 + 0.71875 j
z = −1546.11474609375 + 0.70001220703125 k
```

Positive native axes are L/A/S. Native centres span 0..511, 0..511, 0..919;
voxel-cell FOV extends half a voxel beyond them. The crop is source k=0:920 from
an available **512×512×1214** full CT (`runs/br039-ct-landmarks/tasks/ct-full/environment/volume.npy`,
636,485,760 B). That full CT was **not this attempt's input**. Display its excluded
cranial region only as separately labeled source/reference context with separate
pins; do not give the reader impression that the solver saw it.

A shared landmark adapter can connect every requested delivered view/slab to the
supplied crop using exact native plane or slab bounds. Reader-selected MPR and
window controls remain separate from logged inspection centres. Cyan helper
crosshairs denote requested inspection locations, not detections. Saved landmarks
are fractional native points; world positions, all slice overlays and printed
coordinates must derive from the same affine. Use a bounded display preview for
whole-volume context and native sections for precise inspection; the 482 MB NPY
cannot enter the general catalogue bundle. Derived preview sampling/windowing,
selected image extraction and fallback require new local receipts before binding.

## Seven discrete chapters

Proposed reading-time intervals: **120 frames each at 24 fps, 840 total**. Holds
are presentation timing, not elapsed agent time. Do not interpolate an invented
search path, detection history or vertebral numbering correction.

| Frames | Chapter | Observed steps | Native state / reader interaction |
| --- | --- | --- | --- |
| 0–119 | Receive crop and names | 7,12 | Whole supplied crop, 26 definitions, index/affine contract; no target locations |
| 120–239 | Inspect long views | 10–11,14–17 | Delivered overview and two spine views; place exact requested centres/radii in crop context |
| 240–359 | Compare bone projections | 18–24 | Actual sagittal planes and two MIPs; reader toggles plane versus slab, with native slab bounds |
| 360–479 | Check candidate levels in depth | 26–30,32–33 | Fourteen axial levels plus local/lower checks; selected k list is logged, not a reference inventory |
| 480–599 | Compute image centres | 34–37 | Logged 2D and 3D intensity-weighted centres in tight ROIs; label as solver cross-check, not GT segmentation |
| 600–719 | Save positions and availability | 39–41 | Actual JSON: T4 observed [269.8,154.6,906.1], T13/L6 absent, C1..T3 outside; distinguish contract validation from localization correctness |
| 720–839 | Reveal source and frozen outcome | Private truth/details, existing audit | Saved T4 point versus true T5 [269.7,156.0,908.8]; true T4 [273.0,165.4,937.6] outside crop; reveal source labels and separate localization/availability denominators |

The final reference reveal can cite the existing audit's **2.142 mm** T4-claim to
source-T5 separation. Preserve frozen endpoints: **1/13 within 5 mm, 2/13 within
10 mm, 5/13 within 20 mm**; outside false-observed **1/11**, correct outside
rejections **10/11**, absent false-observed **0/2**, absent rejections **2/2**.
These are saved results; no reevaluation occurred here. The solver's submitted
`evidence.md` claim that the visible column starts at T4 must be presented as its
claim alongside the later reference interpretation, not endorsed narrative.

## Gaps, disputes and integration boundary

- **No hidden cognition:** selected calls, observations and centre outputs are
  available; no continuous screen recording or private reasoning is asserted.
  Weighted centres use threshold >100 and weights clip(intensity,100,600)−100;
  their selected ROIs/level names are solver-authored, not reference locations.
- **References:** VerSe centroids and source availability convention are engineering
  references. T13/L6 absence has source-supplement support, not merely missing
  annotation rows. Variant numbering remains untested. No new clinical dispute or
  reference invalidation was demonstrated by this read-only investigation.
- **Other conditions:** AFIDs rater uncertainty and the missing BR-040 runtime
  atlas image remain documented entry-level limits; neither affects source
  availability for this CT-only slice. Sol partial-CT visible-T5 miss is a separate
  attempt and should not be staged as this Terra attempt's intermediate state.
- **Adapter gap:** existing CT-pose adapter's four rigid planes and MRA adapter's
  mask components do not represent named point/status output or inspection slabs.
  Add a typed landmark projection: input geometry/names, observed per-step views
  and logged centres, saved status/point map, and separately gated private
  point/status/error map. Reference-centred panels and segmentation masks stay
  reference-only. Reuse shared player, source pins and asset-closure packaging.
- **Acceptance remains open:** no prototype or derivative payload was generated
  here. Exact-image packaging, geometry inspection, reference hiding, mobile,
  keyboard and fallback checks remain required before canonical binding. Retain
  VerSe CC BY-SA 4.0 attribution, ShareAlike and derivative disclosures; source
  code's MIT license is separate from patient-image terms.
