# BR-017 — Substantial anatomy absorbed into an adjacent label

**Status: complete; one synthetic detection miss and three passes.**
[Visual presentation and results](BR-017-results.md) · [Per-trial trace analysis](BR-017-traces.md).

On 2026-09-15 the user
accepted the prior negative results, proposed omitted anatomy absorbed into an
adjacent component, and explicitly requested experiments without requiring that
particular hypothesis. The source message is retained in the conversation; its
individual message ID was not captured.

## Question and bounded contrasts

Can Sol/xhigh detect **mixed anatomical ownership inside a named mask**, with
original CT available, rather than identify separately supplied pure organs?
Prior BR013-A02 had an intact compact-pancreas miss; follow-ups passed with CT
or an exact label inventory. BR014-F01's large fragments also passed. This is
a new failure-mode diagnostic, not an inherited model-failure claim.

Use retained TotalSegmentator source case 28 (`s1233`), whose original organs
and fragmented organs were identified correctly by Sol. All 13 source classes
are present and existing cross-label overlaps are at most 0.105 mL. Keep full
source CT, neighboring masks and physical coordinates. Before any model trial,
screen and freeze these three conditions:

1. **M01, whole absorption:** union the pancreas into the duodenum mask and
   remove its separate label. No CT samples or aggregate foreground voxels
   disappear. This calibration can be cued by class absence; it must not be
   called count-resistant.
2. **M02, partial absorption:** transfer approximately 35% of pancreatic voxels
   nearest the duodenum into that mask. Use a curved distance-defined region,
   preserve the remaining pancreas and all class names. Require at least 15 mL
   transferred, at least 25 mL pancreas remaining and at least 95% of the
   transferred region in one 26-connected component. Report the construction
   surface as synthetic; do not present it as a real annotator's error.
3. **N01, unchanged control:** retain original source masks. No foreign-tissue
   finding is expected. It tests false alarms under the same instructions.

M02 is the primary diagnostic; M01 and N01 interpret it. Run sequentially in
M02, M01, N01 order. One fresh Sol/xhigh attempt per admitted task after matched
oracle/nop controls, zero retries, 1,800 seconds, four CPUs/4 GiB. No automatic
Terra follow-up and no post-result stronger mutation. Reject a construction
that fails the size, source-fidelity or display checks rather than tune it
against model responses.

## Compact contract and unambiguous scoring

Audit substantial inclusion of another organ inside a proposed labeled mask.
Report only findings, each with the host object ID, the included anatomical
class and one physical LPS point within that tissue. No contour reconstruction,
exact volume recovery, operation history or disease diagnosis is requested.
Absence of a class alone is not a reportable inclusion. Treat ordinary thin
boundary differences as outside scope; target errors are at least 5 mL.

The private key is the injected region's source lineage. Correct host/class
pairs must be exact, duplicates and extra findings fail, and each point must
be within 3 mm of a voxel centre in the injected tissue. All needed arrays and
ready 3-D/CT views remain public. A valid empty findings list passes N01; the
starter answer is deliberately invalid so a no-op does not get accidental
credit on the control. Scoring is independent of rendering.

Before trials: check source and union conservation, unaffected-mask equality,
CT registration, transferred size/connectivity and broad witness acceptance.
Test oracle, alternate valid point, near/far points, wrong class/host, empty,
extra and duplicate findings, and malformed/non-finite coordinates. A missing
output, tool error, invalid key or timeout is not an anatomical model failure.
Separate detection, identity and localization outcomes in the report.

## Source and error family

The [multi-reader pancreas study](https://pmc.ncbi.nlm.nih.gov/articles/PMC12701807/)
reports adjacent-duodenum inclusion and missed pancreatic portions; the
[postoperative study](https://pubmed.ncbi.nlm.nih.gov/41307673/) illustrates
under-segmentation and splenic vessels included in pancreas. Those are external
segmentation-model observations that motivate the error family. The particular
transfer here is synthetic and uses retained source-mask lineage as its key.

This user-authorized pilot reopens a diagnostic after BR-015's pause
recommendation. A bile-duct source label was unavailable, so the experiment
uses pancreas and duodenum.

## Admission and first observation

M02 transfers 21.04 mL in one connected region and leaves 38.38 mL of pancreas.
M01 adds 59.35 mL to duodenum and removes the separate pancreas label. N01 is
unchanged. All 36 authored controls pass; the independent source audit verifies
CT, aggregate foreground, untouched classes and exact transferred voxels.

M02 completed normally with an explicit empty findings list: a reviewed
synthetic detection miss. It requested 27 images, including additional CT
planes through the affected organs. M01 and N01 were still pending at that observation.
See the [M02 trace review](../evidence/br017-m02-review.json).

## Conditional scope follow-up, declared after M02/M01 outcomes

M02 missed the inclusion; M01 identified it and passed. Before N01 completes,
declare one additional **F01 focused-audit** trial conditional on a healthy N01
pass. This is an explicitly post-result explanatory contrast, not part of the
initial three-condition plan and not a replication of its original scope.

Copy the frozen M02 task and all public inputs byte-for-byte, then change only
the task routing/description and instruction scope: audit the pancreas and
duodenum masks; every other mask remains available as context. Preserve all
class names, images, CT, masks, helpers, key, witness tolerance and limits. Do
not supply the error count, a point hint or the transferred region. All foreign
classes remain possible. One fresh Sol/xhigh attempt after matched controls.

The purpose is to test whether the miss survives a smaller deliverable scope
and lower search burden. A pass retires this focused version and weakens a
global anatomical-reasoning explanation. A miss may offer a more compact
candidate under the same source-lineage contract. Skip if N01 does not
pass normally. Stop after this follow-up regardless of outcome; no stronger
mutation or repeated attempt follows it in this round.

N01 subsequently passed with no findings. F01 was admitted after verifying that
its only changed task files are `instruction.md` and `task.toml`; all public
inputs and the reference key are byte-identical to M02. Its trial then began.

## Final disposition

F01 subsequently passed with the correct host/class and a valid interior
point. Final sequence: M02 detection miss, M01 pass, N01 pass, F01 pass. Every
trial completed normally, with matching controls and no retry. The initial
three-condition plan and later conditional scope decision remain documented
above as chronology; no additional trial is pending.

Retain the original broad M02 result as a synthetic detection failure and retire
the passing conditions. The focused success supports investigating audit
coverage/attention, without establishing a causal mechanism. The round stops
here as declared.
