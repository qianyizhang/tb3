# Feedback ledger: complete-explainers

- Current skill version: `1.0.0`
- Canonical source: `skills/complete-explainers/`

## Active lessons

Scope and live review state have separate owners. A queue containing only deferred
dependencies has no production-ready work. Regression pilots exercise tooling and
preserve the completed-entry count.
Declared audit receipts must exist and match their pins. Browser sign-off needs a
current export/Explorer/harness witness, not a matching story name alone.

## History

### EXPLAINER-2026-001

- Date: 2026-09-29
- Invoked version: initial design before `1.0.0`.
- Source: [scoped workflow request](codex://threads/01a0e024-3705-7a91-9181-d237131801fa).
- Observation: Per-entry acceptance, playback and contact-sheet scripts were copied
  repeatedly; the historical all-entry queue conflicted with a later scope decision.
- Resolution: Centralize mechanical collection, derive selection from scope plus
  live status, retain explicit reviewer acceptance and defer dependencies with reasons.
- Validation: See the workspace's scoped pilot report; packaging alone is not
  evidence of agent behavior or faster production throughput.

### EXPLAINER-2026-002

- Date: 2026-09-29
- Invoked version: `1.0.0` pilot.
- Source: [scoped workflow pilot](codex://threads/01a0e024-3705-7a91-9181-d237131801fa).
- Observation: Independent review reproduced missing source-audit and stale browser
  evidence acceptance gaps before production use.
- Resolution: Require declared audit pins and a browser witness bound to the exact
  batch, export, Explorer and harness; validate coverage and captured image hashes.
- Validation: Twelve focused Python tests, four Node tests and independent targeted
  re-review passed. Two live regression sign-offs preserved original acceptance.
