# Recovering retired material

[Historical navigation](../docs/archive/README.md) · [Current workbench](../README.md)

The [manifest](manifest.json) records each retired file's `original_path`, exact
SHA-256, `source_commit`, reason and ignored `local_copy`. Most entries come from
`pre-tb3-medical-2026-09-20` at `51f3b1224d2069fe931ac28b06fd2ccf38c497ab`.
Later documentation retirements name their own commit; use the entry's origin.
The original manifest covered 1,791 retired tracked files and six navigation
originals; five obsolete documentation originals were added during the docs audit.

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
