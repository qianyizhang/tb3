# BR-043 — Proposed next medical tests

Date: 2026-09-20. Status: proposal and source screen only; no new cases
downloaded, fixtures frozen, model attempts launched, or results claimed.

Source message in the current task: “given what we have done in the past,
propose some medical tasks we should test next”. Task identifier from workspace
context: `01a0bde4-e30d-71c3-8ae4-19d377aee51d`. No historical conversation
reconstruction was needed; retained round reports were read directly.
[Round register](../research-rounds.md#br-043--proposed-next-medical-tests-2026-09-20).

## What the existing evidence suggests

- [BR-042 V3](BR-042-v3-results.md): normally completed Astra/medium recovered
  95.5% of annotated coronary length geometrically, versus 79.3% with the correct
  labels. D2 and OM1 were mostly or wholly missed; other recovered branches had
  identity disagreements. These numbers are length-weighted, not the stricter
  equal-category acceptance scores. Astra/xhigh was interrupted and is not a
  clean completed failure or effort comparison.
- [BR-041](BR-041-astra-results.md): Astra's entire reference route was recovered;
  its failed endpoint/extent score does not establish fabricated distal anatomy.
  A successor should avoid using annotation stopping points as its main crux.
- [BR-034](BR-034-results.md): a normally completed Sol attempt and two
  unchanged-code clinical replays had EF errors of 23.30, 25.94 and 30.49
  percentage points despite mean surface distances around 2 mm. Timing was
  relatively close; contraction amplitude was the clearer gap.
- [BR-040](BR-040-results.md): CT localization remained weak; Sol's lower mean
  error did not improve every fixed-tolerance result. Full and partial CT used
  one typical-numbering subject, so atypical numbering remains untested locally.
- [BR-037](BR-037-results.md): cross-sequence interpretation was often useful,
  but residual extent and measurement reproducibility were unresolved. Its
  mechanical passes were not clinical passes. Later diameter direction was
  insufficiently discriminating, and source diameter units were unresolved.

These favor tasks with one anatomical or measurement decision, a small output,
and scoring that distinguishes discovery, identity, geometry and interpretation.
The following are new task designs; historical difficulty does not transfer
automatically after simplifying or changing inputs.

## Ranked candidate cards

### BR-043-C01 — Name coronary branches when geometry is already supplied

**Priority:** first for a quick, interpretable follow-up to BR-042.

Supply a fresh full CTA and a complete, unlabeled coronary centerline tree;
request anatomical labels and uncertainty for each branch. Use source-confirmed
variation in dominance and diagonal/obtuse-marginal branching. A separate later
image-only condition could test discovery, but is not required for this pilot.
The central question is whether the model can identify a branch from its origin
and course when extraction is removed from the task.

Score branch identity and named-segment transitions separately. Randomize branch
IDs/order and strip label-bearing metadata. Supplied geometry is an explicit aid,
not independent recovery. Unlabeled trees must be complete enough that branch
numbering is identifiable. Source labels require visual review where ramus,
diagonal or segment-boundary conventions could disagree.

Ground truth: [ImageCAS-X](https://github.com/kitbransby/ImageCAS-X) describes
lumen/segment labels and centerlines. The existing locally audited case is a
development case, not a new test. The repository's current README has unpopulated
download-link text, so access to additional cases is not established by this
survey. First obtain and audit fresh cases, then an input-legal author solution.

### BR-043-C02 — Find genuinely new lesions between two brain MRIs

**Priority:** strongest new-domain candidate, conditional on reference access.

Give paired baseline/follow-up FLAIR volumes. Return a follow-up new-lesion mask
and lesion locations; include patients without new lesions. The crux is separating
new lesions from pre-existing lesions, alignment differences and intensity change.
Score lesion sensitivity and false positives separately from voxel overlap.
Keep enlarging pre-existing lesions outside the new-lesion endpoint.

[MSSEG-2](https://portal.fli-iam.irisa.fr/msseg-2/data/) has a directly relevant
longitudinal reference task. Its [organizer analysis](https://www.nature.com/articles/s41598-026-52150-1)
reports expert disagreements and post-challenge additions to the reference.
Version and adjudicate the truth before accepting apparent model false positives.
This is published benchmark evidence, not an observed local agent failure.
Task-level cases and normal completed local baselines still need inspection.

Access to the official portal was blocked to the research browser by robots.txt;
download availability, use terms and availability of the revised masks remain
unverified. Do not substitute old labels silently or describe this as ready to run.

### BR-043-C03 — Measure maximum cardiac contraction from real 3D echo

**Priority:** strongest locally grounded functional follow-up.

Supply an unused full 3D echo cycle and one end-diastolic cavity annotation.
Ask for the end-systolic frame, its cavity segmentation, EDV/ESV and EF. The
crux is recovering the contracted cavity boundary. This reduces the BR-034
task to the failed functional component without requiring a moving mesh,
material mechanics or an etiologic diagnosis.

Use the previously audited [EchoXFlow](https://huggingface.co/datasets/Ahus-AIM/EchoXFlow)
clinical reference surfaces to derive the volume reference. Score ES frame,
cavity volume and EF independently; do not let mean surface distance substitute
for functional accuracy. Supplied ED geometry is initialization. These surfaces
are clinical annotations, not independently measured myocardial trajectories.

Curate reduced and preserved-function cases with comparable visible coverage.
Author feasibility needs a public-input method that recovers contraction, since
the prior agent failed even with a useful initialization. A threshold-only
baseline and the supplied unchanged ED mask should expose trivial shortcuts.

### BR-043-C04 — Identify vertebral levels in anatomical variants

**Priority:** low setup burden after source-case review.

Give a CT containing the anatomical counting anchors and ask for named vertebral
centres. Select a conventional-numbering control and source-confirmed transitional
or numerical variants. Score spatial localization without labels first, then
identity on the same matched vertebrae, plus explicit absence/uncertainty.
This asks whether a model sees the right bone but assigns the wrong level.

The [VerSe source descriptor](https://pmc.ncbi.nlm.nih.gov/articles/PMC8553749/)
documents variants and failure of earlier methods on uncommon anatomy; the
[official repository](https://github.com/anjany/verse) supplies labels and
centroids. Review the source's numbering convention and case-level variant
metadata before admitting a case. Cropping away the counting anchors would
introduce identifiability ambiguity, not a clean reasoning challenge.

### BR-043-C05 — Measure residual lesion extent despite reduced enhancement

**Priority:** clinically interesting, but adjudication must come first.

Give two complete breast MRI visits, with the relevant dynamic phases and T2.
Ask for reproducible residual-lesion measurements and image citations using a
single prospectively specified measurement definition. The crux is distinguishing
weaker enhancement from disappearance or size reduction, as exposed by BR-037.

[I-SPY2](https://www.cancerimagingarchive.net/collection/ispy2/) is already a local
source. Admit fresh cases with expert-reviewed boundaries, resolved physical
units and the selected diameter or volume endpoint. Never treat functional tumor
volume, longest diameter and pathology response as interchangeable truth.
Include a stable or enlarging measurement control. This proposal is not a
retrospective regrade of BR-037 or evidence of a clean previous diagnostic miss.

### BR-043-C06 — Localize pulmonary emboli on CTPA

**Priority:** exploratory reserve for a new pathology and anatomical region.

Give one full CTPA and request embolus locations or masks with supporting image
coordinates, including genuine negative studies. The crux is distinguishing a
filling defect from adjacent structures and acquisition effects across slices.
Score lesion-level detection and false positives; define 3D instances explicitly
instead of counting the same clot once per slice.

The [FUMPE source paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC6122162/)
describes 35 examinations with radiologist annotations and two studies without
clots. Both negatives have thicker slices than most positive studies, so this
small pool is not a matched classification cohort. Verify case geometry and
lesion continuity. Data are promising, but no task-level benchmark miss or local
agent failure was verified here. Under our benchmark-backed selection rule this
remains a source-curation reserve, not a trial-ready hard-task candidate.

## Recommended first slice

Start with C01 for continuity and C02 for diversity; use C03 as the strongest
available alternative if MSSEG-2 access or label revision blocks curation.
For each chosen family, curate about three previously untested patients with
meaningful contrast/negative conditions before spending on model attempts.
This is a diagnostic pilot, not a population estimate or a fixed universal
three-case recipe.

Before trials: verify native coordinates, source terms and label independence;
establish an input-legal author solution; freeze the endpoint and tolerances;
run positive, no-op and relevant shortcut controls. Preserve all screened cases
and reasons for exclusion. Keep ample reasoning time and remove avoidable setup
work rather than manufacturing difficulty through a shorter budget.

Use independent sessions with no prior case feedback. Report permitted source
assistance and public-data exposure, completed misses and execution failures
separately. Repeated attempts are needed before calling a failure reliable.
These recommendations do not choose a model, authorize trials, or alter frozen
historical tasks, the interview synthesis or the submission workspace.

## Directions to defer

- Another all-thoracic-vessel inventory: current private truth covers coronary
  anatomy only, and output breadth adds work without validating completeness.
- More motion/strain reconstruction from cavity shape alone: BR-035 already
  distinguishes accurate geometry from unobserved material motion.
- Generic repair-the-gap cases: BR-030 passed and BR-033 passed with flawed
  negative-control selection; a new failure-backed source is needed.
- Free-form prognosis or broad diagnosis with weak outcomes: BR-037 already
  showed why a permissive format gate and an easy directional baseline are
  insufficient.

Source check completed 2026-09-20. Some publisher opens failed with redirects
or service errors; primary-paper search excerpts and accessible author/PMC
pages supported this screen. Dataset bytes, current access entitlements and
revised-label downloads were not validated. No benchmark difficulty or clinical
validity is certified by this proposal.

## Visual explanation follow-up, 2026-09-20

The user requested actual data or symbolic drawings to understand each task,
its expected outcome and why it is challenging. The explanation uses schematic
coronary ordering, longitudinal lesion comparison, vertebral numbering and
pulmonary-clot examples, with retained BR-034 echo and BR-037 MRI figures.
Schematic anatomy and example answers are not new patient data or trial results.

The newer [BR-042 branch review](BR-042-v3-branch-review.md), inspected during
this explanation, strengthens the small-branch discovery/numbering interpretation
for D2 and OM1/OM2 while retaining unresolved PDA identity and taxonomy questions.
It does not establish incorrect reference labels. C01 should therefore use
adjudicated naming conventions; a simplified supplied-tree task is a diagnostic
test of identity, not already demonstrated to be hard. No new trial is authorized
by the explanation request.
