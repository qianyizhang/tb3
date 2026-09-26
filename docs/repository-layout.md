# Repository layout and file placement

Choose the owner before choosing a filename. A scientific question belongs to a
group; reusable implementation belongs to the package; current shared guidance
belongs in `docs/`. Use [architecture](architecture.md) for component boundaries
and [governance](governance.md) for retention and what may be committed.

Before adding files, inspect Git status and active task ownership, run
`uv run med list QUERY`, then read the relevant group's README and AGENTS.md.
Extend an existing record or guide when it already owns the subject.

## Top-level map

```text
tb3/
├── workbench.toml              Workspace discovery marker
├── pyproject.toml, uv.lock     Python package and locked dependencies
├── package.json, package-lock.json  Browser/media tools and dependencies
├── README.md                  Project entry point
├── CONTRIBUTING.md, AGENTS.md  Development checks and collaboration rules
├── groups/                    Research questions and their owned work
├── datasets/                  Source records, sample receipts and previews
├── src/tb3_medical/            Shared Python services and CLI
├── presentation/              Shared browser assets and external task briefs
├── skills/                    Repository-owned authoring/explanation skills
├── scripts/                   Browser/media harnesses and explicit utilities
├── tests/                     Python regressions and JavaScript/browser checks
├── configs/                   Artifact/link policy and runtime lock records
├── docs/                      Current guides and indexed historical records
├── discussions/               Local scratch plus explicitly retained records
├── exports/                   Recipes, support files and export lineage
├── probes/                    Retained historical implementations and evidence
├── archive/                   Retirement manifests and recovery locators
└── .local/, runs/, jobs/, .cache/, .venv*/  Local payloads and environments
```

This is an ownership map, not an exhaustive listing or a request to create empty
directories. `.github/`, `.githooks/` and root tool configuration own CI and local
checks. Frozen source paths remain valid provenance even when they differ from
the layout used for new work.

## Where a new file belongs

| You are adding… | Put it here |
| --- | --- |
| A research question, source screen or reopening condition | `groups/<group>/ideas/<id>.md`; use `med idea` for the metadata header and `med decide` for actor/source-aware decisions. |
| A new experiment condition | `groups/<group>/experiments/<id>/`; start with `med new`, then author its compact TOML and protocol. |
| A group-specific preparation, scoring or diagnostic method | `groups/<group>/methods/<method>/`, with method documentation and explicit entry points. |
| A reusable command/service or cross-group algorithm | `src/tb3_medical/`, in the module that owns the responsibility described in [architecture](architecture.md#package-responsibilities). |
| A regression for shared behavior | `tests/test_<area>.py`; browser/JavaScript checks use the existing `tests/*.cjs` harness and `scripts/browser.cjs`. |
| A supported claim or evidence explanation | `groups/<group>/findings/`, with a concise discoverable JSON record and linked prose/evidence; `med evidence new` scaffolds explanations. |
| A current story, internal Task Brief or scientific figure | `groups/<group>/presentation/`; link briefs through its `catalog.json`. |
| An external task explanation | `presentation/external-tasks/`, following the [Task Brief rulebook](../presentation/task-explorer/RULEBOOK.md). |
| Shared browser layout, styling or interactions | `presentation/`; Python build/validation logic stays in `src/tb3_medical/`. |
| React components and browser state | `presentation/frontend/`; Python owns payload contracts and generates `contracts.generated.ts`. |
| Reusable conceptual illustration primitives and action recipes | `presentation/assets/teaching/`; preserve provenance at existing source-derived anatomy paths. |
| A dataset/source description or selected-sample receipt | `datasets/<source>.json`, `datasets/receipts/` and the declared preview register; follow the [dataset contracts](../datasets/README.md). Native images remain local. |
| A reusable guide | An existing `docs/*.md` guide, or a focused new page linked from [the docs index](README.md). |
| A dated research closeout, retrospective or trace walkthrough | `groups/<group>/history/<scope>-<topic>.md`, linked from the group README. Current claims still belong in findings. |
| A repository-wide design discussion | `discussions/` as local scratch by default. A durable record in `discussions/records/` needs a stable ID, source-task link, reopening conditions and an exact ignore exception. |
| An export recipe or lineage record | `exports/recipes/` or `exports/records/`; generated packages go to fresh, explicitly owned destinations. |
| A reusable authoring/explanation skill | `skills/<name>/`; packaged solver skills live in `src/tb3_medical/skills/`. Follow [skill lifecycle](skill-lifecycle.md); installed copies are mirrors. |
| Logs, raw answers, scans, caches, rendered reports or videos | An owned local output directory, usually `.local/`; retain paths/hashes in concise source records where needed. |

`scripts/` holds explicit tooling entry points, not a second Python service layer.
Do not add new studies to `probes/` or turn historical round numbers into lookup
aliases. Use semantic IDs and normal package imports; do not add path mutations
or fallback searches for relocated inputs.

## Inside a research group

```text
groups/<group>/
├── group.json                 Stable group identity and question
├── README.md, AGENTS.md        Navigation and scientific/authoring boundaries
├── ideas/<id>.md              TOML metadata plus concise research notes
├── decisions/*.json           Actor, source and disposition
├── methods/<method>/          Owned preparation/scoring/inspection tools
├── experiments/<id>/
│   ├── experiment.toml        Machine-used settings and relationships
│   ├── protocol.md            Question, inputs/reference, method and limits
│   ├── task/                  Authored task when stored with the experiment
│   ├── reproduction/          Declared recovery recipes/support, when provided
│   ├── freezes/               Task-file hashes and snapshot locators
│   ├── attempts/              Execution identity and condition receipts
│   ├── evaluations/           Collected result/replay observations
│   └── reviews/               Issues and scoped reassessments
├── findings/                  Claims, explanations and linked evidence
├── presentation/             Story, catalogue, briefs and static figures
└── history/                   Dated closeouts and retrospectives
```

Only `experiment.toml`, `protocol.md` and a placeholder `task/` are created by
`med new`. Other directories are added as needed. A maintained experiment can
declare task paths outside this illustrative subtree; follow its manifest rather
than moving or copying frozen inputs to make the tree look uniform. The loader
also recognizes retained `plans/` records and group-level `reviews/`; new run
receipts are produced by the workflow rather than hand-authored.

Within an authored task, `instruction.md` describes the deliverable, `task.toml`
declares runtime settings, and `environment/` supplies solver inputs. `tests/`
holds verification/reference material and `solution/` holds the oracle. Keep these
roles explicit; see [research design](research-design.md) before changing access
or ground-truth boundaries.

## Make additions discoverable

File placement and navigation are separate contracts:

- Research records must match `RECORD_GLOBS` in
  [core.py](../src/tb3_medical/core.py) and have a unique valid ID. A loose JSON
  file elsewhere is not automatically a workbench record. Prefer existing kinds
  and CLI scaffolds to a new global registry.
- Group stories are linked by `group.json`. Internal task definitions are linked
  from the group's `presentation/catalog.json`, composed by the
  [root task catalogue](../presentation/task-explorer/catalog.json). Use
  [task taxonomy](task-taxonomy.md) to distinguish a task from an execution
  condition or supporting research.
- Dataset links identify the source; sample receipts and experiment manifests
  pin the actual selection and transformations. Directory proximity does not
  establish a dependency or solver visibility.
- Current docs need an inbound navigation link. `docs/*.md` is already included
  in [doc-links.json](../configs/doc-links.json); add required entry-point guides
  to `required_files`. Extend that policy deliberately for a new maintained tree.
- Retained discussion exceptions are exact paths in
  [discussions/.gitignore](../discussions/.gitignore). Do not force-add scratch
  artifacts or loosen ignore rules to bypass retention policy.

Keep original evidence and scientific outcomes intact when reorganizing
navigation. Migration decisions belong in migration history only when they concern
that migration. Review the diff and run the relevant
[contribution checks](../CONTRIBUTING.md#checks); stage only owned paths. The
artifact gate reads the Git index, so an unstaged correction cannot repair a
staged artifact failure.

## Explanation pilot locations

Canonical internal copy lives in `groups/<group>/presentation/stories/*.story.md`.
External task stories live beside their briefs in `presentation/external-tasks/stories/`. Shared
fixture owners live under `presentation/assets/teaching-fixtures/`, discovered by
`presentation/assets/teaching-prefabs.json`. Generated HTML, video and acceptance
receipts stay under `.local/explainers/`. See [canonical explainers](../presentation/EXPLAINERS.md).
