# BR-042 V4 six-hour Astra/xhigh follow-up

This study is closed. The launch instructions below describe the original execution and are retained as historical protocol. Its one-shot adapters depend on the retired pre-cutover CLI; they are not supported launch commands. Read [the completed continuation](provenance/review.md) and use the [current workflow](provenance/workflow.md) for new work.

User authorized one fresh attempt on 2026-09-20, then requested babysitting every
20–30 minutes. Use 30-minute reports. Source task:
codex://threads/01a0bc95-2598-7810-809e-9c8b6c0969c3.

Condition: openai/gpt-6-astra, xhigh, 21600 seconds of agent wall time, one attempt,
zero retries. Setup and verification are additional. Same CTA, source notice,
license, reference, evaluator, resources and public environment as V4 two-hour.
Only task identifier, allowance and midpoint wording change (180 minutes).
Final review remains the last ten minutes. This is a fresh blind extraction;
no prior answers, branch feedback, reviewer findings or patient-specific cues
are passed to the solver. This outcome-informed budget follow-up is not a
held-out capability estimate or a controlled estimate of time alone.

The migration task (codex://threads/01a0bdeb-7a43-7442-bf34-16d869e23e3b)
reports preserved background files; local hash verification confirms the original
freeze. No historical authoring module is imported or rerun. New ownership is
under this group. The common CLI creates the experiment/freeze and collects
results. A group-owned adapter retains the previously used local Harbor provider
routing, which the current generic runner does not expose. Runtime configs stay
local; launch-freeze.json records their hashes. No shared orchestration changes
are made during the ongoing architecture work.

Launch from repository root:

```sh
.venv-br030/bin/python groups/tubular-anatomy/experiments/br042-v4-6h/run.py --run
```

Without --run, offline byte/config/scorer readiness only. Fresh oracle=1 and nop=0
on matching task checksums must finish before model launch. An existing event
journal or job directory blocks rerun. Setup/infrastructure failure stops the
chain and is reported separately; there is no automatic replacement attempt.

Local bundle: runs/br042-all-vessels-v4-6h. Jobs:
br042-all-vessels-{oracle,nop,astra-xhigh}-v4-6h-attempt1.
Launcher alone writes events.jsonl. Monitor writes monitor-state.json separately.
Respect the frozen task; no model guidance, answer edits, restarts or extensions.
Inspect trace activity and owned processes before declaring a hang. On exit,
retain all partial artifacts, independently evaluate saved geometry and correctly
labeled coverage, compare previous runs, and pause monitoring.

Report broader vessel inventory and source-image review separately from coronary
GT coverage. The unchanged scorer uses category-mean and per-category coverage
gates; extension/precision diagnostics do not create new pass gates. Reference
identity disagreements remain under review. The two-hour review provides context
only to the author and is not solver input.

## Setup interruption and bounded recovery

The first job's package installation received Debian HTTP 503 through the proxy;
its result has null agent_execution, agent_result and verifier_result. It is
retained as infrastructure failure, not a model performance attempt. A disposable
container reproduces the same apt update/install step before any replacement.
The assistant interpreted the user's request to run the model and babysit as
permission for one bounded pre-agent setup recovery; this is an explicit
exception to the initial operational no-replacement rule, not a user-authored
policy change. No inference retry is permitted.

`recover_setup.py --run` permits one fresh job, attempt2, only after proving
attempt1 never entered agent execution and original controls/bytes still match.
It writes a separate setup-recovery-events.jsonl and separate job directory;
attempt1 and its journal remain unchanged. All solver inputs and the six-hour
allowance remain unchanged. If this recovery also fails, stop and report.
