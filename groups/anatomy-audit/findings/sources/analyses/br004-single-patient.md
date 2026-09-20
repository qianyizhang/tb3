# BR-004 single-patient resource benchmark

**Best observed lead: case-32, a small connected kidney-mask extension.**
Terra/max missed it in 10.21 agent minutes, with 23,713 output tokens and
estimated model cost of $0.857. It was the lowest-resource attempt on all four
reported axes: time, output tokens, uncached input and estimated cost.

## One attempt per task

The [frozen protocol](../../docs/research-rounds/BR-004-single-patient-benchmark.md)
gave each of eight existing patients a fresh Terra/max context, its unchanged
10–11 focus labels, and the normal 1,800-second allowance. All eight attempts
completed normally. There were no retries, changed defects, extra hints or
post-result task edits. The [freeze](../../docs/evidence/br004-single-patient-freeze.json)
retains task and patient-file hashes. Matching oracle/nop controls and independent
re-scoring agree for every task.

| Patient task | Raw outcome / review | Agent min | Output tokens | Uncached input | Est. USD |
| --- | --- | ---: | ---: | ---: | ---: |
| 74 — limited coverage | Pass; negative control | 14.83 | 32,336 | 193,907 | 1.901 |
| 19 — thoracic abnormality | Pass; negative control | 14.48 | 31,291 | 252,373 | 1.691 |
| 83 — kidney-pole omission | Miss; reviewed failure | 15.92 | 32,744 | 176,248 | 1.643 |
| 46 — source pathology | Pass; predeclared source hold | 12.24 | 26,836 | 187,660 | 1.566 |
| 28 — local rib exchange | Pass; both labels and points correct | 16.93 | 37,678 | 170,389 | 1.645 |
| 61 — heart-apex omission | Miss; source adjudication hold | 19.89 | 48,633 | 372,883 | 2.487 |
| 95 — source pathology | Pass; negative control | 13.30 | 28,955 | 172,179 | 1.467 |
| 32 — small kidney extension | Miss; reviewed failure | 10.21 | 23,713 | 98,915 | 0.857 |

This is **five raw passes and three raw misses**. After review, retain four
solved controls, two genuine controlled-defect misses, and two source holds
(one raw pass and one raw miss). Keep all eight rows in the resource comparison;
do not reinterpret the held cases as model failures or erase them from the run
record. One observation per task is not a reliable success probability.

Total model use: **117.80 agent minutes, 262,186 output tokens, 1,624,554 uncached
input tokens and $13.257 estimated cost**. Total input is 35,930,858 tokens,
including 34,306,304 cached tokens. Reasoning output (158,896 tokens) is included
in output. The sequential benchmark took 136.22 minutes from first control
launch to final trial completion, including 8.36 minutes in oracle/nop controls.
Model setup and verification are separately recorded. Actual CPU-seconds and
peak RAM were not measured; the limits were 4 CPU and 4 GiB.

## Why the two misses count

**Case-32:** The 63-voxel extension retains Dice similarity 0.993572. It extends
into adjacent fat/muscle; changed voxel centers lie as far as 9 mm from the
original kidney mask, with 44 centers beyond 3 mm. Source/CT/task overlays were
reviewed before the final outcome. Terra received an axial view at the retained
witness slice and later targeted kidney views, then explicitly validated an
empty report. The only missing finding is `kidney_left`; there are no extra
labels or point-format errors. The [stable review](../../docs/evidence/br004-single-case-32-review.json)
retains geometry, source and result hashes, and an actual viewed contact sheet.
This is a local controlled-extension miss, not proof of a general medical deficit.

**Case-83:** Terra also completed with an empty report, missing a 215-voxel
kidney-pole omission with Dice similarity 0.980. Its axial selection stopped at
the submitted mask's upper slice, while the source extends three slices farther.
However, padded coronal views included the omitted region. Slice selection is a
possible contributor, not a demonstrated sole cause. The [stable review](../../docs/evidence/br004-single-case-83-review.json)
retains the source comparison and actual viewed image.

Case-32 used **35.9% less agent time, 27.6% fewer output tokens, 43.9% less uncached
input and 47.9% lower estimated cost** than case-83. Both are single observations.
These are cross-patient measurements, not a causal effect of defect type.

## Source holds and solved controls

Case-46's anterior L2 ambiguity was declared before testing. Its raw pass does
not resolve that question. Case-61 raised additional source questions: the model
reported an original internal liver gap and a detached superior heart component.
Both reported regions are unchanged from the source. Its heart coordinate is
valid LPS but 90.85 mm from the planted inferior omission. Retain the raw miss
and unlocated planted omission; exclude the overall grade from genuine-failure
counts until those source findings are adjudicated. The [stable review](../../docs/evidence/br004-single-case-61-review.json)
retains the exact points and images. Known injected changes do not establish
that every unmodified source annotation is correct.

The three unheld clean controls were accepted without false positives. An empty
nop answer appropriately passes clean tasks; the flag-every-label control fails.
The rib task is a solved positive control: both submitted witness points are
within 0.017 mm of discrepancy voxel centers. Retire these four exact conditions
from difficulty selection rather than making them harder after the pass.

## What to optimize next — proposed, not executed

| Design change | Hypothesis | What to inspect | Evaluation of failure |
| --- | --- | --- | --- |
| Focus a new task on the paired kidneys, retaining the full CT as context | The case-32 miss may survive a smaller review scope with lower cost | Does the same defect still get missed when fewer labels compete for attention? | Same exact-label/spatial-witness rule; retain a matched clean control and one new attempt per newly frozen task |
| Supply a generic viewer with uniform multiplanar views and margins | Less plotting/debugging work may reduce incidental cost | Time and output tokens spent preparing views; whether failures persist when the region is clearly available | Preserve ordinary tools and time allowance; a new pass means retire that narrowed condition |
| Adjudicate all focus labels before freezing | Remove unintended source defects and disputed boundary conventions | Independent clinical review of source regions, especially detached parts and internal gaps | Exclude unresolved regions before launch; keep all executed outcomes in the ledger |

Case-32 is the lead, but **10 minutes and 24k output tokens are still substantial**.
The next useful contrast is reduced review breadth and preparation cost, with
normal reasoning time preserved. The current data does not prove how much either
change would save or whether the failure would survive. No further model run
was launched. Confirmed surgical histories and specialist clinical certification
remain unavailable; the unusual cases are coverage/pathology controls.

## Inspectable evidence

- [Full retained summary](../../docs/evidence/br004-single-patient-summary.json)
- [Authored reviews](../../docs/evidence/br004-single-patient-reviews.json)
- [Token accounting contract](../../docs/evidence/br004-single-metric-contract.json)
- [Interactive local report](../../runs/br004-single/report.html)
- [CSV with all timing and token fields](../../runs/br004-single/benchmark.csv)

Raw runs and image evidence remain local under `runs/`. Harbor's cost is an
estimate, not an invoice. Host activity and API latency can affect wall time.
The earlier eight-patient timeout remains separate: it produced no considered
answer, and its capped 30-minute cost is not an accuracy or efficiency baseline.
Repository checks do not certify clinical validity or final submission readiness.
