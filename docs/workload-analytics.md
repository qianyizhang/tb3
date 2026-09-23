# Local workload analytics

`tb3-workload` builds a local HTML and JSON report for Codex sessions associated
with this repository and for workbench med-run results. It uses
[Codex Usage Tracker](https://github.com/douglasmonsky/codex-usage-tracker)
0.27.0 for canonical Codex model/tool facts and cloned-call deduplication. The
adapter adds repo/worktree selection, purpose labels, med results, a pinned
API-equivalent price card and links into the existing Trace Atlas viewer.

## Build a report

From the repository root:

```sh
mkdir -p .local/workload/tracker
export CODEX_USAGE_TRACKER_CACHE_ROOT="$PWD/.local/workload/tracker"
uvx --from codex-usage-tracking==0.27.0 codex-usage-tracker refresh --wait 30 > .local/workload/refresh.json
uv run tb3-workload --tracker-db "$CODEX_USAGE_TRACKER_CACHE_ROOT/codex-usage-kernel-v1.sqlite3"
```

If the refresh job is still running, repeat `refresh --wait 30` until its JSON
shows `"terminal": true` and `"state": "completed"`. The tracker index is
local and rebuildable; raw Codex logs are read-only. Open
`.local/workload/index.html` after the build. The report and labels stay under
the ignored `.local/` tree. Neither raw transcripts nor the generated report
belong in Git.

The command accepts `--codex-home`, `--root`, `--tracker-db`, `--output`,
`--labels`, `--timezone` and `--atlas-base`. The default time zone is
`Asia/Shanghai`. The adapter checks Codex session headers for this checkout or
a worktree with the same Git origin. It includes delegated sessions and
auto-review traces as their own physical sources. Med-run rows come from
`.local/attempts/*/job/task__*/result.json` and `runs/*/*/result.json`.
Other historical probe formats are outside this first report. It does not
launch or replay a model.

## Purpose labels and trace links

The first pass labels sessions from short saved titles; unlabeled delegated and
auto-review traces inherit their parent task's purpose. Very long saved titles
are not copied into the report. A med result is an `experiment` by default.
Unknown titles remain `unclassified`. The label basis is shown in each source
row, and a session has only one purpose even when its work was mixed. Edit
`.local/workload/purpose-labels.json` to correct a label:

```json
{
  "sessions": {"SESSION_UUID": "curate_data"},
  "attempts": {"attempt-IDENTIFIER": "experiment"}
}
```

The accepted labels are `curate_data`, `research`, `operations`, `babysit`,
`experiment` and `unclassified`. Rebuild after an edit. A purpose total is a
sum of whole sessions, so it is an allocation of observed usage, not a measure
of how many tokens a specific activity caused.

Each aggregate narrows the session table. Session rows link to the original
source in Trace Atlas with its exact physical file key. Run Trace Atlas with
Codex's session and archived-session roots plus this repository's
`.local/attempts/` and `runs/` roots so med-run links resolve. Its default
port is 8765; set `--atlas-base` when using another port. On this machine:

```sh
cd /Users/zhangqy/Documents/Codex/2026-09-12/inv
make start ARGS='--root /Users/zhangqy/.codex/sessions --root /Users/zhangqy/.codex/archived_sessions --root /Users/zhangqy/pkgs/tb3/.local/attempts --root /Users/zhangqy/pkgs/tb3/runs'
```

Source paths also appear in the local report when a trace is absent or not
indexed by Trace Atlas.

## Reading cost and coverage

The [rate card](../configs/workload-rates.json) records the OpenAI
[API Standard prices](https://developers.openai.com/api/docs/pricing) checked
on 2026-09-23. It applies those rates to observed input, cached input, cache
write and output tokens. Per-call Codex estimates apply the published long
context rates when input exceeds 272,000 tokens. Med results have aggregate
token counts only, so their estimate uses short-context rates and is labeled
coarse. Prices are applied retroactively for comparison: **these amounts are
not subscription charges, Codex credits or invoices**. Tool-specific API fees,
Fast service tier premiums and external infrastructure costs are not included.

An unpriced model contributes tokens but zero to the displayed dollar sum;
`priced_token_percent` shows coverage. The `codex-auto-review` model currently
has no defensible public API rate and remains unpriced. `tracker_missing` means
a selected trace was absent from the last tracker refresh; rerun it before
interpreting totals. Med results with missing agent usage remain rows with zero
observed tokens and an explicit missing-usage status. Med usage is assigned to
the result completion day because its result file has no call timestamps.

The report is a workload view, not an experiment outcome. A resumed med run may
contain cumulative result usage; compare its source trace before adding those
rows as independent compute. The tool table counts calls and source sessions;
it does not assign model-token cost to a tool call merely because they occurred
in the same session.
