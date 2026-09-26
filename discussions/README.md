# Discussions

Draft notes, reports, downloads, previews and generated artifacts stay local and
are ignored by default, including nested directories. Do not force-add them.

The exact exceptions in [.gitignore](.gitignore) retain compact records with
stable IDs, source-task links, actor-attributed decisions and reopening conditions.
Retain a narrative only when it adds context that current guides and records do
not cover. Move maintained product content to its owner.

The workbench discovers discussion metadata only in `records/*.json`. Keep scratch
JSON outside that directory. A new retained record needs its own ignore exception.

Completed proposals and implementation reports are recoverable through the
[archive](../archive/README.md). Their decision records remain here; current
guidance lives in the [Task Brief rulebook](../presentation/task-explorer/RULEBOOK.md),
[taxonomy](../docs/task-taxonomy.md) and [workflow](../docs/workflow.md).
