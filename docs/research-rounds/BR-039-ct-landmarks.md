# BR-039 — Expanded CT landmarks and unavailable-target hallucination

**Current frozen test: 26 VerSe vertebral-centre requests, full and partial CT. MedPelvis was rejected before trials.** The initial proposal is retained below for provenance; the revised design owns the actual experiment.

User request (2026-09-17): CT should have more than four landmarks; search for richer candidates, ask for more landmarks than the scan contains, and measure hallucinated detections. This follows BR-038's full-volume coordinate audit. The four-point PDDCA scope was an unexpanded pilot, not a limit of CT landmark datasets.

## Sources and selection, before trials

- [MedPelvis3D v3](https://zenodo.org/records/21757686): 99 CT cases, 57 expert reference points per case, explicit patient LPS millimetres; CC BY 4.0 in the downloaded record metadata. Individual case archives now allow bounded acquisition. Select first listed case 600001, independently of model results. Source MD5 `fab2715b8061cc970e9f051b503de3d2`. [Author repository](https://github.com/SweetDeathh/MedPelvis3D) documents coordinate and label conventions. Companion descriptor is under review, not a completed external validation of this benchmark.
- [MML](https://github.com/ithet1007/mmld_code): dental CT crown/root landmark candidate; potentially valuable for genuinely missing teeth. Not used here because subject-level missingness and dataset permission/annotation conventions have not been validated locally.
- [VISCERAL anatomy challenge](https://lmb.informatik.uni-freiburg.de/Publications/2016/Mai16/2016_visceral_anatomy_challenge.pdf): broader body landmarks, including classical methods. Relevant to future whole-body coverage; not substituted with segmentation-derived centroids or unverified mirror labels.

Use 23 relatively discrete MedPelvis targets: bilateral ASIS, AIIS, PSIS, PIIS, pubic tubercle, ischial spine, ischial tuberosity (14); eight anterior sacral foramina; sacral promontory (1). Retain all 57 source labels locally but exclude 34 broad-region/surface labels such as iliac ala and auricular surface from strict point scoring because a precise point convention is not documented in the accessible mapping. Definitions and overlays must be checked before freezing.

Add 10 named targets beyond a pelvis-only field of view: chin, dens tip, bilateral mandibular condyle apex, carina, sternal angle, C7 spinous tip, sella centre, bilateral medial malleolus tip. Confirm anatomical coverage from the actual CT. These are unavailable in the scan, not proven absent from the patient.

## Frozen design

Two fresh Terra/high attempts, no retries, 3600 seconds each, 2 CPU / 4 GB. One complete native CT and one explicitly partial 3D volume derived from the same CT. The latter tests unavailable pelvic targets rather than relying solely on easy distant-body-region negatives. All intensity voxels of each supplied volume are accessible; no selected image patches or GT-driven views are supplied. Neither positive/negative counts nor GT are given to the model.

Output native zero-based array `ijk`, tagged `voxel_ijk_zero_based`, with per-target `observed`, `out_of_fov`, or `uncertain`. An observed detection requires an in-bounds coordinate. An out-of-FOV answer may be null or an explicitly labelled out-of-bounds estimate; this is not counted as a hallucinated detection. Uncertain/null is tracked separately from a correct out-of-FOV answer. Unknown is not forced into a fabricated diagnosis of anatomical absence.

Primary hallucination metric: observed detections on source-verified outside targets divided by outside targets. Report explicit correct rejections and uncertain abstentions alongside it. Localization: number within 5, 10, 20 mm divided by all visible targets, with missed visible targets retained in the denominator. Mean error only covers returned observed points and is labelled accordingly. Reference interobserver variation reported by the dataset is about 4.56 mm, so a 5 mm cutoff is not a definitive clinical quality threshold.

Coordinates: independent SimpleITK LPS-to-index conversion, cross-checked with nibabel RAS affine; crop origins updated exactly; physical errors calculated using the full affine linear part. Oracle/nop plus synthetic all-present, all-null, wrong-space, one-voxel displacement, and renderer checks precede trials. Frozen task hashes and raw model sessions are retained.

This is a one-subject paired pilot, not an estimate across CT populations or proof of true anatomical-absence detection.

## Pre-trial source rejection and revised frozen design

The MedPelvis proposal above was rejected before freezing or any model trial. The downloaded 600001 archive matches the published MD5. Applying its documented CSV-LPS/NIfTI-RAS convention produces incorrect anatomical overlays (e.g. ASIS in the posterior half); image anatomy also increases inferiorly along a header-labelled superior axis. Saved author audit: `runs/br039-ct-landmarks/source/audit.png`. No guessed sign/registration correction was used to turn this into a benchmark. It remains a candidate requiring source clarification.

Replacement: [VerSe complete](https://github.com/anjany/verse), source subject 823, already selected in BR-012 as a typical-numbering calibration subject before this experiment. New acquisition here is the original CT intensity volume; prior curation had only masks, centroids and previews. The [source supplement](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41597-021-01060-0/MediaObjects/41597_2021_1060_MOESM1_ESM.pdf) records 7/12/5/5 segmentation and 24 presacral vertebrae for 823. Under this convention T13 and L6 are absent; this is stronger evidence than merely missing entries in an annotation file. CC BY-SA 4.0 applies to source and derived scan data.

**Final requests: 26 centres (C1–C7, T1–T13, L1–L6).** Full CT: 24 available / 2 absent. Partial CT: original native `k=0:920`, 13 available / 11 outside / 2 absent. Query sets are identical, neither count nor source subject ID is supplied. The cutoff is fixed before model trials and all centroid distances from that cutoff exceed 5 mm. C1 is the atlas-ring centre; the remaining points are body centres, not whole-vertebra mask centroids. This narrower anatomical family trades breadth for validated point definitions and genuine extra-level absence controls. It does not imply other CT landmark families are unimportant.

Output statuses now additionally include `absent` with a null coordinate. Report hallucination separately for out-of-FOV and absent targets; a wrong absence-vs-FOV classification is recorded in the confusion matrix, not silently accepted. Explicit outside extrapolations remain allowed and separately evaluated against original hidden centroids. A geometry mismatch or invalid output contract is not reported as a zero hallucination rate.

Both attempts retain the same Terra/high resources and controls specified above. No results from MedPelvis or from masks-only input will be attributed to Terra.

The source CT stores integer-valued intensities as float64. The supplied NIfTI and NPY use int16 only after exact equality and range checks; all voxel intensities and native geometry remain unchanged. This avoids spending the 4 GB model environment on redundant floating-point storage. The original downloaded bytes and checksum remain retained separately.

## Expanded candidate catalogue

| Family | Concrete requests | Ground-truth status in this round |
|---|---|---|
| Vertebral centres | C1–C7, T1–T13, L1–L6 | 26-name query implemented; 24 source centroids; extra-level absence supported by case-level source counts |
| Pelvic bony points | Bilateral ASIS, AIIS, PSIS, PIIS, pubic tubercles, ischial spines/tuberosities; S1–S4 anterior foramina; promontory | 23 proposed points within the 57-point MedPelvis release; rejected for scoring because the downloaded case's documented spatial convention failed overlays |
| Whole-body landmarks | Carina, aortic arch/bifurcation, pubic symphysis, clavicular and femoral landmarks | VISCERAL source-backed candidate family; no new verified case acquired here |
| Dental crown/root points | Named mandibular molar crown/root landmarks, with missing-tooth negatives where verified | MML candidate; missingness semantics and source files not locally validated, no trial claimed |

The original PDDCA pilot's four points were chin, bilateral mandibular condyle apex and dens tip. Its fifth supplied point was excluded for an unresolved illustration-dependent definition. Neither that small archive subset nor the prior coordinate audit was an exhaustive CT landmark curation.

Interpretation constraint declared while the blind runs are pending: the partial volume does not include the cranial counting anchor. Its global thoracic enumeration can therefore be less identifiable than in the full scan, particularly for distinguishing T12/T13 conventions. The key retains the full-source convention, but an `uncertain` response is an appropriate abstention and is not a hallucination. Do not turn a partial-volume exact-label mismatch, or the strict all-correct reward alone, into an unqualified anatomical reasoning failure.
