# Comprehensive longitudinal tumor-candidate inventory

The two files `/app/data/baseline.nii.gz` and `/app/data/followup.nii.gz` are
earlier and later CT examinations of the same patient. Build a comprehensive
longitudinal tumor-candidate inventory for oncologic review and subsequent
assessment of disease burden and lesion evolution. A reviewer should be able to
inspect every plausible lesion and its correspondence across the two visits.
No masks, lesion locations or annotated examples are supplied.

## Available clinical background

Patient-specific released metadata: age 44 years; recorded sex female; 121 days
between the baseline and follow-up examinations. The age field's reference date
is unspecified.

Cohort-level clinical background: patients had metastatic malignant melanoma
and underwent systemic therapy. These paired examinations were collected for
staging and longitudinal therapy-response assessment, with an earlier baseline
and later follow-up examination. This is cohort information, not an individual
clinical report. The individual treatment regimen, treatment start/stop dates,
surgery history and relationship of either scan to surgery are unavailable.

No lesion-specific findings or response assessment are supplied. Use this broad
context when interpreting the images; it does not establish that any particular
visible finding is a tumor.

Curate and segment **all plausible tumor-lesion candidates throughout both full
volumes, regardless of size**. Apply no minimum diameter or volume. Do not limit
the inventory to RECIST targets, conspicuous lesions, growing lesions or findings
you consider more likely malignant than benign. Include small, subtle, stable and
indeterminate candidates whenever tumor remains a plausible interpretation,
including when you favor a benign alternative; record that judgment separately.
Exclude definite normal anatomy and findings you confidently regard as benign
with no meaningful tumor suspicion. A scan may have zero candidates.

Review both complete volumes systematically using suitable planes, sampling and
display windows. After contouring conspicuous findings, check the remaining scan
for missed candidates. Assess correspondence for every retained candidate;
uncertain malignancy alone is not a reason to omit its mask or correspondence.

Write these files under `/app/answer/`:

1. `baseline_instances.nii.gz` and `followup_instances.nii.gz`: 3D integer instance
   masks on the respective input's exact voxel grid and affine. Background is 0;
   each distinct candidate has its own positive ID (1–65535; at most 4096 instances
   per volume). Include the full visible lesion extent. Distinguishable lesions
   retain separate IDs even when they touch; voxel connectivity alone does not
   establish confluence. Use one instance only when separate lesions cannot be
   distinguished on the images. Do not label whole normal organs or definite vessels as lesions.
   Retain plausible candidates according to the inclusion rule above.
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

3. `candidates.json`: one entry for every positive mask ID, under its visit.
   `p_tumor` is your subjective probability (0–1) that the candidate is tumor;
   keep plausible candidates even below 0.5. `reason` briefly gives the image-based
   basis and any favored alternative. This made-up format example is unrelated
   to your scans:

```json
{
  "schema_version": 1,
  "visits": {
    "baseline": [{"id": 101, "p_tumor": 0.4, "reason": "Indeterminate finding; benign alternative favored but tumor remains plausible."}],
    "followup": [{"id": 205, "p_tumor": 0.6, "reason": "Tumor favored; some uncertainty remains."}]
  }
}
```

4. `report.md`: a short summary of your method, uncertainty and representative
   image evidence. Note any coverage limitations and notable excluded findings
   with coordinates and reasons. Identify each cited input file and zero-based native slice
   index; distinguish voxel indices from RAS world millimeters if coordinates are
   given. Preserve useful scripts and rendered views under `/app/work/`.

Candidate retrieval/localization, mask agreement, correspondence and events will
be measured separately; the recorded probabilities also allow assessment of your
probable-tumor subset. Do not optimize the inventory for an assumed target count. Do not assume a particular lesion count, anatomical distribution or
event mix. Your outputs should reflect the images.

Use the supplied images and installed tools. External network retrieval, target
dataset lookup, reference annotations and additional pretrained model downloads
are unavailable. You have up to two hours; leave your best complete outputs even
if some findings remain uncertain. No clinical diagnosis or response category is
requested.
