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


### ARTIFACT-2026-002

- Date: 2026-10-02
- Invoked version: `1.0.0`.
- Source: [authorized consolidation](codex://threads/01a0fced-0f0d-75a0-b286-92360438beaa).
- Observation: 47 tracked source records reference worker files; whole-folder
  retirement would break provenance. Snapshot symlinks also cross environment boundaries.
- Resolution in `1.1.0`: preserve explicit referenced paths and symlinks through
  reasoned exclusions. Require exact plan, verified stored manifest and complete
  restore/source comparisons for explicit retirement, with durable intent and
  completion records. Capture unsupported filesystem metadata separately.


### ARTIFACT-2026-003

- Date (UTC): 2026-10-02.
- Invoked version: `1.1.0`.
- Source: [referenced workspace consolidation](codex://threads/01a0fced-0f0d-75a0-b286-92360438beaa).
- Observation: Root references in historical apply/rebuild reports kept 47 copied
  workspaces (272,013 files) live. Most files were repeated repository contents.
- Resolution in `1.1.1`: classify root references, preserve report-listed files and
  complete task asset bundles, and archive the surrounding source with exact
  recovery. Keep unknown outputs and explicitly retain missing-baseline notices.
  Share metadata sidecars and use a verified incremental source bundle chain.
- Validation: The follow-up recovery record pins all 47 restored batches, the
  retained-consumer comparison and the measured file/storage reduction.
