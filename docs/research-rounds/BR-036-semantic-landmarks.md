# BR-036 — semantic landmark localization on CT and MRI

Completed: [four Terra/high results](BR-036-results.md) and [trace interpretation](BR-036-traces.md). Eight matched Docker controls passed; no further trials queued.

The user explicitly resumed research on 2026-09-17: “perhaps another test on
semantic landmark locolization for CT and MRI / propose a list of good candidates
and curate dataset with gt / i assume this task is well within capability of
agent, so test with terra”. Exact message ID is unavailable. This is a capability
calibration request, not an assertion of a benchmark-backed agent failure.
The closed presentation and sibling submission are outside scope.

## Candidate shortlist

| Priority | Candidate | Ground truth and useful task | Disposition |
| --- | --- | --- | --- |
| 1 | [AFIDs SNSX brain MRI](https://github.com/afids/afids-data), [OpenNeuro ds004470](https://openneuro.org/datasets/ds004470) | 32 named brain fiducials; released individual rater coordinates and consensus on T1 MRI. AC/PC, brainstem junctions, mammillary bodies and callosal extrema provide compact semantic targets. | Selected first source-order subject C001; 8 named points, three-rater agreement checked. CC BY 4.0. |
| 2 | [PDDCA head-and-neck CT](https://www.imagenglab.com/newsite/pddca/) | Manual bony point coordinates plus a written marking protocol. Chin, paired condyles and dens give a compact, high-contrast localization task. | Selected first source-order patient 0522c0001; four points. Occipital point held because its definition relies on an illustration. Source calls the dataset public domain. |
| 3 | [VerSe spine CT](https://github.com/anjany/verse) | Named vertebral centroids and masks; useful for vertebral-level identification, including transitional anatomy. | Strong next candidate; centroid definition differs from a discrete anatomical surface point. No new download or trial in this pilot. |
| 4 | [MedPelvis3D pelvic CT](https://zenodo.org/records/20520568) | 57 expert landmarks per case, with semantic mapping and original CT LPS-mm geometry. Bilateral pelvic points would test laterality and spatial anatomy. | Source-screened reserve; 99 cases, 5-case preview. Recent deposit with descriptor under review; annotation reliability and reuse terms need inspection before admission. |
| 5 | [AFIDs LHSCPD brain MRI](https://openneuro.org/datasets/ds004471) | Same semantic framework on a clinical Parkinson's cohort. | Useful second MRI cohort for transfer; source documents open CC BY 4.0 access. Not curated or tested here. |
| 6 | [PDDCA probabilistic atlas](https://www.imagenglab.com/newsite/pddca/) | An averaged CT with five bone landmarks. | Tutorial/calibration only: an atlas is less representative than a patient scan and potentially easy to identify. |

The [nnLandmark repository](https://github.com/MIC-DKFZ/nnLandmark) independently
lists AFIDs and PDDCA as 3D landmark benchmarks. This establishes task relevance,
not a published general-agent failure. Paired registration points without stable
anatomical names and segmentation centroids without a landmark definition are not
substitutes for semantic point localization. ACDC masks alone likewise do not
establish manual valve/apex landmark ground truth.

## Pretrial protocol and curation

Two separate full-volume tasks, one CT and one MRI. Selection is first source
order; no agent outcome was available during selection. MRI queries are AC, PC,
infracollicular sulcus, pontomesencephalic junction, paired mammillary-body
centres, genu and splenium. CT queries are chin, right/left condyle and dens.
Task definitions paraphrase the source protocols; the source identifies the
exact point, rather than asking for an unspecified organ centre.

Inputs are full native-grid image intensities, NIfTI affine, semantic definitions,
and source attribution. Output is one named RAS-mm triple per requested point.
The CT NRRD uses LPS physical geometry; its NIfTI affine explicitly converts LPS
to RAS. Both released FCSV files declare Slicer CoordinateSystem=0 (RAS).
All reference points lie within their images. MRI image and consensus bytes
match their SHA-256 git-annex declarations, and all eight consensus points equal
the mean of the three released raters. Largest individual-rater deviation among
selected points is 1.540 mm. Author overlays were inspected as a technical
alignment check, not an independent clinical adjudication.

Fixed acceptance: each CT point <=5 mm, each MRI point <=3 mm. The CT has 3 mm
slice spacing; the MRI has approximately 0.7 mm voxels. These are explicitly
chosen engineering tolerances, not clinical accuracy standards or claims about
source inter-rater uncertainty on CT. Report every point error, mean, maximum,
and counts within 3/5 mm, so the binary threshold does not hide performance.

Oracle, empty, translated and nonfinite-output scorer controls run before freeze.
Matched Docker oracle/nop controls must pass before a model is started. One
Terra/high attempt per modality, 1,800 seconds, 2 CPUs, 4 GiB, zero retries.
No shorter reasoning budget or artificial software restriction is imposed.
The verifier and reference annotations live in a separate container; they are
absent from the agent build context. Public software and general anatomical
references are allowed; subject-specific answer retrieval is explicitly excluded
and audited. Public training exposure cannot be ruled out.

No independent blind author solver has been run. Published manual placements and
protocols support reference-based feasibility; oracle copying validates packaging
only. In particular, a miss would be a pilot reference disagreement needing review,
not automatically an admitted hard benchmark or clinical capability claim.

## Retained artifacts

- [Authoring scripts](../../probes/semantic-landmarks/authoring/)
- Local source data, curation, frozen task bytes and trial outputs:
  `runs/br036-semantic-landmarks/`
- [Curation receipt](../evidence/br036-curation.json)
- [Pretrial freeze](../evidence/br036-freeze.json)

Only this new round and its probe/evidence paths are owned by this task. Existing
BR-018 preparation, its uncommitted register entry and `site/.openai/` are retained.

## User-requested expansion during the initial trials

The user asked for more landmarks, including targets outside the scan where the
answer may be empty or a reasonable extrapolation, and pointed out the classical
pre-deep-learning medical-CV literature. This is a new condition; original freezes
are retained. No initial model score was available when the expansion was frozen.

[VISCERAL's 2016 benchmark paper](https://lmb.informatik.uni-freiburg.de/Publications/2016/Mai16/2016_visceral_anatomy_challenge.pdf)
reports 12 landmarks in Anatomy1 and 53 in Anatomy2 across CT/MRI, with random
forests, SVMs and template/block matching. It is the closest historical match for
broad semantic body localization. The [early specification](https://visceral.eu/assets/Uploads/VISCERALBenchmark1specification-v1.1.pdf)
includes bilateral clavicular ends, iliac crests, greater/lesser trochanters,
pubic symphysis, carina, aortic arch and aortic bifurcation. The current benchmark
page returns maintenance; no claim of currently downloadable Gold Corpus is made.
Its published voxel-distance scores are not compared numerically with our mm scores.

Additional useful candidates:

| Source | Semantic targets | Why useful / access status |
| --- | --- | --- |
| [MML](https://github.com/ithet1007/mmld_code) | Mandibular molar crown/root landmarks on CT; source reports 648 volumes. | Missing/damaged teeth and variable root count offer genuine anatomical absence. Ground-truth absence semantics, download and reuse terms still need validation. This is distinct from a landmark outside the scan. |
| [LFC](https://huggingface.co/datasets/haifan-gong/LFC) | Six fetal cerebellar MRI points, endpoints for TCD/HDV/ADV. | Compact T2 MRI task that diversifies age and anatomy; source-screened, not downloaded/admitted. |
| [Fetal craniofacial MRI atlas](https://pmc.ncbi.nlm.nih.gov/articles/PMC11343257/) | Published landmarking protocol and an atlas with 50 anatomical points. | Rich semantic candidate bank; atlas-only accessibility does not establish a patient-level benchmark. |
| [Classical collaborative regression](https://pmc.ncbi.nlm.nih.gov/articles/PMC4833677/) | Random-forest landmark prediction, including PDDCA bony points. | Confirms the classical task lineage; trained algorithm results do not establish general-agent performance. |

The expanded MRI task uses **all 32 AFIDs**: commissures; brainstem sulci and
junctions; cerebellar culmen; interpeduncular and intermammillary points; paired
mammillary bodies; pineal gland; ventricular points at AC/PC levels; genu and
splenium; paired temporal/occipital horn points; indusium griseum origins; and
olfactory sulcal fundi. Full definitions are supplied from the source protocol,
without any subject coordinates. All 32 consensus positions are curated and
checked against individual raters.

The MRI input removes slices below original k=145, preserving voxel intensities
and physical geometry. Seven targets are outside; all three raters agree on the
inside/outside assignment of all 32 points. The CT input removes slices below
k=68: chin and dens are outside, both condyles remain inside. These are deliberately
selected inferior FOV truncations, not naturally acquired partial scans or random
crop estimates of robustness. The full reference volumes remain private to scoring.

Expanded output values may be RAS-mm triples, null or []. In-view points retain
3 mm MRI / 5 mm CT tolerances. Out-of-view points accept either empty output or
an estimate outside the true voxel-cell bounds within **10 mm** of the full-volume
reference. This makes “reasonable guess” independently measurable. Empty answers
for visible targets fail. Report localization and outside recognition separately;
absence outside the FOV is not anatomical absence. The model gets up to 3,600
seconds, with one attempt per new condition and no retries. More landmarks are
not accompanied by less reasoning time.

[Expanded curation](../evidence/br036-expanded-curation.json) and
[separate freeze](../evidence/br036-expanded-freeze.json) retain all coordinates,
inside/outside status and controls. Exact-key empty-output oracle and extrapolation
oracle both pass; all-empty and missing-key controls fail. There is no 32-point
full-volume model condition, so comparisons to the eight-point MRI pilot mix
query-set and FOV changes; they are not a causal crop-effect estimate.

The expanded MRI uncertainty audit finds one in-view point, right indusium griseum
origin (27), with maximum rater-to-mean distance 3.138 mm, slightly above the fixed
3 mm threshold. Point 22 reaches 3.588 mm but is outside the crop and accepts null.
Keep the fixed scoring and flag borderline point-27 disagreements for review;
consensus labels are not exact biological truth. This was recorded before expanded
model results. The retained CT archive additionally contains 16 cases / 80 source
points, indexed in [the source inventory](../evidence/br036-ct-source-inventory.json).
Only case 0522c0001 has undergone the pilot's image/geometry checks; the other
15 are reserves, not admitted cases.
