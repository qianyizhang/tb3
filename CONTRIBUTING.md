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
| `make docs-check` | Maintained Markdown paths, heading anchors and closed code fences |
| `make type-check` | Strict mypy across the entire source package, including portable adapters |
| `make lint` | Ruff correctness, imports, modern syntax, bugbear, comprehensions and Ruff rules |
| `make format-check` | Check Ruff formatting for `src` and tests without rewriting files |
| `make format` | Apply Ruff formatting to `src` and tests |
| `make js-check` | Script formatting, player state and encoder failure cleanup; no browser |
| `make presentation-check` | Portable site navigation, sources, keyboard/mobile behavior; disposable browser |
| `make build-check` | Wheel installation and CLI checks from an unrelated temporary directory |
| `npm run format` | Format maintained JavaScript scripts and checks |

Stage intended files, then run `make check PYTHON=python3.12` with the project
environment active. Otherwise `make check` selects `.venv/bin/python`.
The artifact gate reads the index; unstaged edits do not repair staged failures.

## Package structure

| Module | Responsibility |
| --- | --- |
| `cli` | Parse arguments, invoke services, print results and set exit status. `build_parser()` can be used without executing a command. |
| `core` | Record validation, relationships, review projection and append-only research events. Existing storage entry points remain exported for callers. |
| `storage` | Workspace path containment, document encoding, SHA-256 and atomic exclusive/replacement writes. |
| `methods` | The `ExperimentMethod` protocol and the landmark/package adapters for prepare, evaluate, replay and view. `method_for()` selects a declared method explicitly. |
| `workflow` | Freeze, execute, collect, qualify and retain provenance. Adapters call its replay service to append observations. |
| `harbor`, `packaging`, `evidence` | Import external results, assemble exports and collect evidence inventories. |
| `presentation`, `task_catalog`, `task_briefs`, `datasets`, `dataset_previews`, `media` | Read and validate owned records, then produce explanations and derived presentation assets. |
| `scoring`, `score_ct`, `score_mri`, `landmarks` | Validate answer contracts, calculate scores and adapt native landmark inputs. |

Add task-specific behavior behind `ExperimentMethod` when another maintained
method actually needs those operations. Keep execution and review writes in the
workflow layer. Scientific record fields stay with their existing validators.

All source functions have checked signatures. `types.Document` represents an
extensible JSON/TOML object; its fields remain dynamic and need runtime validation.
`storage.read_object()` checks object shape before domain validation, while
`storage.read()` supports arbitrary serialized payloads. The `py.typed` marker
ships the annotations to package consumers. Mypy skips only the explicitly named
optional imaging/model dependencies, whose implementations live in provisioned
runtimes; local checks do not validate those libraries or perform inference.

`task_package.py` is also copied into exports as `reproduce.py`, and the LiteMedSAM
adapter runs inside its separate runtime. Keep both standalone modules free of
workbench imports. Their local helpers preserve that portability contract.

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
