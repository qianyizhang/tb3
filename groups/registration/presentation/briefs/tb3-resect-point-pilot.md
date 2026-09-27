# Correct two MRI-to-ultrasound point correspondences

One retained Astra/medium attempt keeps one supplied point and moves the other.
Its prompt contains a helpful Case B coordinate example, which limits what the
observed improvement establishes.

## Value

Inspect correspondence correction and preservation of an already-close point,
while separating physical error from artifact validity and supplied assistance.

## Given

### Original data

Two complete native FLAIR / pre-resection 3D ultrasound pairs, with one MRI
world-coordinate query per case. Source Case 1 tag index 1 and Case 3 tag index 12
were selected before inference using published paired landmarks and mask centroids.
These are two selected public training points, not blinded or held-out sampling.

### Supplied helpers

Each initial US candidate copies the MRI world coordinate. A generic orthogonal
viewer can inspect arbitrary world coordinates. The frozen instruction also gives
Case B `--us-center -30 15 15`; the trace renders and displays that candidate.
Tumor masks, source names and paired tag files were withheld.

### Callable tools

The agent used Python, native-affine reslicing, image display and exploratory
local normalized correlation. The declared task permits model-service transport
only; this explanation is not a new runtime-isolation audit.

### Reference-only material

The evaluator holds the paired US tag coordinate in `tests/reference.json`.
Reader reveals display it and exact physical errors. These reveals are not
solver inputs; the helpful example coordinate above was solver-visible.

## Task specification

Return retained or corrected US **RAS+ world millimetres** for ordered `case_a`
and `case_b`, confidence in [0,1] and nonempty image evidence. Write `result.json`
and a nonempty `report.md`. This executed pilot differs from the proposed
three-case voxel-output correspondence task.

## Expected output

Actual output keeps A at `[44.528484,-31.304113,29.970621]` with confidence 0.82
and moves B to `[-30.7,14.4,14.4]` with confidence 0.71. Confidence is subjective,
not calibrated. The retained report cites visual inspection and local correlation.

## Evaluation

Case A error stays 1.036242 mm. Case B error changes from 9.574021 to 1.130199 mm;
movement is 10.639783 mm. The two-point mean changes from 5.305132 to 1.083220 mm.
The prompt's B example is **0.505444 mm** from the reference, closer than the
returned point. Unaided recovery and superiority to all supplied cues are unsupported.

Harbor reward tests artifact validity only. The original no-op has no output;
it does not test copying the initial point. Later synthetic unchanged/cue-copy
artifacts both pass. Saved-output replay is byte-identical, not fresh execution.

## Difficulty

MRI and US contrast differ. Shared coordinates can already be useful, and the
prompt supplies an additional candidate. The later correlation search is centred
on the original MRI query, so the cue's causal contribution remains unresolved.

## Coverage

One eligible attempt, two queries, one excluded credential failure, original
oracle/no-op controls and separately labeled verifier diagnostics. No clinical
adjudication, general model ranking, population estimate or new trial.

## Sources

- [Frozen protocol and appended context audit](../../experiments/resect-point-audit-astra-medium/protocol.md)
- [Result, trace, controls and qualified interpretation](../../findings/resect-point-audit-context.md)
- [Pinned context-audit evidence](../../findings/evidence/resect-point-prompt-cue-audit.json)
