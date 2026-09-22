+++
schema_version = 2
kind = "idea"
id = "dental-cbct-agent-pilot"
group_id = "anatomy-audit"
title = "Dental CBCT: tooth audit and canal correction pilot"
idea_state = "exploring"
source = "codex://threads/01a0c25e-4b08-7552-8379-90a2b50ad40f"
+++

# Dental CBCT: tooth audit and canal correction pilot

Can an agent use native CBCT views and fixed tools to correct tooth identity and masks, then trace mandibular canals, without access to evaluation labels?

## Latest closeout — F018 v3 pair, 2026-09-22

Actor: assistant, completing the user's authorized paired repeat and babysitting.
Both fresh attempts and terminal reviews are complete; no further inference is
queued. The [final comparison](../findings/dental-f018-contract-v3-comparison.md)
records macro Dice 0.71084 without an example and 0.82395 with F008, exact replay,
all 29 dataset tooth IDs correct in both, and stronger tooth/pulp geometry with
the example. The reference solver used deformable anatomical transfer followed
by target refinement. Incisive canal localization and one molar's pulp remained
poor; the native-coordinate views and saved-prior diagnostics explain why a
normal example does not guarantee correct small-structure correspondence.

Original GT, scores and prior findings are preserved. Both experiments are closed;
clinical laterality, occupied-pulp and restoration conventions remain unadjudicated.
This one repeated development case does not isolate the effect of the instruction
rewrite or establish population benefit. Reopening inference requires new user
authorization and a separately fixed question/design, rather than retries of these
completed attempts. Source: codex://threads/01a0c3e5-6fb0-7321-a930-a7251047e7ad.

## Earlier closeout — 2026-09-22

The user subsequently authorized the new F018 v3 pair recorded below. This
paragraph describes the earlier completed conditions, not the new live queue.

Actor: assistant, during user-requested worktree closeout. Five authorized CT-only
experiment conditions and their saved-output reviews are complete. Their stages
are closed; no further trial is queued. Read the final comparison and fine-structure
analysis below for current findings. Earlier acquisition blockers and launch
updates are dated history, not current dispatch instructions. Reference laterality,
restoration subtypes and occupied pulp conventions remain unresolved; closing the
work does not settle those questions or replace any recorded score.

## Prior findings

### F018 v3 paired repeat — user decision, 2026-09-22

The user authorized revising the instructions using best judgment for fairness
without target leakage, then retesting F18 with Astra-medium in two settings:
without an example and with the previously selected original F08 CT/annotation,
with babysitting. Source: codex://threads/01a0c3e5-6fb0-7321-a930-a7251047e7ad.
This is new authorization after the earlier closeout, not a restart of an old run.

Assistant implementation: [v3 paired protocol](../methods/dental-f018-contract-v3/README.md)
and its common instructions define general operational boundaries and retain
uncertainty about agreement with original annotations. Target-specific findings,
counts, coordinates, cutoffs and prior methods are excluded from solver inputs.
One fresh medium attempt per setting, two-hour ceiling each, no new tools/weights,
no retries or feedback, original F018 GT unchanged, separate scoring components,
and the inherited 20% account reserve. New experiments:
[without example](../experiments/dental-f018-contract-v3-astra-medium/protocol.md)
and [with F008](../experiments/dental-f018-reference-v3-astra-medium/protocol.md).
The local v3 operation packet and queue are authoritative for live execution.

Assistant observation: both conditions passed isolation and native oracle/nop
controls. The no-example attempt `attempt-3baf235736e24536` launched at
2026-09-21T17:03:51Z (2026-09-22 local); actual inference, pinned image, internal
network, log-only mounts and retained transport capture were verified. The F008
condition remains queued until its predecessor's terminal review. The existing
dental heartbeat is active and points to the new v3 packet/current task.

At 2026-09-21T17:45Z, the assistant completed the first terminal review: valid
output, no terminal exception, exact scoring replay, macro Dice 0.71084 in
1428.15 agent seconds. All 29 matched tooth identities agree with dataset labels;
pulp macro is 0.69887, main canals 0.36062 and small canals 0.14324. These remain
descriptive original-reference metrics. No forbidden data access was observed
in retained commands/transport; invisible pretraining is not adjudicated.
The authorized F008-reference condition then actually launched as
`attempt-72c26b83987d4409`; live inference and isolation were verified. It receives
no information from the first condition and is now the sole running dental unit.

### Dataset contract source audit — assistant observation, 2026-09-22

The user asked whether the unresolved occupied-pulp convention reflects the same
under-specified dataset setup that caused earlier axis confusion, and requested
careful reading of the original documentation. The
[source audit](../findings/dental-dataset-contract-audit.md) found an explicit FAQ
warning that NIfTI direction metadata is not physically accurate; a June 2025
P-subset annotation update; taxonomy/scorer discrepancies; and missing operational
rules for occupied pulp and several class boundaries. The original TF3 structured
proposal describes expert agreement and review rather than a detailed public
boundary manual, and predates the final 77-class taxonomy.

The [separate draft](../methods/dental-dataset-contract/instruction-v3-draft.md)
adds explicit coordinate, encoding, provenance and scoring requirements while
leaving unadjudicated semantics visibly unresolved. This qualifies claims that
v2 settled all annotation rules; it does not invalidate the measured method
failures or establish clinically incorrect GT. No trial, new solver tool,
reference change or scoring change was authorized or performed in this audit.

### ToothFairy3 partial download recovery — 2026-09-21

User requested extracting a few cases from their incomplete Chrome ZIP download
so they can stop the full download. Three independent scans (F_001–F_003) and
`dataset.json` were recovered under `runs/toothfairy3-partial-20260921/source/`
(367 MB total); all member CRCs, lengths and scan gzip CRCs pass. Native NIfTI
headers open with isotropic 0.3 mm spacing. No source download bytes were changed.

**Current limit:** the inspected prefix contains image members only. Matching
labels have not been recovered and these are not yet paired GT fixtures. A
bounded HTTP-range retrieval of the matching labels requires a working source
URL; Chrome Copy download link failed and the user was asked for that link.
Reopen paired-grid/label/visual validation after the masks are acquired. The
local README and extraction manifest retain offsets, checksums and limitations.
Archive JSON says CC-BY-SA 4.0 but the official page says CC-BY-NC-SA; preserve
this unresolved provenance discrepancy. No model ran and no clinical GT claim
is made.

### Separate retrieval: official viewer fallback — 2026-09-21

A bounded archive range request hit the login boundary (302). The authenticated
browser probe remains pending the user's handling of Chrome's console-paste
warning; range support is not established. Independently recovered the official
website viewer's **F_018 image/GT pair** via observed direct media links. Local
`runs/toothfairy3-partial-20260921/viewer-f018/` contains the pair and its parent
folder retains source URLs, hashes, validation and input/GT overlays.

Both gzip streams and paired geometry pass. The viewer image array is exactly
equal to the archived F_018 image array, but z-axis affine metadata differs.
Preserve both sources; pair the viewer mask with the viewer scan. The 69 present
label values include teeth, pulp and canals. Sampled visual QC is useful but
clinical completeness remains unadjudicated. No model trial occurred.

### Downloaded STS validation — 2026-09-21 follow-up

The user explicitly authorized downloading and checking the three suggested
Hugging Face ROI cases. [Retained audit](../findings/dental-sts-gt-audit.md) and
[hash/validation receipt](../findings/evidence/dental-sts-gt-audit.json) supersede the earlier
unverified mirror description for these cases. All six files downloaded, matched
upstream hashes, and passed paired-grid/independent-reader checks. **The inspected
masks do not contain per-tooth FDI GT:** ordinary tooth regions share label 1.
Every mask has a full-image non-anatomical terminal plane; ROI_L_001 additionally
has two internal all-label-1 planes. Original files remain unchanged. No model ran.

**Assistant recommendation:** reject raw-mask anatomical scoring and tooth-number
evaluation on these fixtures. Case 003 may support a later binary-region pilot
after explicit reference interpretation and boundary review. Case 001 requires
re-annotation or excluded-slice scoring, not silent background replacement. This
does not invalidate the entire STS release or establish where the issue originated;
the publisher archive was not compared. Actual native-scan overlays are linked in
the audit and replace schematics for inspecting these downloaded cases.

Source survey on 2026-09-21. The user requested dental CT tasks with samples and
ground truth, and a proposed agent test. This is a proposal, not trial authorization.
`med list dental` found no prior dental idea; the existing repository survey has
DENTEX panoramic X-ray tasks, which do not supply volumetric CBCT references.

### Candidate sources and what their references support

| Source | Samples and GT | Proposed task and access boundary |
| --- | --- | --- |
| [ToothFairy2](https://ditto.ing.unimore.it/toothfairy2/) | 480 released CBCT volumes, paired voxel masks, 42 classes; MHA format. Teeth use an extended FDI label scheme alongside jaws, canals, sinuses and restorations. | Tooth identity/mask audit and canal segmentation. Account required. Freeze the corrected release: the official changelog includes label and geometry fixes. |
| [ToothFairy3](https://ditto.ing.unimore.it/toothfairy3/) | 532 NIfTI volumes, 77 classes; adds pulp cavities and small canals. P/F subjects overlap TF2; 52 S subjects come from another scanner. | Preferred expandable source. Use tooth labels for identification and canal masks for correction. Account required. The page documents RPI orientation and a conversion script. |
| [Original ToothFairy](https://ditto.ing.unimore.it/toothfairy/) | 153 volumes with dense and sparse canal labels, 290 with sparse labels only; NumPy images and labels. | Canal tracing. Only dense-label cases support whole-volume mask scoring; sparse-label absence is not a negative label. Account required; official challenge test remains private. |
| [STS-Tooth](https://zenodo.org/records/10597292) | Publisher-hosted CBCT image/mask archive, 31.8 GB in 15 multipart files. [Dataset paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11747459/) describes annotation and NIfTI packaging. | Tooth segmentation fallback with directly listed download files. Establish patient counts, label semantics and full-FOV versus ROI subsets from the archive before selecting cases: publication counts mix slices and volumes. No archive downloaded here. |
| [ToothFairy4](https://ditto.ing.unimore.it/toothfairy4/) | CBCT paired with clinician-authored Italian reports and English translations. Page advertises 625 patients and 1001 reports per language. | Later structured reporting/audit track. Account required. Reports can omit visible findings; they are not exhaustive voxel/pathology truth. English is LLM-translated with sampled clinician checks in training. |

TF4 metadata needs reconciliation: listed subset sizes sum to 632 rather than
625, and report-count categories sum to 624 patients. Use downloaded case manifests
before making split/count claims. TF4 P/F/S cases reuse TF3 acquisitions with an
orientation warning; never treat release names as independent patient cohorts.

The [TF3 challenge dataset page](https://toothfairy3.grand-challenge.org/dataset/)
search index states CC-BY-NC-SA and private test data. Direct fetch later returned
403. Retain the actual release license on acquisition rather than borrowing a
mirror's license. This survey verifies documentation, not download entitlement.

### Concrete sample and evaluator entry points

The official [TF3 interactive track README](https://github.com/AImageLab-zip/ToothFairy/blob/main/ToothFairy3/Interactive-Segmentation/README.md)
links an [organizer demo folder](https://drive.google.com/drive/folders/1Dd8B_p-hAE2xhMRwafmkg2BaDAWDW0xH?usp=sharing):
the algorithm README requests its `test` folder; the track README requests
`evaluationgroundtruth.tar.gz`. These are documented training demos, not the
private challenge test set. The folder endpoint resolved but its inventory was
not readable through the web tool; paired files, sizes and hashes remain unverified.

The [algorithm instructions](https://raw.githubusercontent.com/AImageLab-zip/ToothFairy/main/ToothFairy3/Interactive-Segmentation/algorithm/README.md)
describe clicks simulated from input labels. Therefore supplied challenge clicks
are reference-assisted prompts, not evidence that an agent can discover an error.
The [evaluator](https://raw.githubusercontent.com/AImageLab-zip/ToothFairy/main/ToothFairy3/Interactive-Segmentation/evaluation/README.md)
documents Dice/HD95 for 0–5 clicks, final metrics and area under the interaction
curve. Agent-selected clicks require a separate condition with no GT feedback.

[ToothSeg](https://github.com/MIC-DKFZ/ToothSeg) supplies tooth segmentation/numbering
code, [checkpoints](https://zenodo.org/records/14893540) and label-aware versus
label-agnostic instance scoring. Its internal dataset is unavailable. It documents
a TF2 70:30 split in fold 5; inspect actual checkpoint training membership before
claiming held-out evaluation. Code availability does not establish local runtime
readiness or GPU feasibility.

Excluded from the immediate CBCT shortlist: DENTEX (panoramic X-ray),
[3DTeethLand](https://crns-smartvision.github.io/teeth3ds/) (intraoral surface scans),
and [Open-Full-Jaw](https://github.com/diku-dk/Open-Full-Jaw) (released meshes/axes
do not by themselves establish paired native CT availability).
[CTooth](https://github.com/liangjiubujiu/CTooth) has historical access notices and
points to STS; avoid representing it as a verified independent ready download.

## Recommended pilot

**Question:** Does iterative image inspection improve tooth identity and mask
correction over a fixed pipeline, without damaging correct structures?

1. Acquire one demo image/GT pair for plumbing. Verify native grid, spacing,
   orientation, label mapping, source revision/license, hashes and visible coverage.
   Preserve originals. Inspect overlays in all three planes. This step remains undone.
2. Select six patient-disjoint cases after author inspection: two for development,
   four frozen evaluation cases. Aim for ordinary dentition, gaps/partial FOV,
   restorations/artifact and a new-scanner example when present. Define selection
   before any target-agent run; do not tune the set based on its failures.
3. First task: give CBCT plus a fixed imperfect tooth segmentation. Ask the agent
   to identify wrong FDI IDs, merged/split teeth and missed visible teeth, then
   submit corrected NIfTI labels and JSON edits with native-coordinate evidence.
   Treat absent-from-image and absent-from-mask separately. Missing-tooth claims
   need coverage adjudication; a zero-valued GT class alone is insufficient.
4. Prefer frozen out-of-fold predictions as the input. If infeasible, use a
   separately named synthetic corruption pilot with label swaps, local merges,
   omissions and untouched controls. It measures recovery from authored errors,
   not real baseline error prevalence. Do not mix these conditions.
5. Give a native multiplanar viewer, zoom/window/crop, component inspection,
   relabel/split/merge tools and scripts. Preinstall the same tool stack for all
   conditions. Suggested exploratory cap: 30 minutes and 40 tool calls per case;
   freeze model, effort and budgets before launch. One attempt per case initially.
6. Compare unchanged input, deterministic postprocessing and the agent using the
   same input/tools. Add evaluator-only oracle and deliberately empty/wrong-label
   controls. Keep untouched teeth as collateral-damage controls.
7. Score instance detection and FDI identity separately, then per-tooth Dice,
   surface error in mm, corrected errors and newly introduced errors. Report
   paired case-level changes, time/tokens/tool calls, and unresolved labels. Tune
   tolerances only on development cases; a four-case screen cannot rank models
   generally. Investigate disagreements rather than silently relabeling GT.

**Second task, after the first fixture works:** trace/correct left and right
mandibular canals on the same eligible scans. Let the agent choose up to five
positive/negative clicks; hold the interactive segmenter fixed. Score Dice/HD95
after each interaction, centerline coverage, gaps, wrong-side edits and false
extensions. Curves/endpoints derived from dense masks are derived references,
not independently annotated endpoints. Do not give evaluator scores back during
an attempt. A GT-click oracle is an upper-bound control only. A working interactive
model must be provisioned and smoke-tested before this condition is called runnable.

**Later extensions:** tooth-to-canal minimum distance or nearest tooth from paired
masks, with a declared surface-distance convention and frozen reference geometry;
this tests geometric measurement, not extraction safety. TF4 can support structured
report facts (tooth, side, restoration, uncertainty), with reviewer-adjudicated
facts and omission-aware scoring. Text similarity or an LLM judge alone is inadequate.

## Leakage and evidence boundary

Keep reference masks, reports, filenames/case mappings, GT-derived prompts and
scorers outside the solver mount. No runtime access to dataset sites or author
workspace in the closed-book condition; retain filesystem/network/tool traces and
state the audit's limits. Check patient overlap across releases and training overlap
for every pretrained tool. Public data may already be in model pretraining, so
local hiding cannot establish globally unseen cases. The claim is bounded agent
improvement on disclosed fixtures.

## Decision and next action

### Visual task explanation

2026-09-21 — User requested input/expected-output visuals. An inline explainer at
`/Users/zhangqy/.codex/visualizations/2026/09/21/01a0c25e-4b08-7552-8379-90a2b50ad40f/dental-task-inputs-outputs.html`
shows tooth-number correction, merged-mask separation, canal correction and
structured reporting. Its anatomy and proposed outputs are explicitly schematic,
not patient evidence or agent results. Each view distinguishes solver input,
submission and hidden GT. An expandable, attributed
[ToothSeg author figure](https://github.com/MIC-DKFZ/ToothSeg/blob/main/figures/Overview_Figure.png)
provides real CBCT/segmentation context. The figure is remotely displayed; no raw
scan or GT was acquired. Local preview checks exercised all four selectors,
verified source-image rendering and checked mobile overflow; desktop/mobile
screenshots were inspected. This explains the proposal without changing its
authorization or scientific status.

2026-09-21 — **assistant recommendation:** start with TF3/TF2 tooth identity and
mask auditing, then canal interaction; defer broad diagnosis/report generation.
Source: [current user task](codex://threads/01a0c25e-4b08-7552-8379-90a2b50ad40f).
No user selection, dataset download, runtime installation or model trial occurred.

Proceed to fixture preparation when authorized and a paired sample is accessible.
Reconsider source choice if access, label quality, checkpoint overlap or runtime
requirements prevent an independent, inspectable pilot. Canal experiments should
be owned by tubular-anatomy and link this source survey; leave current coronary
writers untouched.

### Authenticated archive range support confirmed — follow-up

The user manually enabled console pasting, and a bounded authenticated probe
returned HTTP 206 for the last 256 KiB of the 29,305,037,433-byte ZIP. Its ZIP64
directory contains 1,067 members; image member CRCs/sizes/offsets agree with the
local partial file. F_001–F_003 masks can be fetched in one 2,421,086-byte range.
Mask retrieval is currently pending restored Chrome control after the window
state became empty and screenshots unavailable; user was asked to restore the
visible dataset console. This supersedes the earlier range-support uncertainty.

### GT label briefing and candidate selection — 2026-09-21

User requested a label briefing and one interesting / one challenging case.
Local `dataset.json` contains **77 foreground classes plus background** (78 values):
32 FDI tooth IDs, 32 corresponding pulp IDs (tooth ID + 100), 2 jaws, 2 inferior
alveolar canals, 2 sinuses, pharynx, 3 restoration types, 2 incisive canals and
lingual canal. These are segmentation labels, not comprehensive diagnosis/report GT.
Single-channel tooth and pulp regions are disjoint; freeze the union convention
if scoring a whole tooth rather than separate semantic classes.

**Assistant recommendation, not a user decision:** choose F_018 as the informative
first tooth-identity/mask-audit pilot. Its official viewer pair is technically
validated and contains 29 tooth/pulp pairs plus all five canal IDs; the small
canals have 279–393 voxels. F_002 is the harder candidate among four inspected
scans, based on conspicuous restoration-associated streaks with a common display
window. Its matching masks remain pending, so this is provisional selection, not
a scoring-ready fixture or a measured model-difficulty ranking.

Retained local `case-selection-recommendation.json`, `four-case-screening.png`
and `recommended-two-cases.png` under `runs/toothfairy3-partial-20260921/` contain
the selection evidence and actual input/GT visuals. Recommend authored label
swap/omission for the clean pilot, then posterior-tooth merging/artifact-leakage
correction after F_002 GT recovery and boundary review. No model ran.

### CT-only Astra/medium run authorized — 2026-09-21

**User decision:** run Astra at medium reasoning to regenerate segmentation from
original CT, with no methodological/scoring leakage, and babysit its progress.
This replaces the mask-correction proposal for the current pilot. **Assistant
implementation choice:** one F_018 attempt with a two-hour ceiling; F_002 remains
deferred because its paired reference is unavailable. See
[the experiment protocol](../experiments/dental-ct-only-astra-medium/protocol.md).
The solver receives CT voxels, the complete semantic ID map and a neutral output
contract. GT, case identity, case-specific observations and evaluation rules are
held outside the solver; model-only proxy access is enforced on an internal
container network. Private oracle/nop controls passed. Actual model work began
at about 08:59:14 UTC after a separately retained pre-inference authentication
repair. A task heartbeat monitors progress. No segmentation outcome is claimed yet.

### Completed CT-only attempt — assistant observation, 2026-09-21

The authorized attempt finished voluntarily in 15m47s. Its valid output has
original macro Dice 0.03939 and foreground Dice 0.96861, independently replayed.
Systematic opposing left/right IDs account for much of the discrepancy: a fixed
post-hoc side permutation yields diagnostic macro Dice 0.69246, without changing
the answer or accepted score. The viewer header/GT side convention needs
adjudication before attributing identity failure. No observed dataset/GT access
appears in the retained trace. See [the detailed finding](../findings/dental-ct-only-astra-medium.md).
The monitor closes after terminal review; no new trial is authorized by this finding.

### Two further experiments authorized — user decision, 2026-09-21

User explicitly requested fresh Astra-xhigh on F018 and Astra-medium on F002,
with F002 CT/GT prepared from the completed ZIP. New experiments:
[F018 xhigh](../experiments/dental-f018-astra-xhigh/protocol.md) and
[F002 medium](../experiments/dental-f002-astra-medium/protocol.md).
F018 keeps the earlier task bytes unchanged, including native geometry, for a
controlled effort comparison. F002 uses its archive-native CT/GT pair; selected
ZIP CRCs, dimensions/affines, allowed labels and sampled overlays passed, as did
its exact-reference/no-output lifecycle and malformed-output scorer controls.
Archive and viewer F018 voxel arrays (CT and GT) match, despite different z
headers; the unresolved orientation interpretation is retained, not fed to solvers.

**Assistant scheduling choice:** sequential two-hour ceilings on the existing
four-CPU/~8-GB Docker VM. F018-xhigh began at 10:49 UTC; F002-medium is prepared
and queued for dispatch after terminal boundary review. Both are diagnostic
explorations with separate private GT/evaluators, isolated model-only transport,
neutral CT-plus-label inputs and no earlier outcome/methodology feedback. The
existing current-task heartbeat is active for both experiments. No additional
attempts, inference retries or extensions are authorized by this record.

2026-09-21 11:37 UTC — assistant observation: F018-xhigh completed in 31m22s;
replayed original macro Dice 0.04477 (medium 0.03939), fixed-side diagnostic
0.70342 (medium 0.69246). Both retain the unresolved reference-convention issue.
See [effort comparison](../findings/dental-f018-effort-comparison.md). F002 is
prepared but waiting for shared Docker capacity because an unrelated CT-organ
trial is active. The monitor will dispatch it when resources are free; no model
retry or cross-case feedback is introduced.

2026-09-21 11:57 UTC — assistant action: shared Docker capacity became free;
the unchanged F002 task and controls were reverified and the authorized fresh
Astra-medium attempt `attempt-4338cd3dae024fc8` launched. Actual inference and
live container isolation were confirmed. It receives no findings from either
F018 attempt. The heartbeat now monitors this final run; no further dispatch.

2026-09-21 12:16 UTC — assistant observation: F002-medium completed voluntarily
in 15m46s, with a valid output and no execution exception. Independent replay
matches original macro Dice 0.04964 and foreground Dice 0.87445. Fixed-side
diagnostic is 0.46338 and does not replace its score. All five GT canal IDs were
left empty; restoration and tooth-identity disagreements remain. Retained calls
show no dataset/GT retrieval. Both requested experiments are terminal-reviewed;
the monitor is closing, with no more launches. See
[F002 findings](../findings/dental-f002-astra-medium.md).

### Trace root-cause review — assistant observation, 2026-09-21

At the user's request in
[the follow-up task](codex://threads/01a0c3e5-6fb0-7321-a930-a7251047e7ad),
all three completed dental traces and saved programs were examined. Independent
confusion-matrix replay reproduces every original per-label/foreground Dice;
original artifacts remain unchanged. The
[root-cause finding](../findings/dental-trace-root-causes.md) includes pseudocode,
a process diagram, native-coordinate CT overlays, and
[reproduction scripts](../methods/dental-trace-audit/README.md).

The strongest attribution is a missing trustworthy orientation contract: all agents
followed the supplied affine, while GT sides oppose it. The publisher documents
a special orientation and its inspected conversion script changes arrays while
copying metadata; it was not executed and clinical laterality remains under
review. After the fixed side-ID diagnostic, teeth overlap reasonably but canals
and pulp remain weak. Xhigh improves main-canal and sinus overlap substantially
while pulp does not improve. F002's fixed pulp intensity cutoff discards 6,359
of 10,433 reference voxels surviving its distance gate. Its bridge/crown
disagreement is separate from laterality and requires annotation-rule review.

**Assistant recommendation:** adjudicate orientation, specify dataset-wide
annotation/abstention rules, and report shape, identity and fine structures
separately before drawing broad capability conclusions. Preserve case-specific
blindness and all original scores. Reopen for a versioned, controlled trial only
after these prerequisites and user authorization; no additional model ran here.

### Reference-example comparison — user decision, 2026-09-21

In [the follow-up task](codex://threads/01a0c3e5-6fb0-7321-a930-a7251047e7ad),
the user accepted the first three audit recommendations and explicitly requested
two fresh Astra-medium conditions: corrected/generalized contract without an
example, and the same with an original-dataset CT/annotation example. The user
selected **F_002 for both targets**. No extra tools are requested.

**Assistant implementation:** [versioned protocol](../methods/dental-reference-ablation/README.md),
explicit native RPI semantic naming with original grid retained, general boundary/
uncertainty rules and separate geometry/identity/pulp/canal measures. Acquisition
laterality and restoration subtypes remain unadjudicated. F_008 was selected after
source-inventory and visual QC; all 32 teeth/pulps and five canals are labeled,
with no obvious restoration artifact in reviewed views. It is not clinically
certified normal and has no restoration examples. A preliminary F_031 selection
was superseded before freezing or inference after a suspect pulp region was seen.
Two native experiments are prepared sequentially under the babysit workflow.
No earlier result, target-specific hint or first-condition feedback reaches either
solver. One attempt per arm; compare exploratory deltas and actual example use.

2026-09-21 13:40 UTC — assistant action: both v2 task packages passed live
isolation/file checks and exact-reference/no-output controls (1.0/0.0 each).
Shared capacity became free and the authorized F002 no-example Astra-medium
attempt `attempt-be5fae3cdf024941` launched. Actual inference and its pinned
internal-network/log-only-mount boundary are verified. The F008-example condition
remains queued for dispatch after terminal review, without first-arm feedback.

2026-09-21 14:22 UTC — assistant observation/action: the v2 no-example run
completed in22m55s with valid output, unchanged frozen inputs, no exception and
exact scoring replay. Macro Dice0.45423; whole-tooth shape0.77837, FDI accuracy
among detected teeth0.89474, pulp0.33788, main canals0.11176, small canals0.00149.
These are descriptive reference agreement, with original uncertainties retained.
No observed external dataset/GT access. The authorized example condition
`attempt-36ee0d66d0a64d55` began14:20 UTC and has already read the supplied F008
CT/mask. Live isolation verified. It receives no first-condition feedback.


2026-09-21 — assistant final observation: both authorized F002 attempts completed
with valid masks and exactly matching private scoring replays. The annotated F008
condition improved recorded macro Dice 0.45423→0.50117, correctly identified teeth
17/22→19/22 and main/small canal Dice 0.11176/0.00149→0.19641/0.12707. Pulp Dice
declined 0.33788→0.31470; identity-independent pulp precision and recall also fell.
Whole-tooth shape changed only 0.77837→0.78863. Agent time was 22m55s→49m04s,
so this is not an equal-realized-compute comparison. Reference use was confirmed
in registration, transferred labels, jaw priors and pulp calibration. No extra
library was installed; the attempted SimpleITK retrieval was blocked.

The [final comparison](../findings/dental-reference-example-comparison.md) links
the local full report, actual-method pseudocode, process diagram, native-coordinate
overlays, original output hashes and split evidence. All original scores remain
intact. Active-label denominator sensitivity is reported separately. Acquisition
laterality, restoration subtype rules and exhaustive reference correctness remain
unadjudicated. This single pair supports a local observation, not a general causal
claim. No further dispatch is authorized; the two-run supervision is closed.


### Fine-structure diagnosis — assistant observation, 2026-09-22

The user requested a deeper explanation of low pulp and canal scores even with
the annotated example. No additional inference was authorized or run. Read-only
analysis of saved arrays/programs found a pulp threshold that scores 0.765 on
matching example teeth but only 0.299 on true target tooth masks, misplaced canal
paths, and a prior-based correction that deletes 440/443 correct pulp voxels in
tooth 14. Near-saturated target voxels are also labeled pulp in GT, while the
agent interprets pulp as low-density space. The occupied/treated chamber
convention remains unadjudicated and was not fully settled by the v2 contract.

See [the measured mechanisms](../findings/dental-fine-structure-failure-analysis.md)
for native overlays, program-linked evidence and diagnostic controls. This adds
a specific annotation uncertainty without changing any original outcome.
Assistant recommendation: clarify that convention and use an adjudicated example
that demonstrates it before a future trial; separate canal localization from
width/extent. This is not a user decision to launch another experiment.
