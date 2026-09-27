# RESECT pilot: exact results with a supplied coordinate cue

The retained two-query Astra/medium attempt produced valid artifacts and the
reported physical errors. Its frozen prompt also supplied a near-reference
Case B example. This supports a descriptive, cue-present result; it does not
establish unaided recovery from the designated initialization.

| Query | Initial error | Returned error | Movement | Prompt example error |
| --- | ---: | ---: | ---: | ---: |
| A: Case 1, tag index 1 | 1.036242 mm | 1.036242 mm | 0 mm | No separate example |
| B: Case 3, tag index 12 | 9.574021 mm | 1.130199 mm | 10.639783 mm | **0.505444 mm** |

One eligible attempt contains both queries. Its mean final error is 1.083220 mm,
compared with the designated initialization mean of 5.305132 mm. These are exact
paired-tag distances, not clinically adjudicated accuracy or population estimates.
Original claim, scores and evaluation files remain unchanged.

## Task and context audit

The frozen task supplies four complete native NIfTI volumes, two MRI world
queries and identical initial US world points, plus a generic viewer. Output is
an ordered `result.json` with `us_world_mm`, confidence and evidence for both
cases, and a nonempty `report.md`. It is **world-millimetre output**, unlike the
separate proposed voxel-output correspondence task. The scorer checks finite
coordinates, confidence range and nonempty text; artifact reward has no physical
error threshold and does not establish anatomical plausibility.

Frozen `instruction.md` lines 21–22 include:

```sh
python /app/tools/inspect.py --case case_b --us-center -30 15 15 \
  --radius-mm 12 --out /app/work/case_b_candidate.png
```

This point lies 0.505444 mm from the private tag reference, versus 1.130199 mm
for the returned `[-30.7,14.4,14.4]`. Its origin is not established by this audit;
the observed limitation is the coordinate cue itself. Source names, tag files,
paired reference files and tumor masks were withheld, but this helpful coordinate
was not. Pre-inference query selection used paired tags and mask centroids on
public training data; it was not a blinded sampling scheme.

## Consequential trace and counterevidence

- **Delivered cue:** trajectory step 5 exactly matches the frozen instruction.
  Step 18 renders `b_candidate.png` at `[-30,15,15]`; step 19 displays it.
  Decoded trace image bytes match the retained PNG SHA-256.
- **Image-analysis actions:** step 21 searches inverted-FLAIR/US normalized
  correlation on a 0.6 mm grid, with ±12 mm translations and three patch radii.
  The search is centred on the original MRI query, not the prompt example.
  The small-patch Case B peak rounds to `[-30.72,14.42,14.42]`; larger patches
  give different peaks. These are correlation scores, not GT agreement or
  calibrated confidence.
- **Decision:** steps 22–25 compare alternatives and adjacent slabs. The agent
  keeps Case A despite correlation alternatives, and returns Case B near the
  small-patch peak. `b_final.png` is generated at step 27; the trace shows final
  candidate slabs at step 25, not a display of that later PNG.
- **Interpretive limit:** actual delivered views show MRI contrast and US
  speckled interfaces at the selected locations. This audit does not independently
  adjudicate their anatomical homology. The trace supports image-analysis activity
  in the presence of a cue; it isolates neither the cue's causal necessity nor
  how the answer would change without it.

## Controls and new diagnostics

Original oracle reward 1 verifies the reference-coordinate artifact; original
`nop` reward 0 is a missing-`result.json` failure, not a valid unchanged-coordinate
prediction. The empty-credential HTTP 401 dispatch is an infrastructure exclusion.
The one authenticated eligible attempt completes normally and has reward 1.

The 2026-09-27 assistant audit independently recomputes distances, verifies all
16 frozen files in both live and snapshot copies, checks retained evidence hashes
and matches 12 delivered view images. Saved-output replay metrics are byte-identical
to the original. Two **post-hoc verifier diagnostics**, each with zero confidence
and no anatomical claim, also pass the artifact contract:

| Diagnostic artifact | Mean TRE | Reward meaning |
| --- | ---: | --- |
| Copy both initial coordinates | 5.305132 mm | Valid artifact only |
| Copy A initial and B prompt example | 0.770843 mm | Valid artifact only |

These are synthetic counterexamples to interpreting reward as physical success;
they are not new model attempts, official outcomes or clinical baselines.

## Scoped interpretation and reopening

Retain the exact returned coordinates, distances, movement, artifact validity and
observed actions. Exclude claims of unaided recovery, superiority to all supplied
coordinate cues, pure visual-only reasoning, causal attribution, unseen-data
performance or clinical safety. Reopening unaided capability requires a separately
authorized prompt-neutral revision and preregistered points. No trial or optimizer
was run for this explanation.

The [original receipt](evidence/resect-point-audit-astra-medium.json) retains
frozen outcomes. The [context audit](evidence/resect-point-prompt-cue-audit.json)
pins exact local paths, hashes, trace steps and post-hoc verifier artifacts.
The [pilot brief](../presentation/briefs/tb3-resect-point-pilot.md) owns the current
reader-facing contract; the [protocol](../experiments/resect-point-audit-astra-medium/protocol.md)
retains the historical interpretation beside this appended qualification.
