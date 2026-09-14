# Trial catalog and research workbench

This is a local authoring tool for the TB3 workshop. It imports Harbor evidence,
keeps candidate decisions and trial reviews in small JSON records, and produces
a searchable HTML report. It does not launch trials or certify a submission.

## Design decisions

- Existing `runs/`, task freezes, and source-linked research remain the evidence
  authorities. The catalog is an index over them, not a replacement.
- Use Python's standard library and an HTML report with embedded data: no service,
  database, Node toolchain, or model call is required to refresh it.
- Separate generated `catalog/trials/` from authored `catalog/ideas/` and
  append-only `catalog/reviews/`. Sync cannot overwrite an analyst's review.
- Classify from individual trial results, never a job's mean reward. A completed
  zero-reward model trial is a **failure candidate** until evidence review.
- Retain exclusions and passes. Group snapshots by Harbor's recorded
  `task_checksum`; the runner's `task_sha256` is a different hash algorithm and
  is not interchangeable. A current tree hash cannot prove an earlier run's tree.
- Export an explicit field allowlist. Raw environment/configuration, exception
  tracebacks, trajectories, and model messages stay in the local run directory.
  The report links to evidence without embedding those bodies.

## Start and refresh

From the repository root (Python 3.10+; the existing `.venv` is sufficient):

```bash
.venv/bin/python scripts/tb3_catalog.py sync
.venv/bin/python scripts/tb3_catalog.py serve
```

Open <http://127.0.0.1:8766/>. The server binds to loopback and serves only the
report and its explicitly linked local evidence. Ctrl-C stops it. The generated
[HTML file](../runs/catalog/index.html) also opens directly without a server.

After new trials, repeat `sync` and `report`, then reload the page. If serving,
restart `serve` to include newly linked evidence in its allowlist. Reports are
explicit snapshots, not a live monitor; their generation time is visible.

```bash
.venv/bin/python scripts/tb3_catalog.py report
.venv/bin/python scripts/tb3_catalog.py list --kind ideas --query 'nested'
.venv/bin/python scripts/tb3_catalog.py list --task cache-invalidation
.venv/bin/python scripts/tb3_catalog.py list --status model_failure_candidate --json
.venv/bin/python scripts/tb3_catalog.py show cache-invalidation
```

`sync` scans `runs/<job>/<trial>/result.json`; aggregate job results never become
trials. It preserves earlier imported records if the raw run directory later
disappears, flags missing/changed evidence when building the report, and returns
nonzero with per-file errors when a result cannot be imported. A malformed or
actively changing file does not prevent importing other trials. Directories
without trial result files are not evidence of completed attempts and are not
imported. It neither resumes nor cancels another session's work.

## Capture and curate ideas

Use the [round register](research-rounds.md) to group recurring discussions and
their experiment handoffs. Each candidate keeps one stable catalog ID and links
its owning round specification. Search `brainstorm-round-002` for the four new
Sol/Astra capability ideas. Round membership uses tags and existing evidence
links; a new brainstorm is not a new trial or a model-failure classification.

```bash
.venv/bin/python scripts/tb3_catalog.py idea-add my-candidate \
  --title 'A concrete user problem' \
  --hypothesis 'The behavior that may require difficult reasoning' \
  --next-action 'Build the smallest independent reproduction' \
  --tag correctness --source https://example.org/primary-source
.venv/bin/python scripts/tb3_catalog.py curate my-candidate \
  --status screening --next-action 'Check the observed behavior against the specification'
```

Keep the idea ID equal to the probe directory name to link imported trials.
`curate` preserves omitted fields; repeated `--tag` flags replace the tag list.
For richer edits, directly edit the record in `catalog/ideas/`: retain sources,
evidence paths, why the idea may be hard, and reasons for parking or rejection.
Source URLs in the seed catalog are leads recorded in the research documents,
not newly verified claims about current upstream bugs.

## Analyze a failure candidate

The matrix separates task snapshots and shows each trial's actual observed case
outcomes. Nop failures are controls; missing cases remain **not observed**.
The detail panel links the original result, verifier, submitted artifacts, and
trajectory. The [cache analysis](../catalog/analyses/cache-calibration.md) provides
an example of retaining exclusions and a successful diagnostic together.
Codex's embedded browser may block direct navigation to raw text files; use the
displayed repository path to open that evidence in the file panel or editor.

Before assigning `genuine_failure`, inspect the execution health and frozen
instruction, compare same-snapshot controls, reproduce a concrete failing
behavior independently, and document why the verifier requirement is fair.
Record that work in a local Markdown/JSON file, then append a review:

```bash
.venv/bin/python scripts/tb3_catalog.py review TRIAL_ID \
  --verdict genuine_failure --failure-mode sibling-alignment \
  --explanation 'Describe the reproduced violation and why the requirement is fair' \
  --next-action 'Run a fresh diagnostic against the same frozen snapshot' \
  --evidence catalog/analyses/independent-reproduction.md
```

Other verdicts are `task_defect`, `verifier_defect`, `infrastructure`, `mirrored`,
and `pending`. The command requires existing local evidence. It only accepts
`genuine_failure` for a completed zero-reward model candidate with a recorded
snapshot; the analyst remains responsible for the substantive conclusion.
Every review is a new file under `catalog/reviews/<trial-id>/`. Changes to
imported evidence, the classification, or linked review evidence invalidate
the latest review and remove it from the current genuine-failure count. An
older review is retained in the directory, never silently restored as current.

## Evidence contract and limits

| Field | Meaning |
| --- | --- |
| `classification` | Observed result: control pass/fail, model pass, model failure candidate, execution error, incomplete, or unknown. |
| `task_checksum` | Historical digest copied from Harbor's trial result; snapshot grouping only. |
| `task_sha256` | Unset on imports. The runner's full-tree hash requires its own explicit freeze evidence. |
| `source_sha256`, `evidence_sha256` | SHA-256 of the source result and indexed evidence manifest. |
| `execution_mode` | `harbor` for this importer. A network proxy is still a Harbor run; mirrored reviews do not count as genuine failures. |
| `qualifying_final_trial` | Always false here. Final CI requirements remain in `docs/requirements.md`. |

Harbor's lock additionally contains a publishable-file task digest. That is a
third hash format, accessible through the linked lock; it is not compared to
the runner or trial checksum. Settings come from the trial's config, because
Harbor 0.14 and 0.18 job config formats differ. Token counts are copied when
available; unknown values remain null, and cost estimates are not reported as
subscription spend.

Per-case import currently accepts one JSON object (whole stdout or one JSON
line) with `passed: [case_name]` and `failures: [case_name + ': ' + detail]`.
Object failures using `name`/`case`/`test` are also recognized. Names must be
machine labels; free-text failure details are left in the raw verifier output.
Plain text, unsupported formats, duplicate names, disabled verifiers, nonbinary
rewards, and multi-step results remain explicit warnings or unknown outcomes;
they are never guessed into case successes. Reward contradictions also remain
unknown. Exceptions take precedence over every reward or case observation.

The generated allowlist excludes raw config/env, arbitrary agent kwargs,
tracebacks, trajectory messages, and tool arguments. Raw evidence links are
local and can contain those bodies. Review the authored notes and source
material before publishing a repository or report. No publication is performed
by these commands.

## Validation

```bash
.venv/bin/python -m unittest discover -s tests -p 'test_tb3*.py' -v
```

Tests cover classification precedence, conflicting rewards, malformed evidence,
idempotent imports, raw-field exclusion, snapshot guards, evidence races,
append-only/stale reviews, and idea curation. Browser checks exercise the real
imported report: matrix search, snapshot separation, idea search, links to
trials, and the distinction between missing cases and failures.
