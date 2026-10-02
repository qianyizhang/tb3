# Efficient artifact retention

Preserve provenance for every occurrence; store identical bytes once. A task's
identity, role, original location and review history remain separate from the
content hash of its payload. The [storage review](explainer-framework.md#artifact-retention-review--2026-10-02)
identified repeated worker snapshots and HTML as the main growth drivers.

This guide defines the workflow implemented by `med artifacts` and the
[govern-artifacts skill](../skills/govern-artifacts/SKILL.md). General ownership and
retirement boundaries remain in [governance](governance.md).

## Retention decisions

| Material | Default treatment | Required provenance |
| --- | --- | --- |
| Active work | Keep working paths available | Owner, source task, current writer; no concurrent packing |
| Accepted evidence and unique acquired sources | Keep exact bytes available or in a verified archive with restoration | Original receipt/source hashes, roles, licenses, geometry, references and access limits |
| Failed or rejected attempts | Retain observations and exact evidence needed to explain the failure | Attempt identity, outcome, logs, decisive captures and superseding links |
| Rebuildable builds and extracted workspaces | Prefer deduplicated recovery; retire redundant copies only after scoped review | Baseline commit, dirty patch, lockfiles/tool identity, inputs and tested rebuild/restore route |
| Unclassified files | Hold for review | Owner, consumers and uniqueness still unresolved |

`keep`, `archive`, `rebuild` and `unknown` are retention intentions in a job;
`active`/`closed` describe writer ownership. These fields do not change original
scientific acceptance, promote a task, or authorize deletion. A rebuild recipe
alone is not proof that historical byte-identical recovery will work.

## Shared bytes, separate occurrences

A retention job records owner, source task, provenance links and disjoint scopes.
Each scope supplies role, state, retention intention, reason, references and an
optional rebuild recipe. A plan snapshots the entire job and its hash, timestamp,
Git commit if available, and each regular file's original workspace-relative path,
SHA-256, byte count, mode and modification time. Dirty source bytes are captured
by file hashes; a Git commit by itself does not describe uncommitted work.

The local object store uses:

```text
store.json                      Store format marker
objects/ab/<sha256>.gz           One compressed exact-byte object
manifests/<manifest-sha256>.json Portable occurrence/provenance manifest
```

Objects are verified after compression and reused only after checking their
uncompressed digest and length. Publication is exclusive; receipts never replace
existing receipts. Repeated occurrences can have different modes, timestamps,
roles and review outcomes. Restoration writes separate regular files with their
original contents, permissions and modification times; it does not create shared
writable hard links. Store objects are read-only against accidental edits, not a
security or immutability guarantee against the filesystem owner.

Use a shared store within one access/licensing boundary to deduplicate across
jobs. Do not merge private and public publication stores merely because bytes
match. Source notices and case/reference roles remain occurrence metadata.

## CLI scaffold

Run from the workspace with its existing environment. All outputs must be fresh;
store and output locations must be separate from source scopes. An external
store can be supplied as an absolute path, subject to filesystem permissions.

```sh
uv run --no-sync med artifacts init .local/campaign/worker-finished \
  --id campaign-worker-retention --owner assistant \
  --source-task codex://threads/THREAD_ID \
  --output .local/retention/job.json
```

Edit the generated job after ownership/reference review. Its defaults are
`active`, `unknown` role and retention; planning works immediately but packing
requires closed, classified scopes with reasons. If a folder mixes roles, narrow
the disjoint scopes. Add evidence and handoff paths to `references`; add baseline
commit, dirty patch and source acquisition locators to `provenance`. These are
contextual references, **not automatically followed or copied**; include required
recovery files explicitly in the scopes.

```sh
uv run --no-sync med artifacts plan .local/retention/job.json \
  --output .local/retention/plan.json
uv run --no-sync med artifacts pack .local/retention/plan.json \
  --store .local/artifact-store --output .local/retention/pack.json
uv run --no-sync med artifacts verify .local/retention/plan.json \
  --store .local/artifact-store
uv run --no-sync med artifacts restore .local/retention/plan.json \
  --store .local/artifact-store --output .local/retention/recovery
```

The plan reports file count, unique objects, logical bytes and duplicate logical
bytes. The pack receipt pins the exact portable manifest and reports added and
referenced compressed bytes. Keep its manifest hash outside the object store in a
concise retained record when needed. Later recovery can use the stored manifest
without the original job, source paths or checkout bytes; `verify` and `restore`
do not require a workbench checkout. `verify` checks payloads
against the supplied manifest; compare that manifest's reported hash to the
retained receipt to establish the provenance chain.

Default limits are **20,000 files / 10 GB** per job, checked before hashing.
Deliberate job edits can raise them, but scope by owner or snapshot first. A plan
hashes all selected files for provenance. Packing rehashes sources once, checks
membership and metadata again at completion, and verifies compressed objects.
It does not repeatedly audit unrelated raw runs. Summaries stay small; potentially
large plans stay local. Do not track whole inventories of every intermediate file.

## Verification and retirement

The tool aborts on changed source content/membership, unknown or active packing
scopes, escaping paths, symlinks, special files, unsupported permissions, corrupt
objects or non-fresh outputs. Failed packing can leave verified unreferenced
objects; it does not publish a successful pack receipt. Failed restoration keeps
an `.artifact-restore-incomplete` marker and its partial destination for diagnosis.
There is no automatic garbage collection or age-based prune. Explicit retirement
requires a pinned plan, a verified store and a complete restored copy.

Before retiring an existing live copy:

1. Identify the exact closed scope and consumer references, including source
   receipts, failed attempts, handoffs and dirty changes. The old 154-entry
   closeout inventory is a useful seed; it is not a complete retention graph.
2. Pack, verify and restore. Compare original occurrence hashes, not merely file
   counts. If independent backup is required, copy the store/manifest to the
   designated independent destination and verify there. A same-disk pack does
   not establish independent backup or reclaim any source storage.
3. Retain a compact archive map with original path, manifest/store locator,
   manifest hash, reason, actual actor/source and recovery-verification record.
   Legacy acceptance readers still expect their original paths; materialize exact
   bytes there through an explicitly reviewed recovery operation before use.
4. Retire only the enumerated scope already authorized by the user. Unknown
   dependencies, active writers or missing recovery evidence keep it in place.
   Never rewrite old acceptance hashes to point at newer renders.

Current recovery covers regular file contents, basic modes and modification times.
It does not preserve symlinks, empty directories, hard-link topology, ownership,
ACLs, extended attributes or sparse-file allocation. Directory permissions are
created using the current environment. This limits what can be retired from a
workspace snapshot; preserve unsupported metadata separately or use an appropriate
verified archive. Explicit retirement removes only the enumerated regular files;
parent directories and excluded paths remain in place.

## Prevent the next accumulation

- **Production:** one immutable catalogue build per identical source/build hash;
  selected asset exports for individual tasks; fresh builds when those pins change.
- **Workers:** recoverable baseline plus a focused patch and unique inputs; reuse
  shared objects across jobs instead of repeated full `baseline.tar` and extracted
  snapshots. Keep each worker's handoff and failures independently addressable.
- **Closeout:** pack completed scopes once, link a compact manifest/receipt, and
  measure duplicate bytes and added stored bytes. Review unresolved references.
- **Budgets:** report per-family and per-batch sizes using existing packaging
  receipts. Establish budgets from representative native-image/spatial pilots;
  a symbolic restoration export's 319 KB is not a universal medical-asset budget.
- **Deletion:** no time-based purge or automatic object GC. A future GC requires a
  complete manifest-root set, a grace period, recovery validation and explicit
  retirement authority. Absence from one ledger does not make an object disposable.

Packing is an additive step. The current implementation provides exact-file
deduplication and gzip compression; it does not deduplicate substrings in changing
HTML bundles, automatically migrate receipt readers, or reduce existing storage
until a separately reviewed retirement is performed.


## Authorized migration

`med artifacts retire` applies an already authorized, exact archive scope after
verification. Scope `exclusions` map normalized workspace-relative descendants
to preservation reasons. They must be enumerated; there are no ignore globs.
Use exclusions to retain live references and environment symlinks. Excluded paths
are not archived, so include their separate recovery needs in the record.

```sh
uv run --no-sync med artifacts retire PLAN.json --store STORE \
  --recovery FRESH_RESTORED_DIRECTORY --plan-sha256 EXACT_PLAN_SHA256 \
  --authorization codex://threads/AUTHORIZING_TASK --output NEW_RETIREMENT_RECORD
```

The command rejects tracked files and raw run/input/freeze roots. It verifies the
stored occurrence manifest, every stored object, all restored bytes/modes/mtimes,
and all source fingerprints before proceeding. The recovery, store and record
must be separate from source scopes. Its durable `intent.json` pins the full
manifest before removal; `events.jsonl` records progress in batches of 128, and
`result.json` exists only on completion. After interruption, reconcile the pinned
manifest against live path existence/hashes; absence of a buffered event does not
prove that a source still exists. Never rerun a changed or partial plan blindly.

Keep the compact retirement result and manifest/store locator in the archive map.
Temporary restored copies made solely for verification can be removed after a
successful retirement, preserving their verification receipt and the object store.
This does not confer independent-backup status.


## Applied migration

The [2026-10-02 recovery record](../archive/artifact-migration-20261002.json)
documents the first authorized migration: closed baseline archives, copied worker
source workspaces and superseded HTML. It pins the local occurrence index,
selection, source bundle and retained-file comparison. Per-batch metadata and
full restoration preceded source retirement; raw evidence, acquired inputs,
environments and accepted/live references remain in place. Historical review and
additive-scaffold records remain as dated observations.


## Directory references and copied workspaces

A directory named as a historical apply target or rebuild working directory
does not by itself define a live dependency on every file below it. Inspect the
actual report fields and consumers. Keep explicit receipt/report files, complete
task asset bundles needed by relative manifest paths, local evidence, environment
links and unclassified outputs. Use recorded Git trees to identify copied source
paths; preserve exact bytes through occurrence manifests even when the original
baseline is unknown. Record that gap instead of inventing a commit.

The [47-workspace follow-up](../archive/referenced-workspace-consolidation-20261002.json)
applies this rule. Historical receipts remain unchanged; source needed by an old
rebuild command must first be materialized from its archive. Track only a concise
recovery record; share metadata sidecars and use incremental Git bundles against
an already verified base when that avoids redundant provenance copies.
