# Astra/medium: correct identities, mixed contour gains and losses

2026-09-21 · [Fixed protocol](../experiments/ct-organ-segmentation-astra-medium/protocol.md)
· [Evidence receipt](evidence/ct-organ-segmentation-astra-medium.json)
· [Three-condition comparison](ct-organ-three-condition-comparison.md)

One fresh Astra/medium attempt completed normally in **1,289.35 agent seconds
(21 minutes 29 seconds)**. The ten masks pass the output contract. Parent replay
of the unchanged saved masks matches every original verifier field exactly.
Semantic and matched macro Dice both equal **0.7341910610**; all ten optimal
positive-overlap matches preserve their names. Foreground Dice is 0.89906,
precision 0.91241 and recall 0.88609.

Compared with the original Astra/xhigh attempt, medium improves spleen, both
kidneys and gallbladder but scores lower on the other six organs. Its macro Dice
is lower by just 0.00383416. This single stochastic pair does not establish effort
equivalence, an efficiency advantage or a stable benefit from higher effort.

The saved `build.py` constructs masks from visually placed axial polygons,
interpolates signed distances, and unites separately traced liver/spleen/duodenal
parts. It then applies explicit erosion/dilation, CT intensity rules, hole
filling, smoothing and component filtering. The candidate band can expand one
voxel for liver, two for spleen and three for kidneys, unlike the original
Astra/xhigh boundary trim, which could not grow an underdrawn contour outward.
For liver it additionally removes lateral strips using row gaps and a median
boundary limit, performs opening with a radius-two voxel ball, smooths again,
and subtracts gallbladder and stomach at their interfaces. Pancreas/adrenals use
smoothed-HU thresholds inside their traced regions. These are descriptive
differences; no ablation isolates their contribution to the score.

The complete trace contains 59 outer execution calls, 59 shell commands (all
exit zero), 43 image views and two process polls. Eight image paths are reused
for different renderings; historical image observations remain in the full
rollout/trajectory, not just the final files. Final liver refinement has subsequent
overlay views and structural validation, but no exhaustive review of all final
boundaries. No reference/scorer access, external retrieval or additional
pretrained segmenter use was observed.

The exact frozen task and pinned image match the other two conditions. All nine
live isolation checks passed. The transport log has 75 allowed model-service
connections, 22 denied telemetry connections and four denied CDN connections.
Concurrent JSON records were decoded without discarding concatenated records.
No non-JSON bytes remained. Public-data pretraining exposure and opaque service
traffic cannot be ruled out.

Total trial time was 1,360.19 seconds. Usage was 3,603,190 input tokens, including
3,471,488 cached, and 29,126 output tokens, including 10,017 reasoning tokens.
Counts accumulate across calls. Dollar cost is unavailable. There was no retry,
time extension or feedback. Published reference plus author QC is not independent
clinical adjudication; matched names do not certify every voxel's identity.
