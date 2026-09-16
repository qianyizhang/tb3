# BR-022 — registration failure analysis

Completed 2026-09-16. The unchanged 2D task is solvable by Terra/high, but some
attempts accept wrong anatomical correspondences. The two predeclared fresh
attempts split: one normal failure and one normal pass. The original composition
bug is real; correcting it does not explain away or rescue the original miss.
Retain this case as a diagnostic example of strategy variation, and retire it
as a reliably difficult Terra snapshot under the pass-retirement rule.

The [analysis plan](BR-022-registration-failure-analysis.md) and
[machine-readable plan](../evidence/br022-plan.json) were fixed before these
outcomes. They hold the selected patient, eight queries, task files, prompt,
tool access, 1,800-second limit and 3 mm RMS / 5 mm maximum tolerance constant.
The original [BR-021 results](BR-021-results.md) remain unchanged. These are
lung respiratory correspondences, not expert-certified cardiac standard views.

## Fresh agent outcomes

| Attempt | Selection | RMS / maximum error | Agent time | Outcome |
| --- | --- | --- | --- | --- |
| Original BR-021 | Retrospectively selected miss | 12.641 / 23.796 mm | 306.6 s | Normal failure |
| BR-022 repeat 2 | Prospective, same frozen task | 24.905 / 34.165 mm | 374.7 s | Normal failure |
| BR-022 repeat 3 | Prospective, same frozen task | 2.021 / 4.646 mm | 290.1 s | Normal pass |

Both fresh attempts used independent Terra/high sessions, one attempt each,
zero retries and no hints, earlier code, answers or counterfactual findings.
Both ended voluntarily before the time limit. New matched oracle/nop controls
scored 1/0; independent regrading agrees with all four verifiers. The task
checksum matches the original attempt. Initial images contain exactly the six
public files and an empty answer directory; the full source exhale volume,
author solver and labels are absent. Runtime contexts confirm the requested
model and effort. See the [collected evidence](../evidence/br022-results.json).

**Repeat 2** tried SimpleITK B-spline and Diffeomorphic Demons registration
on a nominal 2D reslice, then chose Demons-derived query starts. Its own patch
search covered ±8 mm in-plane and ±12 mm along the fixed nominal normal;
refinement added ±2 mm translation, in-plane rotation and independent scales.
All eight final errors exceed 5 mm. This route does not contain the original
affine/B-spline composition defect. q04 had approximately 0.816 local
correlation yet was 34.17 mm wrong. This supports correspondence/search problems
beyond that defect, without experimentally isolating repeat 2's cause.

**Repeat 3** explored a correctly composed affine/residual B-spline fit, but
its final search starts from the nominal query locations, independently of that
fit. It searched parallel planes from −30 to +30 mm normal depth and ±28
pixels (35 mm) in-plane, then refined translation and local 3D orientation.
It inspected competing image patches and changed q08 from the highest-NCC
coarse candidate to a lower-ranked anatomical match. It also checked patch
size stability. Final numerical patches were only 15×15 samples at 1.25 mm
spacing (8.75 mm half-span); the stability sweep used 9×9 through 21×21
samples. Thus larger numerical patches are not necessary when combined with
a different search and verification strategy. No counterfactual isolates the
contribution of its visual selection or orientation refinement.

Both fresh traces use installed SimpleITK and self-written NumPy/SciPy code.
No download, annotation lookup or external network use was observed. This is
an audit of recorded behavior, not proof against training contamination from
public source annotations. The two prospective outcomes are not pooled with
the selected original failure into a population success-rate estimate.

## The composition repair does not rescue the original solver

Recovered shell code reproduces all eight original output coordinates to
within **6.4×10⁻⁹ mm**, consistent with printed-number rounding. The original
trial image had been removed by the harness. Replay instead used a retained
image built from the identical frozen Dockerfile, with matching public-file
hashes and pinned numerical packages. The network was disabled and no hidden
labels were mounted. This deviation and the successful numerical equivalence
check are recorded in the [execution audit](../evidence/br022-author-execution.json).

The original code fits a B-spline against the original moving image, then
evaluates `A(B(x))`, adding an affine transform inconsistent with that fit.
The minimal repair evaluates `B(x)` using exactly the same fitted transforms.
This concerns the image used when fitting B, not merely transform order; see
the [SimpleITK transform contract](https://simpleitk.org/doxygen/latest/html/classitk_1_1simple_1_1CompositeTransform.html).

| Mapping, original seed 17 | Search bounds | RMS / maximum error |
| --- | --- | --- |
| Original A(B(x)) | ±9 mm | 12.641 / 23.796 mm |
| Minimal consistent B(x) | ±9 mm | 12.410 / 23.786 mm |
| Original A(B(x)) | ±30 mm | 19.989 / 34.662 mm |
| Minimal consistent B(x) | ±30 mm | 13.799 / 32.156 mm |
| Refit B on affine-resampled image, then A(B(x)) | ±9 mm | 19.839 / 48.517 mm |
| Refit B on affine-resampled image, then A(B(x)) | ±30 mm | 16.996 / 36.075 mm |

All 12 primary combinations (two mappings × two bounds × seeds 17/41/73)
failed. Both secondary refit conditions failed as well. Every result is retained
in the [solver analysis](../evidence/br022-solver-analysis.json); none is selected
using hidden scores for a later agent. At unchanged optimizer settings, wider
bounds enlarge the search problem and competing peaks; these failures do not
show that exhaustive optimization would fail.

Stage errors locate the larger problem upstream: nominal positions have
21.53 mm RMS error, rigid fitting reduces this to 11.07 mm, and direct B-spline
mapping increases it to 13.53 mm. Adding the extra affine changes that to
13.56 mm. Final local patch search reaches 12.64 mm. The extra composition is
therefore a small contributor in this recovered trajectory, not its main cause.

## Different queries fail for different reasons

The following analyses are explicitly privileged: manual target locations enter
geometric bounds and objective diagnostics only. They are not admissible
solver inputs, model hints or autonomous successes.

**Search support makes q04 unrecoverable.** The original final stage permits
±9 mm translation along three orthonormal local axes. q04 needs approximately
(−9.12, −27.27, +14.19) mm in those coordinates. Its manual target lies
**18.99 mm from the nearest point in the search box**, already beyond the 5 mm
maximum tolerance. Across all queries, even perfect optimization inside those
boxes has a 6.78 mm RMS lower bound. Correcting composition alone still leaves
a 6.67 mm lower bound. The ±30 mm boxes for the original and minimally repaired
mapping contain every target, but the finite searches still select bad matches.

**Local similarity can prefer the wrong anatomy.** q01 and q06 are inside
the original search boxes. At the submitted wrong points, the original mixed
raw/high-pass NCC objective exceeds both its value at the manual target and
the best value found by a fixed-seed search within 3 mm of that target.

| Query | Original error | Target in original box? | Score at manual target | Score at submitted point | Best found within 3 mm of target |
| --- | --- | --- | --- | --- | --- |
| q01 | 16.33 mm | Yes | 0.269 | 0.588 | 0.485 |
| q02 | 18.51 mm | No; 2.65 mm from box | 0.553 | 0.599 | 0.722 |
| q04 | 23.80 mm | No; 18.99 mm from box | 0.650 | 0.532 | 0.690 |
| q06 | 8.64 mm | Yes | 0.521 | 0.669 | 0.620 |

These patterns support distinct mechanisms: q04 has a necessary coverage
failure, while q01/q06 show ambiguous local appearance under the chosen
objective and orientation. q02 has a different pattern: a better near-reference
match exists in the privileged search, and its distance to the original box
alone does not rule out a point within 5 mm. The reference-neighbourhood search
is finite and does not prove a global maximum. No post-hoc NCC cutoff is
claimed as a validated acceptance test.

## Controlled context and motion comparison

The already passing public-input author baseline was tested with two local
motion models and two patch half-width schedules. Its broad nominal-geometry
search, blur schedule, optimizer and candidate-selection rule were held fixed.
No hidden labels enter any of these four solver runs.

| Local patch model | Context half-widths | RMS / maximum error | Outcome |
| --- | --- | --- | --- |
| Translation only | 8 / 8 / 8 mm | 25.521 / 51.659 mm | Fail |
| Local affine | 8 / 8 / 8 mm | 24.689 / 44.873 mm | Fail |
| Translation only | 25 / 16 / 10 mm | 1.959 / 3.877 mm | Pass |
| Local affine | 25 / 16 / 10 mm | 2.309 / 4.456 mm | Pass |

Larger context rescues both models within this pipeline; extra local affine
parameters do not. Separate landmark translations still describe a globally
nonrigid correspondence, so the translation result does not contradict the
failure of one global rigid matrix. This is a mechanism contrast inside the
author baseline, which uses different initialization and similarity from the
original agent. It does not establish that enlarging the agent's patches alone
would pass. Repeat 3 additionally demonstrates a successful small-patch route.

## Disposition and remaining limits

The supported failure mode is **accepting locally plausible but anatomically
wrong matches, sometimes after excluding the correct region from the search**.
The original coding defect is a secondary issue in this trajectory. A successful
agent can avoid the miss with broader candidate generation and more effective
verification; richer deformable machinery is not automatically the answer.

Task validity remains supported by passing public-input baselines, healthy
controls, an independent grader and now an unassisted fresh agent pass. Stable
difficulty is not established: the prospective outcomes are mixed on one case.
Under this workshop's pass-retirement rule, retire this exact task as the lead
Terra failure candidate while retaining all traces and interventions as useful
registration research evidence. The passed BR-021 3D snapshot stays retired.

A future, separately authorized study should freeze a multi-patient set before
seeing outcomes and measure correspondence selection, search coverage and
uncertainty handling across repeated attempts. Increasing deformation or
reducing context would be a new experiment, not a retroactive repair of this
one. No extra trials, stronger-model escalation or new patient selection are
scheduled here.

Only eight sparse correspondences are evaluated. Dense-field accuracy,
topology, clinical utility and general registration capability remain outside
scope. The 3/5 mm thresholds are engineering criteria. Author methods were
developed on this case, so their success is not a held-out performance estimate.

## Review and reproduction

- [Interactive local review](../../runs/br022-registration-postmortem/review/index.html): actual CT patches, per-query search geometry, objective curves, all controlled outcomes.
- [Results receipt](../evidence/br022-results.json): independent scores, runtime contexts, hashes and delegated image/trace audit.
- [Solver analysis](../evidence/br022-solver-analysis.json): exact replay, all 14 transform/search variants, four context/motion controls, privileged diagnostics.
- [Execution audit](../evidence/br022-author-execution.json): public-input isolation and implementation hashes.
- [Reproduction notes](../../probes/registration-deformation/authoring/br022_README.md): source and artifact ownership.

The plan/protocol hashes, original task membership and bytes were rechecked at
collection. Raw images, logs, solver outputs, sessions and generated reports
remain local under `runs/`; original BR-019/020/021 evidence is preserved.
