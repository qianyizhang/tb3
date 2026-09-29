# Scoped queue pilot and handoff

**Workflow pilot passed on 2026-09-29. At the time of that pilot, core status was
48 reviewed, 106 deferred, 0 ready out of 154.** This is tooling regression evidence, not new explainer
completion, a medical/model trial or a production-throughput benchmark.

The later user clarification supersedes blanket deferral: all **106** unfinished
entries now enter source resolution first, with symbolic fallback authorized when
actual data remains unavailable. The earlier pilot results below remain unchanged;
read the current [workflow](EXPLAINER-WORKFLOW.md) for selection and acceptance.

## Delivered workflow

- [Scope](EXPLAINER-SCOPE.json) owns eligibility and priority; the live
  [review ledger](EXPLAINER-LEDGER.json) owns statuses and dependency records.
- All 106 blocked core rows now have an explicit `dependency_deferral`: original
  reason, reopening action, user actor, decision source and date. Every pre-existing
  ledger field and all historical acceptance receipts were preserved.
- The [dependency register](EXPLAINER-DEPENDENCIES.md) lists every deferred entry.
  It is a generated view, not a separate authority.
- [Workflow commands](EXPLAINER-WORKFLOW.md) cover queue selection, pinned task
  packets, idempotent deferral, export review collection, browser witnesses and
  attributed sign-off. The repository skill is
  [complete-explainers](../skills/complete-explainers/SKILL.md).

## Exercised pilots

| Existing reviewed entry | Surface | Video | Decoded frames | Result |
| --- | --- | ---: | ---: | --- |
| `tb3-supplied-object-identity` | Native teaching geometry; spatial and no-GPU projection | 42 s | 1,008 | Regression sign-off passed |
| `tb3-vessel-connection-repair` | Explicit binary-grid teaching fixture; planar | 24 s | 576 | Regression sign-off passed |

Both ran fresh HTML/MP4/caption exports, full decoding, complete normal-speed 1x
playback and start/middle/end seeks. The collector retained 28 timed playback
samples with observed time intervals; those samples are not exact-frame captures.
The existing browser matrix checked 12 locale/frame captures across the two
stories, mobile/reveal/reset/no-GPU behavior and 62 integrated navigation cases,
with zero page errors or remote requests. Canonical, mobile, fallback, integrated
Explorer and representative playback images were inspected and attributed in
separate local review records. Original story acceptance was not rewritten.

Two GPT-6 Sol workers with high reasoning implemented disjoint queue and review
modules. The main agent integrated and reviewed them. A third independent Sol
reviewer found missing audit-receipt enforcement and insufficient browser-report
binding. Both were repaired and re-reviewed before sign-off. Workers did not write
the real ledger or accept their own work.

Live CLI checks rejected blocked production preparation, excluded-entry preparation
and attempted regression acceptance. Repeating the same deferral changed no bytes.
Fixture tests cover production acceptance and preservation of other rows, source
drift, invalid/missing audit receipts, stale browser witnesses and missing inspection.
No live unfinished entry was promoted; no entry-authoring throughput gain is claimed.

## Verification and artifacts

The staged tree passed `make check PYTHON=python3.12` in an isolated managed
checkout: **207 Python tests**, artifact policy, records, documentation, skills,
typing, contracts, lint, formatting and workflow syntax. `make js-check` also passed
there. The isolated checkout reused existing runtimes without installation.
Its first setup lacked `.local/` and three ignored archived source/link files;
the retained copies were provisioned with recorded hashes, preserving failed logs.
No archived investigation was resumed. The pilot exports themselves used the main
checkout, including its preserved unfinished EHT source; receipts record that state.

Local receipts and media are under `.local/explainers/scoped-pilot-20260929/`:

- `ownership-start.json`, `owned-paths.txt`, `queue.json`, `pilot-guards.json`.
- `batch-v1/batch.json`, per-story export receipts and `browser-witness.json`.
- `identity-review-v1/review.html` and `repair-review-v1/review.html`.
- `identity-inspection.json`, `repair-inspection.json`, and corresponding
  `identity-signoff.json` / `repair-signoff.json` (regression; acceptance false).
- `isolated-verification.json`, `isolated-local-inputs.json`,
  `isolated-make-check-v3.log` and `isolated-js-check-v1.log`.

## Next session

Read the scope, live ledger, dependency register and workflow before setting a new
goal. The historical all-205 goal remains paused. The 13 candidates and 38 other
out-of-scope entries do not enter automatically. Preserve the excluded EHT-original
implementation and receipts; its dirty-path fingerprints are in the ownership record.

**Start with the source-resolution queue.** The later user instruction authorizes
attempting missing downloads and unfinished audits, then symbolic explanations with
a concise top warning if actual data remains unavailable. The cardiac delivery-scope
question is answered for task interpretation; no public redistribution is required.
Record observed access limits rather than treating missing files as inaccessible.
Keep any remaining dependency explicit and move on. This policy does not assert
source permissions or turn a resolution plan into visual acceptance.

Once an entry becomes ready, use a fresh production packet, bounded workers and
sequential main-agent acceptance. Keep source/asset/reference distinctions and
existing medical trial/publication boundaries. Remote delivery and CI remain
program-level pending work; this pilot establishes local checks only.

Suggested opening request for the new session:

> Set a new goal to finish the remaining core explainers selected by
> EXPLAINER-SCOPE.json. Follow EXPLAINER-WORKFLOW.md and complete-explainers v1.1.0:
> first attempt source resolution, then use a sound symbolic illustration with a
> concise top reason/acquisition warning where actual data remains unavailable.
> Record any dependency that still prevents a supported explanation and continue.
> Use bounded Sol workers for independent work, with the main agent integrating
> and reviewing entries one by one. Preserve existing reviews and excluded work.
