# BR-019 — Registration feasibility results

[Protocol](BR-019-slice-registration.md) · [Freeze](../evidence/br019-freeze.json) ·
[Author audit](../evidence/br019-author-audit.json) · [Measured receipt](../evidence/br019-results.json)

## Result

Both Terra/high attempts completed normally and passed. Retire both exact
snapshots from hard-task selection; no Sol escalation. There are no genuine
Terra failures in this round.

| Condition | Image | RMS error | Maximum error | Agent time | Result |
| --- | --- | --- | --- | --- | --- |
| R01 full view | 192 x 192 | 0.000477 mm | 0.000744 mm | 575.77 s | Pass |
| R02 partial view | 128 x 128 | 0.000586 mm | 0.001163 mm | 115.60 s | Pass |

Acceptance was RMS <=3 mm **and** maximum <=5 mm on the visible field. Both
matched oracle/nop pairs returned 1/0, and independent grading replays agree.
The file manifests and harness task checksums match across controls and each
model run. These are one attempt per condition on one shared source patient,
not success-rate estimates. Cropping did not establish greater difficulty;
the partial attempt was faster, but the two independent search strategies
and single-attempt design do not support a timing comparison.

The author public-input solver passes R01 and R02 in 4.62 and 3.59 seconds,
respectively. An isolated R01 replay inside the same public-only Linux image
passes in 4.51 seconds. These are numerical runtime measurements, excluding
authoring; they are not a comparison of total reasoning effort with the model.

## What the full-view agent actually did

The retained trajectory has 46 steps. Terra constructed a six-parameter
centre/orientation search against the public trilinear forward model. Early
intensity and edge searches found plausible wrong heart sections. It then
used the disclosed in-volume corner constraint to eliminate impossible centres,
matched a smoothed body/lung silhouette, and refined the result with full
resolution intensity least squares. The final public render had 99.8481%
exactly matching pixels and maximum intensity difference 1.

This is independent method discovery from the public task: no author solver,
initial pose or extra advice was sent. The frozen instruction appears in the
recorded user message, and runtime contexts identify `gpt-5.6-terra` with high
effort. The supervisor found no task-bearing user message containing extra
hints and no trace access to authoring, frozen keys, tests or solution paths.
Actual Docker image inventories separately confirm their absence. Trace
consistency cannot establish provider-side model identity or prove an
unobservable absence of all external knowledge.

R01 used 1,061,696 input tokens including 998,016 cached, and 16,202 output
tokens; the harness estimates $0.5214. These are retained harness counters and
cost estimates, not an independently measured bill.

## What the partial-view agent did

The fresh R02 trajectory has 20 steps. It sampled 100,000 six-degree-of-freedom
poses at stride 4, kept 30 candidates and least-squares refined the top four;
three converged to the match. It converted its voxel-space solution to LPS and
checked the public rendering. Its actual image contained only the same allowed
public files, and the supervisor found no access to the R01 solution/history,
author solver, hidden pose, tests or solution. Runtime contexts and the frozen
instruction also match the requested Terra/high configuration.

R02 used 215,922 input tokens including 196,864 cached, and 4,389 output tokens;
estimated cost $0.1302. Combined model execution was 11.52 minutes, with a
harness-estimated cost of $0.6515. This excludes authoring, image building and
the supervisor's work.

## Interpretation and next-stage validity

The design is feasible as a compact geometry task. A thin oblique section from
the same volume also retains exact local texture, allowing almost exact
numerical recovery without identifying the apex or understanding a cardiac
view. The tiny pose errors measure agreement with the generating transform;
they do not establish anatomical precision at that scale. Source spacing is
1.5 mm and the apex-side direction is a mask-based heuristic.

Partial visibility is a distinct predeclared condition, not independent
patient evidence. A different scan or modality would remove the exact-texture
advantage, but first needs verified subject pairing, phase/coverage review and
independent correspondence truth. If no rigid transform can align the anatomy
within tolerance, forcing one would create an invalid task. The initial CT
sample is not an expert-approved standard four-chamber/mitral-valve plane;
that clinical admission step remains open.

The local visual review is generated at
`runs/br019-registration/review/index.html` with target/recovery blends and
`comparison.png`. Generated images and raw trials remain local. No submission
workspace or closed interview report has been changed.
