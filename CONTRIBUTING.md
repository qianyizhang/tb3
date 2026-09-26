# Development

Use [the docs index](docs/README.md) for navigation and
[the workflow](docs/workflow.md) for research commands. Read
[architecture](docs/architecture.md) for component boundaries and the
[repository layout](docs/repository-layout.md) before adding files.
Follow the [coding style](docs/coding-style.md) for contracts, ownership and reuse.
For reader-facing summaries and reports, follow the
[writing guide](docs/writing-style.md).

## Setup

```sh
make hooks
```

Python 3.12 is the local default; CI checks 3.12 and 3.14. Local tooling accepts
uv 0.11.8 or newer; CI pins uv 0.12.15.
`make hooks` runs `uv sync --locked --inexact --group dev` and enables pre-commit
through `.githooks`, refusing to replace another hook directory. `--inexact`
preserves packages outside the lock; shared dependencies follow it. CI uses an
exact sync in a fresh environment.

For frontend development and browser checks, install the declared Node 22.13+
dependencies with `npm ci`, then run `npm run frontend:build` before using
`med present` or `med brief build`. `make presentation-check` builds them for you.
The [frontend guide](presentation/frontend/README.md) describes Vite development,
portable outputs and Python-owned generated type contracts.
Browser setup and the macOS execution boundary are in the
[media guide](presentation/tours/TOOL.md).

## Checks

| Command | Coverage |
| --- | --- |
| `make check` | Git-index artifacts, offline tests, medical records, docs links, types, Ruff, workflow syntax |
| `make pre-commit-check` | All six configured pre-commit checks; no automatic file rewrites |
| `make docs-check` | Maintained Markdown paths, heading anchors and closed code fences |
| `make skills-check` | Canonical skill metadata and portable resources; optional local mirror checks are in the skill lifecycle guide |
| `make type-check` | Strict mypy across the entire source package, including portable adapters |
| `make lint` | Ruff correctness, imports, modern syntax, bugbear, comprehensions and Ruff rules |
| `make format-check` | Check Ruff formatting for `src` and tests without rewriting files |
| `make format` | Apply Ruff formatting to `src` and tests |
| `make js-check` | Script formatting, player state and encoder failure cleanup; no browser |
| `make contracts-check` | Generated TypeScript matches canonical Python presentation types |
| `npm run typecheck` | Contract freshness and strict TypeScript across the interactive frontend |
| `npm run frontend:build` | Checked Vite bundles and source/output fingerprint manifest |
| `make presentation-check` | Portable site navigation, sources, keyboard/mobile behavior; disposable browser |
| `make build-check` | Wheel installation and CLI checks from an unrelated temporary directory |
| `npm run format` | Format maintained JavaScript scripts and checks |

Stage intended files, then run `make check PYTHON=python3.12` with the project
environment active. Otherwise `make check` selects `.venv/bin/python`.
The artifact gate reads the index; unstaged edits do not repair staged failures.

Test behavior with small synthetic inputs. `med check` validates the authored
catalogue; `make contracts-check` validates generated type freshness. Avoid tests
that repeat catalogue labels or counts. Reuse the
[Python assembly fixtures](tests/frontend_fixture.py),
[Vite module loader](tests/frontend_bundle.cjs), and
[disposable-browser harness](scripts/browser.cjs).

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
