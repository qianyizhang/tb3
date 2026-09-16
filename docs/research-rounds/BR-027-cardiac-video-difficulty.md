# BR-027 — Recover cardiac motion from video

Status: author screen completed, 2026-09-16. One-anchor case retained as a harder candidate; no input-legal complete pass or model-difficulty qualification yet. The plan below was recorded before outcomes.

## User request and ownership

The user reviewed the cardiac viewer and said, “this case seems too easy, tune up the difficulty,” in task `01a0a967-f33c-70a0-b661-d8919246b13b`. This authorizes a bounded difficulty follow-up to [the cardiac BR-025 pilot](BR-025-cardiac-reconstruction.md). Another active session used BR-025 for vessel curation and BR-026 for a vessel experiment. Preserve those records and the original cardiac results; this follow-up owns this document, explicitly named `br027-cardiac-*` evidence, `probes/cardiac-reconstruction/authoring/video_difficulty/`, and ignored `runs/br027-cardiac/`.

## Predeclared difficulty change

The earlier solver read accurate cavity contours at every time point, so it did not need to interpret the ultrasound or recover contraction. Keep Patient001, the same four calibrated view directions, the full 30-frame cycle and the same eight withheld evaluation directions. Replace all-frame contours with:

- **Two reference frames:** contours only at filename frames 2 and 17. Treat these as explicit supplied anchors; the source config's frame-index convention remains unresolved.
- **One reference frame:** contours only at filename frame 2. Recover subsequent contraction and relaxation from the actual images. This is the main candidate.

Both conditions retain the native images, scale, view angles, initial anatomy and a coordinate convention. Neither introduces synthetic image degradation, withheld calibration, a single-view uniqueness claim, new anatomy lacking references, or reduced reasoning time.

## Author screen

1. Build separate public-input directories containing only four image sequences, the allowed anchor mask(s), geometry and a short deliverable contract. Exclude all target-time contours, source metadata carrying EF/ES, source OBJ meshes, and dense-reference outputs. Hash the public inputs before solving.
2. Solve using a static-anchor control, endpoint interpolation for the two-anchor condition, and ordinary image-based optical-flow tracking. Freeze predictions before reading withheld masks. Test both one-anchor and two-anchor tracking without selecting hyperparameters using evaluation labels.
3. Reuse the previous development gates: mean withheld Dice >=0.90, mean pairwise HD95 <=1.0 mm, volume-curve mean relative error <=10%, EF error <=5 percentage points, and closed positive-volume meshes. These remain derived-reference development gates, not clinical or final TB3 thresholds. Add direct error on unsupplied frames of the input views to separate segmentation/tracking error from 3D interpolation error.
4. Grade EF from the extrema of the recovered full volume curve and grade the curve separately, avoiding the unresolved source config index base. Recompute the clean-contour control under exactly the same convention. Track phase differences descriptively; exact expert phase acceptance remains unqualified.
5. If simple tracking succeeds, do not describe the case as hard. If it fails, try a stronger image-based author method within this bounded session to distinguish an inadequate baseline from a usable harder task. Report any ground-truth-guided iteration as development, never blind discovery. Do not select stricter gates after seeing failures.
6. Preserve raw outcomes, code, hashes, runtime and a reviewable viewer. No publication, cleanup of other sessions, or formal provider qualification is part of this author screen.

The published [EchoTracker work](https://github.com/riponazad/echotracker) motivates tracking as a real research problem. Its results are not evidence of failure by an LLM on this fixture. The prior clean-contour pass remains a calibration result.

## Stronger-method plan after the first screen

The first DIS screen completed normally: two-anchor tracking passed; one-anchor tracking failed the unchanged Dice/boundary/volume/EF gates. A source-versus-prediction montage shows boundary drift, especially around contraction in the 135-degree view. The next author method is explicitly **development-informed**: refine each propagated mask with image-intensity GrabCut, retaining an eroded interior seed, a bounded exterior search region, the largest connected component touching the interior, and the supplied anchor unchanged. Use fixed constants (interior distance >60% of its maximum, 15-pixel exterior band, 20-pixel crop padding, five GrabCut iterations). Do not grid-search those constants against withheld labels. Freeze its outputs before a new evaluation. This is a bounded stronger baseline attempt, not a promise of an input-legal positive control.

## Result and selected difficulty

**Keep the four-view, one-anchor condition as the harder candidate.** It supplies 120 ultrasound frames but only four masks, all from frame 2; the original four-view control supplied 120 masks. The conceptual task is recovering the inner cavity boundary and basal plane through contraction and relaxation. The deliverable remains one 30-frame LV cavity mesh, volume curve, EF and extrema frame references. Additional chambers, valves and flow would introduce different reference-data requirements, not a calibrated escalation of this case.

All methods completed normally on CPU. All meshes were closed, had positive volume, and had zero nonmanifold edges or degenerate triangles. Every scored sparse reconstruction used the same eight withheld directions and all 30 frames.

| Inputs and author method | Mean withheld Dice | Mean HD95, mm | Volume curve error | EF error, pp | Result |
|---|---:|---:|---:|---:|---|
| All-frame contours, geometric reconstruction | 0.937 | 0.623 | 2.31% | 1.27 | Pass |
| Two anchors, DIS image tracking | 0.920 | 0.841 | 7.82% | 0.82 | Pass |
| One anchor, DIS image tracking | 0.887 | 1.114 | 29.16% | 21.60 | Fail |
| One anchor, DIS plus GrabCut refinement | 0.869 | 1.636 | 7.70% | 1.32 | Fail shape |
| One anchor, static copy | 0.825 | 1.605 | 78.21% | 64.02 | Fail |
| Two anchors, linear interpolation with endpoint hold | 0.889 | 1.039 | 18.42% | 0.26 | Fail shape/curve |

The last control clamps outside the two anchors; periodic interpolation was not tested. Its failure does not establish that all image-free temporal priors fail. Two-anchor image tracking already passes, so that condition is retained as an intermediate control rather than a hard-task claim.

The direct segmentation Dice on unannotated frames of the four input views was 0.897 for one-anchor tracking, 0.937 for two-anchor tracking, and 0.867 after GrabCut. This locates the main loss in image interpretation, before the sparse-view 3D interpolation. One-anchor tracking underestimates contraction: recovered EF 42.42% versus the derived reference's 64.02%. Refinement reaches EF 65.34% while damaging contour agreement. Thus an acceptable scalar EF and a watertight mesh can accompany an incorrect cavity.

The extrema-derived reference has maximum volume at filename frame 3 and minimum at frame 17. One-anchor DIS chooses 30/19, two-anchor DIS 2/19, and refinement 2/20. These are descriptive differences; the source's expert phase-index convention and uncertainty have not been resolved. The current one-anchor origin is derived solely from its supplied mask (y=184.5 px), and EF uses full-curve extrema. The original BR-025 files retain their older origin and config-phase convention; compare methods within this round's recomputed controls.

**What this establishes:** removing all-frame contours makes the author baselines fail at unchanged gates; a two-anchor input-legal method and the clean-contour control pass. **What remains unqualified:** an input-legal complete solution for the one-anchor condition, a normally completed independent agent attempt, annotation uncertainty, and external patient generalization. These baseline failures are not a Terra/Sol failure claim or proof that the task is clinically identifiable. The stronger method used [OpenCV's documented GrabCut interface](https://docs.opencv.org/4.x/d8/d83/tutorial_py_grabcut.html), with fixed, development-informed parameters and no hidden-label sweep.

## Retained artifacts and review

- [Full metrics](../evidence/br027-cardiac-results.json) and [integrity receipt](../evidence/br027-cardiac-integrity.json): source pointer, public-input hashes, code hashes, method receipts, aggregate distributions, topology and versions.
- [Author code and reproduction instructions](../../probes/cardiac-reconstruction/authoring/video_difficulty/README.md).
- Local public packages: `runs/br027-cardiac/public/one_anchor/` and `two_anchors/`. Their `TASK.md` and `geometry.json` define the deliverable; every file is hashed. No target-time masks, clinical config, OBJ meshes or derived answers are included. Access separation is by reviewed code, not an OS sandbox or blind provider setup.
- Raw predictions/receipts: `one-anchor-v1/`, `two-anchors-v1/`, `one-anchor-refined-v1/`; first and second evaluations remain in `evaluation-v1/` and `evaluation-v2/` under `runs/br027-cardiac/`. Solver times were 4.18 s, 4.41 s, and an additional 27.74 s for refinement; acquisition, packaging, evaluation and UI time are excluded.
- Review viewer: `runs/br027-cardiac/evaluation-v2/viewer.html`, served locally at port 8767. It starts with only permitted annotations visible and has an explicit result/reference reveal. It embeds private references for review and must never be handed to the tested solver. The original viewer at port 8766 and its underlying results remain intact.

Input file inventory, hashes, fixed-code receipts and evaluator hashes were checked after execution. This is a local author development screen; data remain local under the source access/redistribution limitations from BR-025. No workshop-tooling changes, formal task admission, publication or commit occurred.
