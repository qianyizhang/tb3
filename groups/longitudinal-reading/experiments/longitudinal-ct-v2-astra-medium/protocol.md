# Revised image-only instructions — Astra medium

User authorization, 2026-09-22: revise generic instructions, give Astra medium a
fresh attempt, and conditionally perform a narrower test if lesions remain missed.
[Source task](codex://threads/01a0c4d1-741f-76e3-9023-1064e5a9a0c5).

Use the same private case, native CTs, reference masks/events, scorer, pinned
solver/evaluator/transport images and two-hour budget as the original comparison.
Only instruction.md changes: distinguishable touching lesions retain separate IDs;
image-based more-likely-tumor findings are included without requiring diagnostic
certainty, while more-likely-normal/benign findings are excluded. Uncertain
candidates require an inclusion decision, coordinates and reason in the report.
Zero lesions remains allowed. No case-specific count, location, disease, event,
prior output, score or author review enters the solver.

One fresh `openai/gpt-6-astra`, effort `medium`, attempt; no automatic retry or
resume. Native oracle/no-op controls use the new digest before inference. Record
live image/mount/network isolation and fresh account quota, with no reset credits.
Run with diagnostic origin: expert partition adjudication remains open even after
instruction clarification. No score thresholds, source labels or original records
are altered. Separate detection/localization, foreground and instance segmentation,
end-to-end and conditional links/events, with the frozen v1 definitions.

Before examining v2 output, define the narrower-test trigger as any reference
instance with <10% coverage by the predicted foreground. This detects substantial
omission independently of the one-to-one instance-partition convention. Select
one affected longitudinal reference group, prioritizing a persistent group and
then larger total reference volume, with numeric IDs as a deterministic tie break.
If misses are only under-separation with substantial coverage, report that fact
instead of calling it a search failure or launching a recognition test.

If triggered, author a separately frozen localized diagnostic: same raw CT pair,
plus exact candidate-center native coordinates for the selected group, with no
GT masks, lesion labels, disease identity, prior feedback or guaranteed-positive
statement. Ask for tumor/normal-or-benign/indeterminate judgments with evidence,
and segment candidates judged tumor. Scope scoring only to selected targets;
do not penalize omission of out-of-scope lesions. Use one fresh Astra-medium
attempt, the same runtime/budget and separate controls. This intentionally supplies
localization and is not another image-only discovery result.

Interpretation declared before dispatch: recovery after localization supports a
search/attention contribution; seeing and rejecting the selected structure supports
recognition/inclusion-policy disagreement with GT; accepted target with poor mask
supports a segmentation bottleneck. Remaining failure can still include viewing
or local interpretation problems. A single adaptive positive-target probe cannot
prove specificity, isolate all causal factors, or establish population accuracy.
One original versus one revised attempt cannot establish a causal prompt effect.
