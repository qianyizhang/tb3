Source: `docs/research-rounds/BR-042-v3-comparison.md`; original SHA-256: `5bf3f6a42e84c72ad0c53b3e16d030db44ff05aea88e44e123dec01480ff3f66`.
Repository source locators below are provenance; they are not required runtime inputs.

# BR-042 V3 — Disambiguated vessel extraction with separate geometry and identity evaluation

User authorized, 2026-09-20: revise the spec to disambiguate it without leaking case context, allow one hour, and run Sol/xhigh, Astra/medium and Astra/xhigh separately. Three fresh model attempts, one each; zero retries. No previous answer, result, reference inventory, route landmark, or case-specific feedback is supplied.

Exact public instructions (repository source locator: `../../probes/vessel-geometry/authoring/br042_v3/instruction.md`) · Input audit (repository source locator: `../evidence/br042-v3-input-audit.json`) · Freeze (repository source locator: `../evidence/br042-v3-freeze.json`).

## Task and exposure boundary

Retain the same full native CTA, generic source notice, libraries and output coordinates. Clarify generic vocabulary mapping, label 0 versus 14, branch numbering, segment transitions, uncertainty inventory and systematic discovery/geometry/identity review. Do not insert observed prior mistakes, patient-specific anatomy, target locations, existing code or previous scores. The reference JSON is byte-identical to V2 and stays in a separate verifier environment. Oracle solution names are private. The unchanged public environment has only CTA, source/license notices and Docker dependencies; prompt separately hashed. No host mounts or session resumption.

This refinement was authored after observing earlier outcomes. It supplies generic specification clarification rather than case answers; it is not a claim of an independently designed held-out task. No V1/V2 bytes or reported scores change.

## Prospective metrics

Use one label-independent nearest-sample correspondence for each reference sample. Sample line segments with physical arc-length weights at ≤0.25 mm, split endpoint label transitions at the midpoint, and break numerical distance ties by submitted sample order (never by label). All output including label 0 can recover geometry. Correct-label coverage requires the fixed geometric match to have the reference code.

Report geometry and labeled coverage side-by-side at 1 and 2 mm: per reference category, equal-category macro mean, and reference-length-weighted overall mean. Two separate passes: macro ≥90% and minimum present category ≥80% at 1 mm, respectively. Conditional label accuracy uses only geometrically recovered reference mass. Partition reference length into missed geometry, covered wrong label and covered correct label; report label confusion in millimeters. Harbor's scalar reward stores the labeled pass, with both pass decisions retained in metrics.json.

Per-output agreement/unmatched length remains a review diagnostic, with no precision, endpoint, length-ratio or unannotated-vessel failure gate. A geometry-coverage pass does not certify centrality, topology or clinical completeness. Category 14 aggregates multiple branch identities. Free-text anatomical name validity requires separate review. Labels 0 and unannotated output remain visible. Exact duplicated alternative polylines are rejected by the output validator.

## Controls, execution and collection

Local oracle, label-swap, all-zero-label, omitted-tree, omitted-small-branch, translation, extension, unscored-extra and duplicate-alternative controls validate the separation and output rules. Run same-byte Docker oracle/no-op before model exposure. Each attempt gets 3600 seconds, 2 CPUs and 8 GB maximum RAM, using a fresh isolated container and separate verifier. Execute sequentially because Docker reports only 4 CPUs / about 8 GB total memory; shared concurrent computation would distort runtime and risk memory contention.

Order: Sol/xhigh (`openai/gpt-5.6-sol`), Astra/medium, Astra/xhigh (`openai/gpt-6-astra`). Use unchanged task bytes/checksums, independent sessions and zero retries. Record infrastructure/timeout exclusions separately; never reinterpret them as anatomical failures. Continue other authorized models if one has an infrastructure failure. Preserve all raw output and trajectory. Verify frozen hashes before/after; replay scoring and independent distances. Report wall time and retained token counts, with no invented cost.

Authoring: `probes/vessel-geometry/authoring/br042_v3/`. Local bundle: `runs/br042-all-vessels-v3/`. Jobs: `runs/br042-all-vessels-{phase}-v3-20260920/`. No interview synthesis, submission, publication or commits are included in this work.

## Pre-model setup recovery

Both initial Astra jobs failed in Harbor's Debian `apt-get install -y curl ripgrep` step (exit 100). Retained records show `agent_execution=null`, `agent_result=null`, and no sessions: neither model received a task turn. The logs truncate the package failure detail; the same installation then completed successfully in a disposable `python:3.12-slim-bookworm` container (`runs/br042-all-vessels-v3/apt-diagnostic.log`). Exact transient cause is unresolved.

To complete the user-authorized tests, run a fresh setup-recovery job for each Astra setting, sequentially, with identical task bytes and agent configuration. Only job name changes; no task/runtime installation patch or case feedback. Preserve both initial records as setup exclusions. This is recovery before any model attempt, not a second scored model attempt; no automatic model retries. Jobs append `-setup-recovery1`. The original no-retry runner remains unchanged; explicit recovery checks absence of model execution/session before launch.

## Recorded outcome

Results and limitations (repository source locator: `BR-042-v3-results.md`): Sol/xhigh and Astra/medium completed normally, with geometric / correctly labeled length coverage of 26.2% / 19.4% and 95.5% / 79.3%, respectively. Both fail the equal-category coverage gates. Astra/xhigh timed out at 3600 seconds after transport interruptions; its saved output scores 91.8% / 68.3% as a partial-artifact diagnostic, with method.md unfinished. This is not a normally completed anatomical failure or a clean effort-level comparison. No started model attempt was rerun. All frozen hashes, verifier replays and dense-distance checks agree; unannotated output remains available for human review.
