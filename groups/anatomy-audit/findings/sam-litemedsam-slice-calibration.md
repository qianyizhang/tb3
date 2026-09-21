# LiteMedSAM leads the narrow CT calibration on this Mac

2026-09-21 · [User task](codex://threads/01a0c423-5d0a-7ee3-97b4-66939a8c9e20)
· [Protocol](../experiments/sam-litemedsam-slice-calibration/protocol.md)
· [Evidence receipt](evidence/sam-litemedsam-slice-calibration.json)

Both official checkpoints were downloaded and run locally on the Apple M5 Pro
with 64 GiB unified memory. No subagent, general-agent trial, training or Docker
workflow was launched. The models, isolated Python environment, inputs and raw
outputs remain in `.local/sam-lite-bench-20260921/`.

**LiteMedSAM is the better first abdominal segmentation tool in this calibration.**
It has higher average agreement, tolerates wider boxes better and encodes images
about three times faster than SAM 2.1 Small on MPS. Duodenum remains difficult;
this is not a finding that LiteMedSAM solves every structure.

## What was measured

One existing TotalSegmentator CT, s1233; liver, right kidney, gallbladder, pancreas,
right adrenal and duodenum; three fixed axial slices per organ. The slices and
boxes were derived from reference masks. Tight boxes add 2 native pixels (3 mm)
on every side; loose boxes add 10 pixels (15 mm). Both models see the same full
265 × 265 slices, CT window and boxes, followed by their native preprocessing.

There are 72 primary GPU predictions, 8 prespecified CPU checks and 36 additional
SAM2 CPU predictions to investigate a reproduced backend discrepancy. The
summary independently recalculates Dice/precision/recall from all 116 saved masks.
Exact-mask and empty-mask endpoints give 1/0. Original CT/reference hashes were
checked before and after inference. Model and code hashes are retained.

## Results

| Model / backend | Tight-box mean Dice | Loose-box mean Dice | Median image encoding | Median cached-box decode |
| --- | ---: | ---: | ---: | ---: |
| SAM 2.1 Small / MPS | 0.7745 | 0.5165 | 134.5 ms | 14.5 ms |
| LiteMedSAM / MPS | **0.8334** | **0.8524** | **42.5 ms** | **12.3 ms** |
| SAM 2.1 Small / CPU, same 18 samples | 0.7905 | 0.5593 | 1,791.8 ms | 42.3 ms |
| Filled prompt rectangle, no learned model | 0.5260 | 0.3090 | — | — |

Timing uses FP32, four CPU threads, one warmup and device synchronization. Image
encoding includes the model's input transform; decoder timing includes returning
the mask to CPU. Disk input, model load and warmup are excluded. The model is
kept loaded and the image embedding reused for the two prompts. Median latency
is descriptive, not a sustained-throughput benchmark. First measured SAM2 encode
was 786 ms; most subsequent encodes were around 135 ms.

On the primary GPU runs, initial model setup plus warmup took 11.6 + 16.8 seconds
for SAM2 and 4.6 + 5.3 seconds for LiteMedSAM. Maximum observed Metal driver
allocation was 2,822 MiB versus 1,140 MiB; process peak RSS was 828 MiB versus
537 MiB. These are different counters, are not additive, and do not establish
total peak unified-memory usage. Both fit comfortably in this tested workload.

| Organ, mean over 3 slices | SAM2 tight | SAM2 loose | LiteMedSAM tight | LiteMedSAM loose |
| --- | ---: | ---: | ---: | ---: |
| Liver | 0.894 | 0.797 | 0.960 | 0.967 |
| Right kidney | 0.855 | 0.672 | 0.962 | 0.963 |
| Gallbladder | 0.755 | 0.514 | 0.860 | 0.805 |
| Pancreas | 0.801 | 0.480 | 0.886 | 0.914 |
| Right adrenal | 0.777 | 0.255 | 0.871 | 0.858 |
| Duodenum | 0.566 | 0.381 | 0.461 | 0.606 |

![Per-organ comparison](../../../.local/sam-lite-bench-20260921/summary/comparison.png)

Mean 2D HD95 was 13.27/26.19 mm for SAM2 MPS tight/loose and 6.40/7.21 mm for
LiteMedSAM. Higher Dice with a loose box need not improve the worst contour
excursion: overlap and surface errors measure different properties.

## Backend checks and visible failures

LiteMedSAM produced pixel-identical CPU/MPS masks on the four prespecified
checks (middle liver/adrenal slices, both boxes). This is reassuring locally but
does not establish parity across all inputs.

SAM2 differed across backends. A full same-sample CPU diagnostic retained the
comparison's direction: 0.7905/0.5593 still trails LiteMedSAM. Across its 36 prompt
pairs, median CPU/MPS mask-to-mask Dice was 0.9546, with 17 below 0.95 and a
minimum of 0.0539. Those are backend-agreement scores, not agreement with GT.
Use backend-specific results; do not assume Apple's Core ML conversion would
produce either result without testing it. The official SAM2 MPS implementation
already labels its support preliminary; the specific numerical cause is not
isolated here.

The fixed middle-slice overlays show SAM2 loose masks including neighboring
tissue, while LiteMedSAM more often follows the reference boundary. The duodenum
middle slice contains separated reference regions: both models also include
intervening/adjacent tissue within the enclosing box. This suggests testing
separate component prompts or slice/volume context, not claiming that either
would fix it without a trial. No prompts were revised after viewing outputs.

- [Tighter-box overlays](../../../.local/sam-lite-bench-20260921/summary/overlays-tight.png)
- [Wider-box overlays](../../../.local/sam-lite-bench-20260921/summary/overlays-loose.png)
- [Per-organ CSV](../../../.local/sam-lite-bench-20260921/summary/per-organ.csv)

Display crops use the reference box for legibility; inference used full slices.
White is GT, cyan is SAM2, orange is LiteMedSAM, dashed yellow is the prompt.

Matching-color legend revisions are available for the
[tighter boxes](../../../.local/sam-lite-bench-20260921/summary-legends/overlays-tight.png)
and [wider boxes](../../../.local/sam-lite-bench-20260921/summary-legends/overlays-loose.png).
The original figures, saved masks and scores remain unchanged.

The reusable [rulebook](../../../docs/segmentation-tools.md) and LiteMedSAM skill
are ready for a future tool-assisted condition. Its adapter reproduced two saved
MPS masks exactly; see the [packaging check](evidence/litemedsam-skill-verification.json).

## What this supports

The Mac can provide a fast local box-to-mask tool. For this CT condition,
LiteMedSAM is the first tool to expose to a general agent. The natural next small
test is whether an agent's image-derived boxes obtain similar masks and whether
inspection/correction improves them, especially on separated bowel regions.

This experiment does **not** measure autonomous localization, semantic naming,
3D propagation or the added value of agent reasoning. It uses a known public case
and reference-derived prompts; checkpoint training overlap remains unverified.
The 18 correlated slices are not 18 patients. These 2D numbers must not replace
or be directly ranked against the earlier ten-organ, full-volume, CT-only agent
scores. No general model ranking or clinical accuracy conclusion is supported.
