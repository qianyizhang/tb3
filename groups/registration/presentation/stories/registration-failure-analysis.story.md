---
schema: 2
id: registration-failure-analysis
title: Analyze a single-view registration failure
locale: en
purpose: Separate composition, search support and objective defects in retained case-one registration
  evidence.
scope: Retained case-one CT, one selected miss, diagnostic interventions and two fresh
  attempts. Reader-only references; no new execution or clinical adjudication.
recipe: registration-analysis-v1
asset_pack: retained-registration-analysis-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/registration/presentation/briefs/tb3-registration-analysis.md
- groups/registration/findings/respiratory-failure-mechanisms.json
- groups/registration/findings/respiratory-failure-mechanisms.md
- groups/registration/findings/evidence/respiratory-failure-mechanisms.json
- docs/evidence/br022-plan.json
- docs/evidence/br022-results.json
- docs/evidence/br022-solver-analysis.json
- docs/evidence/br022-author-execution.json
- presentation/task-explorer/registration-analysis/manifest.json
- scripts/build_registration_analysis_assets.py
- scripts/build_respiratory_assets.py
---

# Registration postmortem

## input

```beat
id: input
frames: 240
scene: input
caption: A postmortem can inspect references the original solver never received.
narration: The solver saw one complete exhalation slice, a complete inhalation volume, eight pixel
  queries and the source pose. It returned eight target points in dataset-world millimetres. Both
  three-millimetre RMS and five-millimetre maximum gates apply. This author analysis adds saved
  code, reconstructed transforms and manual targets.
visual: Show the actual complete source view and eight public queries. Keep all reference images
  and values hidden.
channels:
  reference:
  - 0
  - 0
  bounds:
  - 0
  - 0
  curve:
  - 0
  - 0
```

## replay

```beat
id: replay
frames: 240
scene: replay
caption: Historical replay reproduces the output; it is not a fresh model attempt.
narration: The selected original miss scored 12.641 millimetres RMS and 23.796 maximum. Recovered
  stages reproduce its final coordinates to 6.30 times ten to the minus nine millimetres. The
  original image was removed; historical replay used an identical-Dockerfile image with matching
  inputs and pinned packages. Intermediate states are reconstructed.
visual: Reveal six retained stage RMS values and the final-coordinate drift. Label the replacement
  image and historical replay boundary.
channels:
  reference:
  - 0
  - 1
  bounds:
  - 0
  - 0
  curve:
  - 0
  - 0
cut: intentional-cut
```

## compose

```beat
id: compose
frames: 264
scene: composition
caption: The fitting image makes A(B(x)) inconsistent; direct B still fails.
narration: The code fits B against the original moving image, then applies the affine A again.
  Minimal repair uses that same fitted B directly. A separate structural intervention refits B
  against an affine-resampled image. All twelve primary mapping, bounds and seed combinations,
  and both secondary refits, fail. Simply swapping transform order is not the repair.
visual: Compare original composition, unchanged direct B and refitted B. Show seed-seventeen results
  at both retained bounds without selecting the best answer as an agent output.
channels:
  reference:
  - 1
  - 1
  bounds:
  - 0
  - 0
  curve:
  - 0
  - 0
cut: intentional-cut
```

## support

```beat
id: support
frames: 240
scene: support
caption: q04 is almost nineteen millimetres outside the original search box.
narration: In the saved orthonormal local axes, q04 needs offsets minus 9.115, minus 27.270 and
  plus 14.194 millimetres. Its shortest three-dimensional distance from the plus-or-minus-nine
  cube is 18.994 millimetres. That excludes any answer within the five-millimetre gate. The two
  displayed projections share the same three-dimensional calculation.
visual: Show e1/e2 and e1/e3 projections, the orange cube bounds, pink manual point and dashed
  shortest-distance segment. Keep the full 3D lower bound explicit.
channels:
  reference:
  - 1
  - 1
  bounds:
  - 0
  - 0
  curve:
  - 0
  - 0
cut: intentional-cut
```

## wider-support

```beat
id: wider-support
frames: 240
scene: support
caption: Widening support includes every target, but the finite searches still fail.
narration: Expand the half-width from nine to thirty millimetres as a teaching illustration. Only
  those endpoint searches were executed. At thirty, every manual target is inside its box. The
  retained optimizers still fail under the same finite budget. Geometric inclusion and successful
  optimization are separate claims; wider bounds do not prove an exhaustive search.
visual: Animate the measured box geometry, keeping the target fixed; reduce each exact distance-to-box
  until all eight reach zero. Mark intermediate extents as illustrative.
channels:
  reference:
  - 1
  - 1
  bounds:
  - 0
  - 1
  curve:
  - 0
  - 0
```

## objective

```beat
id: objective
frames: 288
scene: objective
caption: For q01 and q06, the saved patch objective favors the submitted match.
narration: Both manual targets lie inside the original boxes. Yet the recorded raw and high-pass
  correlation mixture scores the submitted points above the manual targets and the best points
  found in a finite three-millimetre reference neighbourhood. Independently centred CT patches
  compare appearance, not displacement. The plotted straight segment is diagnostic sampling, never
  the search trajectory.
visual: Compare actual source, manual-target and submitted CT patches for q01 and q06; reveal
  the recorded objective curves and retain the q02 counterexample.
channels:
  reference:
  - 1
  - 1
  bounds:
  - 1
  - 1
  curve:
  - 0
  - 1
cut: intentional-cut
```

## context

```beat
id: context
frames: 240
scene: context
caption: More context helps the separate author pipeline; extra affine freedom does not.
narration: The author two-by-two control fixes broad nominal search and the remaining optimizer
  rules. Both translation and local affine models fail with small context and pass with a twenty-five,
  sixteen, ten millimetre schedule. This is a separate pipeline, not a repair of the agent. Independent
  translations can still express globally nonrigid correspondence.
visual: Show actual source context windows at one explicitly posthoc location beside all four
  retained grades. Label sizes, units and author-control boundaries.
channels:
  reference:
  - 1
  - 1
  bounds:
  - 1
  - 1
  curve:
  - 1
  - 1
cut: intentional-cut
```

## repeats

```beat
id: repeats
frames: 264
scene: repeats
caption: The two predeclared fresh attempts split, including a small-patch success.
narration: 'Two independent Terra/high sessions used identical frozen task bytes, no postmortem
  hints and zero retries. They completed normally: repeat two failed at 24.905 millimetres RMS;
  repeat three passed at 2.021. The passing trace also uses small patches, with broader candidate
  search, visual and stability checks, and orientation refinement. No single component isolates
  its success.'
visual: Compare all eight per-point errors and exact aggregate grades, separating the selected
  original from the two prospective repeats.
channels:
  reference:
  - 1
  - 1
  bounds:
  - 1
  - 1
  curve:
  - 1
  - 1
cut: intentional-cut
```

## limits

```beat
id: limits
frames: 240
scene: limits
caption: Retain the defect evidence and the successful counterexample together.
narration: q04 establishes excluded support; q01 and q06 establish disagreement with one fixed
  appearance objective. q02 leaves room for optimization error. Manual-reference ambiguity is
  not independently adjudicated. The exact snapshot was retired as a reliably difficult Terra
  candidate after the pass. One case and eight points establish neither population performance
  nor a dense deformation field.
visual: Keep the three attempts visible beside distinct attribution, reference and scope limits.
  No new trial or corrected score is implied.
channels:
  reference:
  - 1
  - 1
  bounds:
  - 1
  - 1
  curve:
  - 1
  - 1
cut: intentional-cut
```
