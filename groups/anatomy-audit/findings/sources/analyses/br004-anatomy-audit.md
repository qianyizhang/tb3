# BR-004: localized anatomical annotation audit

## Result

**The one Terra/max attempt is inconclusive.** It reached the unchanged
1,800-second limit with `AgentTimeoutError`. The extracted `findings.json` is
byte-for-byte the supplied empty starter file. Its reward 0, four passing clean
cases and zero located defects are properties of that unfinished artifact;
they are not Terra's considered anatomical findings or a genuine model failure.

The [round receipt](../../docs/evidence/br004-anatomy-round-summary.json) retains
the actual oracle, nop and Terra results, timestamps, artifact hashes and
independently reproduced grades. All three have the same Harbor task checksum.
All 23 new task files and the original BR-003 freeze remain unchanged.

## What was built and checked

Eight independent TotalSegmentator source patients supply 86 focus-label
decisions. Four cases are unmodified controls admitted as plausible; four
contain five altered labels: a local right rib 7/8 identity exchange, a superior
left-kidney omission, an inferior heart-apex omission, and a small left-kidney
extension. The three organ edits retain Dice 0.980, 0.980 and 0.994. The rib
labels retain Dice 0.864 and 0.851. These describe the source/edit contrast,
not diagnostic performance.

The solver returns exact affected-label sets and one DICOM LPS point per label.
The grader checks each point within 3 mm of a retained discrepancy voxel centre;
it executes no submitted code and uses no language-model judge. Case count and
error counts are distinct: a rib exchange affects two labels in one patient.

All eight source-to-DICOM-to-loader CT, mask and affine checks passed, as did
the independent scalar calculation of private evidence coordinates. Author
controls reject empty findings, flag-everything, wrong locations, omitted
findings, duplicate cases and nonfinite points. Matching actual Harbor controls
completed normally: **oracle 1, nop 0**. The reference report uses authored edit
truth; this is not an independently developed general anatomical detector.

The unchanged saved BR-003 checker misses all five altered labels. That is an
author replay of an older program, not a second fresh model attempt.

## What the trace establishes

The [trace receipt](../../docs/evidence/br004-anatomy-terra-trace-summary.json)
records 109 code-mode tool invocations, including 53 containing image-review
calls. Some calls loop over several images. Overview calls cover all eight
patients; later work uses orthogonal stacks, contextual overlays, connected
components, tissue intensities, organ endpoints and boundary-distance checks.
The model announced a broad review and continued targeted inspection until the
deadline. The trace contains no completed final report.

This was not an immediate installation or decoder failure. SciPy was absent;
the solver implemented its own component analysis. Substantial image-review
work occurred. Nevertheless, a timeout cannot distinguish anatomical difficulty
from review volume, chosen strategy or time management. Configured model and
runtime metadata identify `gpt-5.6-terra` with `reasoning_effort=max`; trace
consistency is not independent authentication of provider internals.

## Truth and scope limitations

Source masks were reviewed by the author, without independent specialist
certification. A deterministic mutation map proves what changed, not that every
unchanged source contour is clinically correct. In particular, the trace's
inspection of detached vertebral components prompted an author spot review of
case-46 L2. That anterior component remains a source-admission question, not a
confirmed annotation error or a final model finding. Do not call its possible
report a false positive without adjudication. The local comparison is retained
at `runs/br004-v1/evidence-images/case-46-vertebrae_L2.png`.

No confirmed operative history was available. Empty spleen masks were not
treated as evidence of surgery; ambiguous absence and narrow muscle-boundary
judgments were excluded. Coverage/pathology variation does not establish
postoperative discrimination. This is a fixed audit, with no hidden patients
or unseen-patient generalization claim.

The catalog importer does not recognize this scorer's case-summary schema.
Its warning is retained. Frozen `verifier/details.json` and the independent
re-score own per-case outcomes; the imported reward alone does not.

## Disposition

Park the eight-patient v1 snapshot as a preserved, inconclusive pilot. Do not
promote it to a short-horizon failure candidate or shorten its time limit.
The next proposed design should use a two-patient batch with one error family,
balanced focus labels and a matched clean control, retaining the same normal
time allowance. Review every graded source region first; independently resolve
ambiguous source labels before freezing. Keep the remaining patients for later
separately declared conditions rather than one long review queue.

No repeat, coaching, post-result mutation change or additional model attempt was
performed. This round adds **one excluded timeout, zero completed model accuracy
results and zero genuine failures**. Final submission gates remain separate.
