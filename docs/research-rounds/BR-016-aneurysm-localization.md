# BR-016 — Aneurysm localization pilot

## Authorization and hypothesis

2026-09-15: the user proposed brain aneurysm detection, accepted a source-backed
localization pilot, and said “yes, go experiment”. This is new research explicitly
resumed after interview closeout. No submission workspace changes are authorized
as a side effect. BR-015 abdominal evidence is preserved separately.

Hypothesis: identifying a focal abnormality within a branching intracranial vessel
network may challenge Sol/xhigh. This is untested locally. Published specialist
performance is not a Sol/Terra result. Difficulty must survive evidence review;
an invisible lesion, incomplete source annotation, or inadequate viewer is a task
validity problem, not demonstrated clinical reasoning failure.

## Source and selection before model outcomes

Use [OpenNeuro ds003949](https://github.com/OpenNeuroDatasets/ds003949),
[study](https://arxiv.org/abs/2103.06168), CC0. Pin the Git tree and verify every
NIfTI against its Git-annex size and MD5; retain SHA256 in a local receipt.

The initial source-order sample is the first two positive subjects, first control,
and first multi-lesion subject, first session each. This is calibration curation,
not a claim these cases are hard or externally documented model failures.
Inspect all labels and images before admission; record exclusions rather than
silently replacing cases. Each task uses one distinct subject. Do not disclose
source IDs, lesion masks, lesion count, or model answers in a blind review packet.

## Task and evaluation

Input: native TOF-MRA intensities with spatial metadata and supplied projection /
slice tools. Initial candidate is imaging-backed; geometry-only is a future
separate condition. No injected abnormalities. Deliverable: a JSON list of
aneurysm locations in a declared coordinate system, empty for no aneurysms.

Freeze acceptance regions before any model trial. Source weak masks support
coarse localization, not exact boundary scoring. One-to-one matches; every lesion
must match, and extra detections fail. Save TP, FP, FN separately. Preserve explicit
invalid-output scoring. Oracle and no-op controls must run on the identical task
snapshot; on a negative case a deliberate false-positive control is additionally
required because an empty-list baseline is clinically correct.

Use the existing Sol/xhigh harness, one attempt per case, 1800 s agent limit,
4 CPU / 4 GiB, no model retries. Run sequentially. Record normal completion,
checksum, reward, agent and total time, input/cached/output/reasoning tokens and
estimated cost. Timeouts, infrastructure errors, and source faults are exclusions.

## Review and interpretation

Before trial: check intensity/label alignment, visible lesion evidence, coordinates,
rendering, independent scoring controls and trivial centre / brightest-voxel
baselines. Keep complete scan coverage; no lesion-centred cropping.

The user offered sampled reviews and reported relevant experience. Keep a sample
blinded to key/model outcomes and record experience, confidence and unanswerability.
Sampled experienced-user review is not automatically specialist validation of the
whole task. A normal model miss remains provisional until evidence sufficiency
and annotation completeness are reviewed. No repeated trials to force a failure.

## State

Three cases admitted: two source-order positives and the first control. The first
multi-lesion subject is held because one label spans about 2 mm; no trial on that
case. This is a visibility hold, not a claim that all small aneurysms are unsuitable.

The v1 oracle exposed a missing separate-verifier Dockerfile. Preserve its failed
run and all three original freezes. Corrected `*-v2` tasks add the missing packaging;
no model attempted v1. The input image / instruction / scorer bytes are otherwise
unchanged (apart from task name in TOML). All six corrected oracle/nop controls
pass as expected. Three Sol/xhigh attempts complete normally: N01 reference miss,
N02 correct localization, N03 correct negative with public-source assistance.
N03 is excluded from unaided capability interpretation. Independent source-grid, region,
renderer and grade-replay checks pass. [Final results](BR-016-results.md) retain
metrics and limitations. Raw assets and receipts: `runs/br016-aneurysm/`.

The current [case explorer](http://127.0.0.1:8766/) presents linked planes,
windowing, MIP slabs, optional reference reveal and per-trial workflow summaries.
It supersedes the original answer-free review presentation; the review form is
retired. Historical guided feedback remains in the evidence archive. See
[final results](BR-016-results.md) for the current synthesis.

## Modality scope

This first pilot uses native MRA, orthogonal slices and slab maximum-intensity
projections. No arterial mesh was reconstructed, so it does not test the separate
geometry-only hypothesis. The source supplies lesion annotations rather than an
expert-labelled full vessel mesh; reconstruction would add another source of error.
The original unstripped volume remains available alongside the source brain extract.

The original review packet was answer-free. The current presentation deliberately
shows outcomes and optional reference locations; it is an experiment explorer,
not a blind review instrument.

## Post-trial source-lookup audit

N03 retrieved the public dataset inventory, matched the original image exactly,
and submitted after reference exposure. Retain its raw pass but mark it source-
assisted. N01 and N02 have no observed source lookup. This newly observed confound
requires a distinct isolated condition before any future clean negative trial; no
retry or changed-input reclassification was performed in this round.
