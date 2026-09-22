# Documentation

This is a medical agent capability research workbench. Useful outcomes include
successes, qualified partial results, source research and visual explanations.
Finding submission candidates is an optional later step, not the research goal.

## Use the workbench

| Need | Start here |
| --- | --- |
| Set up, find work, capture an idea, author/run a study, collect and review results | [Daily workflow](workflow.md) |
| Design a useful medical question, curate references and interpret evidence | [Research design](research-design.md) |
| Track experiment support/backfill, restore inputs, replay outputs, build views and media | [Reproduction and presentation](reproduce.md) |
| Explain an internal or external task and build the Task Explorer | [Task Brief rulebook](../presentation/task-explorer/RULEBOOK.md) |
| Browse by task capability, distinguish conditions and separate supporting research | [Task taxonomy](task-taxonomy.md) |
| Explain results, traces, failures or multi-run comparisons from pinned evidence | [Evidence explanation workflow](evidence-explanations.md) |
| Export a research draft or hand work to a submission owner | [Exports and submission](submission.md) |

## Reference

| Need | Start here |
| --- | --- |
| Understand ownership, preserved evidence and what belongs in Git | [Governance](governance.md) |
| Choose and construct concise conceptual, quantitative and source-derived visuals | [Visual explanation rulebook](visual-explanations.md) |
| Add LiteMedSAM / a SAM segmentation tool to an experiment | [Segmentation tool rulebook](segmentation-tools.md) |
| Interpret badges, assessments and the attention queue | [Status vocabulary](status-vocabulary.md) |

[Contribution rules](../CONTRIBUTING.md) cover development checks. The installed
`med` command is the supported interface; `med --help` and `med COMMAND --help`
describe its arguments. The executable status definitions live in
[vocabulary.json](../src/tb3_medical/vocabulary.json). Maintained-link scope lives
in [doc-links.json](../configs/doc-links.json). Checks cover local links and closed
code fences in maintained guides, including recipe README/acquisition pages;
preserved historical evidence is
excluded explicitly rather than rewritten to match the current tree.

## Historical records

[Historical navigation](archive/README.md) leads to dated research, verification
baselines and retired material. The [migration record](migration/README.md)
preserves the pivot decisions and completed cutover; the
[recovery guide](../archive/README.md) explains how to restore exact originals.

## Where information belongs

| Location | Purpose |
| --- | --- |
| `groups/<group>/` | Current research: question, ideas and decisions, methods, experiments, findings and presentation. Start with its README and AGENTS.md. |
| `groups/<group>/history/` | Canonical home for dated session closeouts, cross-experiment retrospectives and trace walkthroughs; linked from the group README. |
| `datasets/` | Shared source discovery; exact inputs and solver visibility belong to the experiment. |
| [Discussions](../discussions/README.md) | Local artifacts by default; explicit exceptions retain durable decisions and records. |
| `src/tb3_medical/`, `tests/`, `configs/` | Common implementation, regressions and artifact policy. |
| `skills/`, `src/tb3_medical/skills/` | Canonical user-facing skills; installed copies are mirrors. See [skill lifecycle](skill-lifecycle.md). |
| `presentation/` | Shared read-only index and media renderer; groups own their scientific stories. |
| `exports/recipes/`, `exports/records/` | Selected-input recipes and export lineage. Generated packages have a fresh destination. |
| `docs/` | Shared current guides plus clearly indexed historical records. |
| `probes/`, `docs/research-rounds/`, `docs/evidence/` | Retained sources, protocols and receipts at their original paths. They are not a second authoring workflow. |
| `archive/` | Hashes and Git recovery locators for retired material. |
| `.local/`, `runs/`, `jobs/`, `.cache/`, `.venv*/` | Local outputs, inputs, environments and caches, outside tracked source. |

Find medical work through the [research groups](../README.md), not a new global
round or candidate queue. New shared guidance belongs in an existing guide;
group-specific explanations belong with the group. Put completed session narratives
and retrospectives in `groups/<group>/history/<scope>-<topic>.md`, not loose in
`docs/`. Record implementation decisions in the migration history only when they concern that migration. Keep dated source
records intact and link to them instead of copying their verdicts into another index.
