+++
schema_version = 2
kind = "idea"
id = "echo-contraction"
group_id = "cardiac-motion"
title = "Recover contracted cavity and measure function"
next_action = "Assistant recommends this if new-lesion source access is blocked. Curate unused cycles, separate frame/volume/EF endpoints and test an input-legal author solution."
source = "codex://threads/01a0bde4-e30d-71c3-8ae4-19d377aee51d"
decision_provenance = "Assistant proposal; user requested explanation, not trial selection."
historical_ids = [
    "BR-043-C03",
]
idea_state = "exploring"

[[links]]
label = "Proposal and visual explanation links"
path = "docs/research-rounds/BR-043-medical-next-tasks.md"
+++

# Recover contracted cavity and measure function

## Question

Recover contracted cavity and measure function

## Prior findings

BR-034 found large ejection-fraction errors despite relatively small mean surface distances. A supplied end-diastolic cavity can isolate end-systolic contraction without asking for unobserved material mechanics.

## Reopen when

Curate unused cycles, separate frame/volume/EF endpoints and test an input-legal author solution.

## Explainer source review — 2026-09-27

Actor: assistant; source: the user's explainer completion request in
`codex://threads/01a0e024-3705-7a91-9181-d237131801fa`. This is a reader-facing
audit and recommendation, not a user selection of a new medical trial.

- [BR-025 contour brief](../presentation/briefs/tb3-cardiac-contour-feasibility.md)
  now separates all-phase supplied contours, withheld native sections and the
  annotation-derived dense comparator. The [saved-output audit](../presentation/sources/cardiac-contour-audit.json)
  verifies 2,251 source members and reproduces six conditions without refitting.
- Four-view withheld Dice is 0.937 and derived EF error 0.59 pp; one-view EF error
  is 2.68 pp despite 31.10% volume MAPE. These are one-patient author comparisons,
  with pose and phase-index assumptions, not independent clinical performance.
- The retained depth control preserves its observed plane while changing EF by
  13.41 pp. Fixed radial mesh indices establish neither material motion nor strain.
- Source/result overlays at native plane 8, frames 2 and 17, were inspected locally.
  Their exact paths and hashes are in the audit. The canonical story and export
  are still pending; no generic shape animation replaces this entry.
- FeEcho4D permits noncommercial research on its project page; the current Zenodo
  record lacks an explicit license field. Redistribution remains unresolved.
  The assistant requested a concrete delivery-scope decision in this chat and
  recommends retaining raw/derived source assets locally until resolved.

Reopen the contour and anchor asset integration when redistribution permission
is documented or the user explicitly approves private local artifacts as final
scope. Continue other actionable explainer entries while that decision is pending.

The assistant also audited the separate [BR-027 anchor condition](../presentation/briefs/tb3-cardiac-anchor-feasibility.md)
and retained its [package/replay receipt](../presentation/sources/cardiac-anchor-audit.json).
Both exact public inventories contain 120 native images and only four/eight
allowed masks. All seven saved conditions reproduce, without new tracking or
fitting. Unsupplied input-view Dice has distinct 116/112-pair denominators; the
common withheld comparison uses 240 pairs. GrabCut's improved scalar EF does not
repair its shape failure. Native selected overlays show direct mask disagreements
before 3D interpolation and separately reveal withheld mesh sections. This is a
development-informed author study, not an independently isolated model test.
BR-027 uses an anchor-only origin and curve-extrema EF; BR-025 uses a different
origin and config-phase EF. Compare within each round's controls. Its source
rights, canonical story, integrated review and export remain unresolved.

The separate [BR-029 material-feasibility brief](../presentation/briefs/tb3-cardiac-material-feasibility.md)
and [source/mechanics audit](../presentation/sources/cardiac-material-audit.json)
retain the distinction between reference playback, privileged representation
controls and four-video reconstruction. The assistant verified 121 source files,
all 120 public images, seven corrected saved models and the existing full-tensor
export without fitting. Directional statistics cover 31,241 usable cells, whereas
geometry covers all 47,186 tetrahedra. Three unsupported positive-AHA cells remain
explicitly unavailable; superseded outputs and all original predictions are intact.

The tissue method's radial MAE improves to 6.79 pp, but its 4.03 mm global material
RMSE and incomplete regional accuracy still fail the provisional targets. Initial
CG nonconvergence (81/87 solves) and the later 87/87 converged solves are numerical
execution evidence, not agent outcomes. Selected native input views and the
retained source/result strain figure were inspected locally. Neither tissue volume
nor a visually plausible mesh establishes chamber EF or physiological force balance.

Actor: assistant, under the same completion request. STRAUS project/collection
and root-folder metadata still give no explicit redistribution license. The
assistant separately requested a concrete delivery-scope decision for STRAUS;
it remains unanswered. Keep source-derived assets local, leave this explainer
unfinished, and continue the next actionable entry while permission or private-only
final scope is unresolved. This does not authorize a new medical trial.

## Real-echo explainer source review — 2026-09-28

Actor: assistant, under the same user completion request. The
[BR-032 exact brief](../presentation/briefs/tb3-real-echo-reconstruction.md) and
[source/output audit](../presentation/sources/real-echo-audit.json) separate the
72 given plane images from 72 withheld review images, with no contour or 3D truth.
All 18 native decoded volumes, all 144 reslices, the frozen public inventory,
retained mesh metrics and section/brightness calculations were checked without
executing the historical solver or launching a model.

One actual `gpt-5.6-sol`/xhigh attempt completed in 657.06 s and earned artifact
reward 1; the static ellipsoid control also earned 1. The original trace records
image viewing before the solver stored framewise measurements in fixed tables.
The retained static-input replay changes 68/72 images while preserving every
primary and alternative point, including 5.3973 mm RMS motion. The pose replay
preserves the geometric response to calibration. These establish different
properties: original image interpretation and saved executable input dependence.
They do not establish anatomical accuracy, memorization or a failure to view
the original images. Original rewards, failed infrastructure records and missing
auxiliary-file replay checks remain intact.

Source-only images beside primary and basal-alternative sections were inspected
at frames 2/4/10/14 on two given and two withheld planes. At short-85, the primary
has no section in frames 2/14 while the basal alternative does; both intersect
at 4/10. This makes cap sensitivity visible without adjudicating chamber identity.
The 54.08–177.57 mL primary range is model geometry, not clinical EF evidence;
alternative spread is not calibrated uncertainty. The audit retains exact local
image paths, hashes, color/line legends and the selected-still coverage limit.

EchoSlicer repository/release records inspected on 2026-09-27 contain no explicit
redistribution license. The assistant requested a separate EchoSlicer delivery
decision in this chat; no answer has been recorded. Keep derived images and meshes
local, and reopen canonical story/export acceptance when permission is documented
or the user explicitly approves private-local final scope. Continue the clinical
cavity entry meanwhile. This is not a user decision to change the deliverable.

## Clinical-cavity source review — 2026-09-28

Actor: assistant, under the same completion request. The
[BR-034 exact brief](../presentation/briefs/tb3-clinical-cavity-adaptation.md) and
[native/output audit](../presentation/sources/clinical-cavity-audit.json) verify
three selected archives, 114 extracted recording files, all 101 prepared volumes
and 303 previews, supplied initial meshes and withheld reference sequences.
The decoded C-order array digest still differs from the publisher's unspecified
serialization; archive/codec agreement does not resolve that convention.

The frozen scores reproduce without flow fitting or executable/model launches.
Primary, hidden reduced and supplementary preserved-case EF errors remain
23.30/25.94/30.49 pp, despite mean surface distances of 1.89/1.85/2.24 mm.
All three pass the mean-distance gate, as does the static initial surface at
2.70 mm. Preserve separate function and geometry endpoints. Initial-frame
agreement is supplied assistance; clinical cavity indices are not material truth.

The retained original replay matches all vertices. Still inputs produce exactly
stationary output and EF 0%; a five-frame shift produces the corresponding
permutation exactly. These controls establish input response while clinical
contraction remains wrong relative to the source surfaces. There is one actual
model attempt; the two hidden cases are unchanged-executable replays. The
supplementary control's timing, rejected predecessor and replacement remain explicit.

The assistant inspected source-only, solver and private-reference sections at
reference systole in all three orthogonal planes for all three cases. The
transverse solver sections remain larger than their references; longer-axis
sections also show different narrowing. These are selected stills, not a
full-motion review or clinical adjudication. The original pre-fit impression
precedes the flow experiments in the retained tool trace; the final severe
category follows an underestimated EF. That within-session change is descriptive,
not evidence of modeling's causal diagnostic effect.

The pinned EchoXFlow catalogue/license and the official card inspected on
2026-09-28 agree on CC BY-NC-SA 4.0. Continue the same entry with attributed local
source-derived assets and an operation-specific story showing image input,
initialization, saved tracking, reference reveal, volume curves and altered-input
controls. Canonical integration, exports, motion/mobile/no-GPU review and final
acceptance remain pending; the ledger stays at 30/205 reviewed. This record
does not authorize publication or another medical trial.

The clinical-cavity entry subsequently completed its source-derived canonical
story, integrated Explorer review and fresh HTML/MP4/caption export in commit
`c7a01f9006071b1abb4925b446787b36c0e0f949`. Its acceptance receipt is
`.local/explainers/completion-20260927/022-acceptance.json`; the completion ledger
now records 31/205 reviewed. This closes the explainer work described above,
without changing the retained scientific outcomes or authorizing publication.

## Supplied-mask mechanics source review — 2026-09-28

Actor: assistant, under the same completion request. The
[BR-035 exact brief](../presentation/briefs/tb3-mask-to-mechanics.md) and
[input/output audit](../presentation/sources/mask-mechanics-audit.json) verify
219 file fingerprints, including all 77 reproduction-manifest entries. All
30 synthetic and 18 clinical mask/image frames reproduce their retained source
derivations. Six full saved scores reproduce within absolute 1e-8, without
executing either submitted solver or launching a model.

Both synthetic constructions pass, but radial-strain MAE remains 7.37/5.45 pp
against the separate 5 pp diagnostic target. Material coverage is 98.06%, with
45,970 of 47,186 source-cell centroids covered; coverage and strain have different
weights and validity rules. Both agent meshes retain six nonmanifold boundary
edges. Those defects and small severely compressed regions are post-hoc findings,
not grounds to overwrite their original construction rewards.

Source-only slices, supplied masks and saved-mesh voxel occupancy were inspected
in three native planes at synthetic phase index 9 and clinical phase index 11.
Synthetic boundaries differ locally despite high global overlap. Clinical contours
closely follow the supplied cavity masks in these selected views. The retained
volume/strain figure shows the corresponding separation: matching supplied volume
curves does not prevent missing the simulator radial-strain target.

The original executable hashes confirm both methods explicitly match total volume.
The image program uses its texture branch only for myocardial-wall inputs; its
clinical cavity transfer uses masks alone. Both clinical EF values reproduce the
already supplied mask curve. Preserve this assistance boundary, the original
incorrect timestamp boilerplate and the one-case/two-program comparison limit.
This is an endpoint-only comparison, not a causal estimate of image assistance.

The STRAUS delivery-scope question already pending for the material entry also
covers this entry and remains unanswered. Keep all source-derived media local;
canonical story, portable assets, exports and complete visual acceptance remain
unfinished. Reopen when permission is documented or the user explicitly approves
private-local final scope. The assistant advances to named landmarks, retaining
31/205 reviewed and all blocked entries in the denominator.
