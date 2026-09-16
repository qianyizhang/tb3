# BR-021 — respiratory deformation results

[Protocol and source curation](BR-021-anatomical-deformation.md) ·
[Freeze](../evidence/br021-freeze.json) ·
[Author audit](../evidence/br021-author-audit.json) ·
[Results and execution audit](../evidence/br021-results.json)

Both attempts completed normally. Paired 3D passed; single-view 2D-to-3D failed.
The completed image/trace audit and independent regrading support a valid local
failure candidate in the 2D condition. Its implementation defect is a possible
contributor, and one attempt does not establish robust difficulty.

## Measured outcome

| Condition | RMS error | Maximum error | Runtime | Result |
| --- | --- | --- | --- | --- |
| Terra/high, paired 3D volumes | 1.9134 mm | 4.2183 mm | 495.95 s agent / 551.59 s trial | Pass |
| Terra/high, single 2D view and 3D volume | 12.6412 mm | 23.7957 mm | 306.62 s agent / 361.99 s trial | Fail |
| Isolated public-input author baseline, 3D | 1.9409 mm | 4.4548 mm | 21.74 s solver | Pass |
| Isolated public-input author baseline, 2D | 2.3088 mm | 4.4562 mm | 3.70 s solver | Pass |

Both tasks use one real Learn2Reg LungCT inhale/exhale pair and the same eight
manual destination landmarks. Acceptance is RMS <=3 mm and maximum <=5 mm,
in supplied dataset-world coordinates. Oracle/nop controls returned 1/0 for
each matched frozen task. Both submitted point lists were independently
regraded and exactly agree with the verifier metrics. Both attempts returned
normally, with no infrastructure exception, timeout, retry or verifier feedback.
The 2D agent voluntarily finalized after about five minutes of its 30-minute
budget; this is a completed task failure, not a timeout classification.

| Query | 3D agent error | 2D agent error |
| --- | --- | --- |
| q01 | 1.098 mm | 16.334 mm |
| q02 | 0.932 mm | 18.511 mm |
| q03 | 1.501 mm | 1.931 mm |
| q04 | 2.069 mm | 23.796 mm |
| q05 | 4.218 mm | 4.658 mm |
| q06 | 0.215 mm | 8.638 mm |
| q07 | 1.609 mm | 1.586 mm |
| q08 | 0.499 mm | 0.422 mm |

The 2D failure is not merely a tolerance-boundary miss: four points exceed
5 mm, three by more than 11 mm. Keep the 2D snapshot as a failure candidate
for later qualification; retire the passed 3D snapshot as a hard-task candidate.
No stronger-model or additional model run was launched.

## What changed from rigid pose recovery

Respiratory deformation changes local anatomy, rather than only image texture.
The privileged best rigid fit to these eight correspondences leaves over
5.4 mm RMS error. Even unrestricted global affine fitting leaves 3.13 mm RMS
for exact 3D source positions and 3.60 mm for projected 2D positions. A single
global matrix cannot pass this selection's tolerance.

The required output therefore changed to corresponding 3D positions. The
single-view condition receives its nominal exhale acquisition frame: it
isolates deformation instead of combining deformation with the lost-pose
problem from BR-019/020. Only sparse point accuracy is graded; no full dense
field, invertibility or topology claim follows. These are pulmonary vessel
and airway landmarks, not an expert-certified cardiac standard view.

## Observed solving process

For paired 3D volumes, Terra checked ANTs/elastix availability, used the
preinstalled SimpleITK package for deformable-registration attempts, and then
implemented local 3D image patch matching with affine refinement. This is
ordinary registration software use and agent-authored numerical search, not
an annotation-derived answer. The delegated audit observed no downloaded
packages/weights, annotation lookup, network use or injected hints in this
completed trajectory.

For the single view, Terra first estimated a slice-to-volume alignment, then
used a 2D affine/B-spline mapping and local patch search with continuous
optimization to refine each 3D point. Its recorded 25-step trajectory contains
a concrete agent-authored composition defect: after a CompositeTransform API
error, it changed registration to `reg(bs, ...)`, whose closure still uses
the original moving image, then evaluates `aff(bsout(x))`, applying the affine
again. The relevant trajectory steps are 14–15 and 17. Its final local search
was limited to ±9 mm around these estimated initializations.

Several failed queries also have weak or unstable patch correlations in the
trace. Valid IDs/order and the low errors on the other queries argue against
a uniform coordinate-system or output-order error. The best-supported
interpretation is bad initialization and wrong local anatomical matches,
with transform composition as a plausible contributor. No counterfactual
correction was run, so its share of the final error is unmeasured. Do not
recast this as an isolated visual-recognition failure or as proof that all
single-view deformation algorithms fail.

The initial 3D image contained only the two HU/affine arrays, source query
positions and attribution, with an empty answer directory. Destination manual
labels, verifier, oracle and author solvers were absent. The fresh 2D
image contained only the six public files: inhale HU/affine volume, view array,
view preview, view geometry, query pixels and source attribution. It contained
neither the 3D solution nor the full exhale volume. The complete 2D trace shows
no model intervention, downloaded package/weights, web or annotation lookup,
or hidden input access. These findings come from recorded code/tool calls and
actual initial-image inspection, not network packet capture. Runtime contexts
contain the frozen instruction and identify Terra/high. Both task memberships,
freeze hash and matched oracle/nop/model task checksums are unchanged.

## Interpretation and limits

The author trials establish feasibility with public inputs: independent local
patch search passes in both conditions, including isolated no-network Linux
replays. Initial global 2D fitting matched two wrong branches. An initial 3D
patch objective was corrupted by cropped exhale padding; excluding that padding
resolved its outlier. Those retained author misses are method-development
observations, not model failures or evidence that all global/Demons methods fail.

The selected case and plane were deliberately screened for nonrigidity before
solver execution. Author methods were developed on that case. One model
attempt per condition cannot estimate a success rate, and comparisons with
earlier rounds do not isolate a causal effect of morphology: source, task,
output and available geometry also changed.

Manual annotations provide an independent reference but remain publicly
downloadable. Image and recorded-trace audits can detect supplied or observed
answer lookup; they cannot establish absence of all training contamination or
unrecorded prior knowledge. Engineering tolerances are not measured observer
uncertainty or clinical acceptance criteria. Model labels in recorded runtime
contexts are not provider-side identity attestation.

The [local visual review](../../runs/br021-deformable/review/index.html) compares
actual exhale query patches, manual inhale positions and submitted positions.
The [four-miss montage](../../runs/br021-deformable/review/failures.png) provides
a static view of the 2D outliers. All patches use the same nominal orientation
and display window, centred on each respective position; they do not reproduce
every locally optimized orientation from the agent's working solver.
Raw scans, source receipts, configurations and trajectories remain local.
Prior freezes, the closed interview report and sibling submission are preserved.
