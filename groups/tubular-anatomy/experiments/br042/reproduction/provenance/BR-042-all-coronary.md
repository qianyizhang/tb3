Source: `docs/research-rounds/BR-042-all-coronary.md`; original SHA-256: `a738ad17475acd79bfc9eb4c93472d81b778bd02d0f033012f4da0f8eb81b84a`.
Repository source locators below are provenance; they are not required runtime inputs.

# BR-042 — Discover and label coronary centerlines from CTA alone

User request, 2026-09-20, following task `01a0b6ff-f817-77a0-93f6-583edf33a764`: first verify that the sample has ground truth for all clinically relevant vessels, then upgrade the task and try Astra/medium. This authorizes one new trial; the closed interview synthesis and submission remain separately owned.

## Ground truth and supported scope

[ImageCAS-X](https://github.com/kitbransby/ImageCAS-X) provides corrected coronary lumen labels and derived labeled centerlines. The retained case 1 includes both trees: 13 left and 5 right polylines, with LM, LAD, LCx, D1, D2, OM1, OM2, RCA, R-PDA, R-PLA and Other. All points fall inside the original 512 × 512 × 275 CTA; segmentation and image affines match. Case audit and source hashes (repository source locator: `../evidence/br042-gt-audit.json`).

This supports an **all-annotated-coronary** extraction/labeling experiment, not all clinically relevant thoracic vessels. No complete reference for veins, pulmonary arteries, aorta or every tiny coronary branch is established. Labels/centerlines are dataset references, not newly independently adjudicated anatomy. Public development case; no population or clinical validity claim.

## Frozen prospective experiment

One `openai/gpt-6-astra` / `medium` attempt, ordinary 3600-second allowance, no retries or previous solutions/feedback. Deliver the original full CTA rather than the previous annotation-selected crop. Expose the generic 14-class vocabulary but no patient-specific presence list, segmentation, seeds, endpoints or centerline. General methods allowed; case-specific annotation retrieval and pretrained coronary weights of unknown training overlap prohibited. Task and reasoning setting both change, so this is not a controlled effort comparison against BR-041.

Exact prompt (repository source locator: `../../probes/vessel-geometry/authoring/br042/instruction.md`) · Frozen hashes (repository source locator: `../evidence/br042-freeze.json`). Output is JSON polylines with RAS-mm coordinates and per-point anatomical labels, plus method and executable extraction code. No CPR/mesh burden.

Private evaluation densely samples line edges with arc-length weights and measures unlabeled geometric recall/precision and label-specific recall/precision. A predeclared annotation-agreement pass requires macro labeled recall ≥90%, each present label ≥80%, and aggregate labeled precision ≥90%, all at 1 mm. Report 2-mm recall diagnostically. Fine segment-boundary labeling and distal extent can lower agreement without establishing false anatomy; no exact endpoint/length-ratio gate. The 14/Other class aggregates additional branches, so category recall is not individual-branch identification. Topological correctness and clinical completeness are not independently certified by these proximity metrics.

Before model exposure: oracle/no-op in the same-byte separate-verifier environment; local missing-left-tree, missing-small-branch, label-swap and displacement controls. Preserve frozen source and historical task bytes. Collect normal-completion status, runtime and token usage if available, per-label metrics, independent replay, output/code/trace and assistance audit. Infrastructure errors/timeouts are exclusions, not anatomical failures.

Authoring: `probes/vessel-geometry/authoring/br042/`; local runtime: `runs/br042-all-coronary/` and `runs/br042-all-coronary-*-v1-20260920/`.

## V2 — User steering before model exposure

The user explicitly requested broad vessel generation, scoring only where GT exists, and visualization of the rest for human inspection. They also requested coverage-focused passing with tolerance for plausible reference extensions. **This supersedes the coronary-only generation scope and precision gate above.**

V1 oracle passed; no-op was interrupted during the revision, before any Astra job directory existed. Preserve V1 frozen bytes and controls under `runs/br042-all-coronary/`, including its authoring snapshot. V1 launched no model attempt.

V2 asks for all identifiable clinically relevant vessels in the native CTA. Coronary labels 1–14 retain their vocabulary; other named vessels use code 0 and are unscored. Passing requires macro same-label coronary recall ≥90% and every present category ≥80% within 1 mm. Precision, extension and 2-mm coverage remain diagnostics, with no endpoint, precision or length-ratio pass gate. A coverage pass is not proof that every emitted vessel is correct. Human inspection must include unsupported/uncertain extent and noncoronary output on native CTA. Ground truth scope remains coronary-only; generation scope is broader.

V2 freeze (repository source locator: `../evidence/br042-v2-freeze.json`) · V2 GT audit (repository source locator: `../evidence/br042-v2-gt-audit.json`) · Current prompt (repository source locator: `../../probes/vessel-geometry/authoring/br042/instruction.md`). Run fresh same-byte V2 oracle/no-op controls, then one Astra/medium attempt; no previous output or feedback. Runtime `runs/br042-all-vessels-v2/` and `runs/br042-all-vessels-*-v2-20260920/`.

V2 completed: Results (repository source locator: `BR-042-results.md`). Normal Astra/medium completion in 27m 56s; 27 polylines (11 coronary, 16 unscored). 87.0% geometric reference-length coverage at 1 mm, 51.6% mean per-category labeled coverage. Coverage pass not met; extensions do not cause failure. Exact replay and independent distances agree. Viewer retains all output for inspection.
