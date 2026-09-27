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
