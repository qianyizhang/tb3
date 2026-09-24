# Documentation

Reader-facing presentation principles live in [Presentation design](../presentation/DESIGN.md).

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
| Analyze local Codex and med-run tokens, cost estimates, purpose and tool calls | [Workload analytics](workload-analytics.md) |

## Reference

| Need | Start here |
| --- | --- |
| Understand components, research records and execution/presentation flow | [Architecture](architecture.md) |
| Choose types, validation boundaries and shared versus experiment-local code | [Coding style](coding-style.md) |
| Choose where to put code, experiments, findings, docs or generated files | [Repository layout and file placement](repository-layout.md) |
| Understand ownership, preserved evidence and what belongs in Git | [Governance](governance.md) |
| Write concise, structured summaries and reports | [Writing style](writing-style.md) |
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

The [repository layout](repository-layout.md) owns the directory map, placement
examples and discoverability rules. Groups own scientific work, the package and
presentation own shared implementation, and this directory owns current shared
guidance. Dated research closeouts stay with their group; original evidence stays
at its retained source location.
