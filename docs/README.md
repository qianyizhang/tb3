# Documentation

This is a medical agent capability research workbench. Useful outcomes include
successes, qualified partial results, source research and visual explanations.
Finding submission candidates is an optional later step, not the research goal.

## Current guides

| Need | Start here |
| --- | --- |
| Set up, find work, capture an idea, author/run a study, collect and review results | [Daily workflow](workflow.md) |
| Design a useful medical question, curate references and interpret evidence | [Research design](research-design.md) |
| Understand ownership, preserved evidence and what belongs in Git | [Governance](governance.md) |
| Restore selected inputs, replay saved outputs, build views and media | [Reproduction and presentation](reproduce.md) |
| Explain an internal or external task and build the Task Explorer | [Task Brief rulebook](../presentation/task-explorer/RULEBOOK.md) |
| Interpret badges, assessments and the attention queue | [Status vocabulary](status-vocabulary.md) |
| Export a research draft or hand work to a submission owner | [Exports and submission](submission.md) |
| Find earlier results or recover retired material | [Historical records](archive/README.md) |
| Understand the pivot, accepted decisions and completed cutover | [Migration record](migration/README.md) |

[Contribution rules](../CONTRIBUTING.md) cover development checks. The installed
`med` command is the supported interface; `med --help` and `med COMMAND --help`
describe its arguments. The executable status definitions live in
[vocabulary.json](../src/tb3_medical/vocabulary.json).

## Where information belongs

| Location | Purpose |
| --- | --- |
| `groups/<group>/` | Current research: question, ideas and decisions, methods, experiments, findings and presentation. Start with its README and AGENTS.md. |
| `groups/<group>/history/` | Canonical home for dated session closeouts, cross-experiment retrospectives and trace walkthroughs; linked from the group README. |
| `datasets/`, `discussions/` | Shared source discovery and discussion provenance; exact inputs and solver visibility belong to the experiment. |
| `src/tb3_medical/`, `tests/`, `configs/` | Common implementation, regressions and artifact policy. |
| `presentation/` | Shared read-only index and media renderer; groups own their scientific stories. |
| `exports/recipes/`, `exports/records/` | Selected-input recipes and export lineage. Generated packages have a fresh destination. |
| `docs/` | Shared current guides plus clearly indexed historical records. |
| `probes/`, `docs/research-rounds/`, `docs/evidence/` | Retained sources, protocols and receipts at their original paths. They are not a second authoring workflow. |
| `archive/` | Hashes and Git recovery locators for retired material. |
| `.local/`, `runs/`, `jobs/`, `.cache/`, `.venv*/` | Local outputs, inputs, environments and caches, outside tracked source. |

Find medical work through the [seven groups](../README.md), not a new global
round or candidate queue. New shared guidance belongs in an existing guide;
group-specific explanations belong with the group. Put completed session narratives
and retrospectives in `groups/<group>/history/<scope>-<topic>.md`, not loose in
`docs/`. Record implementation decisions in the migration history only when they concern that migration. Keep dated source
records intact and link to them instead of copying their verdicts into another index.
