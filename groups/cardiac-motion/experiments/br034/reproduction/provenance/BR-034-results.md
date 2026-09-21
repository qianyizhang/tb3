Source: `docs/research-rounds/BR-034-results.md`; original SHA-256: `59992d48561779ed126a7fafc4ae31a14f56afe68034cd84511a3516f7a310fd`.
Repository source locators below are provenance; they are not required runtime inputs.

# Clinical adaptation works computationally; functional estimates fail

[Open the Clinical Heart Lab](http://127.0.0.1:8771/index.html).
The frozen protocol (repository source locator: `BR-034-pathological-echo.md`) and
supplementary control amendment (repository source locator: `BR-034-preserved-control-amendment.md`) retain
selection, thresholds and their timing. All source images and raw trials remain
local. This is a selected research pilot, not clinical validation.

## What changed from the previous case

BR-032 had a poor volunteer scan without reconstruction references. This study
uses real clinical [EchoXFlow](https://huggingface.co/datasets/Ahus-AIM/EchoXFlow)
volumes with clinician/software-derived LV endocardial surfaces. Ten examinations
were screened before the trial. The clearer primary case has reference EF
45.31%, supporting a mildly reduced functional phenotype. No patient-level
etiologic diagnosis is supplied by this release. The initial target of 25–45%
was broadened to mild dysfunction before any model result was available.

Sol received 18 contiguous native frames at 22.6 volumes/s, a calibrated 1 mm
Cartesian image volume, unannotated previews and the initial LV cavity surface.
All subsequent reference surfaces and EF values were withheld. The old
fixed-measurement-table solver was optional adaptation context. Sol replaced it
with sequential 3D TV-L1 optical flow and cyclic drift correction. The output
retains 1,946 vertices and 3,888 faces through time. This is initialized cavity
tracking, not segmentation from scratch or a myocardial mechanics solution.

The author curated/decoded the data, supplied the initial clinical annotation,
froze the independent verifier, ran the trials/replays and built the viewer.
Sol authored the reconstruction executable and its interpretations. No reference
motion, later surfaces, source EF or diagnostic feedback was provided to Sol.

## Independent clinical-reference comparison

The fresh Sol/xhigh attempt completed normally in 1,207.8 seconds. Its artifact
is valid, but the frozen pilot reward is zero. The unchanged executable then ran
on two hidden clinical cases without model feedback or code changes.

| Case | Frames | Reference EF | Sol EF | EF error | Mean surface distance | ESV error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Primary, mildly reduced | 18 | 45.31% | 22.01% | 23.30 pp | 1.89 mm | 47.18% |
| Hidden, mildly reduced | 35 | 47.62% | 21.68% | 25.94 pp | 1.85 mm | 57.70% |
| Supplementary hidden, preserved | 48 | 60.29% | 29.80% | 30.49 pp | 2.24 mm | 76.79% |

All three pass the mean-distance and EDV gates. The hidden mildly reduced case
also passes the p95-distance gate. All fail EF, ESV and functional-severity
classification. Maximal framewise p95 distances are 6.90, 5.99 and 7.97 mm.
Initial-frame/EDV accuracy benefits from the supplied reference initialization;
it should not be credited as recovered anatomy.

Timing is much closer than contraction amplitude: reference/estimated systolic
indices are 11/10, 15/15 and 23/24 (zero based). In the primary case, the predicted
minimum cavity is 98.10 mL versus 66.65 mL in the reference. At reference systole,
a posthoc middle axial-third diagnostic shows mean radial narrowing of 1.24 mm
in the prediction versus 6.11 mm in the reference. These local-axis summaries
are geometric diagnostics, not AHA regional strain or material-motion truth.

## Adaptation and executable response

The independent original replay reproduces every vertex exactly. Hidden-case
runtimes are 102.8 and 168.8 seconds on 4 CPUs/8 GB, within the declared five-minute
limit. The still-input replay yields exactly stationary vertices and EF 0.0%.
The five-frame phase shift produces exactly the corresponding permutation of
the original vertices and volumes: zero coordinate difference and zero volume
MAE after undoing the shift. It completes in 70.2 seconds.
This is a substantial improvement over BR-032, whose fixed tables kept pulsing
on a still video. Complete replay results and artifact hashes are retained in
the evidence receipt and viewer.

Code inspection confirms actual volumetric image registration. The executable
reads the current arrays, calibration and initial surface; it does not read the
old solver or preview images and contains no patient-specific motion tables.
However, passing input-response checks establishes behavior under those changes,
not accurate physiology. Its improved image correlation, closed topology and
smooth cyclic motion do not prevent severe underestimation of cavity contraction.

An initial independent replay launch failed before executing because Harbor
removed the tagged image during cleanup. That exit-125 receipt is preserved.
Rebuilding the unchanged frozen Dockerfile from cached layers resolved the issue;
the successful original replay is retained separately as `original-v2`. This is
an infrastructure event, not a model or anatomical failure.

## What the diagnostic component established

Before fitting, Sol described the primary images as provisionally showing
mild-to-moderate reduction, with substantial uncertainty. That impression includes
the reference's mild category. After fitting, it deferred to its computed 22.0%
EF and reported severe reduction with moderate confidence. Its stated sensitivity
range, 16.3–27.7%, excludes the 45.3% reference. The other two stated ranges also
exclude their reference values. The code generates these ranges from a heuristic
using registration residuals and closure error; they are not calibrated clinical
confidence intervals, a limitation Sol itself states.

All three outputs select the severe category. For the preserved-function case,
Sol recognizes proximity to the severe/moderate boundary, but that does not
address the much larger discrepancy with preserved reference function. The two
abnormal cases are correctly recognized as reduced at a coarse binary level,
while severity is overstated and the preserved control is falsely called reduced.

The model therefore made the primary severity interpretation less consistent
with the reference than its initial visual impression. This within-session
comparison is descriptive; it is not a randomized test of whether modeling helps
diagnosis. Functional bins were supplied in the task, so these outputs do not
establish independent medical knowledge. Sol appropriately declined to infer
infarction, ischemic cause, valve severity, hemodynamics or myocardial strain.

## Acceptance criteria and interpretation

Keep geometry, motion response, function and interpretation as separate gates.
The static initial-surface control alone achieves mean distance 2.70 mm, within
the 3 mm threshold, despite a 45.31 pp EF error. Average geometric proximity is
therefore inadequate as the sole acceptance criterion. The independent EF/ESV
checks reject all three moving but functionally inaccurate models.

This case is a useful, bounded challenge: real images with visible borders,
complete primary/hidden reduced-case sector coverage, a helpful initialization,
normal agent completion, and independent dynamic references. It does not prove
a model capability ceiling. A next algorithmic comparison should test whether
explicit endocardial boundary fitting corrects optical-flow undercontraction;
that is a hypothesis, not a result from this trial. A stronger etiologic diagnosis
task would require independent clinical labels and the relevant multiview/Doppler
evidence rather than expanding claims from a cavity model.

The supplementary preserved-function case was added after dispatch and replaced
on input-quality grounds before model completion. Its rejected predecessor had
17.8% of initial reference vertices outside the ultrasound sector; the replacement
has only 0.21% initially and 0.0086% overall. The selected cases differ in image
quality and frame rate and are not a matched diagnostic cohort.

Clinical annotations have uncertainty and are not independently measured material
trajectories. Whole archive SHA-256 values match publisher LFS values; direct
Blosc decoding agrees with Zarr. Publisher per-array hash serialization was not
reproduced by raw C-order byte hashing, and that unresolved convention is recorded.
All scans are public. No external source retrieval or delegation was observed in
the agent trace, but pretraining exposure remains unknown.

Detailed evidence (repository source locator: `../evidence/br034-clinical-adaptation-results.json`) retains
source provenance, snapshots, controls, runtime checks, replays and author review.
