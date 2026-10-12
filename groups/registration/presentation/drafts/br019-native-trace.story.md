---
schema: 2
id: br019-native-trace
title: Recover one CT section inside its source volume
locale: en
purpose: Explain consequential recorded operations and native spatial context from
  one retained task-solving trace.
scope: Retained BR-019 cardiac-r01 full-view calibration run; the complete supplied
  CT crop is not the original full patient scan. Engineering pose scores do not establish
  clinical precision.
recipe: native-trace-v1
manifest: groups/registration/presentation/anatomy-pose/native-trace.json
fps: 24
reference_policy: reader-reference-reveal
source_class: source-derived-teaching
source_locators:
- groups/registration/findings/br019-full-view-trace.md
- groups/registration/presentation/briefs/tb3-oblique-pose.md
---

# Recover one CT section inside its source volume

Unbound native-trace migration draft. Original stories and acceptance receipts remain unchanged.

## 1. Receive the inputs

```beat
id: input
frames: 144
caption: The picture is real. Its position is missing.
narration: The solver inspected the supplied forward renderer, CT dimensions and coordinate
  matrix, then viewed the target and an axial CT slice. It had the entire 180³ crop,
  not merely a few screenshots. The target’s pose was absent.
visual: 'Given: CT + target + spacing + forward renderer → return: one pixel-to-LPS
  matrix.'
state: null
trace_steps:
- 7
- 9
- 10
- 11
reference: false
```

## 2. A wrong first match

```beat
id: search
frames: 144
caption: A plausible cardiac-looking section can be the wrong cut.
narration: The solver searched six pose parameters using differential evolution, then
  refined an intensity mismatch. The recorded step-17 pose produces this convincing
  but wrong image. Later intensity and edge-search variants also failed to find the
  final match.
visual: 'Selected state: step 17, after Powell refinement. Not the final submitted
  answer.'
state: early
trace_steps:
- 13
- 17
- 19
- 20
- 21
- 22
- 23
- 25
reference: false
```

## 3. Use the whole volume

```beat
id: bounds
frames: 192
caption: A finite section has to fit inside the acquired CT.
narration: The task disclosed that every target sample lies inside the crop. The solver
  converted that fact into orientation-dependent bounds on the section centre. This
  pruned impossible poses, but the later step-41 intensity-smoothed result was still
  wrong.
visual: 'For a proposed orientation: corner reach → allowed centre box → search only
  within that box.'
state: bounded
trace_steps:
- 29
- 35
- 36
- 40
- 41
reference: false
```

## 4. Find a coarse match

```beat
id: coarse
frames: 144
caption: First line up the large body–lung pattern.
narration: 'The solver changed the global-search objective to a smoothed foreground
  silhouette: target > 5, Gaussian σ = 2 pixels, compared with a soft threshold of
  the predicted image. Of eight logged restarts, seed 6 had the lowest reported silhouette
  objective. Its reconstructed pose is shown here.'
visual: Coarse shape gives a useful starting region. This display is reconstructed
  from rounded logged parameters.
state: coarse
trace_steps:
- 42
- 43
reference: false
```

## 5. Refine the texture

```beat
id: output
frames: 144
caption: Then use every pixel to tighten the pose.
narration: Starting from that coarse candidate, full-resolution intensity least squares
  took eight reported function evaluations. The solver wrote pose.json, rendered it
  with the supplied forward model, and checked the image and matrix. The saved answer
  reproduces 36,808 of 36,864 target pixels exactly.
visual: 56 differing pixels · maximum intensity difference 1 · rigid, right-handed
  output.
state: final
trace_steps:
- 43
- 45
reference: false
```

## 6. Reveal reference check

```beat
id: reference
frames: 144
caption: The evaluator checks physical positions, not visual similarity.
narration: The hidden reference maps the same 7 × 7 image grid into patient space.
  Both the RMS and maximum point-error limits passed. The amber reference outline
  nearly coincides with the teal submitted section because the geometric disagreement
  is far below this display’s resolution.
visual: 'Frozen result: 0.000477 mm RMS / 0.000744 mm maximum. These are engineering
  scores, not clinical precision.'
state: final
trace_steps:
- 45
reference: true
```
