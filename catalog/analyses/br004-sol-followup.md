# BR-004 Sol follow-up: three reviewed misses, one source hold

One Sol/xhigh attempt per task, sequentially, with zero trial retries. All four
completed normally. The raw grader returned zero on all four; review retains
**three controlled-defect misses** and excludes **case 46** from model-failure
claims because it raised a credible additional source-label question.

## Results

| Task | Reviewed outcome | Agent min | Output tokens | Uncached input | Estimated USD |
|---|---|---:|---:|---:|---:|
| 32: small kidney extension | Miss | 12.60 | 20,930 | 151,865 | 2.072 |
| 83: kidney-pole omission | Miss | 16.61 | 30,292 | 160,702 | 3.092 |
| 46-v2: scoped unusual-anatomy control | Source hold | 13.90 | 16,750 | 187,929 | 1.873 |
| 61-v2: inferior heart omission | Miss | 16.46 | 26,784 | 230,991 | 3.642 |

All resources are retained, including the held case: **59.56 agent minutes,
94,756 output tokens, 731,487 uncached input tokens, estimated USD 10.680**.
Total input is 15,379,807, including 14,648,320 cached tokens. Reasoning output
is 50,383 and is already included in output. The full sequential benchmark took
69.10 minutes, including 4.28 minutes in oracle/nop controls. These estimates
exclude authoring; they are not invoices. Case 46's time includes client
connection retries and a WebSocket-to-HTTPS recovery within its single attempt.

## What was corrected

Cases 32 and 83 retain every task byte and match the earlier Terra Harbor task
checksums. Cases 46-v2 and 61-v2 retain all CT/SEG bytes, focus labels, decoder,
planted discrepancy regions and 3 mm localization tolerance. Three unresolved
source patches were excluded through public, label-specific LPS boxes, with the
same boxes in the private grader. No clinical labels were invented or changed.

The grader ignores a valid point only when its label matches an exclusion and
its point lies inside that box. Such a finding cannot satisfy a planted error.
After filtering, each in-scope label must occur at most once. This lets a solver
report both an excluded heart fragment and a separate actual heart defect
without the two competing for a single permitted output slot.

The correction worked as specified: Sol recognized the excluded L2 fragment in
46 and both excluded patches in 61. It still missed the retained inferior heart
omission in 61, deliberately writing and validating an empty report.

Case 46 revealed a further source issue. Sol reported a tubular hilar component
of the original heart mask. The component has 236 task-grid voxels and remains
isolated at original resolution (1,869 voxels), so its isolation is not solely
a downsampling artifact. CT and neighboring masks support a credible source
question, but do not establish the exact intended heart-label boundary. The
frozen clean-control grade is therefore **not an established model false
positive**. Keep the v2 key and trial unchanged; park this patient for source
adjudication rather than treating its cheap raw miss as useful difficulty.

## What the traces establish

- **32:** an actual kidney axial sheet includes the retained witness slice 94.
  Sol explicitly judged the masks plausible, then wrote and validated no findings.
- **83:** detailed axial sheets stop at the submitted kidney endpoint, but
  delivered whole-volume coronal/sagittal views include the superior pole. The
  miss cannot be attributed solely to never receiving a view of the region.
- **61-v2:** a targeted coronal sheet includes the inferior heart border and
  witness plane. Sol recognized the source exclusions and alleged no new
  in-scope source defect, then finalized no findings.

These observations support misses of the retained controlled alterations. They
do not isolate perception, rendering, attention or inspection policy as the
cause. Source contours are not specialist-certified clinical truth, and no
confirmed postoperative cohort is claimed.

## Difficulty versus resources

**Prioritize case 32.** Among the three reviewed Sol misses it is lowest on all
four primary resource measures: agent time, output tokens, uncached input and
estimated cost. It also has a reviewed Terra/max miss on the identical task.
Case 83 is a useful alternative; 61-v2 is now a defensible Sol failure case.

On the unchanged kidney tasks, Sol did not rescue either Terra miss:

| Case | Terra/max min → Sol/xhigh min | Output tokens | Estimated USD |
|---|---|---|---|
| 32 | 10.21 → 12.60 | 23,713 → 20,930 | 0.857 → 2.072 |
| 83 | 15.92 → 16.61 | 32,744 → 30,292 | 1.643 → 3.092 |

Fewer output tokens did not mean less time or lower estimated cost here. Input,
cache use and model pricing also matter. Image-block counts increased from
12 to 34 for case 32 and from 32 to 50 for case 83; these counts include repeated
or overlapping views and do not measure unique anatomical coverage.

**Next proposed contrast:** provide a standard viewer for case 32 while keeping
its anatomical scope, data and planted error fixed. Include unoverlaid CT,
thin contours and context beyond the mask boundary. Test whether removing
rendering-code work and mask-based cropping reduces resources while preserving
the miss. If the revision passes, retire that revision as a difficulty lead.
A narrower kidney-only scope is a separate subsequent contrast; do not combine
both changes and attribute the result to either. No further trial was launched.

One observation per task/model configuration is not a failure-probability
estimate or final submission qualification. Cases 46/61 changed scope between
Terra and Sol; their outcomes cannot isolate a model effect. Earlier Terra
artifact replays under the new scope remain explicitly retrospective.

## Evidence and verification

The [frozen protocol](../../docs/research-rounds/BR-004-sol-followup.md),
[freeze](../../docs/evidence/br004-sol-freeze.json),
[47 author scoring controls](../../docs/evidence/br004-sol-author-controls.json),
[scope review](../../docs/evidence/br004-sol-scope-review.json),
[case reviews](../../docs/evidence/br004-sol-reviews.json), and
[final summary](../../docs/evidence/br004-sol-summary.json) retain the contract
and outcomes. Eight matching container controls passed their declared outcomes;
all four independent re-scores agree. All task/snapshot hashes remain unchanged.
Local runtime contexts agree with the requested Sol/xhigh configuration; this
does not independently establish provider-side model identity.

The [HTML report](../../runs/br004-sol/report.html) and
[CSV](../../runs/br004-sol/benchmark.csv) retain complete resource rows and
inspectable images. Raw logs, model submissions, traces and original source
review images remain local. The catalog's generic verifier-case parser warning
is retained; exact anatomy grades come from `verifier/details.json` and the
independent replay, not that generic parser.
