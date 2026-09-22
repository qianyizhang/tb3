# Clinical context from a CT pair

`/app/data/baseline.nii.gz` and `/app/data/followup.nii.gz` are earlier and later
CT examinations of the same patient. Examine the images and available headers
to assess what clinical context they support. No clinical records are supplied.

Assess each of these fields: `broad_diagnosis`, `specific_primary_diagnosis`,
`age_years`, `recorded_sex`, `interval_days`, `baseline_scan_purpose`,
`followup_scan_purpose`, `systemic_treatment_context`, and `surgical_context`.
Separate observations from inference. Use `unknown` when a value cannot be
established; do not turn a plausible explanation into a known history. You may
give ranges or alternatives in prose. Visible anatomy does not establish the
patient's recorded demographic fields. An unknown answer with a clear reason
is acceptable. This is context assessment, not a request for lesion masks,
lesion correspondence, treatment advice, or a definitive clinical diagnosis.

Write `/app/answer/context.json` with `schema_version: 1` and a `fields` object
containing all nine keys above. Each field must have:

- `status`: `observed`, `inferred`, or `unknown`;
- `value`: a concise string, number, or `null` (use `null` for `unknown`);
- `confidence`: number from 0 to 1, your confidence in the stated assessment,
  including confidence that a field is unknown;
- `basis`: the image/header evidence and reasoning, or why it is unavailable;
- `alternatives`: a list of plausible alternatives, possibly empty.

Format example only; this field/value says nothing about your scans:

```json
{"schema_version": 1, "fields": {
  "interval_days": {"status": "unknown", "value": null, "confidence": 0.9,
    "basis": "Explain the evidence or its absence here.", "alternatives": []}
}}
```

Include all nine fields in your actual output. Also write `/app/answer/report.md`
with a short method, the most useful image observations, limitations, and what
additional clinical information would resolve the important unknowns. Cite
input filename and zero-based native voxel/slice coordinates for image evidence;
distinguish these from RAS world millimeters. Preserve scripts and rendered views
under `/app/work/`.

Use only the supplied images and installed tools. External network retrieval,
dataset lookup, reference annotations and additional pretrained model downloads
are unavailable. You have up to two hours. Output validity is checked separately
from evidential support and agreement with independently retained metadata.
