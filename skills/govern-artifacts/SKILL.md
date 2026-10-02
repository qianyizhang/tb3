---
name: govern-artifacts
description: Govern local TB3 explainer, build and review artifacts through bounded inventories, provenance-preserving deduplication, verified recovery and scoped retirement proposals. Use for artifact growth, storage cleanup, retention plans and campaign closeout.
metadata:
  version: 1.0.0
---

# Govern artifacts

Keep each occurrence's task, path, role and history; share identical payload bytes.
A matching hash proves byte identity, not scientific equivalence or permission to
delete. Use the workbench's `med artifacts` tooling rather than ad hoc cleanup.

## Establish scope

Locate `workbench.toml`; read the workspace's `docs/governance.md` and
`docs/artifact-retention.md`. Inspect current ownership and Git status. Start from
explicit user-selected campaigns or measured candidate directories; do not crawl
all raw runs, credentials or environments to find something to remove.

Read [active lessons](references/feedback-ledger.md#active-lessons). Reuse existing
inventories when they answer the question; refresh the candidate files before
acting. Report logical bytes separately from actual allocated/reclaimed storage.

Create a job with `med artifacts init PATH... --id ID --owner OWNER
--source-task SOURCE --output JOB.json`. This is the scaffold: scopes begin active
and unknown. Classify them after checking live writers and references. Keep the
source task, baseline commit/dirty patch, handoffs, data receipts and reconstruction
recipe in the job's provenance/references. Use smaller disjoint scopes when file
roles or retention differ. Never mark a scope closed because its folder is dated.

## Plan and deduplicate

- `med artifacts plan JOB.json --output PLAN.json` hashes a bounded selection and
  reports unique bytes and duplicate logical bytes. Default limits are 20,000 files
  and 10 GB; split by owner/snapshot before deliberately increasing them. Plan files
  are local payloads. Track only a concise job/receipt locator and hash if useful.
- For accepted material, follow ledger → receipt → packet/batch → outputs and
  browser/inspection witnesses, plus source pins/notices. For workers, inspect
  handoffs, patches, unique acquisitions and failed attempts. The tool does not
  infer this dependency closure; unknown references remain unresolved.
- Before packing, classify scopes as closed with a role, retention reason and
  explicit rebuild recipe where applicable. A job describes retention; it does
  not authorize retiring sources. Packing is non-destructive and needs no extra
  confirmation when already within the user's authorized task.
- `med artifacts pack PLAN.json --store STORE --output RECEIPT.json` stores one
  compressed object per exact SHA-256 and retains a portable occurrence manifest.
  Separate stores when access or licensing boundaries differ. The manifest itself
  can contain sensitive local paths; keep it under the same access boundary.
- `med artifacts verify PLAN.json --store STORE` fully checks the objects.
  `med artifacts restore PLAN.json --store STORE --output FRESH_DIRECTORY` proves
  restoration. Verify a representative real selection and the original path/hash
  relationships before recommending retirement. Pin the manifest digest from the
  receipt; editing the manifest changes its identity.

Deduplication preserves every occurrence. Failed/rejected attempts keep their own
records even if their bytes equal an accepted build. Do not replace historical
HTML with a new renderer output, transcode evidence, link writable files together,
or use symlinks as a shortcut around receipt readers. Native source and private
reference roles remain distinct even when payload bytes match.

## Closeout and retirement

The current scaffold has no delete, prune or automatic garbage-collection command.
First deliver a reviewable scope, manifest hash, verified object store, restore
result, unresolved references and measured savings. A same-disk pack is a recovery
copy; independent backup and availability are separate claims. Source mutation,
symlinks, unknown file types, corrupt objects or capacity limits stop the affected
operation; diagnose rather than bypass the check.

Retire existing live copies only when the user's scope already authorizes it and
recovery/dependency checks are complete. If authorization is absent, ask once for
that concrete scope. Follow existing repository governance. Preserve old locators
with an append-only archive map and a tested materialization route; no age-based
purge, receipt rewriting or raw-run deletion.

For new production, recommend selected asset exports, one catalogue per exact
source/build identity, focused worker patches plus a recoverable baseline, and
family/batch byte budgets. Keep the accepted/rejected history while reducing
repeated payloads. Do not launch trials, regenerate historical evidence or publish
as part of governance work.

Consider a feedback entry only for a material reusable lesson, using the version
actually invoked. Routine success needs no entry.
