# Feedback ledger

## Active lessons

- Occurrence identity and byte identity are separate. Preserve original paths,
  roles and attempts even when payloads share one object.
- Direct acceptance references are a protected minimum, not a deletion allowlist.
- Whole-campaign inventories can themselves become bulky; use bounded scopes and
  concise summaries. Keep manifests and object payloads local.

## History

### ARTIFACT-2026-001

- Date: 2026-10-02
- Invoked version: initial design before `1.0.0`.
- Source: [governance and scaffold request](codex://threads/01a0fced-0f0d-75a0-b286-92360438beaa).
- Observation: The local review measured 162.05 GB of explainer artifacts,
  including 66.82 GB of latest-campaign worker snapshots and a verified 670 MB
  duplicate HTML sample. These are dated observations, not live totals.
- Resolution: Explicit bounded retention jobs, immutable occurrence manifests,
  compressed objects keyed by SHA-256, full verification and fresh restoration;
  source retirement remains separately scoped.
- Validation: Behavioral recovery/corruption/concurrency tests and the retained
  real-file plan are recorded by the implementation task. No historical evidence
  deletion or independent-backup claim follows from packaging validation.
