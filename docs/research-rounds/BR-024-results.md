# BR-024 — harder real-deformation candidates

Status: complete. One admitted new patient produces a normal Sol/xhigh miss;
the other patient remains unqualified. No further trials are scheduled.

**A valid harder-case candidate is now available:** Sol/xhigh finishes normally
at **12.73 mm RMS / 32.20 mm maximum** on patient 3 / view 1, while an isolated
public-input author method passes at **2.13 / 3.42 mm**. This is one substantial
miss on a selected case, not evidence of reliable difficulty across attempts.

We screened six oblique views from two previously unused patients in the
hash-verified Learn2Reg LungCT 1.11 inhale/exhale data. These are real changes
between respiratory acquisitions. The task remains eight 2D-to-3D point
correspondences with a supplied nominal source frame, 3 mm RMS / 5 mm maximum
acceptance, ordinary library access and a 30-minute model budget.

## What was selected and what was held

The [selection protocol](BR-024-harder-registration.md) fixed the patients,
geometric constraints, three highest-ranked views per patient, admission gate
and maximum two model attempts before screening results. Ranking uses the
privileged best global affine residual: a measure of deformation that a single
matrix cannot explain. It is not an image-matching difficulty estimate or an
unbiased held-out sample.

| View | Best global affine RMS | Local-affine author RMS / max | Translation author RMS / max | Neighborhood author RMS / max | Disposition |
| --- | ---: | ---: | ---: | ---: | --- |
| Patient 2 / view 1 | 10.33 mm | 5.82 / 15.48 | 7.14 / 16.65 | 6.66 / 15.48 | Held |
| Patient 2 / view 2 | 8.76 mm | 13.20 / 27.43 | 14.85 / 35.21 | 2.91 / **5.0013** | Held; near pass |
| Patient 2 / view 3 | 8.71 mm | 20.32 / 41.67 | 22.90 / 46.31 | 8.28 / 14.33 | Held |
| Patient 3 / view 1 | 5.47 mm | 2.66 / 6.18 | **2.13 / 3.42** | Not run | Admitted |
| Patient 3 / view 2 | 4.95 mm | 12.86 / 34.93 | Not run | Not run | Lower-ranked; not admitted |
| Patient 3 / view 3 | 4.95 mm | 14.17 / 34.95 | Not run | Not run | Lower-ranked; not admitted |

Every candidate has eight manual source landmarks within 0.35 mm of the plane,
at least 15-degree obliquity, source spans at least 70 mm in both directions,
16 mm query margins and image corners within the acquired volume. The earlier
patient-1 task had 3.60 mm best global affine residual. Higher residual here
establishes stronger nonuniform deformation of these points, not greater model
difficulty by itself.

All six views fail the unchanged author local-affine patch matcher. A
[separately fixed rescue](BR-024-rescue-plan.md) reuses the existing BR-022
translation-only method and admits the first patient-3 view. Its actual public
task image repeats the same pass at 2.1329 mm RMS / 3.4161 mm maximum. The
independent interpolation check differs by at most 0.000030 HU; oracle,
tolerated perturbation, missing answer, shuffled points and boundary controls
behave as specified. Actual source/manual-target panels show visible anatomy;
this is author review, not expert clinical adjudication.

Patient 2 receives one [final fixed neighborhood rescue](BR-024-neighborhood-plan.md),
with code hashed before execution. It does not admit any view. View 2 misses
the maximum threshold by only **0.00127 mm**. We retain that as a near pass
under the exact frozen gate, without claiming that such a tiny difference
establishes substantive anatomical difficulty or unsolvability. No patient-2
model trial was launched, and there is no further rescue in this round.

## Why the harder patient is interesting

Patient 2 / view 1 exposes a stronger ambiguity than the earlier search-box
failure. All eight manual matches lie inside the initial ±35 mm world-axis
search box; the largest component displacement is 21.25 mm. Yet q02 is already
13.98 mm wrong after the first large-context fit and ends 15.48 mm wrong with
a low matching loss of 0.0534. Subsequent smaller patches do not repair it.

The neighborhood rescue finds 27 nearby image matches. Their robust displacement
prediction lies only 1.11 mm from the wrong query match and 14.98 mm from the
manual reference. Its fixed consistency rule therefore keeps the wrong answer.
It also moves an initially adequate q08 away from its reference. Smooth agreement
among neighbors can support a coherently wrong correspondence. This is an
author-method observation, not a demonstrated failure of Sol's earlier, more
involved visual and neighborhood strategy.

These [offline diagnostics](../evidence/br024-curation-analysis.json) use labels
only after the public-input outputs have been saved. No truth initialization,
per-query oracle selection or label-driven parameter adjustment enters a solver.

## Fresh model attempt and approach

| Attempt | RMS / maximum | Outcome | Agent time |
| --- | --- | --- | --- |
| Oracle | 0 / 0 mm | Pass | Control |
| Nop | No answer | Expected failure | Control |
| Author translation-only baseline | 2.133 / 3.416 mm | Pass | Separate feasibility run |
| Sol / xhigh | **12.731 / 32.203 mm** | **Normal completed failure** | **1,313.1 s (21m 53s)** |

The oracle passes and nop fails on identical task bytes. Runtime records show
`gpt-5.6-sol`, `xhigh`, the frozen instruction, normal finalization and no
exception. The model stops voluntarily before its 1,800-second limit. Independent
host regrading reproduces all errors. q02 is 14.78 mm wrong, q04 32.20 mm, and
q06 5.82 mm; the other five are within 2 mm. This is not a timeout or a tiny
threshold miss.

The initial image has only the five public data files and source notice, an
empty answer directory, and no exhale volume, manual labels, author solver or
prior agent artifacts. No hint or prior answer is supplied. The recorded trace
shows use of the **preinstalled SimpleITK registration library**, NumPy, SciPy
and Pillow. No external installation, download, remote registration service or
annotation lookup is observed. This is different from BR-023's own patch matcher:
here Sol explicitly delegates numerical registration to a standard library.

Its sequence is:

1. Repeat the 2D image into a thin slab; fit Euler rigid transforms from seven
   initial offsets along the plane normal. Inspect resliced comparisons.
2. Add B-spline deformation with correlation or mutual information, then refine
   with ANTS neighborhood correlation. Inspect fitted images and orthogonal
   views. Correct internal SimpleITK API/serialization errors and continue.
3. Search local translations with SciPy differential evolution around the fitted
   positions. Increase B-spline mesh density and check edge-gradient alignment
   after noticing unstable landmarks.
4. Select query-specific estimates from its own image reviews and patch runs.
   Final q01/q02/q05/q07/q08 use `localopt7.py` radius 11; q04/q06 use radius 8;
   q03 uses the edge-refined transform. Submitted coordinates match the printed
   selected positions rounded to 0.01 mm.

## Where this attempt went wrong

The [transform-state audit](../evidence/br024-stage-analysis.json) reconstructs
all 17 retained named transforms with the composition used in Sol's own code.
All fail the point tolerances. Selected intermediate states show why visually
plausible alignment is insufficient:

| Recorded state | RMS / maximum | q02 error | q04 error |
| --- | ---: | ---: | ---: |
| Chosen rigid initialization | 13.61 / 19.30 mm | 19.30 mm | 14.19 mm |
| Correlation B-spline, mesh 5×4×1 | 11.89 / 26.12 mm | 19.71 mm | 26.12 mm |
| Neighborhood correlation, radius 5 | 11.03 / 23.28 mm | 19.41 mm | 23.28 mm |
| Denser correlation mesh 7×6×1 | 12.91 / 32.73 mm | 14.64 mm | 32.73 mm |
| Edge refinement from dense mesh | 12.11 / 27.67 mm | 19.21 mm | 27.67 mm |
| Final mixed local estimates | 12.73 / 32.20 mm | 14.78 mm | 32.20 mm |

The flexible models improve several points but move q04 farther from its true
correspondence. The model recognizes unstable matches yet stays near its fitted
deformation instead of reopening a broad correspondence search.

There is a precise geometric obstruction in the final local search. Around the
dense-mesh q04 estimate, the manual destination requires a **32.50 mm shift in
one local axis**, while the code permits only ±7 mm per axis. Even the closest
allowed translation remains **25.50 mm** from the reference. Therefore that
local stage cannot recover q04, regardless of optimizer quality. The submitted
q04 comes from that stage. Earlier local refinement likewise excludes both q02
and q04 from the 5 mm acceptance region.

The final q02 search is different: its allowed cube reaches within 3.18 mm of
the reference, yet the selected patch match remains 14.78 mm wrong. Search
coverage alone does not explain every miss; image similarity and candidate
selection also matter. The final q06 search includes the reference but ends
5.82 mm away.

These are direct geometry checks and posthoc scores of saved states. They do
not isolate every library, similarity metric, mesh, visual decision or optimizer
as an independent causal effect. No extra model run or label-guided solver
repair was performed. The passing author method shows that this instance is
solvable from the permitted data; adding deformation parameters is not sufficient
to make correspondence selection reliable.

## Interpretation and limits

Retain **patient 3 / view 1** as a Sol failure candidate, with the frozen task,
passing author method, matched controls and concrete failure mode. One attempt
does not establish stable difficulty; replication would be a separate study.
Patient 2 / view 1 is a promising coherent-false-match stressor, and view 2 is
a near-solvable candidate, but neither is admitted under this round's gate.

This round separates anatomical nonlinearity, public-input task feasibility,
and model outcome. Only one selected view has been admitted; author failures
on the other views do not establish Sol failures. One attempt per admitted
patient cannot estimate reliability, and changing patients also changes anatomy,
image appearance, view geometry and landmark placement. It is not a controlled
one-factor deformation ablation.

Source annotations are public, so recorded-trace and image audits cannot rule
out training contamination. Eight sparse points and these engineering tolerances
do not establish dense-field accuracy or clinical usefulness. The prior task
freezes, completed result receipts, closed interview site and sibling submission
remain unchanged.

## Evidence

- [Interactive local CT review](../../runs/br024-harder-registration/review/index.html).
- [Selection and trial protocol](BR-024-harder-registration.md),
  [translation rescue](BR-024-rescue-plan.md), and
  [final neighborhood rescue](BR-024-neighborhood-plan.md).
- [Patient-3 task freeze](../evidence/br024-patient3-freeze.json) and
  [isolated author audit](../evidence/br024-patient3-author-audit.json).
- [Candidate screen](../evidence/br024-screen.json) and
  [curation diagnostics](../evidence/br024-curation-analysis.json).
- [Completed trial and curation receipt](../evidence/br024-results.json) and
  [all retained transform scores and search bounds](../evidence/br024-stage-analysis.json).
- [Concise approach interpretation](../evidence/br024-approach-analysis.json).
- [Authoring and reproduction](../../probes/registration-deformation/authoring/br024_README.md).

The [official L2R repository](https://github.com/MDL-UzL/L2R) supplies evaluation
conventions. Source arrays and manual CSVs remain the previously verified
LungCT 1.11 release, attributed to Hering, Murphy and van Ginneken (2020),
Radboud University Medical Center, under
[CC BY 4.0](https://doi.org/10.5281/zenodo.3835682). Raw scans, sessions, configs,
captured transformations and generated reports remain local.
