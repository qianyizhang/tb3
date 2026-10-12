# Coronary repair, route and CPR: retained BR-030 trace mapping

**Selected 2026-10-12:** tubular-anatomy entry **`ours`**, BR-030 coronary-cpr,
Terra/high attempt `attempt-1fd0ceae7bf0308d3f0a2562`, run
`runs/br030-coronary-cpr-terra-high-v1-20260916/coronary-cpr__qQLEAkL`.
All **18 frozen task files** match their original hashes. The native image/prediction
crop, exact delivered montages, original four-output package and frozen scores are
available. Mapping only: no historical code, scorer, model, browser or asset build ran.

The entry currently uses [route-unfold teaching](../stories/route-unfold-teaching-v1.story.md),
a synthetic branching phantom explicitly separate from solver strategy or patient
results. Use this retained witness to propose a source-backed enhancement, preserving
the existing [brief](../briefs/br030.md), [protocol](../../experiments/br030/protocol.md),
[idea](../../ideas/idea-coronary-route-cpr.md),
[historical results](../../../../docs/research-rounds/BR-030-results.md) and
[input/helper visual receipt](../briefs/br030-visuals.json). BR-041 named-coronary
and BR-042 inventory are different discovery/identity tasks; their attempts are
not this supplied-mask repair witness. The idea remains parked for new trials.

## Exact source pins and roles

`T = runs/br030-vessel-geometry/tasks/coronary-cpr/`

`R = runs/br030-coronary-cpr-terra-high-v1-20260916/coronary-cpr__qQLEAkL/`

`C = runs/br030-vessel-geometry/geometry/terra-arc-correction/`

Current local SHA-256 and byte counts were recomputed. The frozen task checksum is
`44dbf1bed3d74f74406f1624570304db305da7a1c677b3267bc8c8bb067978eb`.
Task/attempt/original output, evaluator reference and post-outcome intervention
are distinct roles. The trial is one natural attempt, not its oracle or no-op control.

| Role | Exact repository-relative file | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Frozen instructions | `runs/br030-vessel-geometry/tasks/coronary-cpr/instruction.md` | 4,562 | `2b8b5d7f41c1c31f1e841e795a857b41f8a95434bca385ff5c7ce9056c61b7bb` |
| Supplied route/CPR request | `runs/br030-vessel-geometry/tasks/coronary-cpr/environment/data/request.json` | 1,321 | `1d63d98bf1b6e506ee34b2f8afd718bd971a588c095a81e9cb9e7a1108dbd6b7` |
| Native supplied CTA crop | `runs/br030-vessel-geometry/tasks/coronary-cpr/environment/data/image.nii.gz` | 30,804,791 | `cb57cf4b0d40d89976359fc5c831cfb003f16f24eaf5c31ad457d00da8c85432` |
| Unedited supplied predicted crop | `runs/br030-vessel-geometry/tasks/coronary-cpr/environment/data/proposed_mask.nii.gz` | 125,258 | `5f7036f84e8688c70ead0800684c72fc9b13759278a224bc4f7b4dd51289a011` |
| Supplied editable region | `runs/br030-vessel-geometry/tasks/coronary-cpr/environment/data/editable_region.nii.gz` | 109,946 | `02fe621bf816238eb197c66210fb51253e885781138203ce1301babea9e9f4d6` |
| Exact source notice | `runs/br030-vessel-geometry/tasks/coronary-cpr/environment/SOURCE_NOTICE.md` | 862 | `c0d5c28cc04e6f66a32ba7259f3c3666fb0d2dffece1e70af51af38340f0d3c5` |
| Exact source terms/code license | `runs/br030-vessel-geometry/tasks/coronary-cpr/environment/DATA-LICENSE.txt` | 1,411 | `7a3bcd40f7b57fe240d475a3b896f5f1c524a43d50a8b0bb7201c5f1e93d52d0` |
| Original private reference | `runs/br030-vessel-geometry/tasks/coronary-cpr/tests/reference.npz` | 30,157,565 | `837ccda884c775e58558ce6110e8a41902c1fcc985e7f6fbc11ad80e1259a3a5` |
| Original scorer (read only) | `runs/br030-vessel-geometry/tasks/coronary-cpr/tests/score_geometry.py` | 7,824 | `90f918e75d242fa065fcf950c6172006e9f398d1742dcd7e7c609362cd8c9b4e` |
| 18-file task freeze receipt | `runs/br030-vessel-geometry/freeze.json` | 2,469 | `eda2e99f7ec3ab1fc476f9829702a30868e71bd8a79dbf4019acec0ff78515c2` |
| Original attempt identity | `groups/tubular-anatomy/experiments/br030/attempts/attempt-1fd0ceae7bf0308d3f0a2562.json` | 271 | `c32f6a9b51c96b967e4d5affb390ba6ee65a4324b4362c55eb8044fdf06bab62` |
| Actual trajectory | `runs/br030-coronary-cpr-terra-high-v1-20260916/coronary-cpr__qQLEAkL/agent/trajectory.json` | 1,639,664 | `4555eee38201527daf5e6f746e92815126a4ab93dd121114d4b63065671aeb97` |
| Original trial result | `runs/br030-coronary-cpr-terra-high-v1-20260916/coronary-cpr__qQLEAkL/result.json` | 4,020 | `a8666365a72dae02c0654d68c8cf546a63c70f7fc63a1fdd3942c74b58af0b44` |
| Frozen original scores | `runs/br030-coronary-cpr-terra-high-v1-20260916/coronary-cpr__qQLEAkL/verifier/metrics.json` | 1,405 | `adb52551d6703c9874f8715429952b4399ac38cd6bbba0f38c5689bafed39651` |
| Original reward | `runs/br030-coronary-cpr-terra-high-v1-20260916/coronary-cpr__qQLEAkL/verifier/reward.txt` | 2 | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` |
| Original saved mask | `runs/br030-coronary-cpr-terra-high-v1-20260916/coronary-cpr__qQLEAkL/artifacts/app/answer/corrected_mask.nii.gz` | 125,347 | `8c9adb361e0b69aef6d979ddbe9142d3f59739c5ec36ee62207938d8e6e3ccd5` |
| Original saved centerline | `runs/br030-coronary-cpr-terra-high-v1-20260916/coronary-cpr__qQLEAkL/artifacts/app/answer/centerline.npy` | 9,032 | `b0a3dfd3dc3e08d696ca7f53916c79a4797e368b32d608965c9c5adc9c4362e1` |
| Original saved CPR archive | `runs/br030-coronary-cpr-terra-high-v1-20260916/coronary-cpr__qQLEAkL/artifacts/app/answer/cpr.npz` | 2,559,450 | `1bc04e90323804171b4d251d752d6a2482a31d444ad10086e081362e9709f72f` |
| Original saved mesh | `runs/br030-coronary-cpr-terra-high-v1-20260916/coronary-cpr__qQLEAkL/artifacts/app/answer/vessels.ply` | 1,372,979 | `e1f7bb1dc5788729580b5f9dea6fa0e0133c705ab15db0e0658481a42bcb51de` |
| Retained build-code tool patch | `runs/br030-vessel-geometry/terra-authored-patch.txt` | 9,863 | `d815247fffc74e1ce0b0b328b7df92e6ef8e280f15f8b4e45ee4df8e1bd69fb4` |
| Source/curation receipt | `docs/evidence/br030-sources.json` | 22,460 | `4b7ff0b6d3e640a683e9a3023188b613e06f8fdbc135ccdae8b34ba91360052a` |
| Prior results/interpretation receipt | `docs/evidence/br030-results.json` | 19,171 | `503917f47d34ea6272e45247abe31b91e32f7e0405f30bd4d8a6e4d194ce8baa` |
| Pretrial author geometry/crop receipt | `runs/br030-vessel-geometry/geometry/build-receipt.json` | 1,687 | `40f83fe96e58786f390f72b8aa1619bff565ccfecfd900baa3382ad79ab0aa00` |
| Full source CTA, not supplied whole | `runs/br030-vessel-geometry/sources/coronary/original/1.img.nii.gz` | 95,770,776 | `c020b1244ac6c841924e27c3f5c328e6cf1eefb70bc14d3b725959ed99b656ff` |
| Full prediction, not supplied whole | `runs/br030-vessel-geometry/predictions/coronary-1-casnet.nii.gz` | 83,620 | `763ad08523bb8423c4ba995d38476a2aa5001a2c2afef623c4e6fecd095d0ce9` |
| Post-outcome intervention receipt | `runs/br030-vessel-geometry/geometry/terra-arc-correction/intervention.json` | 540 | `c8b9e11ef57f3607e453bd5fc188574e90a4cee08e0f1dc7b7dc463ae4261b3c` |
| Post-outcome corrected CPR | `runs/br030-vessel-geometry/geometry/terra-arc-correction/cpr.npz` | 2,560,277 | `bcbedc50e12d485fecdbf9734d241ad5fc9f17cbfb89bad2052af86f0dec9e32` |
| Post-outcome separate score | `runs/br030-vessel-geometry/geometry/terra-arc-correction-score.json` | 1,403 | `6364fdd66cc654fe166845914751cbe53b7dc8bf7da37cab36e2c54fde688c0d` |

## Full source, whole supplied crop and local inspections

**Supplied crop:** 366×319×205 native `[i,j,k]` centres; zero-based array access.
Image, proposed mask and editable region have exactly the same affine and spacing.
Positive native axes are **L/A/S**, even though the instruction calls array axes XYZ.
World coordinates are **RAS mm**; anatomical laterality must follow the affine.

```text
R = 30.4013671875 − 0.376953125 i
A = 127.2548828125 + 0.376953125 j
S = 39.45000076293945 + 0.5 k
```

Spacing is 0.376953125, 0.376953125, 0.5 mm. Native centre indices extend
0..365 / 0..318 / 0..204; physical voxel-cell FOV extends half a voxel beyond.
Plane/slab/ROI bounds should be native half-open `[lo,hi)` endpoints, mapping box
edges via `affine(index−0.5)`.

The complete source CTA and full CAS-Net prediction are 512×512×275. The supplied
packet is the unresampled source slice **i=82:448, j=162:481, k=0:205**, with source
index = crop index + `[82,162,0]`. This mapping compared both retained full-volume
crop arrays to delivered image/prediction arrays: exact intensity/mask identity.
The excluded source regions were not supplied to this attempt. Native context
must show the entire supplied crop, not silently grant the full source scan.

The supplied helpers remove much discovery:

| Helper | Actual supplied coordinate / constraint |
| --- | --- |
| Start | RAS `[−13.7021484375,204.5302734375,104.44999694824219]`; crop ijk approximately `[117,205,130]` |
| End | RAS `[−48.7587890625,181.5361328125,56.44999694824219]`; crop ijk approximately `[210,144,34]` |
| Review centre | RAS `[−23.24529057460036,176.1031639511294,60.71575839132392]`; crop ijk `[142.31652215,129.58714996,42.53151526]` |
| Edit boundary | Supplied binary region, 8 mm review sphere; retain exact mask membership rather than replace it with a rendered analytic sphere |
| Requested route | RCA ostium → distal R-PDA; nearby branches must remain preserved |
| CPR | Eight angles 0,45,…315 degrees; 65 offsets −8..8 mm at 0.25 mm; stored HU, source RAS positions and cumulative saved-centerline distance |

Whole-crop inspection precedes local review. Step 9 observes three proposed-mask
components (12,718 / 21,133 / 477 voxels); start/end lie in distinct components
1/3. The review centre is outside the proposed mask with 169 HU. Step 10's
editable-mask occupied native bbox is inclusive `[122,109,27]`..`[163,150,58]`;
this bbox is context, not permission to edit its non-region voxels.

## Observed operations and exact deliveries

The trajectory has **43 steps**. Selected actions/observations are public trace
records, not a continuous recording or private reasoning account. No output CPR
or mesh rendering was delivered to the model in the retained trajectory.

| Steps | Actual action / observation | Native state and qualification |
| --- | --- | --- |
| 7,9–10 | Read request/notice, image/mask/region geometry, components and nearest boundaries | Entire supplied crop and helpers; nearest component pair is not automatically an anatomical bridge. |
| 11–16 | Sample a candidate line, author local inspection script and montages | Native local slices and CT/proposed-mask/editable overlays. Step14 fails because ImageMagick `montage` is absent; step15 adds a Pillow montage implementation and step16 succeeds. This is tool availability, not medical failure. |
| 17–19 | Open axial/coronal/sagittal local montages | Exact three image deliveries below; actual sequential slice ranges and ROI bounds retained. |
| 20–24 | Print HU distributions, skeleton endpoints and candidate distances | Quantitative image/mask checks; editable non-mask median −66 HU; proposed-mask components/nearby endpoints retained as hypotheses, not reference labels. |
| 25–30 | Inspect high-HU local components and sample potential bridges | Native intensity-guided local alternatives; preserve selected calls and their observations instead of inventing continuous point motion. |
| 31–36 | Compare HU-weighted local paths, endpoint neighborhoods and cross-sections | Step31 searches from `[142,130,43]` to components1/3 with coefficients1,2,4,8. Selected bridge is later explicitly written; no intermediate repaired masks were retained. |
| 38–39 | Write/run complete review-package method | Four original saved artifacts; chosen 14-point voxel bridge, 0.9 mm physical envelope restricted to editable voxels with CTA≥100 HU, 103 additions. Skeleton physical shortest path, endpoint-exact resampling, parallel-transport CPR and world mesh. |
| 40–42 | Inspect saved route/CPR shapes, mesh properties and edit preservation | Actual saved outputs; printed start/end, point steps, original `arc_mm` ending 184.809253 mm, mesh closure/winding and 103 edits outside 0. Frozen verifier is separate. |

The recorded local montage recipe (step12, amended step15) uses the same three
input arrays. It transposes native sections, maps CTA with `(HU+200)/700` clipped
and cast to uint8 (window **−200..500 HU**), then resizes each tile 3×. Red `[255,40,40]`
replaces proposed-mask pixels; green channel is raised to at least 180 for editable
pixels outside the proposed mask. Reader legends must match that color/role meaning.
These are supplied-mask/review overlays, not detections or reference masks.

| Delivery | Actual native slice sequence | Half-open inspection support |
| --- | --- | --- |
| Axial/z | k=34..54, i=118:168, j=105:155; 7 columns, 21 tiles | `[118,105,34]`..`[168,155,55]`, axis2; exact k list |
| Coronal/y | j=112..144, i=118:168, k=25:60; 7 columns, 33 tiles | `[118,112,25]`..`[168,145,60]`, axis1; exact j list |
| Sagittal/x | i=128..157, j=105:155, k=25:60; 6 columns, 30 tiles | `[128,105,25]`..`[158,155,60]`, axis0; exact i list |

Exact PNGs are embedded at `steps[step_id].observation.results[0].content`, decoded
item1 (`input_image`); locate by `step_id`, not trajectory list position. They were
decoded/hashed in memory, not extracted into new files:

| Step | Requested path basename | Result/item | PNG dimensions | Decoded bytes | PNG SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| 17 | `z_montage.png` | 0/1 | 1050×450 | 335,534 | `a2e53580318de80899002dbc0f47e553ae07b00914a495213da9dfed698644b8` |
| 18 | `y_montage.png` | 0/1 | 1050×525 | 411,436 | `e05d1d7ab5d1adb66928f9f290c36a3549589cbd2307fbaeeb43026b825be94c` |
| 19 | `x_montage.png` | 0/1 | 900×525 | 383,372 | `bbe7544ff7d74287e0a8446fe20b52ceded4cfee803a80373517359393791511` |

The original local PNG files, montage files and `inspect_local.py` are absent from
retained `artifacts/app`; exact embedded deliveries and authoring patches are present.
`build_review_package.py` is also absent as a plain artifact. Its full source remains
in trajectory step38 and separately in `terra-authored-patch.txt`; read/recover it as
text, never execute it merely to inspect this attempt. No continuous optimizer or
search history should be fabricated from the selected states.

## Saved outputs and source-coordinate linkage

**Original saved mask** shares the input shape/affine. Frozen results show local
Dice 0.944812, recall 0.910638, 103 changed voxels, zero far additions; logged checks
show zero edits outside the binary region and components 3→2. These are one-fixture
engineering observations, not whole-population repair or clinical accuracy.

**Original centerline:** float64 `[371,3]`, ordered RAS points with exact supplied
start/end. Step40 prints consecutive point lengths 0.308920..0.499484 mm. Final
method skeletonizes the repaired mask, finds a 26-neighbor shortest path weighted
by physical spacing, replaces endpoint coordinates by landmarks, and interpolates
at a nominal 0.5 mm grid. The 14-point local bridge in step38 is:

```text
[136,130,44], [137,130,44], [138,130,43], [139,130,43],
[140,130,43], [141,130,43], [142,130,43], [142,130,42],
[143,130,42], [144,130,42], [145,129,42], [146,128,41],
[147,128,41], [148,127,40]
```

This is the solver's chosen ridge, not a reference centerline. Display it as a
discrete logged choice. Do not reconstruct masks for earlier alternative paths and
call them delivered intermediate states.

**Original CPR:** `hu` float32 `[8,371,65]`, `source_ras_mm` float32
`[8,371,65,3]`, `angles_deg` float64 `[8]`, `offsets_mm` float64 `[65]`,
`arc_mm` float64 `[371]`. These are genuine sampled curved planes, not MIPs.
Every reader-selected CPR pixel should link to its retained source RAS coordinate
and native index using the inverse affine. Every central sample belongs to the
same saved centerline. Reader angle/position controls are reader navigation;
no model CPR screenshot or model review of that navigation is asserted.

**Original mesh:** binary PLY in RAS mm, logged 36,128 vertices  / 72,248 faces,
closed and winding-consistent. It contains both coronary trees for spatial context.
Step38 uses zero-padding before marching cubes, removes padding from indices and
applies the affine, then fixes winding/normals. Any later display simplification
must be labelled and preserve full mesh as a separately pinned output; visual
sampling is not the original surface verifier.

## Frozen original result versus author intervention

Frozen reward is **0**, stages **repair=true / trace=true / CPR=false / mesh=true**.
All thresholds were supplied before the run. Original metrics include:

| Endpoint | Frozen observation | Scope |
| --- | --- | --- |
| Trace reference coverage | 100% within 0.8 mm; p95 distance 0.499599 mm | Agreement with this mask-derived route reference |
| Saved centerline length | 175.9177551358793 mm | Cumulative Euclidean distance along saved points |
| CPR source-coordinate error | Maximum 0.0000085293 mm | Coordinates agree with saved route/frame |
| CPR HU error | p99 0.00161743 HU | Retained source sampling agrees |
| Mesh | Closed; surface p95 approximately 0.0000038147 mm; volume ratio 0.977911 | Geometry versus saved corrected mask, not anatomical independence |

The check named `cpr_coordinates` also includes distance-axis consistency. Here the
failure is the original **`arc_mm`** array: its endpoint is 184.80925341171147 mm,
while saved-centerline cumulative distance ends 175.91775513587936 mm, a maximum
8.891498275832106 mm discrepancy in the retained intervention receipt. Interpolation
cuts skeleton corners, so the old skeleton arc grid cannot be used unchanged as
cumulative distance of the saved polyline. This is a software-consistency miss,
not evidence of wrong-branch tracing, fabricated HU or anatomy.

**Post-outcome author correction is separate:** C replaces only `arc_mm`. This
mapping compared retained arrays/bytes: `hu`, `source_ras_mm`, angles and offsets
are identical; corrected mask, centerline and mesh are byte-identical to original
saved outputs. Its separate retained score passes all stages. No scorer replay was
run now, no new model attempt occurred and original reward 0 remains preserved.
The existing brief's displayed CPR comes from this corrected author package;
it must not be called an image delivered to this original agent or an original pass.

Oracle, image-guided author and matched geometry-only repair/trace baseline passes
are separate calibration evidence. The supplied mask, review sphere and anchors
remove much search. They do not establish difficult anatomical discrimination.

## Source/reference boundaries and terms

- **Input:** CTA crop, unchanged CAS-Net mask crop, binary edit region, requested
  route landmarks and reproducible CPR specification. Parent/full-source CTA is
  provenance, not extra solver-visible input.
- **Observed:** exact tool actions, local supplied-mask overlays, printed paths/HU
  checks and saved artifact inspections. No hidden reasoning or uninterrupted video.
- **Saved:** original four outputs only, with original distance metadata intact.
- **Reader reference:** private `reference.npz`, source ImageCAS-X annotations,
  frozen score, author baselines/oracle and post-outcome distance correction. Gate
  these independently; never use corrected/GT paths as early solver states.

ImageCAS case 1 is in ImageCAS-X's **training split**. Source receipt reports excellent
image quality/right dominance, but no lesion-specific stenosis/plaque ground truth.
The natural internal RCA→R-PDA prediction gap was sourced before the run: prior
screen describes approximately 4.98 mm sampled gap, versus 94.14% global Dice.
Reference centerlines/surfaces derive from corrected masks, so they are related
engineering references rather than independent anatomical votes. No separate
second-rater masks were found in the retained archive inventory. No population,
held-out prediction or clinical diagnostic performance claim follows.

Preserve exact `SOURCE_NOTICE.md` and `DATA-LICENSE.txt`: ImageCAS CTA listing
Apache 2.0; ImageCAS-X annotations/derived geometry CC BY 4.0; source code MIT.
Keep separate licenses/attributions and transformation disclosures. Dataset source
lookup is explicitly discussed in original instructions; no new external retrieval
or source-case audit ran here. Training exposure remains unknown. No new download,
trial, source inference or publication is implied by preparing a reader package.

## Proposed discrete chapters and next bounded action

Seven 168-frame holds at 24 fps (1,176 frames / 49 s), subject to readability review.
These are presentation holds, not agent elapsed time or an interpolated search path.

| Chapter | Actual source steps | Native state / role |
| --- | --- | --- |
| Receive crop and helpers | 7,9–10 | Entire supplied native CTA/mask, sphere membership and supplied endpoints; no private reference. |
| Inspect local planes | 11–19 | Exact three montage deliveries with sequential native plane support and overlay legend; missing `montage` tool boundary. |
| Compare possible connections | 20–36 | Printed component/HU/path alternatives and eventual explicit 14-point bridge; no invented intermediate masks. |
| Save repair and route | 38–40,42 | Original 103-voxel repair and 371-point RAS line linked to native crop; endpoint/spacing assertions separated from reference accuracy. |
| Link CPR samples to source | 38–40 | Original eight-angle HU/source-coordinate arrays; expose reader-controlled column/offset link, retain original reported distance. |
| Show complete mesh/package | 38–41 | Original world-space surface and four outputs; geometry/closure versus saved mask only. |
| Reveal frozen miss and correction | Original metrics + retained intervention | Reward 0 CPR distance-axis miss, separate author correction and related-reference/training-split limits. Saved original state remains fixed. |

**Next action:** create a fresh, source-pinned reader preparation recipe using the
whole supplied crop, input mask/edit region and original four outputs; extract the
three exact embedded PNGs; retain complete route/CPR pixel source mapping and a
bounded native context preview. Add a separately gated frozen/reference/intervention
projection. Reuse the shared player with a typed coronary adapter representing
local edits, RAS paths, sampled CPR planes and mesh. No trial or scorer execution
is needed to prepare this retained explanation.

**Open gaps:** no derivative payload, extraction manifest/receipt, story draft,
static fallback or visual acceptance was created here. Missing intermediate on-disk
scripts/PNGs are recoverable as text/deliveries, not fresh execution. No solver-viewed
CPR/mesh image is retained. Source native geometry and exact-image closure, original
wrong distance-axis disclosure, reference hiding, mesh-display simplification,
narrow/keyboard controls and independent visual review remain required before
canonical binding. Keep MRI/catalogue/shared code unchanged during this mapping.
