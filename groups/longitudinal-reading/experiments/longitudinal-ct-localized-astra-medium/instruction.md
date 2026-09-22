# Paired CT lesion analysis

The two files `/app/data/baseline.nii.gz` and `/app/data/followup.nii.gz` are
earlier and later CT examinations of the same patient. Review only the structures
at the candidate centers below, using adjacent slices and surrounding anatomy.
These coordinates specify what to review, not its diagnosis. No masks or
annotated examples are supplied. Other findings are outside this task's scope.

| Candidate | Input | Zero-based native voxel center (i, j, k) |
|---|---|---|
| R01 | `/app/data/baseline.nii.gz` | 304, 263, 213 |
| R02 | `/app/data/followup.nii.gz` | 302, 221, 216 |

Use your best image-based judgment of lesion presence: include findings you judge
more likely tumor than normal or benign tissue, even without diagnostic certainty.
Exclude findings you judge more likely normal or benign. In the report, list
uncertain candidates with native coordinates, included/excluded status and a brief
reason; uncertainty alone is not an exclusion rule. A scan may have zero lesions.

First record a judgment for each listed candidate: `tumor`, `normal_or_benign`,
or `indeterminate`, with an image-based reason. Segment only candidates judged
`tumor`; do not assign tumor masks to rejected or indeterminate candidates.
Use the event rules below for the candidates you segmented.

Write these files under `/app/answer/`:

1. `baseline_instances.nii.gz` and `followup_instances.nii.gz`: 3D integer instance
   masks on the respective input's exact voxel grid and affine. Background is 0;
   each distinct lesion has its own positive ID (1–65535; at most 4096 instances
   per volume). Include the full visible lesion extent. Distinguishable lesions
   retain separate IDs even when they touch; voxel connectivity alone does not
   establish confluence. Use one instance only when separate lesions cannot be
   distinguished on the images. Do not include normal organs, vessels or other
   non-tumor structures.
   IDs are local to each visit; equal numbers do not establish correspondence.
2. `events.json`, with this structure. **This is only a made-up format example;
   its IDs, counts and event do not describe your scans:**

```json
{
  "schema_version": 1,
  "groups": [
    {"baseline_ids": [101], "followup_ids": [205], "event": "persistent"}
  ]
}
```

Use one group for each longitudinal lesion or connected group of lesions:

| Event | Baseline IDs | Follow-up IDs |
|---|---|---|
| `persistent` | one | one |
| `merging` | two or more | one |
| `disappearing` | one | empty |
| `newly_appearing` | empty | one |
| `unresolved` | one or more on either side | any, except both sides empty |

Every positive ID in each mask must occur exactly once in the corresponding JSON
ID lists. A merging group links every listed baseline instance to its single
follow-up instance. `persistent` means identity persists, not stable size.
Use `unresolved` when identity, visibility or more complex correspondence cannot
be established; it makes no asserted links. Do not declare disappearance solely
because an anatomical region is outside the follow-up field of view.

3. `report.md`: a short summary of your method, uncertainty and representative
   image evidence. Identify each cited input file and zero-based native slice
   index; distinguish voxel indices from RAS world millimeters if coordinates are
   given. Preserve useful scripts and rendered views under `/app/work/`.

4. `candidate_judgments.json`: one entry per listed candidate, using this format.
   The following entry is a format example, not a judgment about your scans:

```json
{"schema_version": 1, "candidates": [{"candidate_id": "R00", "judgment": "indeterminate", "reason": "Explain the image evidence."}]}
```

Candidate judgment, mask agreement, correspondence and events will be measured
separately. Do not assume a particular lesion count, anatomical distribution or
event mix. Your outputs should reflect the images.

Use the supplied images and installed tools. External network retrieval, target
dataset lookup, reference annotations and additional pretrained model downloads
are unavailable. You have up to two hours; leave your best complete outputs even
if some findings remain uncertain. No clinical diagnosis or response category is
requested.
