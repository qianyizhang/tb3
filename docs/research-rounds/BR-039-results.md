# BR-039 — Expanded CT landmark results

The previous CT pilot contained four landmarks because it reused the small PDDCA subset. This fresh test requests 26 named vertebral centres from full 3D CT intensity arrays, with available and unavailable targets mixed. Source: VerSe subject 823, original native geometry and losslessly preserved intensities.

| Input | Requested | Visible / outside / absent | ≤5 / ≤10 / ≤20 mm | Invented outside | Invented absent | Correct rejection outside / absent |
|---|---:|---|---|---|---|---|
| ct-full | 26 | 24 / 0 / 2 | 2 / 7 / 9 of 24 | 0 / 0 | 0 / 2 | 0 / 2 |
| ct-partial | 26 | 13 / 11 / 2 | 1 / 2 / 5 of 13 | 1 / 11 | 0 / 2 | 10 / 2 |

Each localization numerator uses all visible targets as its denominator, including missed targets. A 0/0 outside cell means that condition had no outside targets, not an estimated zero population rate. Absent targets are T13 and L6 under the published source numbering convention.

## ct-full

Normal completion in 597.2 seconds. Mean error among returned visible points: 24.774 mm. Visible omissions: 0. Uncertain negatives: {'out_of_fov': 0, 'absent': 0}.

Status confusion: `{'observed->observed': 24, 'absent->absent': 2}`.

Invented observed detections: none.

## ct-partial

Normal completion in 458.8 seconds. Mean error among returned visible points: 20.846 mm. Visible omissions: 0. Uncertain negatives: {'out_of_fov': 0, 'absent': 0}.

Status confusion: `{'out_of_fov->out_of_fov': 10, 'out_of_fov->observed': 1, 'observed->observed': 13, 'absent->absent': 2}`.

Invented observed detections: T4.

## Validity and limits

- Same frozen bytes for reference, no-op and Terra within each condition; reference reward 1 and no-op 0 in both. Terra/high, one attempt per condition, no retries.
- Source centroid directions match the CT; C2–L5 points lie in the matching private source bone labels. C1 is the centre of the atlas ring. SimpleITK and nibabel agree; all rendered axes pass an asymmetric-array check.
- Host score replay matches the container score exactly. Independent voxel→world distance calculations agree to numerical precision.
- Source and partial scans share native geometry; the partial scan contains all voxels k=0:920. The nearest reference centre is 7.49 mm from its boundary.
- One subject and two correlated conditions. T13/L6 classification follows the source convention. Missing cranial context in the partial scan can make enumeration uncertain; uncertainty is not hallucination.
- The richer 57-point MedPelvis source was rejected before trials after its documented coordinate mapping failed anatomy overlays. No heuristic repair or model-failure claim was made from it.

## Artifacts

- [Curation and protocol](BR-039-ct-landmarks.md)
- [Results JSON](../evidence/br039-results.json)
- [Curation evidence](../evidence/br039-curation.json)
- [Frozen task manifest](../evidence/br039-freeze.json)
- [Validation controls](../evidence/br039-validation.json)
- Local generated review: `runs/br039-ct-landmarks/review/index.html`
- Per-point nearest-reference diagnostics: `runs/br039-ct-landmarks/nearest-reference.json`. A nearest-neighbour match is a descriptive diagnostic, not an alternative score.

## Error interpretation

The partial scan's only unsupported observed detection is T4, whose submitted point is 2.142 mm from the source T5 centre. It is a wrong-level detection on real anatomy, not a fabricated structure in empty space. T13 and L6 were correctly rejected in both conditions (four answers on two correlated views of one patient, not four independent cases).

In the full scan, T12 and L2 meet 5 mm; all five lumbar points are within 10 mm. Errors are substantially larger in the cervical and upper thoracic regions, with multiple predictions nearest to lower-level vertebrae. This is inconsistent with a single global coordinate offset and does not rescue the named-target scores. A nearest-point diagnostic is not a relabelled success score.

Raw-session audit found 17 actual input-image blocks for the full run and 10 for the partial run. Both executed the coordinate check and supplied viewer. The command review found no web/download candidates or detected case-specific annotation retrieval. See [trace evidence](../evidence/br039-trace-review.json). The claim is limited to these preserved traces; it is not proof about hidden training exposure.
