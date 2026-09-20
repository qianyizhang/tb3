# BR-041 — Named coronary centerline from CTA alone

User request, 2026-09-19: test whether Terra can generate centerlines from image inputs, either all major vessels or a named vessel. The original BR-030 task already required tracing, but supplied a predicted mask and exact route endpoints. This follow-up removes those aids.

One Terra/high attempt receives only the same coronary CTA crop and a named RCA ostium → distal R-PDA request. No mask, centerline, landmarks, review marker or previous solution is exposed. General methods are allowed; case-specific annotation retrieval is prohibited and the trace will be audited. Public development case, not a held-out clinical estimate. The crop itself remains author-selected anatomical context.

Predeclared outcome: ordered centerline in RAS mm, 95th-percentile distance ≤1 mm, ≥95% reference coverage within 1 mm, endpoints ≤5 mm, length error ≤15%, 0.05–0.75 mm point steps. Report individual metrics, including coverage at 2 mm, alongside the conjunction. Relaxed endpoint tolerance acknowledges that a named distal terminus is less exact than a supplied point. Reference is annotation-derived, without new expert adjudication. Do not treat terminal extent disagreement alone as failed anatomy.

Freeze before model exposure; run same-byte Docker oracle/no-op controls and local reverse/shift/straight negative controls. One attempt, no retries, ordinary 3600-second allowance. Exclude infrastructure errors and timeout from normal model failure claims. Preserve all BR-030 bytes. No CPR or mesh requirement: this tests image-to-route tracing only, and changes multiple inputs relative to BR-030 rather than isolating one aid.

[Freeze](../evidence/br041-freeze.json). Scripts: `probes/vessel-geometry/authoring/br041/`. Raw inputs, controls, configuration and trajectories: `runs/br041-image-only-centerline` and `runs/br041-named-rca-*`.

Completed: [results](BR-041-results.md). Terra finished normally but traced a substantially different route; 0% reference coverage even at 2 mm. Controls and independent replay agree.

## S01 — Sol/xhigh comparison, 2026-09-19

User follow-up: “try with sol xhigh”. Run one fresh `openai/gpt-5.6-sol` / `xhigh` attempt on the unchanged frozen task, with the same 3600-second allowance and separate verifier. Reuse the healthy same-byte oracle/no-op controls; verify frozen hashes before/after and require equal Harbor task checksums. No retries, hints, Terra output or private references supplied. Compare model plus reasoning setting, not model alone. Preserve the original Terra result and receipts. Collect artifact replay, independent distances and a source/coordinate audit.

S01 completed: [Sol/xhigh results](BR-041-sol-results.md). 80.6% requested-route coverage within 1 mm; the final distal continuation matches R-PLA instead of R-PDA. Normal completion, same-byte controls and independent replay verified.

## A01 — Astra/xhigh comparison, 2026-09-19

User follow-up: “ok, now let Astra-xhigh have a try”. Run one fresh `openai/gpt-6-astra` / `xhigh` attempt on the unchanged frozen task, same 3600-second allowance, isolated verifier and healthy same-byte controls. No retries, previous answers, branch-error feedback or private references supplied. Verify hashes and task checksums. Preserve Terra/Sol receipts; independently replay the final route and audit source exposure. This is a model-plus-setting comparison on the same public development case.

A01 completed: [Astra/xhigh results](BR-041-astra-results.md). 100% requested-route coverage within 1 mm, but roughly 15 mm beyond the annotated endpoint. Frozen score fails distance/endpoint checks; correct-branch tracing and unresolved distal extent are reported separately. Same-byte controls and independent replay verified.

## Interactive result review

User requested reuse of the earlier CPR presentation scaffold to verify all three model results. [Local interactive viewer](../../runs/br041-image-only-centerline/presentation/index.html) ([launcher](../../runs/br041-image-only-centerline/presentation/Open%20review.command)); [build/reopen guide](../../probes/vessel-geometry/authoring/br041/presentation/README.md). Uses unchanged submitted routes, original native CTA, evaluator reference branches and reference-assisted surface context. CPRs are author-generated review artifacts, not new model outputs. No new trial, scoring revision or deployment.

## Guided video comparison — 2026-09-20

User requested a video tour comparing the three solutions and questioned using reference distance as anatomical correctness, especially for Sol and Astra. The user considers Astra's continuation plausible and potentially preferable to the annotation. The tour reflects that distinction without treating this opinion as independent adjudication.

[Local narrated video](../../runs/br041-image-only-centerline/presentation/guided-tour.mp4) · [transcript](../../runs/br041-image-only-centerline/presentation/tour-transcript.md) · [render receipt](../../runs/br041-image-only-centerline/presentation/tour-validation.json). Six chapters compare shared route, branch choice, and distal extent using unchanged lines and source-derived CPR/sections. Terra is a localization mismatch; Sol closely traces the alternate R-PLA; Astra closely follows the requested R-PDA and extends beyond the annotation. The final extension remains an image-review question. The interactive viewer embeds the video with chapter navigation and moves the unchanged frozen scores into secondary context.

Validation: the 1280 × 720 H.264/AAC video decodes fully; narration is nonempty (mean −16.0 dB, peak −1.8 dB). Astra's chapter was played and visually checked in the browser after fixing seeking on the simple local HTTP server. Numerical source sampling and unchanged model-file digests remain verified by the presentation validator. No new trial or clinical adjudication was performed.
