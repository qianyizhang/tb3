# BR-017: anatomy under the wrong label

[**Visual presentation**](../../../../runs/br017-absorption/review/index.html) ·
[Results](../../../../docs/research-rounds/BR-017-results.md) ·
[Per-trial trace analysis](../../../../docs/research-rounds/BR-017-traces.md) ·
[Protocol](../../../../docs/research-rounds/BR-017-absorbed-anatomy.md)

Four frozen conditions compare partial pancreatic inclusion in a duodenum mask
(21.04 mL), whole inclusion (59.35 mL newly added), unchanged labels and a focused
audit of the partial case. Original CT and aggregate foreground are preserved.
The deliverable is a host/class finding plus one point with 3 mm tolerance.

**M02 missed; M01, N01 and F01 passed.** Each received one fresh Sol/xhigh trial
and matched oracle/no-op controls. The round is complete.

## Files

| Files | Purpose |
| --- | --- |
| `screen.py`, `build.py`, `build_focus.py` | Source construction, task freezing and declared scope contrast |
| `scoring.py`, `inspect_ct.py` | Exact finding/tolerant point grading and public CT reslicing |
| `run_trials.py` | Sequential oracle/no-op/Sol execution, immutable inputs, no retries |
| `collect.py`, `audit.py`, `review.py` | Runtime metrics, independent source reconstruction and answer/trace checks |
| `make_visual.py` | Source-aligned before/after CT figures |
| `presentation.json` | Authored per-trial stages, interpretations, pseudocode and evidence anchors |
| `presentation.html`, `present.py` | Standalone visual report and Markdown trace analysis, built from verified evidence |
| `common.py` | Local paths, hashes and immutable freeze writer |

The builders use retained BR-013/014 helpers and the TotalSegmentator source at
`runs/br004-v1/source/s1233`. Arrays, task archives, raw runs and generated media
stay ignored under `runs/br017-*`. This folder is workshop authoring material.

## Rebuild the presentation

From the workshop root, using the existing Python 3.12 environment:

```sh
.venv-br003/bin/python probes/revisions/br017/authoring/make_visual.py
.venv-br003/bin/python probes/revisions/br017/authoring/present.py
```

Open `runs/br017-absorption/review/index.html`. It embeds its images and scripts,
works offline and includes four trial tabs, a label-state toggle, exact returned
image sheets, pseudocode and provenance. `present.py` also writes the Markdown
trace analysis and compact trace index after verifying result/trajectory hashes,
public excerpts, measurement outputs and step references.

These commands make no model calls. `audit.py`, `collect.py` and `review.py` can
refresh source checks and completed-run evidence independently. Do not rebuild
frozen tasks or rerun existing jobs to regenerate the presentation.

## Experiment record

Initial sequence: M02 → M01 → N01. After the M02 miss and M01 pass, a conditional
F01 follow-up was declared before N01's result and executed after N01 passed.
Only scope/routing files change from M02; every public input and reference-key
byte is retained. One trial per condition, 1,800 seconds, four CPUs/4 GiB,
zero retries. No stronger mutation or repeated attempt followed.

Native pancreas/duodenum overlap is 0.074 mL. Partial absorption preserves those
voxels in the remnant, leaving three tiny islands (22 voxels) under 26-neighbor
connectivity. All 13 names remain in M02/F01; M01 has a missing-label clue. N01
uses an invalid starter so no-op fails, while an explicit empty list passes.

[Original data and derived material](https://zenodo.org/records/10047263) are
CC BY 4.0, with TotalSegmentator taxonomy notices retained. Author before/after
figures are separate from model inputs; trace sheets are decoded from the exact
returned image payloads. Clinical performance was not measured in this experiment.
