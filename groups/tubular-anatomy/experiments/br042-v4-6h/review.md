# Six-hour-allowance Astra/xhigh: transport-interrupted review

The agent ran from 2026-09-20 12:06:15.384 UTC to 14:54:00.574 UTC,
10065.19 seconds (2h47m45s). The final trace records exhausted request retries,
`request timed out`, then `turn.failed`. Harbor records
`NonZeroAgentExitCodeError`. This is a transport-interrupted attempt, neither
normal completion nor expiry of the 21600-second allowance. It cannot answer
how well Astra would perform with six hours of effective work. Seventeen
structured error entries include WebSocket reconnects, HTTPS fallback and later
request timeouts; exact aggregate lost time is not isolated.

The earlier attempt1 failed in package installation before any agent execution.
It remains a separate infrastructure record. Attempt2 is not replaced or resumed.
The heartbeat was paused after detecting termination.

## Saved output and comparison

The retained 60 courses contain 7107 points and 3134.63 mm of path. There are 49
all-zero-label courses, including both noncoronary and out-of-taxonomy coronary
vessels. They are not 49 independently validated noncoronary vessels. The JSON
passes the frozen format checks; all points are within the native scan bounds.
Extraction scripts, image-derived control specifications and junction metadata
survived. The 1781-byte method report is still the early preliminary draft and
does not document the final inventory or all later uncertainties. No independent
clean extraction reproduction is claimed.

All percentages below use the same evaluator/reference and 1-mm tolerance.
Length-weighted coverage and equal-category mean are separate measures.

| Condition | Geometry, length | Correct label, length | Geometry, category mean | Correct label, category mean |
| --- | ---: | ---: | ---: | ---: |
| V2 Astra/medium, completed (diagnostic rescore) | 87.0% | 76.0% | 70.1% | 51.0% |
| V3 Sol/xhigh, completed | 26.2% | 19.4% | 15.8% | 8.6% |
| V3 Astra/medium, completed | 95.5% | 79.3% | 81.3% | 55.3% |
| V3 Astra/xhigh, 1h timeout partial | 91.8% | 68.3% | 72.0% | 48.2% |
| V4 Astra/xhigh, 2h timeout partial | 94.1% | 74.8% | 76.9% | 51.7% |
| V4 Astra/xhigh, 6h allowance, transport-interrupted partial | 94.0% | 79.3% | 75.5% | 54.1% |

Relative to the two-hour xhigh output, correctly labeled length coverage gains
4.5 percentage points, while geometry is essentially unchanged (-0.15 points).
It nearly ties V3 medium on labeled length (79.297% versus 79.309%), but falls
behind its geometric coverage and both category means. These are descriptive
comparisons on one development case with changed prompts/budgets and interrupted
execution, not a causal estimate of extra time or model ranking.

Both frozen coverage gates fail. At 2 mm, geometric/labeled length coverage is
95.8%/80.1%. Of 646.24 mm of reference, 512.45 mm is covered with the correct
label, 94.92 mm is covered under a different label, and 38.86 mm is missed.

## Branch review

| GT category | Geometry at 1 mm | Correct label at 1 mm | Interpretation of retained output |
| --- | ---: | ---: | --- |
| LM | 75.1% | 42.0% | Proximal geometry and segment-boundary disagreement; geometry reaches 100% at 2 mm, label agreement remains 42%. |
| D1 | 99.6% | 99.6% | Early lateral branch assigned D1, consistent with reference. |
| D2 | 3.1% | 0% | Still effectively missed; only incidental LAD match. |
| OM1 | 0% | 0% | Still missed. |
| OM2 | 57.2% | 0% | 8.08 mm recovered under OM1 label, leaving numbering unresolved. |
| R-PDA | 100% | 69.5% | Geometry fully recovered; 14.05 mm assigned label 0. Better reference agreement than two-hour output, unresolved identity convention. |
| R-PLA | 100% | 99.0% | Most prior RCA/PLA boundary disagreement resolved relative to reference. |
| Other | 99.6% | 0% | 53.68 mm is labeled D2; missed upstream branch still affects numbering. |

The trace documents distal extension review, artery/vein connection corrections,
and withholding unresolved small daughter candidates. It also expanded to internal
thoracic arteries and cardiac veins. These are useful behaviors, but trace claims
and anatomical names are provisional. This closeout independently checked score,
format and field of view, not every vessel's central lumen or parent connection.
Broader clinical completeness has no exhaustive GT. Reference identity disputes
remain under review; no reference labels or original scores were changed.

## Verification and visual review

The unchanged scorer replay matches every saved verifier metric exactly. Frozen
task file hashes match; oracle=1, no-op=0 and attempt2 share the same Harbor task
checksum. CTA/reference/scorer hashes also match the two-hour condition. Only the
predeclared task identifier and timing text changed between conditions.

[Structured evidence](evaluations/saved-output-review.json) and [replay script](review.py)
retain exact input/output hashes and the transport-error sequence. The local
[CTA comparison viewer](http://127.0.0.1:8796/v4-6h/) includes the previous three
V3 runs, two-hour V4, and this interrupted output, with explicit partial status,
native slices, reference toggles and the original preliminary method. This
Markdown table is the static score fallback; source data and generated media
remain local. Original results and answers remain unchanged.
