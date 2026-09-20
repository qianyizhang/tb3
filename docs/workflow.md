# Daily workflow

Install once with Python 3.12: `uv sync --locked`. Run commands with `uv run med`
(or activate `.venv` and use `med`). The installed package finds `workbench.toml`
from the current directory; `med --root /path/to/workspace ...` works elsewhere.
No command runs a model except an explicit `med run`.

## Find and capture ideas

```sh
uv run med list atlas
uv run med show anatomical-landmarks-br040
uv run med idea anatomical-landmarks idea-example --title 'Example' --question 'What is unresolved?' --source 'codex://threads/TASK'
uv run med decide idea-example parked --reason 'Needs adjudicated references' --actor assistant --source 'codex://threads/TASK'
```

Ideas are Markdown with a small TOML header. Keep the question, prior findings,
research/visual links, accepted decisions and reopening conditions concise.
Search before researching again. `decide --actor assistant` records a recommendation;
it cannot replace an accepted disposition. Use `--actor user`, or `--accepted`
with the actual user decision's source, only when the decision was accepted.

## Author and run

```sh
uv run med new anatomical-landmarks my-study --title 'A focused question'
```

Edit `experiment.toml`, `protocol.md` and the scaffolded Harbor task. The config
holds machine-used settings; the protocol holds the question, inputs, method,
findings and limits. Implement the verifier and oracle before qualifying results.
No hand-authored freeze, plan or dependency graph is required.

```sh
uv run med run my-study --model openai/MODEL --effort high --diagnostic --preview
uv run med run my-study --model openai/MODEL --effort high --diagnostic --harbor /path/to/harbor
uv run med run my-study --agent oracle --harbor /path/to/harbor
uv run med run my-study --agent nop --harbor /path/to/harbor
```

A launch snapshots the selected task, assigns a fresh attempt and records its
condition. Runtime config, logs and payloads live under `.local/`; concise receipts
live with the experiment. There is one attempt and no automatic retry per launch.
Harbor and Docker are separately managed optional runtimes, never installed by
inspection or checks. Select the Harbor executable from its Python environment.
Provider environment/routing belongs to that runtime; secrets are not authored
in experiment records.

Diagnostic model runs may precede controls. A model run without `--diagnostic`
requires an oracle pass and expected no-op failure on the exact same task, and
no unresolved experiment assessment. These local controls do not certify TB3
submission requirements. Diagnostic origin remains visible after reassessment.

`med collect EXPERIMENT RESULT.json ...` imports externally launched Harbor
outputs or collects after interruption. Repeated collection preserves attempt
identity and appends changed observations. Partial results and execution errors
remain distinct from scorer failure. Inspection shows recorded status and time;
it does not infer that an old “running” observation is a live process.

## Review conclusions

```sh
uv run med issue ATTEMPT_OR_EXPERIMENT --reason 'Specific reproduced defect' --evidence path/to/receipt.json
uv run med review EXPERIMENT usable --reason 'Narrower conclusion survives' --scope 'Cases and claims retained' --resolves ISSUE_ID --evidence path/to/reassessment.json
```

An issue names affected runs and flags the experiment, its group synthesis,
findings and exports. A review records a scoped assessment without changing old
scores. Unassessed evidence creates no review task. An acknowledged withdrawal
can remain `invalidated` without occupying the attention queue. A partial
withdrawal stays in history when an explicit reassessment finds narrower evidence
usable. Fixing code alone does not restore conclusions.

To reassess a diagnostic attempt against later controls, add
`--qualify-attempt ATTEMPT_ID` to a review. It verifies the selected task binding,
unchanged inputs, completed scoring evidence and matching controls. Reusing that
attempt still depends on the target submission rules; no repeated inference is
required merely for bookkeeping.

## Replay, view and export

The maintained landmark method covers CT full/cropped fields and MRI. Restore
inputs to the exact paths in its [input manifest](../groups/anatomical-landmarks/experiments/br040/inputs.json).
The manifest includes hashes and historical source locators; the CLI never searches
old directories as a fallback. Missing inputs give an actionable operation error.

```sh
uv run med prepare anatomical-landmarks-br040 --case ct-partial --execute
uv run med replay anatomical-landmarks-br040
uv sync --locked --extra imaging
.venv/bin/med view anatomical-landmarks-br040 --case ct-partial
uv run med export exports/recipes/landmarks-mri-v2.json /fresh/destination
uv run med verify-package /fresh/destination
```

Replay appends a scoring observation of the same attempt and records its comparison
criterion. It is not a new execution. Native views use declared image geometry.
The optional imaging extra is needed only for views and media optimization.

Exports use explicit Git-commit or local-artifact origins, verify only selected
inputs, and require a fresh destination. A flagged research draft requires
`--include-flagged` and includes the assessment reason and scope. Every export
starts as a draft. A clean export can become a separately owned submission repo;
current TB3 requirements and any later qualification remain a separate assessment.

## Inspect and present

```sh
uv run med check
uv run med present --serve
uv run med media prepare
uv run med present --serve --local-media
```

Ordinary reads parse known metadata locations; they do not hash runs, poll processes
or inspect Docker. Experiments show progress and evidence assessment from the
[shared vocabulary](status-vocabulary.md). The attention filter shows experiments
with an unresolved issue or explicit review request.

Portable presentation includes authored stories and retained figures. Local tours
use the exact retained derived snapshot listed in `presentation/tours/inputs.json`;
raw dataset derivation scripts are historical. `med media check` checks that selected
snapshot and its display invariants. `med media optimize` writes lossless player
assets. Optional video/still rendering uses `npm ci`, `npx playwright install chromium`,
then `npm run media -- --help`; FFmpeg is required for video. No personal tool cache
or implicit browser path is used. See [the media guide](../presentation/tours/TOOL.md).

`make check` is the one developer gate: staged artifact policy, offline tests,
metadata/story checks and formatting. Stage intended files before running it.
Full media generation, Docker, dataset downloads and inference are never routine
validation. Historical recovery and migration receipts live under `docs/migration/`
and `archive/`, outside the regular command path.
