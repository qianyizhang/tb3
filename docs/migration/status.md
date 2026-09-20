# tb3-medical migration completion record

The authorized migration is implemented. The [design record](tb3-medical.md)
retains the agreed decisions; [workflow](../workflow.md) is the current interface.
The local directory and GitHub remote name are unchanged because existing work
uses them. No remote publication, new model trial, runtime installation or raw
run deletion was performed.

## Milestones

| Commit | Delivered |
| --- | --- |
| `5fe3f90` | Group-owned research records, idea/decision history, evidence lifecycle and explicit task workflow. |
| `da40955` | Seven stories, scientific assets/tours, historical trial import and isolated MRI export/replay. |
| `046a25e` | Verified legacy archive, removal of obsolete interfaces and nonmedical families from active tracking. |
| Final polish commit containing this record | Independent-review corrections, regression coverage, versioned replay launcher and completion checks. |

Seven semantic groups index 37 medical experiments. The import contains 214
individual trial receipts: 73 control passes, 62 control failures, 35 model
passes, 38 model-failure candidates and six execution errors. These categories
are observations, not automatic qualification judgments. All 50 medical entries
from the old catalog reconcile on source hash, reward and classification; nine
authored reviews retain their proof hashes. [Import reconciliation](attempt-import.json).
The six BR-043 proposals retain concise prior findings, reopening conditions and
separate assistant recommendations. Their ongoing source document remains with
its original owner; proposed trials are not treated as authorized.

Landmarks provide the detailed pilot: six source-linked evaluations preserve
cross-round attempt reuse, a qualified finding links the story and future ideas,
and a representative MRI package independently replays both saved model outputs.
Other historical work remains indexed at its stated depth; this migration does
not claim every old experiment has been fully restored or clinically adjudicated.

## Verification

- Python 3.12 `make check`: staged artifact policy, offline lifecycle/import/ownership
  tests, seven stories, 153 source-linked values and 17 exact retained assets.
- A clean Git archive passes checks and builds the portable presentation without
  ignored runs, environments, native arrays or the legacy payload. It explicitly
  reports the missing local evidence for 214 imported observations.
- Two isolated MRI package builds have identical payload/manifest hashes. Saved
  Terra and Sol scores exactly replay (3/32 and 14/32 within tolerance); the saved
  oracle passes 32/32 and an empty-output control is rejected. The packaging-only
  v2 launcher suppresses bytecode, preserving the exact inventory after replay.
  [Original check](recovery-check.json) · [v2 check](recovery-v2-check.json).
- Legacy recovery restored and SHA-256-verified all 11 files of one complete task
  using only the pre-migration Git bundle in a fresh repository, with no ignored
  archive copy or execution. [Recovery receipt](archive-recovery-check.json).
- A real browser check retrieved the recurring vertebral-numbering idea, opened
  the landmark story, exercised its missing-visible-target scene, and changed
  CPR angle and route position. A fresh landmark still export had zero browser
  errors. Existing media checks verified 45 source hashes, 984 derived files,
  scientific display invariants and video manifests/streams.
- Installed Harbor 0.14.0 accepts the new job configuration with one attempt,
  one concurrent trial and zero retries. This was schema validation only.
- All 944 retained probe/evidence files match their pre-migration hashes,
  including 89 files owned by the background BR-042 experiment. Its source,
  frozen task and runtime paths were preserved. The separate five-test BR-042
  readiness suite passed in the existing numerical environment.
  [Preservation receipt](preservation-check.json).

## Independent review and corrections

A separate reviewer inspected the implementation and reproduced issues in
isolated fixtures with execution mocked. Its review led to regression tests and
fixes for experiment revocation/invalidation (including old freezes), interrupted
attempt identity, mixed-batch collection, early collection followed by verified
binding, per-target issue resolution, removal of local media from portable
rebuilds, full immutable commit pins, exact package inventory, recipe integrity
and unchanged qualification claims. All original and follow-up reproductions
passed the independent re-review. The v2 replay launcher received a separate
real isolated replay plus post-replay inventory verification.

## Explicit limits and ownership

The archive removed 1,791 files from active tracking, with six additional original
navigation documents preserved. No history rewrite occurred. The verified bundle
and ignored archive are same-disk recovery, not independent backup; off-machine
storage remains unverified. [Manifest and recovery](../../archive/README.md).

Reproducible packaging, saved-output replay, evidence validity and submission
qualification remain distinct. Historical Docker base tags were not rebuilt or
independently pinned to image digests here. Fresh external model execution may
produce different outputs. Actual TB3 promotion must pin and check the then-current
upstream profile, licensing/access, human-authored requirements and qualifying
trials. Every generated package is explicitly a draft. The existing sibling
submission retains its independent owner.

The broad historical medical backfill does not imply fresh source access checks,
a population estimate, clinical validation or independent recovery of every
large scan. In-progress BR-042 ownership and the unrelated dirty BR-043 document
are preserved rather than included in migration commits.
