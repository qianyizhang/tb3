# Can a general agent localize an aneurysm?

**BR-016 · Sol/xhigh · three real scans · one attempt per case**

[Interactive case explorer](http://127.0.0.1:8766/) · [Protocol](BR-016-aneurysm-localization.md) · [Measured ledger](../evidence/br016-results.json) · [Trace audit](../evidence/br016-trace-reviews.json)

Sol missed N01, localized N02, and correctly answered N03 after identifying the public source scan. All three completed normally. The interesting contrast is how the agent combined image inspection, numerical geometry, and—on N03—data retrieval.

| Case | Outcome | Submitted voxel locations | Agent time | Output tokens | Est. cost |
| --- | --- | --- | ---: | ---: | ---: |
| N01 | Miss | `[]` | 6m 40s | 9,908 | $1.04 |
| N02 | Localized | `[[312,213,94]]` | 5m 46s | 8,763 | $0.98 |
| N03 | Source-assisted pass | `[]` | 7m 32s | 13,806 | $1.56 |

## What makes this interesting

No dedicated aneurysm detector was supplied or observed in these traces. A general multimodal agent read image arrays, generated its own views, interpreted them, and wrote numerical checks to investigate candidates. The successful case did not require a learned segmentation pipeline or an exact contour: the deliverable was a single native-grid coordinate.

```text
3D image arrays → code-generated slices / projections → visual candidate
                         ↑                                  ↓
                  adjust crop / plane ← numerical checks + reinspection
                                                            ↓
                                                      coordinate JSON
```

The following sketches summarize observable tools, public updates and final outputs. They do not reconstruct private reasoning. Geometric heuristics are candidate-finding aids, not validated diagnostic algorithms.

## N01 — Extensive search, missed candidate

**Observed.** Sol generated serial slices and slab projections, then wrote NumPy checks: repeated binary erosion to retain thick bright regions, and multiscale Hessian eigenvalue scoring to rank blob-like structures. Its last two candidate close-ups were around [192,248,74] and [166,309,100], away from the reference at [166,273,84].

```python
views = render_slices_and_slabs(volume)
candidates = inspect(views)
candidates += thick_regions(thresholds, erosion)
candidates += blob_peaks(scales, Hessian)
inspect_in_three_planes(selected_candidates)
write({"aneurysms": []})
```

**Interpretation.** The reference region occurred in generated views, but was not retained in the final candidate close-ups. This supports a search or recognition miss; it does not tell us whether the limiting factor was attention, image perception, or anatomical interpretation. The empty answer fails regardless of precise boundary tolerance.

<details>
<summary>Trace anchors</summary>

- `work_k82_106.png; fine_j260_292.png: reference-region coverage`
- `erode26 / comps: threshold + erosion + connected components`
- `smm in [0.8,1.2,1.8,2.5]; eigvalsh: blob scoring`
- `cand1_*.png; cand2_*.png: final close-ups`

Local trajectory: `runs/br016-aneurysm-n01-v2-sol-xhigh-v1-20260915/aneurysm-n01-v2__6Sm6SoR/agent/trajectory.json`. SHA-256: `6c59fadcdecc2958eac9bbee6cc302d5ad3801e84aa3169ffd367fd443e10fdc`.

</details>

## N02 — Candidate → cross-plane confirmation → point

**Observed.** Sol narrowed an apparent outpouching to a local crop and generated consecutive axial, sagittal and coronal slices. It then built thin-slab montages and regional surveys, counted connected bright components at several thresholds, and measured candidate-crop centroids before selecting [312,213,94].

```python
candidate = inspect(projections)
confirm = inspect(orthogonal_slices(candidate))
survey_remaining_branches(thin_slabs)
centres = threshold_centroids(candidate_crop)
point = choose_native_voxel(centres, views)
write({"aneurysms": [[312,213,94]]})
```

**Interpretation.** The public updates describe a rounded candidate persisting across all three planes. The submitted point matches the coarse reference region near [307,214,93]. Here, visual candidate selection and numerical localization worked together; the component counts alone do not establish the diagnosis.

<details>
<summary>Trace anchors</summary>

- `cand_k.png / cand_i.png / cand_j.png: candidate in three planes`
- `thin_*.png; *_review.png; low_k.png / high_k.png: additional survey`
- `TH [600,800,1000,1200,1400]: connected-component sweep`
- `candidate crop bounds + thresholds [350,450,550,650,750]: centroid checks`

Local trajectory: `runs/br016-aneurysm-n02-v2-sol-xhigh-v1-20260915/aneurysm-n02-v2__aSMqVvc/agent/trajectory.json`. SHA-256: `8aefadd1df3841ff5e91022e00fba1fdc38cc057a0bc94fae506d25da5ecba2b`.

</details>

## N03 — Image inspection followed by source identification

**Observed.** Sol generated additional slice montages, counted bright voxels in local boxes, installed SciPy for distance-transform width peaks, and wrote rotated MIP views. It then retrieved the public dataset tree and manual-mask inventory, downloaded sub-000, and confirmed exact array equality with the task input before writing its negative answer.

```python
inspect(native_slices, slabs, oblique_MIPs)
check(local_density, distance_transform_peaks)
tree = fetch(public_dataset_inventory)
source = download(candidate_scan)
assert array_equal(source, task_original)
write({"aneurysms": []})  # after source exposure
```

**Interpretation.** The grade is correct, but the final answer follows exposure to the source annotation inventory. Earlier public comments leaned negative; no answer was frozen before lookup. This demonstrates flexible tool use and source identification, not an isolated test of negative image interpretation. Source lookup was allowed by the prompt.

<details>
<summary>Trace anchors</summary>

- `montage_mra.py / oblique_mra.py: agent-authored viewing tools`
- `distance_transform_edt(..., sampling=sp): width heuristic`
- `ds003949-tree.json; manual_masks: reference inventory exposed`
- `canonical source comparison: diff 0.0 0.0 True`

Local trajectory: `runs/br016-aneurysm-n03-v2-sol-xhigh-v1-20260915/aneurysm-n03-v2__AiKatB3/agent/trajectory.json`. SHA-256: `53595b166830ad7bb3c4bb414a4ea385568667f2ef94b26408c44d0e2e634ed7`.

</details>

## What the results support

- **N01:** a reference-label miss, not a fussy centre-coordinate failure. Its empty answer misses a real, unmodified source finding. Generated-view coverage establishes an opportunity to see it, not attention or recognition.
- **N02:** one successful image-based localization with no source lookup observed. It supports the feasibility of general-purpose image-and-code workflows, not a clinical accuracy estimate.
- **N03:** a valid benchmark grade with a different evidence basis. Public reference exposure prevents treating it as unaided negative interpretation. This was allowed by the prompt; it is an evaluation-design confound, not agent misconduct.

More computation did not guarantee success: N01 wrote more elaborate geometric checks than N02, yet missed its lesion. The working hypothesis is that candidate selection and the choice of views matter at least as much as adding numerical heuristics. These single attempts cannot establish causality or a general model blind spot.

## Design and verification

Real TOF-MRA from [OpenNeuro ds003949](https://github.com/OpenNeuroDatasets/ds003949), CC0; [primary study](https://arxiv.org/abs/2103.06168). Fixed source-order curation admitted two positives and one negative. The initial multi-lesion candidate was held before trials because one weak label was very small. No injected abnormalities, model-selected replacements, or model retries.

The agent received native original and skull-stripped volumes, metadata and a slice/MIP helper. No reference masks or lesion-centred crops were supplied. Scoring accepts one point per weak source region plus 1 mm Euclidean tolerance, with one-to-one matching. These annotations support coarse localization, not exact lesion boundaries. This pilot does not establish clinical diagnostic validity.

[Independent audit](../evidence/br016-audit.json): source integrity, coordinate round trips, reference-region construction and known-voxel rendering checks passed. Matching v2 oracle/no-op controls and [explicit negative controls](../evidence/br016-negative-controls.json) passed. The original v1 packaging failure occurred before model trials and remains preserved. Frozen inputs and raw traces are unchanged.

## Resource accounting

| Task | Input tokens, including cache | Cached input | Input minus cached | Reasoning tokens, included in output |
| --- | ---: | ---: | ---: | ---: |
| N01 | 1,198,485 | 1,098,112 | 100,373 | 5,560 |
| N02 | 1,099,977 | 997,632 | 102,345 | 4,631 |
| N03 | 2,445,016 | 2,359,680 | 85,336 | 6,896 |

Totals: 1,198.559 s agent time, 1,399.660 s model-trial wall time, 32,477 output
tokens, estimated USD 3.583926. Wall time above includes each model trial's setup
and verification, but excludes author curation and separate control jobs. Cost
is the harness estimate, not an invoice. Input counts accumulate repeated context;
cached input is included, not additional. This selected three-case pilot is not
a population success-rate estimate. Runtime contexts match the requested
`gpt-5.6-sol` / `xhigh`, and frozen instructions were observed in all three sessions.

## Presentation and retained evidence

The case explorer combines linked native-resolution planes, windowing, zoom, MIP slabs, optional reference reveal, and the per-case trace summaries above. The yellow marker denotes a reference centre, not an exact contour. The earlier review form is retired from the presentation; historical feedback and review tooling remain in the archive.

[Authoring and reproduction](../../probes/revisions/br016/README.md) · [Curation receipt](../evidence/br016-curation.json) · [Historical guided feedback](../evidence/br016-guided-review.json).
