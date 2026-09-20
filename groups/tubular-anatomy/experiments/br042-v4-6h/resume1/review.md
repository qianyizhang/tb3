# Completed resumed Astra/xhigh continuation

The original Codex session completed normally at 2026-09-20 17:13:55 UTC,
after 5167.06 seconds (1h26m07s) of resumed agent execution. Combined with
10065.19 seconds before interruption, this is 4h13m52s of agent execution,
excluding setup and the gap between runs. It did not exhaust the new six-hour
allowance. This is a resumed continuation with additional budget, not an
independent attempt or an uninterrupted run. Eleven structured transport errors
occurred during the continuation, but the final trace is `turn.completed` and
Harbor reports no exception. Monitoring is paused. At closeout, account-wide
weekly quota remaining was 68%, versus 75% before restoration; that difference
includes all concurrent account usage, not just this trial.

## What changed

The completed answer contains 64 named courses, 7430 points and approximately
3276.4 mm of geometry. It adds a superior right atrial coronary branch and three
pulmonary arterial courses relative to the interrupted 60-course output. The
agent also reviewed names, connections and distal portions, and saved a detailed
method, CSV inventory, explicit unresolved candidates, runnable reconstruction,
coordinate/spacing validation, static native-CTA overlays and a reproduction
receipt. The prior incomplete report has been replaced in the continuation only;
the interrupted artifact is unchanged.

The method describes the ambiguous upstream diagonal candidate and explains why
it was withheld. That makes the reasoning auditable, but does not resolve its
disagreement with the reference or recover the missing vessel. The atlas was
visually inspected as a native-slice review aid; nine selected slices cannot
establish correctness of every course or parent connection. Broader clinical
completeness remains unscored and unproven.

## Coronary results

Independent replay matches every verifier metric. All per-category coronary
coverage results are exactly unchanged from the interrupted output, including
both 1-mm and 2-mm coverage. The additional work improved broader reconstruction
and completion/documentation, without improving these coronary metrics.

| Condition | Geometry length coverage at 1 mm | Correctly labeled length coverage at 1 mm |
| --- | ---: | ---: |
| V3 Astra/medium, completed | 95.5% | 79.3% |
| V4 Astra/xhigh, 2h timeout | 94.1% | 74.8% |
| V4 six-hour allowance, transport-interrupted | 94.0% | 79.3% |
| Same session resumed, completed | 94.0% | 79.3% |

Equal-category means remain 75.5% geometry and 54.1% correctly labeled; both
frozen category-based pass gates fail. D2 remains effectively missed (3.1%
geometric / 0% labeled coverage), OM1 is missed, and OM2 is 57.2% geometrically
covered under OM1. R-PDA remains 100% geometry / 69.5% labeled, and R-PLA
100% / 99.0%. The reference Other category is 99.6% recovered under D2 rather
than Other. Reference identity disagreements remain under review. No score,
reference or answer was corrected retrospectively.

## Verification and limits

Frozen task bytes are unchanged. The restored original answer/session hashes
were verified before model execution. The completed JSON passes the unchanged
scorer and independent native-affine field-of-view check. Its SHA-256 is
`b88be6300213139ef6126d49988500b99d389378642dbe477abaf481c96994dd`.
The model's logged full feature/extraction rebuild took 76.3 seconds and reproduced
that hash exactly. The reviewer verified the receipt and score replay, but did
not independently rerun the extraction. Reproduction depends on the agent's saved
image-derived control points and anatomical decisions; it is not a fresh blind
rediscovery experiment.

[Structured evaluation](evaluation.json) · [Replay script](review.py) ·
[Interactive native-CTA comparison](http://127.0.0.1:8796/v4-resumed/).
The viewer preserves all previous outputs and marks this one completed/resumed.
Original `coronary_review.png` and `major_vessels_review.png` under the run's
`artifacts/app/answer/` are static source-image review aids; generated data remain
local. The table above is the portable static comparison.

The resume succeeded operationally and yielded a completed, documented artifact.
It did not eliminate the recurring small-branch discovery and numbering errors.
