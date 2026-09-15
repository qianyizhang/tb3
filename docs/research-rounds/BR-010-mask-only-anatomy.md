# BR-010 — From boundary inspection to anatomical consistency

**Status: retrospective investigation complete; two proposed candidates, no new
model trials or task packages.** This follow-up revises the recommendation to
lead with case 32. Historical BR-004 grades and snapshots remain unchanged.

## Source and scope

Captured 2026-09-15 from the DICOM annotation conversation. The user questioned
whether the small injected boundary defect was too picky, then requested:
“investigate a little on how sol/terra solve this kind of problem and propose
their blindspot,” suggesting masks alone with unary, pairwise and overall
geometry reasoning. The exact message text is available in this conversation;
a separately exported message ID was not captured.

Seven historical tool trajectories were inspected: Terra/max cases 28, 32 and
83; Sol/xhigh cases 32, 83, 46-v2 and 61-v2. The
[audit receipt](../evidence/br010-mask-reasoning-audit.json) records paths,
SHA-256 hashes, step anchors and a new independent coordinate reconstruction.
This is a targeted strategy audit, not a population-level capability estimate.

## What the agents actually did

| Observation | Evidence | Interpretation |
| --- | --- | --- |
| Both used volume/bounding-box inventories, connected components, CT intensity summaries and multiplanar views. | Terra 32 steps 18/23/31; Terra 83 17/26/44; Sol 32 19/23/34; Sol 83 17/22/33/47 | They already perform substantial quantitative QA. Basic shape/component defects are poor new difficulty hypotheses. |
| Terra solved the rib exchange using within-label fragment distances, cross-label distances and mirrored opposite-side rib matching. | Terra 28 steps 42/49/52/53; correct artifact 60/61 | Direct counterevidence to a blanket claim that Terra lacks anatomical or relational reasoning. These were diagnostic tools, not a validated clinical symmetry rule. |
| Sol examined eroded interiors, surrounding bone candidates, local occupancy, opening/closing and boundary-face concentrations. | Sol 32 34/44; Sol 61 41/48/49/50 | Its checks extend beyond a glance at a contact sheet; it can implement geometric algorithms. |
| The detailed axial kidney views in case 83 stop at the submitted-mask endpoint. Other planes contain the omitted pole. | Terra 83 11/32/44; Sol 83 11/35/46; retained BR-004 image reviews | Mask-driven inspection can underemphasize missing tissue. This does not prove that the model never saw the error. |
| Sol's case-32 numeric probe surfaced signal inside the actual extension, then it finalized an empty report. | Sol 32 step 34; output 47/48 | The issue includes interpreting or acting on evidence, rather than merely failing to access it. The original clinical significance/tolerance remains unvalidated. |
| Sol investigated neighboring labels around a detached heart component in case 46. | Sol 46 24/28/29/34 | Relational checks are present here too. The held source finding cannot be counted as an established model failure. |

The new reconstruction repeats Sol 32's two six-neighbor erosions and negative
HU query. Its three remaining left-kidney coordinates, in task `[z,y,x]` order,
are `[94,62,52]`, `[95,62,52]`, `[94,63,52]`, with HU values -83, -35, -65.
All three belong to the planted extension. The source comparison was performed
only by this retrospective review; Sol had no clean masks. Negative HU alone
does not adjudicate an anatomical defect.

## Blind spots worth testing

1. **Coverage guided by the answer under review — observed behavior.** The mask
   supplies both the hypothesis and the locations to examine. Boundary omissions
   can escape some views; repeated images need not supply new evidence.
2. **Local plausibility without a final consistency check — plausible mechanism.**
   The agents collect useful signals but can finish without resolving them into
   a definite finding. The permissive original anatomy contract may contribute.
3. **Combining several individually reasonable labels into one consistent
   interpretation — untested hypothesis.** The traces contain pairwise checks,
   especially Terra's successful rib analysis. They do not establish a weakness
   at global assignment; a task must test it before we make that claim.
4. **Weak anatomical knowledge — unresolved.** No matched prior-information
   contrast was run. Current evidence is insufficient to diagnose this cause.

## The mask-only boundary

Removing CT changes what can be established. A short kidney mask can describe
a genuinely short organ or an omitted pole. Smoothness and location alone do
not distinguish those possibilities. Do not transfer the case-32/83 boundary
answer keys into a mask-only task.

Instead ask whether **the assigned identities and relationships satisfy a
specified anatomical contract**, given trusted anchors and declared exceptions.
Shape is evidence, not a requirement that every patient match an average atlas.
Surgery, absent structures and incomplete scan coverage require supplied,
verified context; an ambiguous case should be excluded before testing.

## Candidate BR010-M01 — Coherent anatomical identity error

**Task:** Audit a compact group of intact vertebral and rib instances (roughly
12–24 masks). Their geometry is fixed; some semantic labels are wrong. Return
the affected instance IDs and corrected labels. Supply masks, physical
coordinates, stable instance IDs, trusted landmarks, coverage information,
label conventions and a basic viewer. The source labels are not supplied.

**Hypothesis:** A coordinated identity error can preserve plausible individual
shapes and some local relationships while conflicting with the complete ordered
arrangement and trusted anchors. This tests evidence integration without a tiny
boundary target. It is an extension of a solved positive control, not a newly
demonstrated failure.

**Unary / pairwise / global:** First check each instance's shape and orientation;
then anatomical neighborhood and continuity; finally require one consistent
identity assignment across the group. A nearest-centroid rule is not an
anatomical attachment definition. Curvature, articulation conventions and
transitional anatomy must be represented correctly, not used as hidden traps.

**Author screen before any trial:** Apply whole-instance label permutations,
preserving the label multiset and every voxel. Reject cases solved by a
duplicate-label count, obvious component outlier or trivial coordinate sort.
Compare nearest-neighbor/local assignment with a complete constraint solution.
If both work, retain as a useful control and stop claiming a hard global crux.
Do not distort a patient merely to defeat these baselines.

**Evaluation:** Independent identity adjudication plus a unique assignment under
the supplied contract. Enumerate alternative assignments on the small candidate
set before freezing. Reject underdetermined cases; do not accept the planted
permutation as proof of uniqueness. Grade exact `(instance_id, corrected_label)`
pairs, including missing and extra repairs. No pinpoint voxel or prose judge.

## Candidate BR010-M02 — Root-to-target identity in a branching mask

**Task:** Audit named branches in a small, complicated 3-D tubular network with
trusted root and endpoint identities. Report branch identities inconsistent with
their complete root-to-target paths. Use a documented anatomical model or an
explicitly synthetic anatomy-inspired network, never an invented patient history.

**Hypothesis:** Locally plausible tubes, branch degrees and nearby neighbors may
not establish which distal territory a branch belongs to. The solver must trace
the whole route. A simple disconnected fragment is only a calibration control.

**What to look for:** Does the solver validate connectivity to named anchors, or
stop at local shape/degree? A local crossing in a 2-D projection must not be
mistaken for a 3-D connection. Genuine shortcuts remain allowed.

**Evaluation:** Independently extract the graph from voxel masks and compare
root reachability/ancestry with an author-checked graph. Specify foreground and
background connectivity and verify robustness to resolution and surface
representation. Reject one-voxel, ambiguous or rasterization-dependent joins.
Accept every equivalent valid witness path. Exact identity/path grading is
possible; no claim of clinical correctness follows from a synthetic network.

**Priority:** M01 has stronger local provenance and lower authoring risk; M02 is
the more direct global-topology hypothesis, with greater source/ontology risk.
Neither is presently established to be difficult for Sol or Terra.

## Small explanatory experiment — proposed only

Freeze one legitimate candidate and its clean/variant controls before trials.
Use one fresh attempt per model/configuration, normal reasoning time and the
same geometry. Do not execute all configurations as a default batch.

| Condition | Added information | What a rescue would suggest |
| --- | --- | --- |
| A | Masks, viewer, required label/coverage/exception conventions and trusted anchors | Baseline; enough information for a unique answer, with routine anatomy knowledge assumed |
| B | A plus an explicit anatomical relation sheet, without instance-specific answers | Access to relevant anatomical rules, their salience or their interpretation may be limiting |
| C | B plus exact instance geometry and observed geometric relations, without semantic correctness flags | Geometry extraction or inspection policy may be limiting |

B and C also make useful facts more salient, so a one-run rescue does not isolate
knowledge or perception causally. A failure even in C would be stronger evidence
for assignment/consistency reasoning. A pass should retire that exact condition
from difficulty selection. The same solver may use arbitrary legitimate tools;
we cannot require a particular unary/pairwise/global internal workflow.

Benchmark success, false repairs on controls, agent wall time, output tokens,
uncached input, tool/image counts and verifier time. Keep estimates and billed
cost distinct. Supply working geometry libraries and a ready viewer to reduce
the plotting and fallback implementations observed in BR-004. A sub-minute
verifier is an authoring target, not a measured result.

## Research basis and limits

- [VerSe benchmark](https://www.sciencedirect.com/science/article/pii/S1361841521002127)
  reports vertebral identification difficulty around rare anatomical variants.
  It motivates the problem family; those specialized-model results are not
  evidence of Sol/Terra failure on masks alone.
- [Anatomic consistency cycle](https://arxiv.org/abs/2110.12177) combines
  localization, segmentation and identification using graph optimization.
  This supports a coherent task formulation, not a difficulty prediction.
- [clDice](https://arxiv.org/abs/2003.07311) motivates connectivity-aware treatment
  of tubular segmentation. Its comparison metric uses segmentation/reference
  information; it is not a reference-free answer key for our proposed task.

All three are primary research references, not original task submissions.
No new clinical annotation, model result or submission qualification is claimed.
