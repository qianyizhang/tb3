# Canonical task explainers

The Task Explorer combines task-specific narratives, source assets and a shared
interactive player. Scope and acceptance remain explicit in the
[scope register](EXPLAINER-SCOPE.json) and [review ledger](EXPLAINER-LEDGER.json).
The [2026-10-02 closeout](EXPLAINER-COMPLETION-20260929.md) records 154/154 accepted
core entries; the full catalogue retains 205 entries.

Start with [owners](#owners), [build and export](#build-and-export), and
[review requirements](#checks-and-visual-acceptance). The
[framework review](../docs/explainer-framework.md) proposes simplification;
it does not change the current contract.

## Selected source-specific contracts

`imaging101-eht-original-v1` uses all 421 native visibility rows, per-scan closures,
six UV-matched gain controls and the six saved calibrated/corrupted outputs.
Its [source notice](task-explorer/imaging101-eht-original/NOTICE.md) records log
image display, original pixel sums and distinct metric conventions. `view`
selects station pairs, controls or methods; `reference` gates truth and scores
for readers. Actual L1–L3 expose truth. The fitting diagram is conceptual;
no optimizer runs or new method-performance claims are implied.

`imaging101-eht-features-dynamic-v1` preserves ten native snapshots, fixed station-gain
cancellation controls, four parameter examples and histograms of every retained
weighted sample. Its [source notice](task-explorer/imaging101-eht-features-dynamic/NOTICE.md)
records unit-flux images, native array orientation and bin widths. `view` selects
epochs or parameter controls; `reference` gates reader comparisons, not solver
access. Independent fits, effective sample size, weighted spread, point error
and image scores remain distinct. No new training or calibration is implied.

`imaging101-eht-dynamic-v1` uses all twelve native epochs, explicit DFT weights,
a conceptual temporal model and both retained videos. Its [source notice](task-explorer/imaging101-eht-dynamic/NOTICE.md)
preserves array axes, noise convention, synthetic provenance and oracle controls.
`view` selects epochs or controls; `reference` gates truth, error and answer-based
diagnostics in explicit chapters. Native image scores, descriptive brightness
direction and temporal-difference error remain distinct. Actual L1–L3 expose
truth; the planar player performs no simulation or EM reconstruction.

`imaging101-eht-uq-v1` uses native sparse Fourier coverage, exact station-gain
cancellation controls and saved posterior arrays. Its [source notice](task-explorer/imaging101-eht-uq/NOTICE.md)
retains sky coordinates, sample-file identity, source drift and third-party
attribution. `view` selects native rows and arithmetic controls; `reference`
gates supplied truth, error and containment for the reader. Actual L1–L3 expose
truth. One-image containment is distinct from calibration, and generic image
scoring does not evaluate uncertainty. No flow training, sampling or NUFFT runs
in the player.

`imaging101-dti-v1` uses native synthetic signal planes, exact gradient/design
rows, fixed pixel controls and saved tensor-derived maps. Its [source notice](task-explorer/imaging101-dti/NOTICE.md)
retains source coordinates, display quantization and contradictory source labels.
`view` selects retained volumes, pixels, scalar maps and evaluator controls;
`reference` gates truth and error maps for the reader. Actual L1–L3 expose truth
and the mask. Tensor glyph projections use saved eigenvalues in source axes;
the planar player performs no fitting. Masked FA, generic full-grid/reference
selection and the missing-NPY fallback remain distinct scoring conditions.

`imaging101-deflectometry-v1` explains one refracting-lens case using retained
notebook camera panels, a separate synthetic phase fixture and analytical sections
from source parameters. Its [source notice](task-explorer/imaging101-deflectometry/NOTICE.md)
separates rendered pixels from unavailable raw intensities. `view` selects fixed
phase controls, initial/saved states and a recorded-loss cursor; `reference` gates
manufacturer dimensions for the reader. Actual L1–L3 staging exposes that truth.
The custom score ignores pose, and the generic output contract rejects the full
truth vector. The planar player performs no ray tracing or optical optimization.

`imaging101-fan-beam-v1` uses native full/short sinograms, the source pixel-driven
geometry, released Parker weights and three saved images. Its [source notice](task-explorer/imaging101-fan-beam/NOTICE.md)
preserves signed projection values, pixel coordinates, upstream attribution and
operator controls. `view` selects exact pixel controls and saved outputs;
`reference` gates truth before switching to the actual normalized scoring crops.
The saved loss cursor is an inspection aid, not a fresh optimizer. Actual L1–L3
staging exposes truth; native crop-normalized and generic full-image metrics
remain distinct. The shared planar player works without WebGL.

`imaging101-dual-energy-v1` uses paired native count sinograms, supplied spectra
and attenuation curves, selected saved-ray forward checks and both saved material
maps. The [source notice](task-explorer/imaging101-dual-energy/NOTICE.md) preserves
pixel geometry, physical units, approximate calibration and separate MIT notices.
Its `view` channel selects rays, energy bins, saved domains and scoring controls;
`reference` gates truth before matched tissue and bone comparisons. Actual staging
exposes the truth archive at every assistance level. Saved FBP replay and the
shape-dependent generic scorer do not establish fresh decomposition or a pass.

`imaging101-ptychography-v1` uses native simulated diffraction, exact encoder
windows, labeled initial-state intensity projections and the saved complex object.
Its [source notice](task-explorer/imaging101-ptychography/NOTICE.md) preserves pixel
geometry, phase scales and original attribution. `view` selects source scans,
saved views or controls; `reference` reveals synthetic truth only in its chapter.
Actual released staging exposes that truth at every assistance level. Generic
magnitude scoring and native phase scoring remain separate; no fresh inverse or
benchmark pass is implied.

`imaging101-nlos-v1` uses exact confocal histograms, calibration shifts and
Stolt-map probes with the released saved-volume projections. The
[source notice](task-explorer/imaging101-nlos/NOTICE.md) retains Stanford data
terms, source coordinates, native-pixel display transforms and the identical
baseline/reference boundary. Its `view` channel selects measured points,
frequency samples, projection axes and scoring controls; `reference` reveals
the baseline only in its chapter. Small operator checks and saved-output replay
do not establish a fresh full-size reconstruction or independent scene truth.

The operation library preserves the original `ours` route pilot and adds explicit
spatial and planar stories. [The candidate map](EXPLAINER-CANDIDATES.md) and
[per-entry ledger](EXPLAINER-LEDGER.json) use all **205 entries** as the denominator.
A bound story is not automatically accepted; unresolved entries remain visible.

## Owners

- Internal canonical scripts live in `groups/<group>/presentation/stories/`.
  External task scripts live beside their briefs in
  `presentation/external-tasks/stories/`. Scripts own captions, narration, scope,
  sequencing and integer frame timing. Scientific briefs/protocols remain authoritative.
- `explanation_stories.py` retains the v1 route parser and adds closed v2 models
  discriminated by recipe. Frontmatter and fenced beats are parsed once; only
  integer schema 1 or 2 selects validation. Comments, spacing and CRLF are accepted;
  booleans, numeric strings, duplicate keys and malformed beats are rejected.
  It checks continuity, source locators, provenance,
  recipe dependencies and hashes before projection. No validator acquires data.
- Python presentation contracts still generate browser DTOs. Bindings are explicit
  `illustration.story_id` values, including nested WSI collections.
- [The retained pack index](assets/teaching-prefabs.json) references the existing
  route owner, seven selected mathematical fixture packs and the existing anatomy
  owner. Topology checks the original route hash; anatomy checks its common source
  case/frame and exact parts/notices. Explicit source-reference packs require a
  recipe-specific reader-only reveal; they are not solver inputs. Public input/contract
  packs declare `no-reference-assets` and reject reference-role assets.
- `story-timeline.ts` returns an immutable, recipe-discriminated absolute state.
  `use-scene-player.ts` owns the single clock, seek, visibility, reduced motion and
  cleanup for both spatial and planar content.
- `stage.ts` remains the camera, lights, renderer, projection and disposal owner.
  New spatial content uses its existing native seam. Planar stories use DOM/SVG
  without creating WebGL. Recipe dispatch precedes legacy mode selection.
- `TaskVisual.tsx` composes chapters, stage, output, current caption, matching
  legend and transcript. No-GPU spatial views derive from the same fixture and
  plan. Planar stories remain interactive without a GPU. Chinese controls retain
  the explicit English-source note.

## Integrated operations

| Recipe | Distinction preserved |
| --- | --- |
| Route v1 | Original synthetic sampling ribbon; not full BR030 |
| Topology | Selected connected path vs seven-edge inventory; teaching graph is not CTA input |
| Rigid correspondence | One transform, P1–P3 fit, P4–P5 held-out checks, absent P6 and deformation boundary |
| Multiscale | Twelve supplied slots, coordinate navigation, and six-code coverage are separate stories |
| Local edit | Bounded correction, unsupported source-evidence gate, valid unchanged control |
| Shape/material | Identical analytic shells with two material maps; calculation/sparse/volume conditions distinct |
| Longitudinal | Explicit match/new/unobserved relations; actual CT task supplies no candidate locations |
| Anatomy audit | Existing seven-part s1233 assembly; label/witness schema and clean-control semantics |
| Object identity | Anonymous teaching IDs, shared source geometry, condition-specific vocabulary, assignment output and explicit source-name reveal; seven-part s1233 subset is not full A01 |
| Anatomy curation | Seven retained VerSe source volumes, five distinct candidate decisions, reference partition reveal, focused preservation measurements and explicit admission limits |
| Mask shortcut screen | Retained author ordering and leave-one-patient-out baselines; exact source centroids, coverage exception, separate reference reveal and pre-trial admission limits |
| Prototype identity | All 17 actual case-32 I2 objects as sampled surface points; 117-name vocabulary, complete assignment list, private-key reveal and prototype admission limits |
| Mixed tissue | Retained M02 CT with supplied host/donor outlines; author-only region and LPS witness revealed explicitly; whole/partial/unchanged/focused conditions stay distinct |
| Respiratory correspondence | Actual oblique CT, calibrated source/target sections, source-depth contracts, ordered historical output and separate numerical/visual judgments |
| Registration postmortem | Retained composition repairs, calibrated search boxes, actual CT patch objective and separate author controls/fresh repeats |
| Clinical cavity | Actual EchoXFlow frames, supplied initial surface, saved tracking, private reference reveal, volume/EF gates and distinct static/shift controls |
| Dental contract v3 | Same-target F018 pair; saved example transfer, explicit target-reference reveal, five exact pulp refinement stages, fixed canal search crop and complete-axis silhouettes; original metrics and development-case limits |
| Segmentation calibration | One public CT; fixed reference-derived slices and boxes, all 116 saved tool masks, input/output/reference separation, per-organ box sensitivity, cached encode/decode denominators and distinct CPU/MPS disagreement |
| Aneurysm localization | Full native MRA, discrete slabs and sections, returned point, weak-region matching, reference miss and source-assisted negative |
| CT organ segmentation | Ten independent binary masks; native CT, saved polygon interpolation, image-conditioned tool candidates, explicit private-reference reveals and organ-balanced comparisons |
| Named landmarks | Actual CT/MRI sections, native-to-world conversion, saved point/status outputs, private reference reveal, wrong-level detections and visible-target denominators |
| CT/MRI | Separate Radon/FFT measurements and image outputs; toy vs task dimensions/assistance explicit |

V2 multiscale stories require `operation: coordinate-navigation`, `supplied-patches`
or `annotation-coverage`; topology requires `ordered-path` or `edge-inventory`.
Every correspondence beat declares `show_deformed_target: true` or `false`.
These fields drive the sampler, scenes, output and legends; renaming IDs does not
change their meaning. The six original sources at revision `0ea91a5` retain their
bytes through compiler-local path/hash/recipe matching. Editing or copying one
requires explicit fields; a familiar filename does not enable legacy decoding.

`anatomy-identity-v1` traverses anonymous teaching objects with `focus`, describes
the condition's vocabulary with `inventory`, and exposes source names only through
`reveal`. Its no-GPU projection retains the same clock, chapters and input-first
state. The retained seven-object s1233 subset shares a source with BR-013 A01;
teaching IDs and source-name rows are explicitly separate from the frozen task.

`mixed-tissue-v1` uses three native CT slices with an explicit
`reader-reference-reveal` policy. The reference region and witness are absent
from the initial rendered view, including without a GPU. Crops are oracle-centred
and labeled as such from the start; this is a reader explanation, not blind search
or solver input. The dedicated source-slice pack pins CC BY / Apache terms,
source hashes, native pixel-to-LPS transforms and separately classified reference
paths. Other recipes retain `no-reference-assets`. Rebuild instructions and
limits are in [the source notice](task-explorer/mixed-tissue/NOTICE.md).

`prototype-identity-v1` shares the identity channels but uses its own 17-object
source pack and private-key reveal. All source clouds keep one proper rotation,
centre and uniform fit; point samples do not become watertight meshes or imply
connectivity. [Its notice](task-explorer/prototype-identity/NOTICE.md) retains
the public-file hashes and source-occupancy identity checks. Every asset pack's
declared files now enter the frontend fingerprint, including source packs outside
the earlier anatomy/fixture folders. A changed reference cannot reuse old bundled
bytes. The Explorer's directly cited text bundle is bounded at 2 MiB for the
205-entry catalogue; the 64 KiB per-file limit and private-runtime exclusions remain.

`mask-screen-v1` explains the BR-010/011 author study with discrete source scenes
and `measure`, `prediction`, `reference` and `focus` channels. Source-scene changes
require an explicit cut; scene meaning never comes from chapter names. The
[mask-screen notice](task-explorer/mask-screen/NOTICE.md) pins all eight source
arrays, seven audit trajectories, 24 recomputed ordering rows and 131 recomputed
organ predictions. Selected source points retain one physical frame per scene;
centroids use full occupancy. Dashed centroid guides are not anatomical connections.
The baseline's labeled training examples remain distinct from I2 solver assistance.

`anatomy-curation-v1` uses discrete candidate scenes with explicit cuts and separate
`reference` and `focus` channels. All seven VerSe source volumes are represented;
the 406 preservation view selects T9-T11 without changing their relative geometry.
The [source notice](task-explorer/anatomy-curation/NOTICE.md) records the 21 source
hashes, 145 full-occupancy measurements, 104,100 verified boundary points and
mask/centroid discrepancy. The pack checks its exact CC BY-SA 4.0 terms, independently
of the TotalSegmentator source packs. Independent scan fitting is never registration.

## Build and export

`respiratory-v1` preserves dataset-world geometry across source pixel coordinates,
calibrated CT sections and the retained target points. Its source-depth reveal does
not move points. The q06 reference scene preserves the candidate-centred physical
offset, with the frozen score separate from later visual judgment. The
[source notice](task-explorer/respiratory/NOTICE.md) describes four task contracts,
two cases and reference provenance. No-GPU views use the same calibrated sections.

`registration-analysis-v1` is a planar author postmortem with explicit source-scene
cuts and `reference`, `bounds` and `curve` channels. The
[source notice](task-explorer/registration-analysis/NOTICE.md) pins recovered code,
fresh traces, original scores and diagnostic artifacts. Box extents interpolate
for teaching; only the ±9/±30 mm endpoints were executed. Objective curves sample
a diagnostic straight segment, not a solver path. Independently centred actual
CT patches compare appearance without depicting displacement. Neither presentation
constitutes a blind solver packet or a new medical execution.

`resect-pilot-v1` explains the executed two-query world-output task separately
from `resect-correspondence-v1`, the proposed voxel-output task. Its closed scenes
separate input, prompt cue, delivered slab inspection, retained correlation,
output, manual reference, controls and limits. The
[source notice](task-explorer/resect-pilot/NOTICE.md) pins actual trace images and
calibrated source sections. `view` changes the inspected slab; `output` and
`reference` control separate reveals. The supplied coordinate cue, exact original
scores and later synthetic verifier diagnostics retain distinct roles.

`vessel-source-v1` separates BR-025 author source curation from later repair trials.
Its [source pack](task-explorer/vessel-source/NOTICE.md) pins four actual MRA
projections, calibrated native sections, masks and graph nodes. `scan` selects a
native section; `reference` reveals annotations, and `output` reveals curation
records. Node projection clips to the actual source box and preserves the native
affine. Closed scene cuts retain source selection, topology checks, proposed solver
inputs and the unresolved natural-defect admission boundary.

`airway-repair-v1` explains the BR-033 airway pilot using [retained source assets](task-explorer/airway-repair/NOTICE.md).
Native meshes, CT sections, submitted routes and CPR coordinates share physical
RAS+ mm. `view` selects a native section, saved route cursor, CPR angle or explicitly
labeled control case; `output` and `reference` reveal separate saved and private
assets. The no-GPU projection preserves these boundaries. Whole-crop connectivity
is distinguished from the frozen route-tube check; detached preservation controls
and the valid local pass remain visible together. No solver iterations are simulated.

`topbrain-screen-v1` explains the separate BR-033 brain source study through
[five retained MRA cases](task-explorer/topbrain-screen/NOTICE.md). Closed scenes
separate development prediction comparison, variant preservation, contact conventions,
reference-parent gaps, saved geometric calibration and the admission decision.
`view` selects an actual case/plane/CPR angle; `output` and `reference` reveal
separate saved and reference material. Native pixel spacing controls both display
axes. MIPs collapse depth; full-volume audits establish the reported discrete
contacts and selected parent attachments. No new inference or agent trial is implied.

`hubmap-inventory-v1` uses the [retained PAS slide and polygons](task-explorer/hubmap-inventory/NOTICE.md) to explain the proposed contour/area inventory separately from historical point-only pilots. `view` controls a teaching viewport, worked arithmetic or row progression; `reference` gates source polygons, counts and reference-derived measurements. Native level-0 extents preserve physical aspect, local coordinates return through explicit crop origins, and area uses squared OME pixel spacing. Optional cortex/medulla helpers are a distinct condition. The crop is reference-selected and the duplicate example constructed; neither is agent-search evidence.

### Draft a canonical story

`named-landmarks-v1` uses [retained native sections](task-explorer/named-landmarks/NOTICE.md)
from PDDCA, AFIDs and VerSe. Closed scene cuts separate source inputs, coordinate
conversion, teaching navigation, saved outputs, private references and comparisons.
`view` selects acquired sections or discrete score thresholds; `output` and
`reference` reveal separate records. Diagnostic sections are reader-selected, not
supplied hints or an agent trajectory. Physical aspect, native directions, signed
plane offsets and equal-scale full/crop views preserve three-dimensional meaning
without requiring WebGL. MRI atlas assistance, unrecovered runtime atlas bytes,
reference uncertainty and all-visible-target denominators remain explicit.

```sh
uv run med story recipes
uv run med story new ENTRY STORY_ID --recipe RECIPE --preview
uv run med story new ENTRY STORY_ID --recipe RECIPE
uv run med story check groups/GROUP/presentation/stories/drafts/STORY_ID.story.md
```

Drafting resolves the entry's leaf catalogue and creates an unbound file in its
owner's `stories/drafts/`. Replace all `[[AUTHOR:...]]` fields and check the finished
story before moving it to `stories/` and explicitly setting `illustration.story_id`
in the owning catalogue. Drafts are excluded from normal story discovery; unfinished
authoring fields fail compilation. Inverse drafts also require explicit
`--acquisition ct-parallel` or `--acquisition mri-cartesian`. The retained v1 route
pilot remains supported but is not a new-draft template.
Multiscale and topology drafts require `--operation` from the values above.
Correspondence drafts include an explicit false flag on each beat; author the
deformation chapter deliberately. `med story recipes` lists each recipe's choices.

### Review a selected batch

```sh
# After the current frontend build; new only prepares a pinned batch.
uv run med story batch new tb3-oblique-pose wsi-hiesd-map --output .local/explainers/NEW-BATCH
uv run med story batch run .local/explainers/NEW-BATCH
uv run med story batch check .local/explainers/NEW-BATCH --decode
```

`new --stills-only` prepares a batch without video encoding. `run` invokes the
existing exporter, stops on the first failure and retains execution logs. It needs
the same approved browser execution boundary as individual exports. An attempted
batch is never retried in place. Source changes stop the batch; create a fresh
destination after rebuilding. `check` verifies required output hashes and one
source/frontend snapshot against current sources; it is not an offline historical
verifier. Its schema-1 receipt reader validates consumed fields and safe leaf
filenames while preserving additional producer metadata. Invalid counts, hashes,
links, missing files and recorded errors remain failures. `--decode` additionally checks full MP4 decoding,
dimensions, frame counts and fps. These operations never mark visual acceptance.
The generated `review.html` links interactive outputs, source captions, receipts
and representative frames; record actual inspection and limits separately.

Use the existing environments and exporter. Generated media, review frames and
receipts stay in fresh local destinations; nothing here launches tasks or publishes.

```sh
UV_CACHE_DIR=/tmp/tb3-uv-cache npm run frontend:build
npm run media -- --story=topology-path --output=.local/explainers/NEW-STILLS --stills-only
npm run media -- --story=topology-path --output=.local/explainers/NEW-VIDEO
```

Each export contains interactive single-file HTML, the canonical script and plan,
first/chapter/poster frames, VTT/SRT, transcript and a receipt. Full export adds
silent H.264 MP4 at the script's fps. V1 retains `route-unfold.mp4`; v2 filenames use
story IDs. The capture bridge exists only in the dedicated export entry.

Capture seeks the exact integer frame and waits for React commit, fonts, HTML and
SVG image decoding before screenshotting the complete 1280×720 root. Capture uses
the verified viewport rectangle and rejects any frame or root-bound change across
the screenshot; it does not require the interactive animation clock to advance. Receipts pin
source/asset/frontend/lock hashes, dirty files, OS, browser, renderer and outputs.
These are local rendering receipts, not scientific evidence or cross-GPU equality.

Renderer inputs exclude narrative stories. Selected plans pin their exact story,
source locators, pack dependencies and compiler implementation/runtime lock files.
`med story export-context` reads checked frontend/exporter fingerprints and the
Python runtime version without capture. Individual exports and batches reject
source drift; failed captures retain their receipt and errors in the fresh folder.
Story dependencies use `storage.inside`: workspace-relative paths without parent
segments or symlinks. Pack files are relative to their manifest directory. All
13 original stories passed this policy before migration; historical task/import
digest encodings and the standalone reproduction runner are unchanged.

`presentation/tooling/review-samples.mts` selects frame 0 and each beat's
`endFrame - 1`, deduplicating within a beat; explicit motion review can add
midpoints. Canonical exports retain `first.png`, chapter PNGs and `poster.png`,
and generate `review.html` from those same captures. Receipt samples identify the
export surface, story/source/plan, beat, phase, requested and committed frame,
renderer and viewport. Standalone canonical exports have no entry scope: their
images cannot establish correctness of every catalogue binding.

Explorer review remains a UX capture at chapter starts, with its entry scope and
surface labeled separately. It never gains the export bridge. Saved inventory
replay keeps original bytes/errors and labels missing frame metadata as unknown.
Explorer plan fingerprints use the serialized embedded payload; export plan
fingerprints use the exact `plan.json` bytes.

## Checks and visual acceptance

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_explanation*.py' -v
node tests/scene_player.cjs
node tests/explanation_story.cjs
node tests/explanation_expansion.cjs
.venv-br030/bin/python tests/expansion_fixture_numerics.py -v
node tests/explanation_expansion_browser.cjs REVIEW-DIR EXPLORER-HTML
node tests/explanation_story_browser.cjs ROUTE-EXPORT-DIR EXPLORER-HTML
make presentation-check
make check PYTHON=python3.12
```

Browser commands use the disposable repository harness outside the restricted
macOS command sandbox. The expansion matrix exercises actual `file://` pages,
English and Chinese-source fallback, first/decisive/ending frames, narrow screens,
no-GPU mode, repeated seeks and navigation. Exact sampled states are required.
The composed DOM must match exactly on repeated seeks. A documented raster allowance
covers at most 2,048 of 921,600 pixels differing by one channel level at Chromium
SVG antialias/translucent-fill edges. V1 retains its existing 16-pixel / 8-level
raster allowance; displaced content is a failure.

Inspect the resulting scenes in addition to tests. Keep per-entry observations,
before/after frames, source boundaries and unresolved dependencies in the ledger
and local acceptance report. A legacy diagram or passing build is not migration
completion. Do not remove scientific conditions or frozen outcomes for uniformity.

`tiger-context-v1` uses the [retained TIGER ROIs](task-explorer/tiger-context/NOTICE.md) to explain source tissue masks, merged cell centers, boundary attribution, ROI-to-slide transforms and calibrated compartment densities. The `reference` channel gates masks, points and derived measurements; `view` controls explicit worked arithmetic or a constructed boundary displacement. Proposed cells/regions/summary files remain separate from retained point-only pilots. Code 0 is excluded, absent area is unavailable, and codes 2+6 pool counts and areas. Fixed cell-marker boxes are not nuclear outlines. No new model result is produced.

`longitudinal-mri-v1` uses [retained BR037 MRI](task-explorer/longitudinal-mri/NOTICE.md) for native citations, phase/sequence choice, saved component-box methods, source endpoint comparisons and forecasts. `output` gates saved points and reproduced method boxes; `reference` gates source-selected crops and source/future measurements. Initial/reset views show input previews without either. P03 acquisition phases are separate 3D files (citation phase 0). Visits remain unregistered, source diameter units unresolved, and mechanical completion distinct from clinical correctness. One same-image pair with several method changes is diagnostic, not causal.

`longitudinal-ct-original-v1` explains the original full-volume CT task through [native retained views](task-explorer/longitudinal-ct-original/NOTICE.md). Closed scenes separate inputs, saved instance maps, the open reference-partition review, an omitted focus, physical detection matching, link eligibility, complete events and file-contract validity. `view` advances six actual native sections; `output` and `reference` independently reveal saved and private material. Mask-selected crops and source-selected crops retain distinct roles. Fixed HU windows, native spacing and per-visit affines preserve scale without depicting registration. Saved-score replay is not new inference; instance/confluence adjudication stays open.

`longitudinal-ct-revised-v1` explains revised inclusion/instance rules and broad supplied context through [audited native views](task-explorer/longitudinal-ct-revised/NOTICE.md). Twelve closed scenes separate two full CT pairs, generic rules, retained partition changes, volume dominance, all size strata, exact context fields, reported exclusions, accepted-focus contours, complete event denominators and qualified comparisons. `view` advances three native sections in each comparison; `output` and `reference` preserve saved-answer and private-label boundaries. Report-selected exclusions appear before their reference reveal. Shared CT drawing helpers retain native scale and orientation. All three saved-score sets replay exactly; no clinical adjudication, new inference or causal context effect is implied.


`clinical-cavity-v1` advances `phase` through discrete acquired frames; `helper`,
`output` and `reference` control separate reveals. Native paired surfaces use the
same fixed input bounds within each case. The no-GPU player retains synchronized
calibrated sections, volume curves and all chapters. Source positions use float32
for display (maximum audited error below 0.000002 mm); curves and grades retain
original float64 values. Dashed sections join existing intersection endpoints.
Static images with a responsive executable and static initialization against a
moving reference are different controls. See the [source notice](task-explorer/clinical-cavity/NOTICE.md)
and [canonical story](../groups/cardiac-motion/presentation/stories/clinical-cavity-adaptation.story.md).

`ct-organ-v1` uses seventeen actual CT sections and saved masks/prompts from the
four completed single-case conditions. Its `view` channel selects discrete native
planes or organ IDs; it never morphs contours between unrelated acquisitions.
`output` and `reference` keep submitted geometry and private research labels
separate. The [source notice](task-explorer/ct-organ/NOTICE.md) pins the exact CT,
mask, polygon and candidate provenance. Six stomach planes distinguish signed-
distance mask interpolation from box interpolation followed by per-image learned
inference. Output remains ten overlapping binary masks, not one exclusive volume.
Full 3D scores and conditional same-plane diagnostics have distinct denominators.

`dental-original-v1` separates the original exclusive-label CBCT contract from
post-submission ID diagnostics. The [native source pack](task-explorer/dental-original/NOTICE.md)
preserves F018/F002 voxel positions and saved outputs. The `diagnostic` channel
changes displayed IDs only; separate reference panels keep opposing labels
legible. Discrete `view` and `gate` channels select real native planes and five
reconstructed/saved pulp stages. All scores retain active-class denominators;
reference-overlap counts are not precision. Native i/j/k coordinates remain
explicit because physical laterality is unadjudicated. Source and reference
visibility use the shared planar player and work without WebGL.

`dental-v2-v1` compares the same F002 target with and without a supplied F008
annotation. The [native source pack](task-explorer/dental-v2/NOTICE.md) keeps the
supplied example, saved target outputs and private target reference distinct.
`transfer` wipes between the target CT and the example sampled through the saved
displacement field; it does not reenact optimization. Discrete `view` changes
select native pulp/canal sections, while `stage` shows four saved or exactly
reconstructed prior-clipping states. Macro scores retain their original active
denominators; a separately labeled common-union diagnostic and pooled pulp scores
do not replace them. The story qualifies unequal realized compute, one-target
scope and unresolved reference conventions, and supports explicit reference
reveal/reset in the shared planar player without WebGL.

`localized-ct-v1` explains supplied-location candidate judgment using [native retained views](task-explorer/localized-ct/NOTICE.md). Its `view` channel selects discrete axial, orthogonal and serial planes, while `output` and `reference` keep saved judgments and private source labels separate. Supplied points remain fixed in 3D; native affine directions, physical aspect and signed plane offsets distinguish off-plane projection from point containment. Four saved JPEG montages reconstruct exactly. The decision-first contract, empty output, reference disagreement, verifier consistency gap and clinical-report context gap remain distinct. This planar recipe works without WebGL and implies no new trial or clinical adjudication.

`mri-importer-v1` uses [retained synthetic frame records](task-explorer/mri-importer/NOTICE.md) to separate storage order, descriptor ordinals, actual acquisition labels and physical LPS coordinates. Closed scene cuts retain the original task and saved-code replay. `view` visits each actual frame or physical corner discretely; `output` reveals replayed public results and `reference` reveals private aggregate grades. Numerical tiles are exact source samples; projected geometry is labelled as a diagram. The no-GPU view uses the same SVG/DOM data. No new model execution or clinical DICOM conformance claim is implied.

`bcer-workflow-v1` uses [native PI-CAI MRI and public BCER contracts](task-explorer/bcer-workflow/NOTICE.md). Eight closed scenes trace modality names, physical-header coordinates, the exact eight-node template, four artifact keys and five nonclinical validator fixtures. Its single `view` channel selects discrete source points, nodes, artifacts or fixtures. Base stage success, ten-part TCR and five artifact invariants remain independent; a source documentation discrepancy is explicit. No patient mask or private reference is supplied, so this source-derived pack uses `no-reference-assets`. Synthetic grids are separate from native MRI. The planar recipe works without WebGL and implies no medical tool, model or controller run.

`rex-topcow-v1` uses [native TopCoW CTA](task-explorer/rex-topcow/NOTICE.md) to
explain the pinned ReX-MLE preparation, 13 vessel IDs, CSV/NIfTI submission and
nine-measure ranking. `view` selects native planes, public label names or actual
nonclinical fixtures; `reference` gates case 012's held-out source mask and
annotation-derived crop. The complete-release filename replay puts this upstream
training example in the ReX test subset. Magnification preserves source pixels;
the crop is a reader aid, not solver assistance. Five toy arrays distinguish class
Dice, binary clDice, B0 and simplified presence/IoU topology. Eight selected metrics,
a geometry fragment and a rank tie were reproduced; HD95 and the full grader were
not executed. The planar recipe requires no WebGL and implies no model run.

`imaging101-cars-v1` plots [exact CARS spectral arrays](task-explorer/imaging101-cars/NOTICE.md),
fixed forward proposals and saved-fit residuals. Eight explicit scenes separate
input units, L1–L3 staging, forward operations, retained fit, reader reference,
scoring paths, array shapes and limitations. `view` advances discrete conditions;
`reference` reveals the clean curve halfway through its chapter and resets hidden.
This display boundary is not solver privacy: audited staging copies ground truth.
No inverse solve or agent result is produced; missing thresholds remain unresolved.


`healthagentbench-ct-findings-v1` explains the pinned CT requested-label contract with an empty input socket and three hypothetical comparison controls. Report-phrase-derived labels, alias/parser behavior and all-match binary reward remain distinct from diagnosis. The [source notice](task-explorer/healthagentbench/NOTICE.md) records the exact CT-RATE gap. No patient labels, gold, prediction or score are shown.

`radagent-report-v1` exposes the pinned nine-area checklist and tool-action contract without a CT, specialist trace or generated report. The prompt/tool-description draft-order conflict, minimal versus full scenario reference handling, optional reward and separate offline metrics remain explicit. The [source notice](task-explorer/radagent/NOTICE.md) retains the acquisition boundary; checklist selection resets on leaving its scene.

`healthagentbench-tumor-tiles-v1` maps an authored blank 28 by 25 grid to verified native extents, including the half-height final row. Its cursor is unclassified. The [source notice](task-explorer/healthagentbench-tumor-tiles/NOTICE.md) preserves local recovery and unresolved image-reuse terms; no WSI pixels enter the portable pack. Required output, private mask-derived tile set and F1 rule stay separate, with no prediction or score.

`healthagentbench-cxr-correction-v1` uses two abstract existing-clause slots to explain evidence review and keep/correct/remove choices. No new finding action, patient sentence or judge output exists. The [source notice](task-explorer/healthagentbench-cxr-correction/NOTICE.md) identifies missing credentialed report/JPG inputs. FINDINGS-only output, default five calls/absolute three votes, infrastructure errors and the unpinned judge source remain explicit. All four Interpretation A recipes are planar and use the same source-labeled DOM controls without WebGL.
