# Discussions

Draft notes, reports, downloads, previews and generated artifacts stay local and
are ignored by default, including nested directories. Do not force-add them.

The exact exceptions in [.gitignore](.gitignore) retain three accepted design
histories and six compact records with stable IDs, source-task links and reopening
conditions. Add an exception only when a durable decision or dependency needs it;
move maintained product content to its owner instead.

The workbench discovers discussion metadata only in `records/*.json`. Keep scratch
JSON outside that directory. A new retained record needs its own ignore exception.

- [Task Brief decisions](task-brief-format.md) and [current rulebook](../presentation/task-explorer/RULEBOOK.md).
- [Task taxonomy decisions](task-taxonomy-refactor-2026-09-22.md).
- [Workbench refinement decisions](workbench-refinement-sweep-2026-09-21.md).
- [External task collection](../presentation/external-tasks/catalog.json): maintained briefs and required source receipts.

The completed support-backfill narrative remains local; its original Git bytes are
indexed in [the recovery manifest](../archive/manifest.json). The concise retained
record points to the canonical verification receipt and current methods.
