# Repository work

## Candidate research scope

- Stay away from security tasks. Do not pursue vulnerability discovery,
  exploitation, authentication/authorization, sandbox escape or protocol attacks;
  do not resume the stopped security research. Preserve its historical evidence.
- Seek **hard but less complex, short-horizon tasks**: one conceptual crux,
  a small deliverable and fast, independent verification. Diversify field and
  task type. Do not manufacture difficulty through long workflows, setup cost,
  arbitrary restrictions or shorter reasoning time.
- Start new selection from **benchmark-backed failures**, not just plausible
  difficult bugs. `docs/research-benchmark-backed.md` owns the current shortlist;
  the bounded round in `docs/research-short-horizon.md` is complete. Inspect
  task-level results, normal completion, verifier failures and task digests.
  Prefer a compact crux already missed with ample reasoning time; distinguish
  published external results from this workshop's local trial ledger.
  Published tasks are calibration references, not original submissions.
  A source bug, oracle fault, agent crash or timeout is not a genuine Terra
  failure. Final submission gates remain separately owned by requirements.md.

## Artifact ownership and checks

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
