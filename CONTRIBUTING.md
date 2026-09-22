# Development

Use [the docs index](docs/README.md) for navigation and
[the workflow](docs/workflow.md) for research commands.

## Setup

```sh
uv sync --locked --inexact --group dev
make hooks
```

Python 3.12 is the local default; CI checks 3.12 and 3.14. Local tooling accepts
uv 0.11.8 or newer; CI pins uv 0.12.15.
`--inexact` preserves packages outside the locked dependency graph; shared
dependencies still follow the lock. CI uses an exact sync in a fresh environment.
`make hooks` enables pre-commit through the tracked
`.githooks` wrapper and refuses to replace another hook directory.

For browser checks, install the declared Node 22+ dependencies with `npm ci`.
Browser setup and the macOS execution boundary are in the
[media guide](presentation/tours/TOOL.md).

## Checks

| Command | Coverage |
| --- | --- |
| `make check` | Git-index artifacts, offline tests, medical records, docs links, types, Ruff, workflow syntax |
| `make pre-commit-check` | All six configured pre-commit checks; no automatic file rewrites |
| `make docs-check` | Maintained Markdown paths and heading anchors |
| `make type-check` | Strict typing for link validation and shared CT/MRI scoring |
| `make js-check` | Script formatting, player state and encoder failure cleanup; no browser |
| `make presentation-check` | Portable site navigation, sources, keyboard/mobile behavior; disposable browser |
| `make build-check` | Wheel installation and CLI checks from an unrelated temporary directory |
| `npm run format` | Format maintained JavaScript scripts and checks |

Stage intended files, then run `make check PYTHON=python3.12` with the project
environment active. Otherwise `make check` selects `.venv/bin/python`.
The artifact gate reads the index; unstaged edits do not repair staged failures.

## Working rules

- Inspect Git status and task ownership first. Preserve concurrent work and stage
  explicit paths in focused Conventional Commits.
- Keep shared code in `src/tb3_medical/` and `presentation/`; use normal package
  imports. Do not add import-path mutations, compatibility readers or cache lookups.
- Keep experiment TOML compact and scientific explanations with the owning group.
  Dated closeouts belong in `groups/<group>/history/`; link them from the group.
- Preserve frozen bytes, original outcomes and evidence hashes. Append scoped
  observations/reviews when interpretation changes.
- Maintenance does not launch trials, install medical runtimes, render media or
  publish. Raw runs, credentials, environments and generated assets stay local.
- Diagnostics may precede controls; claims require scoped assessment.
  [Submission](docs/submission.md) has separate ownership.

[Governance](docs/governance.md) defines retention.
[Reproduction](docs/reproduce.md) defines recovery, replay and export evidence.
