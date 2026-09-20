# Architecture review: finish the native medical workbench

Reviewed 2026-09-20 against commit `02b9287db9c701bb4f9aa93cb81122ad7acaca60`.
The subsequent [minimal implementation plan](native-workbench-plan.md) narrows
the proposed architecture and separates everyday usage from temporary migration
work. Its four decisions are confirmed; the findings below remain the review
record, not a requirement to build every abstraction suggested here.
The requested standard is a coherent fresh design with no compatibility shims.
This review changes documentation only. Its reproductions used temporary fixtures
or an in-memory copy of the record graph; no actual scientific verdict changed.

## Verdict and migration depth

The first pass delivered a useful evidence index, archive, presentation and a
tested orchestration foundation. It did **not** finish converting the existing
research into native, reproducible experiments. Calling that a complete
architectural migration was too broad. A dedicated engineering pass is warranted;
it can continue in this task and does not require new model trials.

| Inspected surface | Current coverage |
| --- | --- |
| Indexed medical experiments | 37 |
| Existing experiments with a native `task_path` | 0/37 |
| Existing experiments with a declared preparation command | 0/37 |
| Existing experiments enabled for native execution | 0/37; do not enable merely to make the count green |
| First-class native freeze records | 0; historical freeze receipts still exist |
| Historical attempts | 214, all with empty `depends_on` |
| Evaluations | 220: 214 imported observations and six deeper landmark evaluations |
| Group methods implementations | 0/7; each methods directory contains only a README |
| Independently demonstrated export/replay | One representative MRI package, including two saved model outputs |
| Historical probe files still tracked | 668, including 97 Python filenames beginning run/collect/prepare/build |
| Runtime presentation relocation map | 2,140 path mappings |
| Import-path mutations outside frozen probes | Six `sys.path.insert` sites in launchers/checks/tests/media |

The old experiment cards explicitly call themselves historical indexes. Their
case/condition/revision boundaries remain in prose and old runners. BR-042 also
has a migration-time owner handoff, not a live status integration. The background
owner and dirty BR-043 discussion must remain protected during any cutover.

## Findings

### AR-01 — P1: imported lineage does not provide the advertised invalidation behavior

`src/tb3_medical/core.py:168` traverses only explicit `depends_on` edges. All 214
imported attempts have no dependencies, and six group findings depend on coarse
experiment cards rather than their supporting evaluations. The group relation
and `experiment_id` are ownership fields, not evidence edges.

Reproduction: inject a synthetic confirmed issue against the imported BR-035
evaluation `observation-7ec037c2dd3d4449ecfb2a7b` in an in-memory copy of the graph.
The evaluation becomes `invalidated`, while `cardiac-motion-current-synthesis`
and `cardiac-motion` remain `qualified`. No source files were changed. This is a
workflow defect, not evidence that the actual cardiac result is scientifically bad.

Resolve together: explicit task/reference/scorer revisions, attempt inputs,
evaluation inputs and finding support. Validate required edge types and test
invalidation against the actual migrated graph. Findings must name the specific
evaluations or reviewed source records that support them; broad experiment
ownership must not stand in for scientific support.

### AR-02 — P1: arbitrary task payloads share the record namespace

`core.py:82` recursively parses JSON under groups, including new experiment task
payloads. It excludes selected folder names but not `task/`. An intentionally
malformed JSON input fixture makes workbench validation fail with JSONDecodeError.
A valid payload with `kind: experiment` is silently indexed as a research record.
Separately, an evaluation containing only version, kind and ID passes validation.

Resolve together: explicit record locations and schemas for each kind, typed
reference checks, and an artifact store outside the record discovery namespace.
Validate records before writing and before projecting them. Use atomic record
publication so concurrent readers cannot observe a half-written JSON document.
Do not grow a list of excluded directory names as the workaround.

### AR-03 — P2: experiment migration is primarily an index over the old layout

`workflow.py:54` requires `task_path`; all 37 existing experiments lack it. None
of their preparation/scoring/viewer code has moved into a maintained group
implementation. BR-040 contains CT and MRI comparisons with attempts reused
across BR-038/039, while BR-042 includes several task revisions. A round number
alone is not an executable task revision or a complete experiment specification.

Resolve together: inventory every experiment's cases, conditions, task and scorer
revisions, source artifacts, attempts, evidence gaps and supported operations.
Each entry gets an explicit disposition: native and replayable, historical with
known recovery gaps, or retired. Convert reusable implementations by family and
retain immutable original evidence. Reconstructing unknown settings is forbidden.
Do not run 37 fresh trials merely to claim migration coverage.

### AR-04 — P2: package, workspace and machine environment are conflated

`scripts/med:6`, `scripts/check_medical.py:6` and three test files mutate imports.
`scripts/prepare_med_tours.py:52` reaches into a historical authoring directory.
There is no project package manifest; `cli.py:13` derives the data workspace from
the package installation path. Merely adding an installed entry point would then
point at the wrong workspace. `scripts/med-media:6` discovers Playwright through
a Codex-specific cache; media instructions depend on `.venv-br030`.

Resolve together: an installable `src` package, declared `med` console command,
workspace discovery from an explicit config/current directory or `--root`, and
declared core/Harbor/imaging/media environments. Keep heavy optional dependencies
out of inspection-only commands. Migrate all consumers and remove old launchers,
path injection and personal cache fallback. Verify a built wheel from outside the
checkout, not only editable source imports.

The packaging direction follows the official [pyproject guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
and [src-layout guidance](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/).
The recommendation does not require publishing a package or choosing a hosted
service.

### AR-05 — P2: export provenance and recipe identity need a single contract

`packaging.py:18` verifies that a commit exists; `packaging.py:36` copies files
from the current workspace. A temporary repository with an empty commit accepts
an exact export of a file absent from that commit. Hashes prove the selected
payload bytes, but the claimed source commit does not establish their origin.

Another reproduction: writing the same valid recipe as compact JSON causes the
exporter to mark its own output INCOMPLETE with `Package recipe changed`.
`packaging.py:49` hashes original recipe bytes, then `:65` reserializes them before
verification. Whitespace becomes an accidental semantic requirement.

Resolve together: distinguish the committed recipe/code revision from externally
stored immutable artifacts. Read committed inputs from the selected Git tree and
verify artifact IDs/digests for external inputs. Represent adaptations explicitly.
Choose exact recipe-byte copying or a defined canonical serialization and hash it
consistently. A fresh export must be reconstructible from its declared origins.

### AR-06 — P2: recommendations and accepted decisions collapse into one state

`core.py:192` projects the latest disposition regardless of actor. In a temporary
fixture, a user selection followed by an assistant recommendation to park the idea
changes its current disposition to `parked`. Actor labels preserve attribution,
but not the user's decision authority.

Resolve together: separate recommendations from accepted decisions, with explicit
acceptance/supersession relationships. An assistant may record an already
authorized decision with its source, but a recommendation alone must not replace
it. Retain both streams in the concise idea history and UI.

### AR-07 — P2: media still depends on legacy source paths and special-case scripts

`scripts/check_med_tours.py:9` falls back through the 2,140-entry relocation map.
Tour preparation dynamically imports old authoring modules and hardcodes specific
round/runtime paths. The renderer, media preparation, export scripts and current
source cards do not share one artifact-resolution contract. Static assets work,
but rebuilding them still needs knowledge of the historical workshop layout.

Resolve together: group-owned view recipes, package-owned reusable rendering
methods and artifact IDs resolved through one store. Keep historical paths in
provenance only. Archive the old derivation receipts, produce new receipts for the
canonical recipes, and remove runtime path fallbacks. Immutable scorer replay
belongs in an isolated verified task snapshot; active application imports must
not depend on archived authoring modules.

### AR-08 — P2: current checks do not establish the new completion standard

The passing tests establish useful lifecycle behavior, importer integrity and
selected regressions. They do not install the package, exercise group methods,
reject incomplete record schemas, or replay each retained task revision. Most
orchestration tests use a synthetic task and mocked Harbor, correctly avoiding
unrequested trials. Readable presentation and preserved hashes are insufficient
acceptance criteria for a native experiment migration.

Add focused acceptance checks for the contracts above, real migrated lineage and
offline saved-output replay. Keep install/build checks, core unit tests, optional
imaging tests, external runtime integration and scientific qualification clearly
separate. Formatting and static import checks should prevent dense one-line code,
path injection and new imports from retired directories from creeping back in.

## Target design

Keep the file-backed workbench; no database, plugin framework, scheduler or hosted
application is needed to solve these problems. The package should have clear
boundaries for records, repository storage, artifacts, execution, export and
presentation. Avoid splitting every small function into an abstraction.

```text
pyproject.toml                  package, med command, dependency groups, checks
workbench.toml                  workspace identity, schema and storage/runtime config
src/tb3_medical/
  cli/                         argument parsing and command composition
  domain/                      record types, evidence graph, decision semantics
  repository/                  explicit record locations and atomic persistence
  artifacts/                   digest identity, resolution and verified recovery
  execution/                   task preparation, freezing and Harbor integration
  exporting/                   committed recipes and self-contained packages
  presentation/                shared index, stories and view building
  groups/                      importable group-specific reusable implementations
groups/<group>/                ideas, protocols, methods/recipes, studies, findings, views
datasets/                      exact source versions, terms and artifact references
exports/                       selected recipes and handoff lineage
archive/                       historical inventory and recovery, never an active import
.local/                        ignored artifacts, attempts and derived builds
tests/                         contract, migration, replay and presentation coverage
```

Group-owned scientific recipes and context stay together under `groups/<group>`;
reusable Python implementations use normal imports in the installed package.
There must not be competing implementations under both roots. First-class task
revisions connect source inputs and scorer versions to attempts and evaluations.
Group stories consume those findings rather than creating a second result ledger.

## Delivery order and exit criteria

1. **Core contracts and packaging.** Define record/reference/decision/artifact
   contracts, package the application, separate workspace discovery, migrate the
   stored records once, and repair graph propagation. Build and install the wheel
   in a fresh environment; use it from an unrelated directory with an explicit
   workspace. No alias readers, compatibility wrappers or `sys.path` mutation.
2. **One complete vertical slice.** Finish landmarks across CT and MRI, preserving
   cross-round attempt identity. Prepare from declared artifacts, recover exact
   snapshots, replay saved outputs, derive views and export from the same records.
   Verify equality or document justified differences; do not silently regrade.
3. **Remaining medical families.** Apply the proven contracts to all 37 entries.
   Every case/revision is native with verified supported operations, or explicitly
   historical/retired with recorded gaps. Complete source/case metadata and
   dependencies even where external data prevents replay. Cut over BR-042 only
   after its owner has handed off the current run; never move its live paths.
4. **Remove old runtime dependencies and review again.** Retire obsolete runners,
   duplicate commands, path maps and stale active documentation after their
   canonical consumers work. Preserve original evidence bytes in recoverable
   snapshots. Run installation, graph, replay, export and browser checks from a
   clean workspace, then obtain a final independent review of these criteria.

Use meaningful commits at these milestones and smaller group-sized commits where
that keeps scientific review manageable. A dedicated engineering session is
useful for focus, but a new Codex task per old experiment would add coordination
without fixing the shared architecture. No new task is created by this review.

Completion means the active workbench has one source of truth and no legacy-path
dependencies. It does not mean inventing lost artifacts, altering frozen task
bytes, deleting raw evidence, or declaring every historical experiment rerunnable.
