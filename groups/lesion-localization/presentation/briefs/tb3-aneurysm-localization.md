# Search for aneurysms and preserve negative cases

Search a complete native TOF-MRA examination, check candidate structures in
multiple planes, and return one voxel coordinate per finding or an empty list.
The retained pilot contains one reference miss, one successful localization and
one negative answer after public-source identification. Keep those conditions separate.

## Value

Connect full-volume visual search with a numerical deliverable. This task stops
at localization; it does not estimate rupture risk, segment sac boundaries or
choose treatment. No dedicated aneurysm detector was supplied or observed.

## Given

### Original data

Three distinct public OpenNeuro ds003949 examinations. Each task includes original
and source skull-stripped TOF-MRA, with unchanged sample values and RAS affine.

| Case | Native grid | Spacing i/j/k, mm |
| --- | --- | --- |
| N01 | 350 × 448 × 144 | 0.46875 / 0.46875 / 0.70000 |
| N02 | 512 × 512 × 140 | 0.41016 / 0.41016 / 0.55000 |
| N03 | 350 × 448 × 160 | 0.46875 / 0.46875 / 0.70000 |

### Supplied helpers

Metadata, three full-volume maximum-intensity projections (MIPs), twelve equal
axial-slab MIPs covering the entire scan, and a slice/MIP helper. No lesion-centred
crop, lesion count or private reference mask was supplied. A source notice named
the public dataset while omitting patient identifiers.

### Callable tools

Python, image rendering and public network access; four CPU cores, 4 GiB memory,
no GPU. Three completed `gpt-5.6-sol` / `xhigh` attempts had a 1,800-second agent
limit. The agent could author views and numerical checks. N03 used allowed lookup.

### Reference-only material

Source masks and frozen acceptance regions belong to the separate evaluator.
Reference-centred crops, outlines and scores are post-result reader aids. A
source-derived crop can remove the search problem even with its outline hidden.
The selected source regions are coarse annotations, not exact sac boundaries.

## Task specification

Write exactly `{"aneurysms": [[i,j,k], ...]}`. Return an empty list for no findings.
Indices are zero-based native voxel centres; axes increase Right, Anterior,
Superior. Display horizontal follows the first remaining array axis and vertical
points upward along the second. This is an explicitly labelled coordinate display,
not the usual radiological left-right convention. Preserve anisotropic spacing.

Check projection candidates in individual sections or smaller slabs. A MIP
collapses depth and can superimpose unrelated structures. No abnormality is injected.

## Expected output

| Case | Saved points | TP / FP / FN | Evidence condition |
| --- | --- | --- | --- |
| N01 | `[]` | 0 / 0 / 1 | Reference miss; no source lookup observed |
| N02 | `[[312,213,94]]` | 1 / 0 / 0 | Matching localization; no source lookup observed |
| N03 | `[]` | 0 / 0 / 0 | Negative after source and annotation-inventory exposure |

All three completed normally; one attempt per selected scan. Do not convert the
three outcomes into a population success-rate estimate or causal method ranking.

## Evaluation

Round each finite coordinate with `floor(x + 0.5)`. Match its rounded voxel to a
released source region or its **1 mm Euclidean voxel-centre expansion**, one point
per region. All regions must match and no extra detections may remain. Duplicates
cannot match the same region twice. This is not exact-centre or contour scoring.

N02's point is **2.1625 mm from the reference centroid** and inside the released
region itself. The [fresh replay audit](../sources/aneurysm-audit.json) verifies
75 frozen-file checks, six exact source-to-input arrays, independent acceptance
regions and nine saved grades. Three oracles pass; three `{}` no-ops fail schema
validation. An empty valid list passes N03, while an added corner detection fails.
Invalid-schema no-op failure does not establish a difficult negative case.

V1's oracle failed on a missing separate-verifier Dockerfile. V2 adds the file
and changes task naming, preserving image, instruction, reference and scorer
bytes. No model attempted v1. Preserve the setup failure separately.

## Difficulty

N02 trace steps 14–15 generate and display candidate views in three planes. The
explainer reconstructs selected native sections using that exact crop/window;
point-centred reader sections are a separate post-result view. Further branch
surveys and threshold/centroid checks preceded the submitted point.

N01's final candidate montages, steps 28–29, focus near `[192,248,74]` and
`[166,309,100]`, away from reference centroid `[166,273,84]`. Earlier views included
the region. Coverage does not prove discernibility, attention or recognition;
its empty answer is a reference miss regardless of precise tolerance.

N03 reads the public manual-mask inventory at step 42 and confirms source array
equality at step 48 before submission. No negative answer was frozen before lookup.
Its pass supports source-assisted exclusion, not isolated image-only interpretation.

## Coverage

Fixed source-order curation admitted two positives and one control. A multilesion
case with a roughly 2 mm weak label was held before trials. No outcome-selected
replacement or model retry occurred. The [source paper](https://doi.org/10.1007/s12021-022-09597-0)
describes radiologist annotations checked by a senior neuroradiologist and weak
spheres enclosing lesions. That protocol does not adjudicate these pilot outcomes.
Independent clinical reference/visibility review and training overlap remain
unresolved. The pilot supplied MRA, not every clinical record available during
source-cohort construction. These views are teaching aids, not clinical validation.

## Sources

- [BR-016 protocol](../../experiments/br016/protocol.md)
- [Retained case and trace results](../../../../docs/research-rounds/BR-016-results.md)
- [Measured ledger](../../../../docs/evidence/br016-results.json)
- [Current synthesis](../../findings/lesion-localization-current-synthesis.md)
- [Independent saved-evidence audit](../sources/aneurysm-audit.json)
- [Source dataset](https://github.com/OpenNeuroDatasets/ds003949)
