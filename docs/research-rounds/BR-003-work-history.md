# BR-003 — Failures from the user's own work

## Intake

Captured 2026-09-15 (Asia/Shanghai); **complete**. The user authorized digging
through past work and making hard tasks while they are asleep. Two explicit
leads: PDF cropping/interpretation in chronical-management, and Tavern message
orchestration in conversation-workbench. This is a new round after BR-002.
Current task ID: `01a0a0cf-3d4b-7f00-a47f-4133211cb483`; the current user
message has no exposed stable message ID. Its identifying prefix is
“ok, go hunt for failed sessions in the past of my work”.

This explicit personal-history sourcing request supplements the usual
[benchmark-first shortlist](../research-benchmark-backed.md). It does not
promote these historical incidents to benchmark failures. BR-002's eight
healthy passes argue against trusting plausible difficulty alone.

Read-only retrieval used the local session index scoped to the two repositories:
395 records, including 142 automatic approval-review records. Excluding that
model and titles of 1,000 characters or more leaves 237 navigable records.
Nine selected original conversations were inspected; this is not an exhaustive
audit of all 237. Raw exports remain in ignored `runs/br003-history/`.
The scoped index includes child sessions; records are not independent attempts.

## Evidence and exclusions

Exact source coordinates, excerpts, hashes and retrieval limits belong in
`../evidence/br003-source-audit.json`. The substantive findings are:

* PDF: user-reported crop defects recur after claimed fixes; the June 10 report
  describes bottom-row-only vector crops and neighboring-column contamination.
  Later fixes are retained as successful repairs, not counted as failures.
* Tables: the current generic parser truncates rows to five columns, while its
  seven-column epidemiology table is handled by a bespoke parser. This is a
  source implementation limitation, not a Terra outcome. A separate ingestion
  session repaired `(kind, number, page)` identity collisions; that is too small
  a crux to pursue alone.
* Tavern: an empty bounded wait was followed by resident completion while the
  durable host remained alive. Later work found queued requests and stale
  session scope. Exact “verdict timeout then reroute” history is not recovered;
  that part is a new experiment inspired by the user's recollection.
* A missing PDF renderer, stale root-vs-worktree state, model lifecycle exits,
  and tool/process errors are not benchmark model failures. Role-label styling
  and a single composite-key fix are rejected as insufficient difficulty.

## Candidate queue

| ID | Crux and deliverable | State |
| --- | --- | --- |
| H01 / `pdf-table-lineage` | Reassemble logical cells from continued and rotated table fragments while rejecting nearby non-table text; one JSON evidence artifact | Healthy Terra pass; retired |
| H02 / `chat-round-recovery` | Preserve logical delivery identity through asynchronous assignment, timeout, stale completion, cancellation and restart; one Python coordinator | Healthy Terra pass; retired |
| H03 / `dicom-label-audit` | Infer annotation defects from CT coverage and anatomy; full label vocabulary, no supplied organ-relation rules | Healthy Terra pass; retired |
| H04 / `dicom-triplanar-svg` | Render masks at specified patient coordinates in axial/sagittal/coronal SVG views | Healthy Terra pass; retired |
| H05 / vector crop ownership | Complete diagram boundary without absorbing surrounding prose | Park separately; retained as a future extraction, not another combined deliverable |

## H01: PDF table lineage

Original, synthetic materials-survey PDF; no medical interpretation or copied
guideline content. A small fixed document supplies all values. Agent may inspect
images, use any library, or transcribe manually. Output reconstructs typed table
rows with explicit source-page attribution and cell-scoped notes. Repeated
headers, nonrectangular surrounding prose, page rotation and physical row splits
must not silently change the meaning of the table. Public contract defines all
normalization and scoring. Independent author transcription is compared with
generator ground truth; geometry inspection and simple extraction baselines
test legibility and which errors the fixture actually exposes.

Hypothesis: local extraction that looks plausible on individual pages loses
cross-page row/cell identity, units, or footnote ownership. A healthy model pass
is evidence against this fixed snapshot. Source failure rates do not transfer.

## H02: Chat round recovery

A deterministic simulated many-to-many chat system accepts timestamped events
and emits worker jobs and room replies. The submitted coordinator owns durable
JSON state. Independent logical recipient slots may share workers; workers may
serve multiple rooms; reply order is per room. Worker restarts and task retries
have distinct identities. A timeout can move a slot to its next worker, but a
late verdict must not settle the replacement. Replayed input, missing delivery
receipts and a coordinator restart must preserve logical identity. All semantics
are public; the verifier controls schedules rather than waiting on real clocks.

Hypothesis: a locally reasonable retry path corrupts another logical request or
replays an already completed effect. A tiny idle polling loop alone is rejected
as easy. No Lark connection, real external messages, protocol attacks, or access
control behavior is part of this task.

## Frozen execution protocol

This is research execution authorized by the current request, not hygiene work.
For each candidate: author controls, strongest simple permitted baseline,
targeted incorrect controls, source freeze, then one Harbor 0.18.0 oracle and
nop run. Only a healthy oracle=1/nop=0 permits one Codex Terra/high diagnostic
with Harbor 0.14.0, Docker, 1,800 agent seconds, one concurrent model trial,
the existing explicit subscription proxy, and normal Internet/image access.
Do not reduce time, ban libraries, or add requirements after seeing a pass.
Retire a healthy easy pass. For a completed zero, inspect the full trajectory
and independently reproduce the mismatch before deciding whether to advance.
At most one repaired retry for an infrastructure error, preserving both runs.
Final Sol/Opus qualification is outside this diagnostic protocol and remains
owned by [requirements](../requirements.md).

## Medical-imaging additions from later user messages

Two later messages in this active conversation add H03 and H04. Their stable
message IDs are not exposed. The first begins “another idea is to build sanity
annotation verifier for dicom labeling”; the clarification begins “you can give
the total labels list, the rest can be/should be figured out at testtime”.
The clarification explicitly supersedes a proposed public anatomical rule list:
the agent must infer anatomical expectations from the scan and its coverage.
A missing heart in a full-thorax scan is the user's example. Partial coverage
is a necessary negative control, not a hint disclosing which case is mutated.

H04 comes from the same clarification: a prior chat struggled with SVG axial,
sagittal and coronal views. No exact historical trace is recovered yet. A new
coordinate-to-render task will use rendered per-label Dice, not SVG source
similarity or a whole-image score dominated by background. Display convention,
pixel-center sampling and coordinate frame must be specified because several
view orientations are legitimate. These are geometry-interface definitions,
not anatomical hints. Keep H03 semantic judgment separate from H04 rendering.

Primary-source screen: DICOM PS3.3 2026c Image Plane Module defines BIPED patient
axes and row/column spacing; TotalSegmentator's current total map has 117 labels,
including five lung lobes and left/right ribs 1–12. The small official dataset
is CC BY 4.0. Its reference test CT and segmentation differ in slice extent
(112 versus 30), so they cannot establish a full-thorax missing-heart case.
The selected source is subject s1245 from the versioned small subset v2.0.1.
Selective ZIP-range retrieval downloaded 16,052,313 bytes for its CT and 117
mask files, avoiding the complete 3.24 GB archive. The source CT has 181 slices;
heart and all five lung-lobe masks lie within its acquired superior/inferior
extent. First-rib masks touch the boundary, so this case cannot support a
complete-rib-count assertion. [Source receipt](../evidence/br003-medical-source.json)
retains version, license and per-file hashes. Derived fixtures contain synthetic
patient fields and new UIDs, with CC BY 4.0 attribution and the label-map license.

Sources: [DICOM Image Plane Module](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.2.html),
[TotalSegmentator](https://github.com/wasserth/TotalSegmentator),
[official small subset](https://zenodo.org/records/10047263).

The same diagnostic stopping rules apply after each new candidate's author
controls. Runtime limits should reflect measured coded verification costs;
the 1,800-second reasoning allowance stays unchanged.

## Imaging contracts and controls

H03 provides five correlated packets from this one source: a clean full scan,
heart omission, exchanged upper-lobe labels, a clean superior crop, and a seventh
rib assigned to the wrong side. Packet and scan names are opaque. The callable
must work under renamed paths; no public anatomy rules, expected counts or
mutation descriptions are supplied. Its four requested labels keep the verdict
small while the complete taxonomy and annotations support contextual reasoning.
Known controlled changes determine truth. This is gross annotation QA, without
expert clinical certification or claims about arbitrary patients. The bounded
author control suite takes about 2.36 seconds locally; a 120-second batch limit encourages
coded checking without compressing the model's 1,800-second reasoning allowance.

H04 rigidly tilts a downsampled source by 17 degrees around z and 11 around x,
then encodes real CT instances and sparse DICOM BINARY SEG frames. Local segment
numbers and sequence/file order are permuted. Four physical query points yield
12 views. Expected masks come independently from the original NIfTI array and
transformed affine, bypassing the DICOM reference decoder. CairoSVG renders the
submitted SVG; each nonempty label must have Dice >=0.98, and absent labels must
remain absent. Black/transparent background does not contribute. All SVG
techniques, including embedded raster masks, are permitted. Author validation
takes about 0.54 seconds locally; Docker verifier timings are reported separately.

Both SEG encodings were read back through highdicom using source references and
matched every encoded voxel. The author oracle's 72 label/view comparisons are
exact; mirrors, transposes, empty canvases and bounding boxes are rejected.
These are solvability and discrimination controls, not model difficulty results.

## Outcomes

All four Terra/high diagnostics completed normally, once each, and passed.
Eight Docker controls completed with oracle=1/nop=0, no exceptions and matching
historical Harbor task checksums. There were no model infrastructure attempts,
retries or genuine failures in this round. All four snapshots are retired under
the predeclared stopping rule; no further model trials or difficulty inflation
were performed after a healthy pass.

| Candidate | Final verifier | Agent seconds | Verifier phase seconds | Disposition |
| --- | --- | ---: | ---: | --- |
| BR-003/H01 PDF | 4/4 content/geometry checks | 146.066 | 11.967 | Retired |
| BR-003/H02 chat | 22/22 traces | 197.254 | 12.894 | Retired |
| BR-003/H03 anatomy | 5/5 packets | 293.135 | 13.364 | Retired |
| BR-003/H04 SVG | 12/12 views; 72 label comparisons, all Dice 1.0 | 217.431 | 12.847 | Retired |

The 1,800-second allowance is unchanged. Phase timings include verifier container
overhead and differ from local author-control timings. They are observations on
these fixtures, not a model-speed benchmark. [Round receipts](../evidence/br003-round-summary.json)
include every individual result, output hashes, frozen source checks and exact
local snapshot archives. Harbor includes ignored Python caches in its digest;
those bytes match across each task's controls and model run and are preserved
locally. The authored source freezes exclude rebuildable cache files. A fresh
clone's Harbor checksum may therefore differ while retained input bytes match.

[Trajectory inspection](../../catalog/analyses/br003-work-history.md) explains
the solutions and their limits. Terra used permitted text/geometry inspection
for the PDF, a durable transition system for chat, DICOM affine/source mapping
for SVG, and patient-coordinate laterality plus coverage and CT tissue checks
for anatomy. The anatomy run initially transposed DICOM row/column directions,
then diagnosed and repaired it before completion. That intermediate failure
does not count as a benchmark failure. No public anatomical rules were added.

The wrong-side-rib packet moves the left seventh-rib mask into the right label
in a categorical volume; the left label becomes empty as a consequence. Only
the requested right label is graded. This exact mutation is preserved rather
than described as an independent binary-mask copy retaining both labels.

The scoped history search confirmed repeated PDF crop defects and resident
lifecycle/queued-work problems. A later global title screen found no relevant
additional SVG conversation. It did not recover the exact recalled SVG or
verdict-timeout incident. Historical reports do not become Terra benchmark
failures by being used to design a new fixture.

Human-authored submission experience sections and final qualifying trials remain
outstanding: 0/6 standard, 0/2 adversarial, no final task selected. Fixed-cohort
recognition and library-assisted solutions are permitted by these contracts;
neither a pass nor a miss measures broad medical or document-processing ability.

## Next selection decision

Keep the four prototypes as calibration and fixture infrastructure. The original
diagram-boundary failure with prose wrapped around vector flowcharts is the
closest untested historical crux; H01 tested table lineage instead. H05 remains
parked until a compact authentic source fixture and independent boundary truth
are established. For anatomy, a future task would need evidence of a harder
semantic confusion than gross absence or contralateral assignment, with clean
coverage controls and a small target verdict. These are proposed investigations,
not authored tasks or completed experiments. Do not stack more labels, formats,
or time restrictions onto the passed versions. The benchmark-backed shortlist
retains overall priority; this authorized history-derived round makes no new
promotion.

## Follow-up: SVG solution-provenance audit

On 2026-09-15 the user questioned whether perfect Dice came from copying the
generation code. The [audit](../../catalog/analyses/br003-svg-provenance-audit.md)
checks the launch, all eight paired tool calls, public prompt, input archive,
container construction, output hashes and exact patch-to-artifact lineage.
No private solution/generator/GT read or additional model assistance is observed.
The original container image was not retained for a direct filesystem audit.
The corrected interpretation is exact agreement on a strongly specified
mask-resampling fixture, not unaided anatomical drawing. The pass and retired
disposition remain unchanged; no new model trial was run.
