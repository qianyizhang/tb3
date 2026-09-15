# BR-015: clinical evidence and anatomical identity

[Earlier-trial presentation and current verdict](../../../../docs/anatomy-experiments.md) ·
[Trace walkthroughs](../../../../docs/anatomy-traces.md)

[Protocol](../../../../docs/research-rounds/BR-015-clinical-evidence.md) ·
[Results](../../../../docs/research-rounds/BR-015-results.md) ·
[Measured receipt](../../../../docs/evidence/br015-results.json) ·
[Authored source/outcome audit](../../../../docs/evidence/br015-reviews.json)

C01 adds the original CT to the actual BR013-A02 identity failure while retaining
its masks, IDs, broad vocabulary and key. V01 uses eight intact, specialist-named
ColonVessels masks with same-phase CT and anonymous surrounding veins. One
Sol/xhigh attempt per frozen task passed: 11/11 and 8/8. Both conditions are
retired. These are completed research diagnostics.

## Files and ownership

| File | Responsibility |
| --- | --- |
| `common.py` | Local paths, hashes and refusal to overwrite a freeze |
| `build_ct.py` | C01 evidence addition and lossless CT/geometry checks |
| `fetch_vessels.py`, `fetch_vessel_ct.py` | Bounded source ZIP-member acquisition, ranges, checksums and receipts |
| `screen_vessels.py` | Decode Slicer layer/value labels; retain private names and native masks |
| `build_vascular.py` | Predeclared V01 targets, native CT crop, previews, exact key and seven author controls |
| `inspect_ct.py` | Public multiplanar CT/outline helper |
| `make_review.py`, `review.template.html` | Answer-free browser review packet derived from public task data |
| `run_trials.py` | One oracle, nop and Sol/xhigh run per task; no retry or Terra branch |
| `collect.py` | Freeze/runtime verification, independent grading replay and token/time receipt |
| `review.py` | Authored trace interpretation and independent source-voxel comparison |

Source CTs, converted arrays, task snapshots, images, model runs and the review
packet remain local under `runs/br015-clinical/` or `runs/br015-*`. Receipts retain
their hashes. No source data, model logs, credentials or binary review bundle
are added to the authored record. Existing BR-013/014 source helpers and freezes
are explicit dependencies; this folder is not a standalone submission package.

## Refresh existing evidence without new trials

From the workshop root, using the existing Python 3.12 environment:

```sh
.venv-br003/bin/python probes/revisions/br015/authoring/collect.py
.venv-br003/bin/python probes/revisions/br015/authoring/review.py
.venv-br003/bin/python -m compileall -q probes/revisions/br015/authoring
```

The review reads all retained source arrays and verifies the eight V01 targets
plus the context, the full C01 CT, the V01 CT crop and all BR-013/014/015 frozen
task hashes. The retained receipt includes historical source-review limitations.

Do not rerun builders or trial commands over existing snapshots. Acquisition,
task construction and Docker/model execution are separate, explicit operations.
The runner refuses existing jobs and checks the frozen task before and after
execution. Models used Harbor 0.14.0; controls used 0.18.0. Model runtime was Codex
0.154.0. The existing local baseline configuration supplies credentials; do not
copy it into the repository.

## Frozen helper limitation

The frozen CT helper needs an equals sign for comma-separated negative slice
positions, for example `--positions=-195,-185`. A C01 model command without it
failed argument parsing. This limitation is documented rather than silently
changing the evaluated task. Neither trial failed or timed out because of it.

The maintained source attribution is [ColonVessels](https://zenodo.org/records/17407158)
and its [paper](https://doi.org/10.1038/s41597-026-07303-2), CC BY 4.0; C01 retains
the original TotalSegmentator source/license notices. The data paper's phase
registration warning is respected by using only the venous acquisition in V01.
