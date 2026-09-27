# Transfer landmarks across respiratory deformation

Given eight source queries in an exhalation CT observation, return the corresponding inhalation points in dataset-world millimetres. The source observation changes by frozen condition; its known acquisition pose does not solve respiratory correspondence.

## Value

Tests sparse anatomical correspondence across real deformation. A successful eight-point answer does not validate a dense deformation field, topology, unqueried anatomy or clinical equivalence.

## Given

### Original data

Learn2Reg LungCT 1.11 supplies paired exhale/inhale CTs and manual corresponding landmarks. The retained cases are cropped, resampled and affine prealigned. Expiration coverage is incomplete. Each volume has shape **192 × 192 × 208**, spacing **1.75 × 1.25 × 1.75 mm**, and its own explicit voxel-to-world matrix. Use the task's **dataset-world** convention; do not assert original patient LPS/RAS.

| Frozen task | Solver-visible source | Target |
| --- | --- | --- |
| BR-021 case 1, `deform-2d` | Complete 118 × 171 oblique array, fractional query pixels, `view.json` pose and spacing | Full inhale CT |
| BR-021 case 1, `deform-3d` | Full exhale CT and exact manual source query coordinates | Same full inhale CT and eight targets |
| BR-024 case 3, `deform-harder-patient3` | Complete 121 × 189 oblique array, fractional query pixels, pose and spacing | Full inhale CT |
| BR-028 case 3, `deform-patient3-source3d` | Adds only full source `reference_volume.npz`; retains the BR-024 slice and queries | Identical target, truth and grader |

Array dimensions above are rows × columns. The full-source files contain `hu` and `voxel_to_world`. BR-023 reuses the exact case 1 2D freeze; its four later author component interventions are diagnostic assistance, not four additional model trials or new source contracts.

### Supplied helpers

For 2D queries, compute `source_world = slice_to_world × [u × sx, v × sy, 0, 1]`. This is a nominal source location, not an anatomical mapping into the inhale scan. Projection makes the case 1 source locations differ from exact manual queries by up to **0.313 mm**. BR-028 keeps the projected case 3 queries rather than replacing them with hidden exact source landmarks.

### Callable tools

Frozen tasks allowed ordinary installed libraries and network access, with 1,800 seconds, four CPUs and 4 GB RAM. The initial solver payload excludes manual target references, prior solution code and solution hints. External public annotations remain a contamination limitation; this is not a sealed annotation-free benchmark.

### Reference-only material

Private evaluator `truth.json` contains ordered manual target coordinates and **RMS ≤ 3 mm AND maximum ≤ 5 mm** gates. CSV landmarks use zero-based voxels and are transformed by the matching image affine. The actual release arrays, not duplicated phase images from an auxiliary evaluation repository, are authoritative.

The story embeds a reader-only reveal of these targets and the retained BR-028 output. q06 is selected after the trial as a teaching example. Its target close-up is centred on the returned point, preserving the manual target's true offset; centred independent comparison panels must not erase that offset.

## Task specification

Identify the same anatomical locations in the target phase. Preserve query ordering, coordinate convention and the exact condition's source information. The task asks for target points; it does not require a single rigid transform, source pose estimate or dense warp.

## Expected output

Write `/app/answer/points.json` containing `query_ids` and eight finite XYZ rows in `points_world_mm`, in the requested order. Output coordinates are dataset-world millimetres.

## Evaluation

Euclidean errors against the eight manual targets determine RMS and maximum error. Both gates must pass. BR-028 Sol/xhigh retained **2.604 mm RMS / 6.412 mm maximum**, so its original reward remains **0**. q06 is the only point over 5 mm; the other seven are at most 2.181 mm. These are historical outputs, not a new model run.

The user subsequently judged q06 good enough for the intended example and retired the full-source condition as a hard-task candidate. That practical acceptance did not change references, tolerances or rewards and was not independent clinical adjudication.

## Difficulty

BR-024 case 3's public-input author translation method passed feasibility at **2.133 mm RMS / 3.416 mm maximum**. Its fresh Sol/xhigh attempt reached **12.731 / 32.203 mm**. The later full-source attempt used a different strategy and reached **2.604 / 6.412 mm**. One attempt per condition cannot isolate the causal effect of source depth or establish a model ranking. Case 1 was retired after repeated passes; case 2 was screened but not admitted or model-trialled.

## Coverage

The story covers all four frozen source contracts and the case 3 retained answer. It shows calibrated source-derived CT sections, not volumetric rendering, a solver search trajectory or an estimated deformation. Source and target views are separated for display; case 1 and case 3 slices are independently posed. Manual references appear only at the explicit reader reveal. Data and landmarks are CC BY 4.0; attribution, hashes, pixel calibration and derivation checks are retained in the source pack.

## Sources

- [BR-021 — paired 2D and 3D source conditions](../../experiments/br021/protocol.md)
- [BR-023 — same frozen task and author interventions](../../experiments/br023/protocol.md)
- [BR-024 — harder case admission and trial](../../experiments/br024/protocol.md)
- [BR-028 — source-depth condition](../../experiments/br028/protocol.md)
- [Frozen scores](../../../../docs/evidence/br028-results.json) and [user visual judgment](../../../../docs/evidence/br028-adjudication.json)
- [Dataset record](../../../../datasets/learn2reg.json) and [source member receipts](../../../../datasets/receipts/learn2reg-files.json)
- [Teaching manifest](../../../../presentation/task-explorer/respiratory/manifest.json) and [attribution and limits](../../../../presentation/task-explorer/respiratory/NOTICE.md)
