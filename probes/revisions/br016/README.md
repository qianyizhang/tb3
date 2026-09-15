# BR-016 — Imaging-backed aneurysm localization

A small calibration pilot using real public TOF-MRA volumes from OpenNeuro
[ds003949](https://github.com/OpenNeuroDatasets/ds003949) (CC0). The agent writes one
voxel coordinate per aneurysm, or an empty list. Source weak annotations support
coarse localization, not exact boundaries. No abnormalities are synthesized.

[Results](../../../docs/research-rounds/BR-016-results.md): one reference-label miss,
one clean pass and one source-assisted pass; all three Sol/xhigh attempts completed
normally. N03 matched public source data before submitting;
its reward does not establish unaided anatomical success.

[Protocol](../../../docs/research-rounds/BR-016-aneurysm-localization.md) owns
selection and interpretation. Source data, task builds, model traces, and the
interactive case explorer remain local in `runs/br016-aneurysm/`. The sibling
interview submission is unchanged.

## Authored components

- `fetch.py`, `fetch_raw.py`: fixed source-order selection, pinned Git tree,
  Git-annex MD5/size validation and SHA256 receipts.
- `inspect_mra.py`: native-resolution slice and slab projection tool.
- `build.py`: original frozen fixtures, source alignment and scoring controls.
- `revise_verifier.py`: preserved revision correcting missing separate-verifier
  Docker packaging before any model attempt. Never overwrite v1 freezes.
- `scoring.py`: strict point schema and one-to-one reference-region matching.
- `audit.py`: independent brute-force acceptance-region and coordinate checks.
- `run_trials.py`: oracle, no-op, then one Sol/xhigh trial; no model retries.
- `collect.py`: immutable-input verification, grade replay, usage/time/provenance.
- `negative_controls.py`: actual-container empty and false-positive checks.
- `trace_review.py`: observable image/render coverage, output and source-retrieval audit.
- `grade_review.py`: retained historical review-export grader; the presentation no longer collects reviews.
- `review.html`, `build_review.py`: original and skull-stripped volume review,
  linked MPR, windowing, MIP slabs, magnification and reference reveal.
- `case-stories.json`: authored per-trial workflow sketches and trace anchors.

Run only on a fresh output namespace or inspect existing receipts first. Builders
and runners intentionally reject existing task / trial destinations. A no-op
leaves an invalid placeholder on every case and should fail; a legitimate empty
prediction is separately checked to pass the negative reference.

The case explorer presents outcomes and trace summaries alongside the scans. The earlier review form is retired; historical responses and evidence are preserved. Frozen model tasks are unchanged. Restore the local server with:

```sh
.venv-br003/bin/python -m http.server 8766 --bind 127.0.0.1 --directory runs/br016-aneurysm/blind-review
```

A model miss alone does not establish clinical validity; source weak labels support coarse localization. This selected pilot is not an accuracy estimate.
