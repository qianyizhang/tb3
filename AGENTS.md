# Repository work

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/governance.md](docs/governance.md)
for artifact ownership and checks. `docs/requirements.md` owns final submission
requirements; repository hygiene does not certify a benchmark task.

- Inspect Git status before editing or staging. Concurrent experiment tasks may
  own probe sources, freezes, catalog imports, and ledgers. Stage explicit paths
  or hunks; preserve their unfinished changes.
- Preserve historical evidence and task snapshots. Do not rewrite freezes to
  match today's tree, classify infrastructure errors as model failures, or
  replace authored reviews with generated catalog data.
- Keep raw runs, credentials, environments, compiler outputs, and reports local.
  Retain source fixtures and licenses required by Docker/verifier inputs.
- Run `make check` with Python 3.12 before committing changes to workshop tooling.
  The artifact gate reads the Git index: stage your intended changes first.
- Use focused Conventional Commits. Do not launch trials, install Harbor,
  publish artifacts, or delete evidence as a side effect of hygiene work.
