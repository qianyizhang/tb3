# Calibrate promptable segmenters on CT slices

Compare two frozen box-to-mask tools on the same full CT slices and two supplied
box sizes. LiteMedSAM has higher mean agreement and lower image-encoding latency
in this retained one-case calibration; duodenum and SAM2 backend differences
prevent treating the mean as a universal ranking.

## Value

Establish conditional mask quality, sensitivity to box extent and measured local
runtime cost before exposing a segmenter to an agent. The supplied localization
comes from the reference. This does not test whether an agent can find an organ,
choose the box, correct a mask or assemble a 3D segmentation.

## Given

### Original data

One known public TotalSegmentator v2.0.1 CT, **s1233**, on its original
265 × 265 × 401 grid with 1.5 mm isotropic spacing. Six reference labels select
liver, right kidney, gallbladder, pancreas, right adrenal and duodenum.
The 25th, 50th and 75th percentiles of each organ's nonempty slice-index list
give **18 correlated organ/slice pairs from one patient**.

Each input is a full 265 × 265 axial section, clipped to **[-160,240] HU**,
scaled to uint8 and replicated into three grayscale RGB channels. Native
display x=i, y=j increases down and k identifies the slice. No radiological flip
or target-mask resampling is applied. Reader detail crops are not model inputs.

### Supplied helpers

Each reference bounding rectangle is expanded by **2 pixels (3 mm)** or
**10 pixels (15 mm)** on every side, clipped to the image boundary. Coordinates
are half-open xyxy in the native image. The same slice and native box go to
both tools. Slices and boxes are fixed before outputs are inspected.

### Callable tools

Direct official **SAM 2.1 Small** and **LiteMedSAM** checkpoint inference, retained
from 2026-09-21 on an Apple M5 Pro with 64 GiB unified memory. Both use PyTorch
2.10, FP32, evaluation/inference mode and four CPU threads. There is no general
agent, training, Docker execution or interactive correction in this calibration.

Their native preprocessing differs: SAM2 resizes to 1024² with floating-point
box scaling; LiteMedSAM resizes to 256², normalizes intensities and truncates its
scaled box coordinates to integers. Each encodes a full image once and reuses
the embedding for the two box decodes. Native-resolution binary masks are
returned; no extra connected-component cleanup is applied by the benchmark.

### Reference-only material

Dense organ masks are author/evaluator material. They select slices and derive
the supplied boxes, but neither model receives the dense mask or the semantic
organ name. Reference outlines, agreement scores and display crops are reader
aids with explicit reveals. This privileged prompt origin remains visible even
when the dense reference overlay is hidden.

## Task specification

Run both fixed models with tight and loose boxes on the fixed 18 samples.
The retained primary comparison contains **72 MPS predictions**. Eight
prespecified CPU checks cover both tools on middle liver/adrenal slices and both
boxes. After a SAM2 backend discrepancy, **36 additional SAM2 CPU predictions**
repeat the complete sample set as a diagnostic. They do not replace the MPS
results or constitute another patient.

## Expected output

For every model/backend/sample/box: a 265 × 265 Boolean mask, native box and
slice ID, synchronized encode/decode durations, predicted model quality and
reference-based measurements. All **116 masks** and their receipts remain local.
The model quality-head score is distinct from measured Dice and is not assumed
to be calibrated confidence.

## Evaluation

The [saved-output audit](../sources/segmentation-calibration-audit.json) reconstructs
all input images, selected slices and boxes from the original source files, then
recomputes Dice, precision, recall and HD95 from every saved mask. All four
measurements match the historical receipts exactly. The replay runs no model.

HD95 uses 4-connected erosion to identify 2D boundary pixels and takes the
95th percentile of **concatenated bidirectional** nearest-boundary distances,
with 1.5 mm sampling. It is not a 3D surface score or the maximum of two
directional percentiles. Both mean scores below use 18 samples per box condition.

| Tool / backend | Tight mean Dice | Loose mean Dice | Median encode | Median cached decode |
| --- | ---: | ---: | ---: | ---: |
| SAM 2.1 Small / MPS | 0.7745 | 0.5165 | 134.5 ms | 14.5 ms |
| LiteMedSAM / MPS | 0.8334 | 0.8524 | 42.5 ms | 12.3 ms |
| SAM2 / CPU, later diagnostic | 0.7905 | 0.5593 | 1,791.8 ms | 42.3 ms |
| Filled supplied rectangle | 0.5260 | 0.3090 | — | — |

Timing denominators are **18 unique image encodes / 36 cached box decodes** per
complete run. Encode time is repeated in the two prompt rows but counted once
per image. Synchronization and CPU mask return are included; disk input, model
load and warmup are excluded. First measured SAM2 MPS encoding takes 786 ms,
so the median is not a startup estimate. These are descriptive local timings,
not sustained throughput. RSS and Metal-driver allocation are different,
non-additive counters; they do not establish total peak unified memory.

Exact-reference/empty masks produce Dice 1/0 on all 18 nonempty references.
Filled-box controls show how much localization the prompt already supplies.
Mean Dice and mean boundary error can move differently: LiteMedSAM's loose-box
mean Dice improves while mean HD95 rises from **6.40 to 7.21 mm**.

## Difficulty

Box expansion can include neighboring tissue or multiple disconnected regions.
For duodenum, tighter-box mean Dice favors SAM2 (**0.566 vs 0.461**); wider-box
mean Dice favors LiteMedSAM (**0.606 vs 0.381**). The fixed middle slice shows
both wider-box predictions joining or including tissue between separated
reference regions. Wider boxes also lower LiteMedSAM's mean gallbladder Dice.

Across 36 SAM2 CPU/MPS prompt pairs, median mask-to-mask Dice is **0.9546**,
17 pairs are below 0.95 and the minimum is **0.0539** on loose liver q25.
That extreme is selected after inspecting results. These are backend agreement
scores, not scores against GT. Four LiteMedSAM prespecified pairs are
pixel-identical; all four SAM2 subset masks also match their later CPU repeats.
Neither observation establishes universal backend determinism or isolates the
cause of SAM2's discrepancy.

## Coverage

The source/grid audit supports faithful replay, not clinical adjudication of the
reference masks. One known development case, correlated selected slices and
unverified checkpoint training overlap do not support population or causal
claims. No revised prompts, component-specific retries, volume propagation or
agent reasoning were tested. Do not rank these 2D, reference-box numbers against
earlier CT-only whole-volume agent scores.

## Sources

- [Original protocol](../../experiments/sam-litemedsam-slice-calibration/protocol.md)
- [Original finding and visual comparisons](../../findings/sam-litemedsam-slice-calibration.md)
- [Retained inference and provisioning receipt](../../findings/evidence/sam-litemedsam-slice-calibration.json)
- [Source manifest and licenses](../../experiments/ct-organ-segmentation-astra-xhigh/source/selected-source-manifest.json)
- [Fresh read-only audit](../sources/segmentation-calibration-audit.json)
- [Agent-prompted study idea and decisions](../../ideas/agent-prompted-segmentation.md)
- [Segmentation tool rulebook](../../../../docs/segmentation-tools.md)
