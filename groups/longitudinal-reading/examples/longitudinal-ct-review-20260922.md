# Longitudinal-CT: four local case reviews

Actor: assistant. Date: 2026-09-22 (Asia/Shanghai).
Source: [current task](codex://threads/01a0c4d1-741f-76e3-9023-1064e5a9a0c5),
following [Medical Image Reasoning Tasks](chatgpt-conversation://6ab15587-d73c-83ee-a5d8-d5defad31b8d).
The user requested a few downloaded cases, data/GT illustrations and task framing.
This is an author review and proposal, not an experiment or a model result.

## What was acquired

Pinned source: [Longitudinal-CT v3](https://fdat.uni-tuebingen.de/records/qe950-g4h94),
DOI `10.57754/FDAT.qe950-g4h94`, published 2026-09-18. The release API declares
**CC BY-NC 4.0**, attribution to Küstner, Peisen, Gatidis and collaborators,
University Hospital Tübingen. Use the exact release terms; the paper's shortened
CC BY description does not replace them. The v3 change note is added demographics.

The ZIP is 51,047,900,775 bytes, advertised MD5
`cde33aed3ed708065f5a1970b5079098`. HTTP range retrieval recovered the central
directory, all 300 patient CSVs plus demographics, and **four** complete patient
bundles (8 CTs, 8 masks, 8 center JSONs, 4 CSVs). Large/raw files stay under
`.local/longitudinal-ct-review/raw/`. Each acquired member's decompressed size and
ZIP CRC32 were checked; SHA-256 digests of selected patient members are retained
in the [audit](longitudinal-ct-review-20260922.json). The full ZIP was not downloaded,
so its advertised MD5 was **not verified**.

The paper describes 600 CT studies in 300 patients, with 4,079 baseline and 3,103
follow-up lesions. These are source-published counts, not a whole-image audit here.
The local CSV screen contains 4,638 rows: 2,506 UNCHANGED, 1,407 DISAPPEARING,
559 NEWLYAPPEARING and 166 MERGING. A MERGING row is a baseline member, not one
distinct merger or one distinct follow-up lesion. There are 135 rows with
`linking_unclear=True`; two CSVs (`38db3aed92`, `8fc4c7ab44`) omit the column,
covering four rows. Missing does not mean false. All rows in the four selected
cases explicitly have `linking_unclear=False`.

## Selected cases and what they show

Selection was purposive by metadata event type, compactness and inspectability,
before any model execution. These are development illustrations, not a random
sample or an estimate of prevalence/performance. Intervals below come from v3
demographics, in days.

| Patient | Interval | Source reference | Use in review |
| --- | ---: | --- | --- |
| `0a09c8844b` | 76 | B1+B2+B4 → F4; B3 → F3 | Three-to-one abdominal nodal merger; a separate persistent target |
| `02522a2b27` | 112 | Four persistent IDs, two new nodal labels | New lesions near existing lesions; persistent identity despite size change |
| `06eb133bbf` | 190 | Two disappearing lung labels; empty FU mask | Why absent reference labels need coverage and anatomical review |
| `0777d5c17d` | 97 | One disappearing soft-tissue/skin label | Held for review: baseline label in visibly defaced anterior face |

For the merger, the baseline CSV volumes are 18.164, 1.211 and 49.648 mL;
combined 69.023 mL. The one follow-up region is 116.905 mL, a **69.4% increase
in this annotation-derived group volume**. All three merging rows repeat the
116.905 mL value. Summing those fields produces 350.714 mL and triple-counts
the same region. This is not a RECIST assessment or treatment-benefit conclusion.

For `02522a2b27`, source ID 1 stays UNCHANGED while its volume rises from
3.633 to 13.036 mL. This directly illustrates that UNCHANGED means topology /
identity persistence, not unchanged size. The two new nodal labels have source
volumes 0.342 and 0.569 mL. Their proximity to persistent nodes makes a useful
local correspondence illustration; no measured agent difficulty is established.

For both disappearance cases, the FU views use **conventional registration's
propagated locations**, not manually identified FU lesion centers. A single
empty slice or mask does not establish disappearance, comparable coverage or
absence of residual disease. The lung case still needs explicit anatomical
coverage review before becoming a hard disappearance test.

The facial baseline mask has 92 voxels, all in the −413 to −321 HU range. The
label lies in the visibly defaced anterior facial region and does not provide
clear original lesion appearance in the soft-tissue view. This supports holding
the case out of an image-grounded test pending image/reference adjudication.
It does **not** establish that the radiologists' original correspondence was wrong,
that all marked tissue was deleted, or that an agent failed. Source bytes and
annotations remain unchanged.

## Geometry and measurement checks

All eight downloaded CT/mask pairs have equal shapes and matching NIfTI affines.
Their voxel axes are L/P/S; affines map zero-based native voxel indices to RAS
millimeters. The reader displays native axial arrays transposed, patient R at
left, A at top, and preserves equal in-plane physical aspect. BL and FU are not
registered, have different geometry, and must not be matched by slice number.

For the 19 present mask labels in the selected cases, CSV `cog_*` coordinates
are approximately **mask-centroid + (0.5, 0.5, 0.5)** in voxel units. The small
exception from exactly 0.5 is the same baseline mask with a one-voxel volume
discrepancy. Treat this as an observed convention in these files, not a proven
universal rule for propagated points. The reader selects slices from inspected
mask centroids and rounds propagated locations only for explanatory viewing.
An executable scorer should declare and test its coordinate conversion explicitly.

Mask-derived volume is labeled voxel count × absolute determinant of the image
affine's spatial block. `0a09c8844b` BL label 1 differs from its CSV volume by
one voxel (~2.028 mm³, ~0.011%); other selected present-label volumes agree within
floating-point precision. Preserve CSV and recomputation as separate references.
The [audit](longitudinal-ct-review-20260922.json) records both, native centroids,
physical coordinates, shape/spacing/affines and hashes.

## Proposed agent task

Start with **marked baseline lesion correspondence**. Give full native BL/FU CTs,
baseline target masks with opaque IDs, visit order and geometry. Ask the agent to
localize corresponding FU regions, link each baseline target, allow many-to-one
mergers, identify unsupported/uncertain matches and provide source series + native
voxel/RAS locations + short image evidence. Require follow-up masks only in a
separate segmentation/measurement condition; point localization alone cannot
support independently reproduced lesion-volume claims.

Keep whole-volume detection of new lesions separate. Marked baseline targets
remove baseline detection but do not specify where genuinely new lesions might
appear. If a bounded anatomical search region is supplied, define it before
target review rather than crop it around hidden GT. Do not frame this initial
study as response classification, diagnosis, causality or RECIST assessment.

Proposed outputs: per-visit region IDs; correspondence edges; event per connected
group; native series and coordinates; optional instance masks; group volumes and
change computed without duplicated destinations; a small image-evidence list.

Proposed evaluation, not a frozen scorer:

- Match FU points/masks to manual regions in physical geometry; report localization
  and segmentation separately, with reviewed tolerances.
- Score correspondence edges allowing many-to-one associations and events per
  connected group. Report per-event results rather than an aggregate dominated
  by persistent lesions.
- Measure volume error only for correct region/group matches with submitted masks;
  separately assess correct deduplication and calculations.
- Exclude or adjudicate unclear/missing link flags, visibility problems and
  non-comparable coverage before binary scoring. Allow unresolved outputs, and
  report their rate rather than quietly dropping them.
- Compare a fixed registration + matching method, agent inspection with the same
  inputs, and agent audit of that fixed method. Include correct proposals and
  count correct matches damaged as well as wrong matches repaired.
- A reference-mask condition can isolate association given candidate geometry,
  provided visit-specific IDs are independently randomized. Passing it does not
  demonstrate lesion detection/segmentation from CT.

## Leakage boundary

Do not pass the source `inputsTr/` folder as solver input. It includes FU center
JSONs, CSV answers (`cog_fu`, event, merger destination, volumes), propagated and
backpropagated locations and flags. Baseline and FU masks reuse lesion IDs, so
supplying both without independent permutation can solve correspondence by ID.

Use an allowlisted solver bundle: renamed CTs, declared baseline helpers, geometry,
visit order, prompt and output schema. Keep raw source bundles, this reader, CSVs,
FU references and acquisition code outside the solver mount. Restrict target-source
retrieval in the primary image-grounded condition. An unrestricted-source condition
is separately labeled. Patient identifiers removed from filenames alone do not
prevent public-source lookup or training exposure. The current local review folder
is an author workspace containing GT, **not** an isolated solver environment.

## Illustration and recovery

Open `.local/longitudinal-ct-review/review/index.html`. It starts with raw CT,
offers baseline-only masks, and reveals both reference masks/CSV links on demand.
Each visit has an independent slider, explicit native slice and physical position,
soft-tissue/wide windows, full-slice and detail views, and matching color legends.
The selected slabs/crops are disclosed as reference-assisted reader views. Static
input/helper/reference sheets accompany it. The standalone HTML embeds its images.

The [Task Brief](../presentation/briefs/longitudinal-ct-correspondence.md) uses the
repository convention; its private collection builds with the existing renderer.
Local images are intentionally untracked and must be recovered before rebuilding
its native illustrations. No raw scans/media were added to Git or published.

From already acquired members, using the existing imaging runtime:

```sh
.venv-br037/bin/python groups/longitudinal-reading/methods/longitudinal-ct-review/build_review.py \
  --data-root .local/longitudinal-ct-review/raw \
  --output .local/longitudinal-ct-review/review
UV_CACHE_DIR=.cache/uv uv run med brief build \
  --catalog groups/longitudinal-reading/presentation/longitudinal-ct-catalog.json \
  --output .local/longitudinal-ct-review/task-brief.html
```

Recovery uses each listed patient prefix and all its members from the pinned
archive. The local `acquire.py` retains the bounded range extraction procedure;
source API snapshot, central directory and acquisition receipt remain under
`.local/longitudinal-ct-review/source/`. Do not recover by importing historical
probe authoring modules. Runtime libraries were already present; none were installed.

## Verification

The staged review was checked in a clean index snapshot, excluding the concurrent
anatomy-audit task. `make check PYTHON=python3.12` passed (81 tests, one skipped),
and `make presentation-check PYTHON=python3.12` passed the existing workbench and
Task Explorer browser suites. The custom four-case reader passed input-first,
baseline-only helper, GT reveal, per-case reveal reset, all eight view selections,
slice/crop controls and mobile layout checks with no page errors or remote loads.
The one-brief collection separately passed three assistance conditions, all three
native sheets and two embedded local-source checks. A hands-on Codex browser check
confirmed the raw-input and GT/detail states; the deliverable was left input-first.
Local QA receipts/logs are under `.local/longitudinal-ct-review/`. These checks
verify data handling and the presentation, not clinical correctness or agent skill.

## Sources

- [Pinned release and schema](https://fdat.uni-tuebingen.de/records/qe950-g4h94)
- [Release API and exact rights](https://fdat.uni-tuebingen.de/api/records/qe950-g4h94)
- [Dataset paper](https://www.nature.com/articles/s41597-026-07466-y)
- [Organizer description](https://autopet.org/longitudinalct.html)
- [Official processing repository](https://github.com/lab-midas/autoPETCTIV)
- [Provenance audit](longitudinal-ct-review-20260922.json)

Before a trial: review geometry/coverage and disputed labels, freeze independently
held-out cases and task/scorer contracts, test leakage controls, then obtain a
separate explicit instruction to run the selected agent condition.
