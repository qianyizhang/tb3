# Medical research workflow

`python3.12 scripts/med --help` is the supported entry point. Use `list QUERY`
to search questions, ideas, decisions, models and evidence. Filter with `--group`
or `--kind`; `show ID` exposes the full record and current validity. BR-025 is
ambiguous by design: use `tubular-anatomy-br025` or `cardiac-motion-br025`.

## Discussions and decisions

Search before researching again. Keep a concise idea card with the question,
previous findings, source discussion, useful visuals and the condition that would
justify reopening. Capture material additions, not full chat transcripts.

```sh
python3.12 scripts/med idea anatomical-landmarks idea-example --title 'Example' --question 'What is unresolved?' --source 'codex://threads/TASK'
python3.12 scripts/med decide idea-example parked --reason 'Needs adjudicated references' --actor assistant --source 'codex://threads/TASK'
```

Decisions append history; the latest disposition is projected for readers. The
actor records who made the decision. A later discussion may link an existing idea
and append a new decision rather than producing another disconnected research note.

## Experiments and orchestration

`new GROUP ID --title TITLE` creates a disabled experiment, protocol and task
scaffold. Fill the protocol and complete source/reference checks before setting
`execution_enabled`. A `prepare_command` is an explicit argv array; `prepare ID`
prints it and `prepare ID --execute` runs it. `validate ID` performs static checks.

`freeze ID` records a content-addressed file map and local exact snapshot.
`plan FREEZE --agent oracle` and `--agent nop` create single-use control plans.
`run PLAN --harbor /absolute/path/to/harbor` executes one plan with no retries and
collects its allowlisted receipts. A codex plan requires `--model` and can include
`--effort`. It runs only after normal oracle=1/nop=0 on the same freeze. This is
an execution preflight, not proof of clinical validity or submission readiness.
Runtime environments/credentials remain outside tracked records. Each new model
attempt receives a new plan. Never infer authorization to run from a draft idea.

`collect EXPERIMENT runs/JOB/TRIAL/result.json` imports explicitly selected Harbor
individual results. Repeated identical collection is idempotent. Partial and
later complete observations share attempt identity; neither overwrites the other.
Saved-output reevaluations should reference the attempt and identify their scorer
revision. They are not additional model attempts. Historical adapters may need
extra collection/replay fields; missing raw formats are documented, not guessed.

## Bugs and evidence reviews

Use `issue TARGET --impact suspected|confirmed --reason TEXT --evidence PATH
--actor NAME`. Target the narrowest affected evaluation or finding. Add explicit
`depends_on` links for downstream findings, ideas, story-owning group records
and exports. Confirmed technical defects require reproduced evidence; use
suspected for unresolved clinical/reference disputes.

`review TARGET qualified --reason TEXT --evidence PATH --actor NAME --resolves
ISSUE` appends a reassessment. Original rewards remain unchanged. Resolution
requires existing matching proof and a review of the affected target. Multi-target
issues are resolved separately for each affected target; changed or
missing review evidence reopens the issue. A fix alone does not reinstate results.

## Presentation and clean export

`present --serve --local-media` builds a searchable read-only local index and
serves it on loopback. Without local media it builds portable stories with static
figures and explicit unavailable-media notes. `assets` verifies retained source
figures; `assets --write` restores exact derived exports. Media tools are described
in presentation/tours/TOOL.md. No browser action launches an experiment.

`export exports/recipes/NAME.json /fresh/destination` requires a pinned source
commit, selected record dependencies, exact source digests, explicit destination
files/roles, target profile and remaining gates. Exact exports preserve all bytes.
Adapted exports take reviewed changed source files and require a changes list;
old results never qualify changed task bytes automatically. `verify-package DIR`
checks a package without importing authoring code. Use its included replay guide
for environment-specific replay. New exports are drafts. Inspect current upstream
rules at actual submission time; never overwrite the existing sibling submission.
