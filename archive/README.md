# Historical sources and recovery

Current work uses the [workbench guides](../docs/README.md). Historical status,
commands and proposed next actions describe their capture date. Restoring a
source does not authorize executing it or establish reproducibility.

## Retained research

Group READMEs link their dated closeouts and trace accounts under `history/`.
Current findings and presentation stay separate from those sources.

| Source | Where to read it |
| --- | --- |
| Anatomy, registration, cardiac and landmark session histories | [Anatomy](../groups/anatomy-audit/README.md), [registration](../groups/registration/README.md), [cardiac motion](../groups/cardiac-motion/README.md), [landmarks](../groups/anatomical-landmarks/README.md) |
| Original protocols, outcomes and receipts | [Round register](../docs/research-rounds.md); the owning experiments cite files in `docs/research-rounds/` and `docs/evidence/`. BR numbers are historical provenance, not unique experiment IDs. |
| Dated support and replay baseline | [2026-09-21 receipt](../docs/evidence/experiment-support-backfill-20260921.json); current operations are in [reproduction](../docs/reproduce.md). |
| External-task source research | [Repository survey](../presentation/external-tasks/sources/repository-survey-2026-09-20.md) |
| Retired figure attribution and hashes | [Figure provenance](report-figure.json) |
| Native migration evidence | [MRI replay receipt](../docs/migration/recovery-check.json) and [retired interfaces](../docs/migration/retired-interfaces.json) |

Retained protocols and receipts keep their original bytes. Append corrections or
scoped reviews through the owning experiment. Old `site/`, `site_med/` and `runs/`
links may require retired sources or local artifacts; do not regenerate evidence
to repair them. Build the current presentation with `uv run med present --serve`.

## Recover retired files

The [manifest](manifest.json) records each original path, source commit, SHA-256,
reason and ignored local copy. It covers the closed interview investigation,
retired nonmedical probes, superseded guides and completed design proposals.
Use the entry's own commit: later retirements are not in the pre-pivot snapshot.

Inspect with `git show SOURCE_COMMIT:ORIGINAL_PATH`. To restore an example into a
fresh directory, then compare its digest with the manifest:

```sh
history_dir=$(mktemp -d /tmp/tb3-history.XXXXXX)
git show f5b2ced2d85e13e325bf535d444b574fedd9dd39:docs/requirements.md > "$history_dir/requirements.md"
shasum -a 256 "$history_dir/requirements.md"
```

Use `git archive SOURCE_COMMIT PATH | tar -x -C "$history_dir"` when original
relative paths matter. Never overlay recovery onto the active checkout or import
old authoring modules; some mutate artifacts.

If a shallow clone lacks the commit, fetch the entry's verified Git bundle into
a separate repository. An available `local_copy` is another exact-byte source;
check its hash before use. Recovery records for earlier maintenance remain in
the [cleanup receipt](../docs/evidence/docs-artifacts-cleanup-20260922.json) and
[pruning receipt](../docs/evidence/docs-artifacts-prune-20260922.json).

The 2026-09-26 retirement originals were restored from their bundle into an empty
repository and compared byte for byte. The [quality record](../discussions/records/source-package-quality.json)
records that scope. These same-disk bundles are recovery conveniences, not
independent backups. Raw runs, scans and environments need their own recorded
recovery sources. See [governance](../docs/governance.md) for retention.
