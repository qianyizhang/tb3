# Vessel repair feasibility pilot

[BR-026 plan](../../../docs/research-rounds/BR-026-vessel-repair-experiment.md)
· [Source curation](../../../docs/research-rounds/BR-025-vessel-connectivity.md)
· [Frozen tasks and author controls](../../../docs/evidence/br026-freeze.json)
· [Completed results](../../../docs/research-rounds/BR-026-results.md)

The gap diagnostic passes (198/200 removed voxels recovered, zero collateral
edits). The unchanged-mask diagnostic fails preservation after 244 additions
beside L-ACA; the absent Pcom stays absent. Visible source signal makes this
a reference-disagreement case requiring adjudication, not a confirmed
anatomical failure. The public-input image baseline passes both cases.

Two local tasks use TopCoW MRA annotations: a disclosed synthetic right-Pcom
gap in subject 007 and an unchanged left-only Pcom configuration in subject
012. No pretrained segmentation inference or natural prediction error is
represented by these fixtures. The data and full local task directories stay
under ignored `runs/br026-vessel-repair/`.

The image crop retains native raw sample values and the source NIfTI scaling.
Reloaded physical intensities are exactly equal to the source crop. The public
input is one image, one proposed binary mask and one broad editable region.
No source class masks, graph nodes, reference path, defect coordinates,
author baseline or answer are copied into the agent image. The source notice
and usage terms remain available. Public-source retrieval is permitted but
must be distinguished from image-based repair when interpreting the trace.

## Implementation

- `build.py` verifies retained source checksums, creates the crops and the
  synthetic deletion, extracts reference paths from source voxel annotations
  using mediality-weighted shortest paths, and creates targeted controls.
  The curated source node coordinates anchor those paths; this is not a
  claim to have independently adjudicated every source graph edge.
- `score.py` is a data-only separate verifier. It checks native grid, physical
  centerline coverage, local branch routes, reference overlap, unintended
  changes and distant foreground. For an absent Pcom, a local corridor
  between nearby ICA/PCA surfaces tests false connections independently of
  the edit-volume allowance. A one-voxel false connection is a negative
  control. These are limited local engineering checks, not complete
  anatomical graph equivalence for arbitrary CoW variants.
- `baseline.py` reads only public data. Its component-only predecessor misses
  the gap because the network remains globally connected. Its final version
  proposes nearby skeleton endpoint pairs, then either closes the local mask
  or thresholds the local image from surrounding vessel intensity. The
  image-guided version passes the frozen criteria. The old source and
  pre-calibration scores are retained under the local run folder.
- `freeze.py` validates the source/reference and non-identical repair controls,
  malformed-output controls, and baseline artifacts before hashing the exact
  task file membership. It refuses to replace an existing freeze.
- `run_trials.py` uses existing local runtime configuration without exposing
  credential values. It runs one oracle and nop with Harbor 0.18.0, then one
  Codex Terra/high diagnostic with Harbor 0.14.0, sequentially for each task.
  Existing jobs and changed frozen bytes are rejected; automatic retries are
  disabled. Only output artifacts cross into the verifier environment.
- `collect.py` replays delivered masks, verifies frozen hashes and same-task
  checksums, and records a safe result subset plus trace model/effort metadata.
  A completed reward alone is not an image-reasoning claim; inspect the trace.
- `audit_traces.py` inventories retained native tool calls and binds authored
  manual reviews to exact session hashes. `review_output.py` documents the
  post-outcome source-label disagreement and renders orthogonal image sections;
  it never changes frozen tasks, thresholds or scores.
- `present.py` produces a local native-slice source review. Orange voxels are
  the authored deletion, not a predicted finding.

## Validation and interpretation

The freeze has 20 author control observations, including exact and non-exact
accepted repairs, delivered unchanged masks, missing output, wrong affine,
nonbinary values, broad closing, deletion of present branches, thin connectors
and repair with collateral damage. These are verifier checks, not model
attempts. Nop's missing artifact must fail for both tasks; delivering the
unchanged mask intentionally passes the no-defect task.

The original 1 mm³ collateral bound rejected a successful public-input repair
for 1.216 mm³ of nearby boundary additions. It was changed to 2 mm³ before
the freeze/model runs; the independent 1 mm³ distant-foreground cap remains.
This is development-case calibration and is documented in the plan. Neither
this tolerance nor the source annotations establish clinical validity.

The author environment is Python 3.12, NumPy 2.2.6, SciPy 1.15.3, nibabel
5.3.2, Pillow 11.3.0 and scikit-image 0.25.2. Ordinary numerical tools and
public network access are available to the agent. No stricter timeout or
library restriction was added to manufacture difficulty.

For existing evidence only:

```sh
.venv-br026/bin/python probes/vessel-repair/authoring/collect.py
.venv-br026/bin/python -m compileall -q probes/vessel-repair/authoring
```

Do not rebuild over or alter frozen tasks. A normally completed pass retires
this snapshot as a difficulty candidate. One gap and one unchanged source
cannot establish general vessel-repair performance; real false-bridge repair,
natural model errors and clinical expert adjudication remain untested.
