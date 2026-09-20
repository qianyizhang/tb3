# Working on tb3-medical

Start with [the documentation index](docs/README.md). Use Python 3.12 and
`uv sync --locked`, then `make check`. The installed `med` command is the supported
interface. The [daily workflow](docs/workflow.md) covers research operations;
[governance](docs/governance.md) defines artifact ownership and retention.

Inspect Git status and concurrent task ownership before editing. Stage explicit
paths and use focused Conventional Commits. `make check` includes the staged
artifact gate, offline regressions, metadata/story checks and formatting. It does
not run models, Docker, media rendering or whole-dataset integrity scans. Another
task's dirty experiment must not be staged to make your checks pass.

Author compact experiment TOML plus scientific Markdown; generated receipts carry
execution details. Use normal package imports. No import-path mutation, legacy
fallback reader, machine-cache dependency or migration command belongs in daily
usage. Optional imaging and media dependencies have their own declared setup in
[reproduction](docs/reproduce.md) and the linked media guide. Keep shared guidance
in the current docs hub and group-specific explanations with their group. Dated
session closeouts and retrospectives live in `groups/<group>/history/`, linked from
the group README and shared historical index; do not create another global research queue.

Diagnostics may run before controls. Claims require scoped assessment; current
submission qualification is separately owned. Preserve historical scores and
frozen bytes. `make hooks` installs the staged artifact gate without overwriting
another hook directory. The [accepted design](docs/migration/native-workbench-plan.md)
records the minimal validation boundary. With the project environment active,
`make check PYTHON=python3.12` uses the installed package and Python 3.12;
`make check` otherwise selects `.venv/bin/python` when present.

For presentation changes, also run `make presentation-check` using the declared
existing Node/Playwright environment. It builds a portable site and exercises
navigation, sources, keyboard/mobile behavior and deferred tour loads without
raw scans or media generation. Set `PLAYWRIGHT_CHANNEL=chromium` for the bundled
browser; installed Chrome is the local default. A separate changed-input CI job
runs this command. See [reproduction](docs/reproduce.md) for its coverage boundary.
