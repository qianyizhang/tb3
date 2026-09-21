# F018: Astra xhigh versus medium on identical CT-only inputs

2026-09-21 · [User authorization](codex://threads/01a0c25e-4b08-7552-8379-90a2b50ad40f)
· [Xhigh protocol](../experiments/dental-f018-astra-xhigh/protocol.md)
· [Xhigh evidence](evidence/dental-f018-astra-xhigh.json)
· [Earlier medium finding](dental-ct-only-astra-medium.md)

Xhigh completed voluntarily after 1,881.67 agent seconds (31m22s), with no
execution exception. Its output passed geometry/integer-ID validation. Independent
offline replay exactly reproduced every private metric. Both attempts use the
same frozen task digest, scientific runtime, CT/GT, neutral prompt and evaluator.

| Observation | Medium | Xhigh |
| --- | ---: | ---: |
| Original macro Dice | 0.039394 | 0.044766 |
| Foreground Dice (ignores identity) | 0.968609 | 0.970754 |
| Fixed L/R ID permutation, diagnostic only | 0.692457 | 0.703420 |
| Agent seconds | 947.10 | 1881.67 |
| Uncached input tokens | 104690 | 167555 |
| Cached input tokens | 1984512 | 5085568 |
| Output tokens | 24304 | 54975 |

The side-convention issue recurs: xhigh explicitly assigned laterality from the
NIfTI affine and disagrees with the GT's lateralized IDs. The diagnostic permutation
is an analysis of the unchanged confusion matrix; it is not a corrected answer,
replacement score or a clinical pass. Source-header/GT laterality remains under
review. Foreground overlap is dominated by large structures and is not per-class
anatomical accuracy. These are single attempts, not population-level evidence
that increased reasoning effort reliably improves performance.

Xhigh produced 66 foreground IDs versus 68 in the GT: 29 tooth/pulp pairs,
jawbones, sinuses, pharynx, inferior alveolar canals and lingual channels. It
explicitly omitted the two incisive canals. It chose visually located markers and
3-D watershed for teeth, local intensity/morphology for other regions, and
landmark-guided canal paths, while documenting fine-boundary uncertainty.

The retained session has 56 top-level exec calls; inspection found no external
dataset requests or GT/scorer reads. Proxy logs show 74 accepted CONNECT requests,
all to chatgpt.com, and 36 denied CDN/telemetry requests. This is bounded access
evidence, not a claim about pretraining or encrypted payloads. No reviewer feedback
was delivered to either solver. Output/metric/trace hashes are in the receipt.

F002 remains a separately authorized blind experiment. At the 11:37 UTC heartbeat,
an unrelated user CT-organ trial was using the shared Docker VM. F002 therefore
waits for capacity; its inputs/controls are ready and no inference has been
dispatched. The monitor will start it once that VM is free and quota remains above
the reserve. No unrelated container is stopped or modified.
