# BR-004: corrected-scope Sol follow-up

## Authorization and frozen question

On 2026-09-15 the user asked to fix the task, labels or evaluation for promising
source-held cases, include reviewed failures, and test Sol/xhigh. This is a
correction to BR-004, from the same [conversation](codex://threads/01a0a248-241a-76b0-8ecf-15e259df9734).
The user message is available in this task; its individual message ID is not.

Can the two reviewed kidney misses survive a fresh Sol attempt, and can the
two source-held patients become unambiguous scoped audits without inventing
clinical labels? Prior results remain in the
[single-patient analysis](../../catalog/analyses/br004-single-patient.md).

## Changes declared before execution

| Order | Case | Condition | Expected discrimination |
|---|---|---|---|
| 1 | 32 | Original single-patient bytes | Detect and locate the small connected kidney extension |
| 2 | 83 | Original single-patient bytes | Detect and locate the superior kidney-pole omission |
| 3 | 46 | v2 public regional exclusions | Accept unusual anatomy outside the disputed L2 patch |
| 4 | 61 | v2 public regional exclusions | Detect the inferior heart omission despite unrelated source irregularities |

Cases 32 and 83 retain every task byte. Cases 46 and 61 retain every CT/SEG byte,
focus label, decoder, planted discrepancy and 3 mm witness tolerance. Their
instructions and grader publish and honor the same label-specific LPS boxes.
These boxes enclose source patches whose anatomical identity remains unresolved
after author CT review: detached L2 tissue in 46; a small liver gap and detached
superior heart tissue in 61. The boxes pad the retained voxel bounding boxes by
6 mm on each patient axis. The builder verifies that every planted discrepancy
voxel lies outside every exclusion for its label.

This is an audit-scope correction, not clinical adjudication or relabeling.
No specialist certification or confirmed surgical history is claimed. Source
uncertainty inside excluded patches remains preserved in the earlier reviews.
There is no new viewer, anatomical focus reduction or shorter time allowance.

The public exclusion contract uses closed, axis-aligned LPS boxes. A finding
with the matching label and a finite point inside a box is ignored and cannot
satisfy a required finding. After filtering, one finding per label is allowed.
Thus the same-label excluded heart island cannot compete with the required
heart omission. Malformed points are rejected before filtering; points with a
different label do not inherit the exclusion. Exact affected-label and spatial
checks apply to the remaining findings. No positive finding count is disclosed.

## Execution and independent controls

Freeze all four task references and execution copies before the first model
attempt in `docs/evidence/br004-sol-freeze.json`. Use one fresh
`openai/gpt-5.6-sol` / `reasoning_effort=xhigh` attempt per task, sequentially in
the order above, zero retries, 1,800 seconds, 4 CPUs, 4,096 MB RAM, public network.
Model harness: Harbor 0.14.0; separate-verifier controls: Harbor 0.18.0.
Each model attempt follows matching oracle/nop controls. Oracle must pass all
four; nop must pass only case 46. Freeze mismatches or failed controls stop
execution; infrastructure failure or timeout is retained, never auto-retried or
classified as a genuine model failure. Do not provide prior answers or findings
to the solver. All old trials, freezes, and authored reviews remain unchanged.

Author controls cover oracle, empty answer, flag-every-label, correct label at
wrong coordinates, excluded-only findings, oracle plus excluded findings,
duplicate in-scope labels, same-label excluded and required findings, wrong
label at an excluded point, nonfinite/malformed points, and closed box bounds.
The tests also check public/private exclusion equality and source-byte identity.

## Evaluation, review and resource interpretation

Report every attempted row: normal completion, exact success, label/localization
errors, independent replay, agent and total elapsed seconds, input/cache/output
tokens, reasoning tokens when matched to Harbor's counter, estimated USD, tool
and image counts. Input includes cached input; reasoning is included in output.
Missing measurements are unavailable. Costs are estimates, not invoices;
CPU/RAM limits are not peak usage. Retain raw files and hashes locally.

Review each miss for task or source problems before calling it genuine. A
completed miss of the retained planted region can support that narrow failure
hypothesis; an additional unresolved in-scope source allegation remains a hold.
Successful cases are retired for this tested model/condition. One observation
per task cannot establish failure probability or final submission readiness.

Only cases 32 and 83 permit a same-task Terra/Sol comparison. Cases 46 and 61
change scope and evaluation, so any comparison confounds model and correction.
Any replay of their old Terra artifacts is explicitly retrospective, without
turning it into a fresh trial or rewriting the old source-held verdict.
