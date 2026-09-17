# Diagnostic reading preparation

This is a preparation scaffold for [BR-018](../../../docs/research-rounds/BR-018-report-backed-diagnosis.md).
**No clinical cases admitted, no diagnostic grading implemented, no model trial
launched.** Use Python 3.12; the local `.venv-br003` already has NumPy, nibabel,
and Pillow. No package installation was needed.

## Local manifest

Create a JSON list locally under `runs/br018-diagnostic/`. Each entry has:

```json
{
  "case_id": "C001",
  "patient_key": "host-only source patient identifier",
  "source_url": "source landing page",
  "source_revision": "pinned dataset revision",
  "reference_kind": "clinical_radiologist_report",
  "report_path": "/absolute/local/path/report.txt",
  "images": [{"path": "/absolute/local/path/scan.nii.gz"}],
  "context": {"indication": "verified pre-exam indication"},
  "technical_review_complete": true,
  "solver_metadata_review_complete": true,
  "rights_review_complete": true
}
```

Booleans are curator attestations, not automatic checks. The metadata review
covers identifiers, answer leakage, appropriate clinical context and image
headers/pixels. Never set these simply because the dataset is called deidentified.
One patient per case. `context` allows only `age`, `sex`, `indication`,
`technique`, and `available_comparisons`; use actual source data, omit unknowns.
The packer is format-neutral for `.nii.gz`, `.nii`, and `.png` inputs. Reference
kind currently requires a clinical report; AI-generated reports need a separately
designed provenance condition. Metadata is retained inside copied source files,
so manual review is essential before sharing a solver packet.

```sh
.venv-br003/bin/python probes/diagnostic-reading/authoring/prepare.py \
  runs/br018-diagnostic/manifest.json --out runs/br018-diagnostic/pack-v1
```

Creates a new output directory, refusing reuse. `solver/C001/` has anonymous
images, prompt, safe context, `inspect_ct.py` and a tools guide. `reference/`
has the source mapping, report copy and input/output SHA-256 hashes. Mount only
one solver case into an isolated runtime. Sibling paths are not an access
boundary; never give a solver the host filesystem or the pack root. Freeze a
reviewed case-specific source-claim ledger separately before the first trial.

## Rendering

```sh
.venv-br003/bin/python probes/diagnostic-reading/authoring/inspect_ct.py \
  /absolute/local/path/scan.nii.gz --plane axial --positions 0,10,20 \
  --level -600 --width 1500 --out runs/br018-diagnostic/views/example.png
```

Positions are physical RAS mm; omission gives a whole-volume overview. Keep
native volumes; no crop or lesion-directed preprocessing. `--info` reports bounds
and spacing. Rendered PNGs get distinct view IDs and a JSONL entry with window,
coordinates and image hash. The runtime must capture actual image delivery;
rendering does not prove the model saw or used an image. The helper resamples
display planes only, using nearest-neighbor sampling, with full-volume bounds.
Small findings require individual slices and adequate output size. It is a
research viewing helper, not a validated diagnostic viewer.

## Mechanical checks

```sh
.venv-br003/bin/python -m unittest discover \
  -s probes/diagnostic-reading/authoring -p 'test_*.py' -v
```

Synthetic checks cover affine orientation sampling, window mapping, reference
separation, duplicate patients and refusal of unfinished review attestations.
They do not establish clinical reference correctness or model performance.
