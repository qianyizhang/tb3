# Recovering retired material

[Historical navigation](../docs/archive/README.md) · [Current workbench](../README.md)

The [manifest](manifest.json) records each retired file's `original_path`, exact
SHA-256, `source_commit`, reason and ignored `local_copy`. Most entries come from
`pre-tb3-medical-2026-09-20` at `51f3b1224d2069fe931ac28b06fd2ccf38c497ab`.
Later documentation retirements name their own commit; use the entry's origin.
The original manifest covered 1,791 retired tracked files and six navigation
originals. Documentation cleanup added five obsolete guide originals and five
medical session-report originals. The latter preserve old citations; maintained
narratives now live in their [owning groups](../docs/archive/README.md#group-research-history).

Retired scope includes nonmedical probe families, the old catalog, original
assignment and interview site, and superseded guidance. Retained medical evidence
stays at its original paths. Restoring files does not execute them or establish
that their historical environments can be reproduced.

## Inspect or recover with Git

The former `scripts/med restore-legacy` command was removed with the old interface.
Use ordinary Git from this checkout. For example, inspect the original requirements:

```sh
git show f5b2ced2d85e13e325bf535d444b574fedd9dd39:docs/requirements.md
```

For an exact file copy, create a fresh temporary directory and compare its digest
with the matching manifest entry:

```sh
history_dir=$(mktemp -d /tmp/tb3-history.XXXXXX)
git show f5b2ced2d85e13e325bf535d444b574fedd9dd39:docs/requirements.md > "$history_dir/requirements.md"
shasum -a 256 "$history_dir/requirements.md"
```

To inspect an earlier publication with its original relative paths intact:

```sh
history_dir=$(mktemp -d /tmp/tb3-publication.XXXXXX)
git archive pre-tb3-medical-2026-09-20 site | tar -x -C "$history_dir"
```

Use the original `source_commit` and path for other scopes. Verify selected file
hashes against the manifest before relying on the recovered bytes. Do not overlay
recovered files on the active checkout or run old authoring scripts as a repair.

## When history or local artifacts are missing

A shallow clone may not contain the named commits. Obtain that history from its
owner or use the recorded Git bundle in a separate recovery repository. The
pre-pivot bundle is `.cache/migration/pre-tb3-medical.bundle`; it contains tracked
history only, and does not include later native-workbench/doc commits. An entry's
ignored `local_copy`, if available, is another exact-byte recovery source; verify
its recorded hash. [Retired native interfaces](../docs/migration/retired-interfaces.json)
also retain Git locators.

These same-disk copies are recovery conveniences, not independently verified
backup. Ignored scans, raw runs and environments need their own recorded recovery
sources. No history rewrite, raw-evidence deletion or remote publication is implied.

## Documentation cleanup — 2026-09-22

The manifest retains nine originals from
`d85f388deb9a3f993b9c3e9fc47d71e3f81458a4`: seven method indexes before separating
their dated baselines, the repository survey before relocation to the external-task collection,
and the report figure manifest now retained at [report-figure.json](report-figure.json).
Each entry names its current location, original hash, exact local copy and bundle.

The self-contained Git bundle `.cache/docs-cleanup-20260922/pre-cleanup.bundle`
was verified and fetched into an empty temporary repository; all nine recovered
files matched their original hashes. This is local recovery verification, not an
independent backup or proof that raw images and runtime artifacts are recoverable.
The [cleanup receipt](../docs/evidence/docs-artifacts-cleanup-20260922.json) records
the bundle fingerprint and preserved scope. Historical receipts retain their
original paths as provenance; use the manifest to recover those originals.

## Documentation pruning — 2026-09-22

Completed migration reports and inventories, the root ledger/brainstorm/audit,
the trace-audit viewer, old operations and editorial brief are indexed by their
original paths at `8a07094da83d74012030b57d8c7df38819b9a29d`. The original full
editions of the retained workbench plan and editorial guide are indexed too.
Use each manifest entry's Git locator to inspect or recover it in a fresh directory.

The verified `.cache/docs-prune-20260922/pre-prune.bundle` contains that history.
All 24 proposed tracked retirements were restored and hash-checked in an empty
recovery repository. The MRI replay receipt remains at its original path because
the frozen BR-040 protocol cites it; the other 23 files were retired. The file bundle `.cache/docs-prune-20260922/retired-docs.tar.gz` also
preserves seven discarded, uncommitted baseline-page projections; all 31 files
were extracted and verified. Their underlying scientific verification remains
in the original [backfill receipt](../docs/evidence/experiment-support-backfill-20260921.json).
The [pruning receipt](../docs/evidence/docs-artifacts-prune-20260922.json) records
scope and recovery fingerprints. These are same-disk recovery copies, not an
independent backup. Historical citation strings are preserved in frozen sources.

## Discussion ownership — 2026-09-22

The maintained collection moved from `discussions/medical-agent-repository-survey/`
to `presentation/external-tasks/`, preserving filenames. Six stable discussion
records moved from `discussions/*.json` to `discussions/records/*.json`. Historical
receipts keep their original citation strings. Recover the old paths from
`c9a7953` using `.cache/docs-prune-20260922/pre-discussions.bundle`; the
[pruning receipt](../docs/evidence/docs-artifacts-prune-20260922.json) records the
full commit, bundle fingerprint and verified relocation scope.

The completed support-backfill narrative is now ignored locally and has an exact
entry in the recovery manifest. [Discussions](../discussions/README.md) documents
the default ignore policy and the few retained decision histories.
