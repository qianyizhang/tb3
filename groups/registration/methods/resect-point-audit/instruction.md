# MRI-to-ultrasound point audit

Two neutral cases contain a pre-operative FLAIR MRI and a pre-resection 3D
ultrasound from the same operation. For each case, an anatomical point is marked
in MRI and the identical world coordinate is supplied as an initial ultrasound
candidate. Inspect the images and either retain or move the ultrasound point to
the homologous anatomical location.

Inputs are under `/app/data/`:

- `case_a_flair.nii.gz`, `case_a_us.nii.gz`
- `case_b_flair.nii.gz`, `case_b_us.nii.gz`
- `queries.json`, containing the MRI query and initial US candidate in world mm

The complete native volumes are available. A convenience viewer is installed at
`/app/tools/inspect.py`. For example:

```sh
python /app/tools/inspect.py --case case_a --radius-mm 18 \
  --out /app/work/case_a.png
python /app/tools/inspect.py --case case_b --us-center -30 15 15 \
  --radius-mm 12 --out /app/work/case_b_candidate.png
```

Each PNG has FLAIR on the top row, ultrasound on the bottom row, and native array
axes 0/1/2 from left to right. Gold crosshairs mark the requested centers. You may
render as many alternative US centers/radii as useful or write other analysis code.
Do not retrieve the source dataset, annotations or pretrained registration models.

Write `/app/answer/result.json`:

```json
{
  "schema_version": 1,
  "cases": [
    {
      "case_id": "case_a",
      "us_world_mm": [1.0, 2.0, 3.0],
      "confidence": 0.5,
      "evidence": "Brief description of the matching image feature"
    },
    {
      "case_id": "case_b",
      "us_world_mm": [4.0, 5.0, 6.0],
      "confidence": 0.5,
      "evidence": "Brief description of the matching image feature"
    }
  ]
}
```

Also write `/app/answer/report.md` summarizing the inspection method, uncertainty
and the saved views used. Coordinates must be finite world millimetres. Confidence
is between 0 and 1. Both cases are required; retaining an initial point is allowed.
The example numbers above are invented and do not describe either case.
