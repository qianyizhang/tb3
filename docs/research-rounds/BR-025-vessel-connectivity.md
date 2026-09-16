# BR-025 — repair one vessel connection from angiographic evidence

Captured 2026-09-16. **Source curation and task design; no model trial and no
admitted failure fixture.** [Candidate card](../../catalog/ideas/vessel-connectivity-repair.json)
· [Curation receipt](../evidence/br025-curation.json)

## Recommendation

Build a small **Pcom connection audit and repair** task: one native-resolution
MRA region, one proposed binary vessel mask, and one corrected mask as the
deliverable. The agent must decide whether to reconnect, disconnect, or leave
the mask alone. Start with posterior communicating arteries (Pcoms); retain
enough ICA/PCA context to identify their attachments. Do not begin with a whole
brain segmentation task or ask the solver to train a model.

Suitable public image and reference data exist. What is still missing is an
admitted, image-resolvable **faulty prediction** and evidence that repairing it
is difficult for a general agent. A synthetic corruption can establish task
mechanics, but cannot substitute for an observed prediction failure.

## Source provenance and scope

The user pasted a brainstorm headed “Repair a vessel segmentation’s
connectivity,” linking TopCoW and requesting a meaningful task plus a search
for suitable samples with ground truth. The earlier brainstorm session and
message IDs were not supplied or retrieved. This round retains that retrieval
gap rather than assigning an invented source session.

This request resumes only this bounded source search and task design. The
closed interview synthesis, earlier freezes, ongoing registration work, and
separate submission remain under their existing owners. No training, inference,
Harbor trials, publication, or contact with dataset owners occurred here.

## What the published evidence actually establishes

[TopCoW's 2024 paper version](https://arxiv.org/html/2312.17670v2), §4.5 and
Figure 10, describes a fragmented PCA at the Pcom junction in case 126, a
false PCA/BA contact in case 115, and ACA crossover in case 118. These are
specific external segmentation failures, not local agent-repair failures.
Some involve class identity: a broken class can disappear as a defect when
all vessel labels are merged. Only a defect that survives binarization
qualifies for the proposed binary task.

The [updated 2026 paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC13496301/)
reports that merged binary segmentation was considered sufficiently solved
and replaced in the 2024 challenge. It also states that hypoplastic vessels
count as present. The published motivation is therefore strongest for
anatomical topology, not generic binary mask cleanup. Do not transfer old
aggregate failure rates or illustrated test-case outcomes to this new task.

The illustrated 2023 cases above are not among the selected public training
samples. No byte-matched prediction/reference pair for those figures was
retrieved. The curated cases below are source candidates, not reproductions
of those failures.

## Curated data sources

| Source | What is available | Role and boundary |
| --- | --- | --- |
| [TopCoW training release](https://zenodo.org/records/15692630) | 125 paired CTA/MRA subjects; 250 annotated scans, multiclass vessel masks, CoW boxes, and anterior/posterior edge-presence labels. The main ZIP is 10.51 GB. | First choice. Individual files can be retrieved through Zenodo's archive API. Public training data supports development; it is not an unseen challenge test set. The small validation image set has no accompanying labels. |
| [CoW centerline graphs](https://zenodo.org/records/17358162) | Matching 250 labeled VTP graphs, node descriptions, variant descriptions, meshes and morphometric features; 373 MB archive. | Supplies spatial branch references. Graphs are derived from TopCoW masks, so agreement is useful technical corroboration, not a second independent anatomical ground truth. |
| [TopCoW external annotations](https://zenodo.org/records/15692630) | 20 IXI HH MRAs, 20 Lausanne MRAs, 26 ISLES TUM CTAs, plus annotations for 20 LargeIA CTAs. LargeIA images must be obtained from their original source. | Reserve for screening errors from a fixed pretrained model, after auditing its training sources. Do not call an external dataset unseen without that audit. These sets were source-screened, not downloaded in this round. |

The [centerline paper](https://arxiv.org/html/2510.13720v1) describes mask-based
extraction, anatomical postprocessing, and expert inspection. Skeletonization
itself can introduce incorrect edges; do not treat a fresh unreviewed skeleton
as unquestionable truth. VTP coordinates must be checked against the native
NIfTI affine before use in grading.

**Usage terms:** the TopCoW release requires attribution and owner permission
for commercial use. The graph release is CC BY-NC. These are suitable sources
to investigate, but the observed terms do not establish permission for a
commercial benchmark release. Raw downloads stay in the ignored local run
folder; permission and redistribution suitability remain release questions.

### Four concrete source candidates

Screening was deliberately small: inspect MRA edge annotations for IDs
001–012, then choose four distinct subjects spanning the Pcom configurations.
For these four, CTA and MRA edge annotations agree. That agreement alone does
not prove congenital absence or resolve vessel visibility in the offered MRA.

| MRA source ID | Left Pcom | Right Pcom | Proposed use |
| --- | --- | --- | --- |
| `topcow_mr_007` | Present | Present | Lead for a broken-connection candidate; preserve the other real connection. |
| `topcow_mr_009` | Absent | Absent | Candidate for removing a false Pcom bridge, conditional on finding a real erroneous prediction. |
| `topcow_mr_004` | Absent | Present | Correct-mask control: preserve the real right connection and absent left connection. |
| `topcow_mr_012` | Present | Absent | Opposite-sided unchanged control, preventing a fixed-side shortcut. |

“Absent” here means the released annotation says absent. It is not a new
clinical diagnosis. A control needs adequate offered-image evidence, a checked
mask/graph match, and case-level adjudication before it is called a genuine
anatomical-variant control. CTA labels were read; the paired CTA images were
not downloaded or reviewed. Detailed retrieval hashes and technical checks
are recorded in the [receipt](../evidence/br025-curation.json).

The selected 30-file download is 211.86 MB. Every file's ZIP CRC was verified
and its SHA-256 recorded. All four image/mask pairs have identical shapes and
affines, at approximately 0.297 × 0.297 × 0.600 mm spacing. Each present Pcom
label is one 26-connected component contacting the expected ICA and PCA
labels; absent Pcom labels have zero voxels. All checked graph-node coordinates
lie within 0.335 mm of a foreground voxel center using the stored physical
coordinates. This is a node-alignment screen, not complete graph validation.
An [axial projection contact sheet](../../runs/br025-vessel-curation/source-screen.png)
was visually screened; projection overlap cannot establish 3-D connectivity
or distinguish congenital absence from nonvisualization.

## Proposed solver contract

> A vessel segmentation in the supplied MRA review region may contain a
> broken connection, an unsupported connection, or no connectivity defect.
> Use the MRA to correct the vessel mask while preserving the patient's
> anatomy. A vessel may be small or absent; a complete circle is not required.
> Save `corrected_mask.nii.gz` on the same voxel grid. Preserve the mask
> outside the supplied editable region. If the mask is already correct,
> return it unchanged.

Public inputs are `image.nii.gz`, `proposed_mask.nii.gz`, a broad
`editable_region.nii.gz`, and a short geometry/format description. The native
image includes the review region and a context halo. The mask is binary;
multiclass labels, source graphs, correct edge states, and exact defect
locations stay in the verifier. Do not give a ground-truth-shaped path corridor
to the solver. Use the same region-construction rule for defects and unchanged
controls, so the crop itself does not reveal the required action.

Each task instance contains **one local decision**, not all four patients.
The four sources form an authoring/control panel. The agent may use ordinary
image-processing packages, viewers, scripts, and pretrained tools. It need not
justify a diagnosis or write a clinical report. Judge the submitted mask.

The proposed input mask must already be satisfactory outside the edit region;
otherwise an exact preservation requirement would prohibit necessary repairs.
Retain sufficient context to distinguish the two parent arteries and any
neighboring real branch. Fix crop dimensions from anatomy and source spacing,
not a desired failure rate.

## Hypothesis and discriminating observations

**Hypothesis:** image evidence allows the agent to repair an erroneous local
connection while preserving a real asymmetric or incomplete configuration.
Anatomical symmetry or nearby endpoints alone are insufficient.

Record whether the output repairs the intended connection, changes the wrong
branch, joins an absent vessel, erases a thin present vessel, or makes unrelated
edits. Image-use claims need controls: success by itself does not establish
that the image was necessary. Compare a competent mask-only repair baseline
with an image-guided baseline on the same frozen cases. A geometrically
matched present/absent pair is useful only if both states are actually
resolvable from the supplied image.

## Verifier design

Use the reference mask and reviewed graph to judge the output independently
of the proposed-mask generator. Report each criterion separately; a high
whole-volume Dice must not compensate for a wrong connection.

1. **Format and grid:** readable binary NIfTI; matching shape, voxel spacing,
   orientation and physical affine; no image-header substitution.
2. **Specific connection:** for a present Pcom, require a continuous path
   between the appropriate ICA and PCA attachment neighborhoods through the
   local Pcom region. For an absent Pcom, reject such a local bridge. Evaluate
   this local route, not arbitrary whole-CoW reachability: an alternate route
   around the circle can hide the broken branch. Check neighboring branch
   attachments so a shortcut to the wrong vessel cannot pass.
3. **Geometry:** compare repaired local centerline coverage and spurious
   centerline length in physical millimetres. Also check local surface/radius
   agreement so a one-voxel string or thick dilation cannot satisfy topology
   alone. Define absent-reference metrics explicitly; do not turn empty-set
   Dice into the entire no-repair score.
4. **Preservation:** no changed voxels outside the public edit region. Within
   it, bound damage to already-correct vessel regions and new foreground
   outside the accepted anatomical tolerance. Emptying the region and
   resegmenting everything must fail when they erase a valid branch.

Use published [TopCoW metrics](https://github.com/CoWBenchmark/TopCoW_Eval_Metrics)
for diagnostic comparability, supplemented by these local checks. Whole-mask
Dice, clDice and component counts are informative summaries, not sufficient
pass conditions. Declare foreground connectivity (for example 26-neighborhood)
and test diagonal contacts explicitly. An accidental one-voxel touch should
not be accepted merely because it joins two components.

Numeric distance, coverage, surface, and edit tolerances are **not yet frozen**.
Calibrate them on acceptable independent repairs and annotation uncertainty
in authoring cases, expressed in millimetres and physical volume. Establish
that the reference and a real image-guided repair pass, and targeted wrong
masks fail, before evaluating any agent. Do not tune tolerances to an agent's
output or demand exact manual-boundary voxel reproduction.

## Getting a credible faulty mask

The reviewed releases contain reference annotations and model packages; this
search did not establish a downloadable collection of faulty predictions
aligned to these four cases. [Official model containers](https://zenodo.org/records/15665435)
and the [CLAIM inference code](https://github.com/claim-berlin/TopCoW_2024_MRA_winning_solution)
provide an author-side route to produce predictions. They were not run here.
If used, retain the model digest, preprocessing, raw output, and training-data
overlap. Models trained on these public cases cannot supply an unseen-test
claim. Check label conventions when comparing model output with the source
annotation scheme.

Prefer a real binary break or bridge from one frozen model, selected by an
image/annotation audit. If none is available, a transparently declared local
cut or bridge on the reference mask is a **synthetic feasibility fixture**.
Choose plausible defects from the observed error mechanism, avoid obvious
flat cuts or artificial intensity markers, and retain the construction.
Do not advertise synthetic defects as TopCoW model predictions.

## Admission, controls, and stopping rules

Before a model trial, admit one small defect case and matched unchanged
controls only after native-image review confirms the target is resolvable,
mask/graph alignment is checked, and boundary or flow ambiguity is excluded.
Paired scans may help author adjudication, but hidden CTA evidence cannot
make an ambiguous MRA-only task fair.

The reference/oracle must pass. An unchanged proposed mask must fail on the
defect instance and pass on a correct instance; an all-correct panel cannot
validate a nop-failure gate. Add targeted wrong controls: connect-all, remove
all thin branches, wrong-parent bridge, erase-region, one-voxel bridge, and
repair-plus-collateral-damage. A strong permitted image-guided path/region
growing method is an author baseline, not an answer to withhold by banning
libraries. If ordinary local processing cleanly solves the frozen panel,
retain it as useful calibration and retire its difficulty claim.

After controls, a separately requested diagnostic would use a frozen package
with the repository's ordinary model settings. Review normal completion,
verifier result, image evidence, and submitted mask. Distinguish wrong repair
from ground-truth ambiguity, format defects, source-answer retrieval,
timeouts, and infrastructure errors. Public masks can be retrieved online;
cropping or renaming them does not make the source private, and a
source-assisted result is not evidence of image reasoning.

**Disposition at curation close:** promising data-backed task design; sample sources
curated, but no natural defective prediction, complete verifier, expert
case adjudication, or model-difficulty result has been established.

The subsequently authorized [BR-026 experiment](BR-026-results.md) completed
two fresh diagnostics: synthetic-gap pass and unchanged-mask preservation
failure with unresolved reference ambiguity. This curation record describes
the evidence available before those trials.
