# Working on tb3-medical

Use Python 3.12 and `uv sync --locked`, then `make check`. The installed `med`
command is the supported interface. Start with [the daily workflow](docs/workflow.md)
and [artifact ownership](docs/governance.md).

Inspect Git status and concurrent task ownership before editing. Stage explicit
paths and use focused Conventional Commits. `make check` includes the staged
artifact gate, offline regressions, metadata/story checks and formatting. It does
not run models, Docker, media rendering or whole-dataset integrity scans. Another
task's dirty experiment must not be staged to make your checks pass.

Author compact experiment TOML plus scientific Markdown; generated receipts carry
execution details. Use normal package imports. No import-path mutation, legacy
fallback reader, machine-cache dependency or migration command belongs in daily
usage. Optional imaging and media dependencies have their own declared setup.

Diagnostics may run before controls. Claims require scoped assessment; current
submission qualification is separately owned. Preserve historical scores and
frozen bytes. `make hooks` installs the staged artifact gate without overwriting
another hook directory. The [accepted design](docs/migration/native-workbench-plan.md)
records the minimal validation boundary.
