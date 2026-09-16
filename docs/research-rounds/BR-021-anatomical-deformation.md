# BR-021 — anatomical deformation in registration

Status: [completed](BR-021-results.md). Fresh Terra/high passed paired 3D
(1.91 mm RMS) and failed single-view 2D-to-3D (12.64 mm RMS), both with healthy
controls and normal completion. Retain the 2D failure candidate, including its
observed transform-composition defect; retire the passed 3D snapshot.
[BR-020](BR-020-results.md) remains retired and frozen.

[Candidate card](../../catalog/ideas/respiratory-deformation-registration.json)

## Request and scope

In the owning [research task](codex://threads/01a0a845-7c2d-7992-a662-24d52831af90),
the user asked to increase difficulty through “morphology”, then explicitly
chose “try both” when offered 2D-to-3D correspondence with local deformation
and paired 3D deformable registration. Both conditions will use one paired
clinical source if source validity permits. The source-message IDs are not
exposed; the complete request is visible in the current conversation.

Morphological variation is appropriate for differences in anatomical shape
or size. Respiratory motion is more specifically nonrigid deformation. The
BR-020 trace used multiscale intensity correlation; no denoising ablation
established denoising as the sole cause of its success.

## Bounded plan before new model outcomes

1. Prefer real intra-patient inhale/exhale CT with independent manually matched
   landmarks, licensed for the local experiment. Do not replace missing labels
   with an optimizer's predicted correspondences and call that ground truth.
2. Check image/landmark pairing, voxel/physical conventions, coverage and
   annotation provenance. Quantify identity, best rigid and best affine fits
   to reference correspondences. The best rigid fit is a privileged diagnostic
   lower bound, not an allowed solver or model input.
3. Prepare two compact conditions: paired 3D registration and an oblique 2D
   view localized in the other respiratory phase. A single rigid matrix cannot
   generally encode the latter mapping. Score corresponding anatomical points
   in physical units, with tolerances fixed before model execution, and state
   which aspects of a dense deformation remain unvalidated.
4. Retain a permitted public-input author baseline for each condition, including
   failed searches. Check whether real nonrigidity remains after global
   alignment and whether target anatomy is sufficiently visible. An invalid
   or underdetermined instance must not become a model-failure claim.
5. Freeze admitted inputs, isolated geometry verifiers and oracle files. Use
   matched oracle/nop controls, then one fresh Terra/high attempt per condition,
   1,800 seconds each, zero retries and ordinary library/network access. Earlier
   solver code, author labels and other-condition answers are not provided.
   Delegated supervision follows the original user-authorized benchmark flow.
6. Inspect traces and independently replay outputs. Preserve infrastructure
   errors separately. No automatic stronger-model escalation or publication.

These are local feasibility diagnostics; success on one pair does not estimate
a success rate or establish clinical usefulness. The prior round's same-grid
geometric precision must not be carried over as annotation precision here.

## Source screening

- [Learn2Reg LungCT](https://learn2reg.grand-challenge.org/Datasets/) provides
  inspiration/expiration data with large motion and incomplete expiration
  coverage. Its preprocessed version is affine prealigned. Manual validation
  landmarks and automatically computed training keypoints are distinct.
- Challenge attribution: Hering et al.,
  [Learn2Reg: comprehensive multi-task medical image registration challenge,
  dataset and evaluation in the era of deep learning](https://arxiv.org/abs/2112.04489).
  This supplies external registration context, not a language-agent outcome.
- Official [training](https://zenodo.org/records/3835682) and
  [test](https://zenodo.org/records/4048761) Zenodo metadata reports CC BY 4.0.
  Their original archive indexes contain scans and lung masks, not landmark
  files. The current challenge download includes additional evaluation data.
- The official [L2R evaluation repository](https://github.com/MDL-UzL/L2R),
  inspected at commit `88475095e35442087a24439ff34ec09f54bc7dac`, contains
  manual and automatic correspondence files. Its `L2RTest/ground-truth/imagesTr`
  pairs have identical Git blob IDs for both phases: they are unsuitable as
  real paired source images. Use the actual dataset release and verify linkage.
- [DIR-Lab 4DCT](https://med.emory.edu/departments/radiation-oncology/research-laboratories/deformable-image-registration/downloads-and-reference-data/4dct.html)
  supplies expert reference landmarks, but downloads currently require a
  provider-issued password after a request form. No form was submitted and no
  unofficial mirror was used.
- [Lung250M-4B](https://github.com/multimodallearning/Lung250M-4B) distinguishes
  manual evaluation landmarks from CorrField pseudo-labels. Its published
  registration results motivate deformation as a meaningful algorithmic
  challenge; they are not LLM failures or a local outcome.

Raw metadata, downloads and generated artifacts are retained under ignored
`runs/br021-deformable/`. New authoring belongs under
`probes/registration-deformation/authoring/`; prior freezes and the closed
interview/submission surfaces remain unchanged.

## Admitted source and paired task design

The actual official LungCT 1.11 archive was selectively downloaded from the
challenge's current [provider share](https://cloud.imi.uni-luebeck.de/s/o7LyCbJCie8fQ3B/download).
Its first three manually annotated validation pairs were screened before any
solver run. These are distinct inhale/exhale images; archive landmark CSVs
are byte-identical to the official evaluation repository's manual references.
Automatic CorrField keypoints were not downloaded or used as truth. The
dataset description attributes these clinical scans to Radboud University
Medical Center and identifies the reference landmarks as manually annotated.

All images have shape 192x192x208 and dataset-world spacing 1.75x1.25x1.75 mm.
The task preserves this supplied geometry. It does not relabel arbitrary
preprocessed coordinates as native patient LPS. The direction is exhale to
inhale. Source audit checks hashes, bounds, phase differences, coordinate
conventions and landmark linkage.

| Case | Manual correspondences | Identity RMS | Best rigid RMS | Best affine RMS |
| --- | --- | --- | --- | --- |
| 1 | 81 | 20.94 mm | 6.84 mm | 5.63 mm |
| 2 | 100 | 16.50 mm | 12.82 mm | 9.81 mm |
| 3 | 100 | 9.17 mm | 7.63 mm | 5.99 mm |

Case 1 was selected as the first case whose privileged best rigid and affine
fits both exceed 3 mm RMS, before baseline execution. An oblique section was
selected from near-coplanar source landmarks, preferring the largest query
count and then footprint, subject to visibility and nonrigidity checks.
Eight queries lie within 0.313 mm of its plane. The 118x171 view has 1.25 mm
pixels. All corners are inside source coverage. Independent interpolation
at 300 points agrees within 0.000031 HU. Source and manually corresponding
image patches were visually inspected; all eight positions have visible
vessel/airway structure. This is author visibility review, not clinician
certification of correspondence or a standard diagnostic plane.

Both conditions use these same eight destination landmarks and require only
an ordered list of corresponding 3D positions. The 3D condition supplies both
complete challenge volumes and the exact source 3D query positions. The 2D
condition supplies one oblique source view, fractional query pixel positions,
and the destination volume. Its nominal **source acquisition frame is public**:
this scaffold isolates deformation rather than repeating the lost-pose problem
from BR-019/020. It does not reveal where source anatomy moved. The projected
2D and exact 3D source locations differ by at most 0.313 mm.

For these eight queries, the best rigid residual is 5.46 mm RMS in the 2D
condition and 5.42 mm in 3D; even unrestricted affine fits leave 3.60 mm and
3.13 mm respectively. These are truth-assisted diagnostic lower bounds and
are withheld from the agent. They establish that a global matrix cannot pass
the unchanged 3 mm RMS / 5 mm maximum limits for this selection. These limits
are engineering tolerances, not measured observer uncertainty or clinical
equivalence margins. Only sparse point accuracy is validated, not a dense
deformation field or its topology between queries.

## Author feasibility, before model execution

All implementations read only their explicit public input directory. The 2D
solver never receives the full exhale volume or destination annotations.
Development used the selected case, so these are feasibility baselines, not
unbiased held-out method comparisons. Failed versions and their code remain
in the raw record.

| Author method | Condition | RMS / maximum error | Outcome |
| --- | --- | --- | --- |
| Multiresolution SimpleITK Demons with histogram matching | 3D | 23.29 / 35.57 mm | Fail |
| Whole-view affine correlation, then local affine patches | 2D | 21.97 / 55.10 mm | Fail; two wrong branch matches |
| Independent local patch search with translation multistart | 2D | 2.37 / 4.72 mm | Pass |
| Independent local patch search, before padding handling | 3D | 9.47 / 26.23 mm | Fail; one cropped-coverage query |
| Same 3D patch method, excluding uniform source padding | 3D | 1.94 / 4.45 mm | Pass |

The passing methods use ordinary NumPy/SciPy interpolation and Powell
optimization with local affine patch models. They require neither pretrained
weights nor annotation-derived initializations. Solver time is about 4 s for
2D and 23 s for 3D on the author host, excluding author development. Fresh
isolated Linux replays passed before freezing: 2D RMS 2.31 / maximum 4.46 mm;
3D RMS 1.94 / maximum 4.45 mm. These used network-disabled task images with
only the author code and a condition-specific output directory mounted.
Image inventories confirm private labels and the verifier/oracle are absent.
The [author audit](../evidence/br021-author-audit.json) and
[freeze](../evidence/br021-freeze.json) retain hashes and exact measurements.

Agent images include only their public payload, source attribution and generic
libraries (NumPy, SciPy, Pillow, SimpleITK). The verifier and manual destination
landmarks live in a separate image. Author code, prior agent solutions and
other-condition inputs are excluded. Public source attribution is retained;
the public dataset also has downloadable annotations, so this is not a claim
of immunity to training contamination or outside answer retrieval. The task
requires recovering correspondence from supplied images; execution traces
must be reviewed for annotation lookup and unexpected data access.
