# Daily workflow

From the repository root, use Python 3.12 and install the package once:

```sh
uv sync --locked --inexact --group dev
uv run med list --kind group
uv run med list landmark
uv run med show anatomical-landmarks-br040
```

`--inexact` preserves separately installed research dependencies in a reused
environment; declared packages still follow the lock.

`uv run med` uses the installed package. With `.venv` activated, use `med` directly.
It discovers `workbench.toml` from the current directory; use
`med --root /path/to/workspace ...` from elsewhere. Inspection does not download
scans or start a model. Model execution requires an explicit `med run`.

## Find and capture ideas

Read the owning group's README and AGENTS.md, then search before researching again.
The [research design guide](research-design.md) covers references, controls and
what a result can support. For a new idea:

```sh
uv run med idea anatomical-landmarks idea-example --title 'Example' --question 'What is unresolved?' --source 'codex://threads/TASK'
uv run med decide idea-example parked --reason 'Needs adjudicated references' --actor assistant --source 'codex://threads/TASK'
```

Ideas are Markdown with a small TOML header. Keep prior findings, research/visual
links, decisions and reopening conditions concise. `--actor assistant` records a
recommendation; it cannot replace an accepted disposition. Use `--actor user`, or
`--accepted` with the actual user decision's source, only for an accepted decision.

## Author and run

```sh
uv run med new anatomical-landmarks my-study --title 'A focused question'
```

Edit the generated `experiment.toml`, `protocol.md` and `task/` under the group.
Link the experiment from the group's `presentation/catalog.json` with its task
definition and explicit scope; see [task taxonomy](task-taxonomy.md). A new
model/effort condition normally reuses a brief, while a changed contract may
need a separate definition or revision.
The config holds machine-used settings; the protocol explains the question,
inputs/reference, method, findings and limits. The scaffold's verifier and oracle
are placeholders. Implement them for the intended study; controls are required
before a nondiagnostic model launch. No hand-authored freeze, plan or dependency
graph is needed.

For an authorized study, replace the example model and runtime paths:

```sh
uv run med run my-study --model openai/MODEL --effort high --diagnostic --preview
uv run med run my-study --model openai/MODEL --effort high --diagnostic --harbor /path/to/harbor
uv run med run my-study --agent oracle --harbor /path/to/harbor
uv run med run my-study --agent nop --harbor /path/to/harbor
```

Preview checks the selected task without launching. A launch snapshots its task,
assigns a fresh attempt and records the condition. Runtime config, logs and payloads
live under `.local/`; concise receipts live with the experiment. Each launch uses
one attempt with no automatic retry. Harbor, Docker and provider routing are
separately managed optional runtimes; maintenance and inspection never install them.
Keep secrets out of authored records.

### Local Codex launch rulebook

#### Preflight

1. Confirm authorization, active ownership, usage reserve, model and effort.
2. Inspect the solver image, Codex version, `task.toml` and
   `environment/docker-compose.yaml` when present. Host success does not verify
   container execution.
3. For a new or repaired route, run one bounded toy with the same image, network,
   capabilities and verifier arrangement. Require a completed turn, correct
   shell-produced answer and passing verifier before the medical attempt.

#### Authentication and network

| Setting | Rule |
| --- | --- |
| API key | Harbor's default auth path uses `OPENAI_API_KEY`. |
| ChatGPT login | Set `CODEX_AUTH_JSON_PATH`, or `CODEX_FORCE_AUTH_JSON="1"` for the default cache. |
| Direct networking | Use the verified container-reachable proxy for that task. |
| Isolated proxy sidecar | Inherit Compose's proxy, such as `http://transport:3128`. Do not override it with a host/LAN proxy. |
| Restricted capabilities | Uploaded auth may retain the host owner. With `cap_drop: [ALL]`, even container root may be unable to read a host-owned 0600 file. Use the temporary-copy recipe below. |

`med run --agent-env-file PATH` accepts a flat JSON object of string values:

- Relative paths resolve from the workbench root.
- Values become Harbor `agents[].env`; host proxy variables are not automatically forwarded.
- Preview validates settings and shows key names only; it does not test login or connectivity.
- Values remain in local runtime files; keep profiles private and out of Git.
- Reuse settings only when the task's network and permission requirements match.

#### Temporary auth copy for restricted containers

- Copy the existing login into a fresh **0700 host directory**; set only the copy to **0644**.
- Pass the copy through `CODEX_AUTH_JSON_PATH`; leave proxy settings to the task's Compose file.
- Keep the copy until Harbor exits, then remove it. Never print credentials or change the original file's permissions.

Run from the repository root with an authorized experiment, model and effort:

```python
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory(prefix="tb3-codex-auth-") as directory:
    private = Path(directory)
    auth = private / "auth.json"
    shutil.copyfile(Path.home() / ".codex/auth.json", auth)
    auth.chmod(0o644)
    profile = private / "agent-env.json"
    profile.write_text(json.dumps({"CODEX_AUTH_JSON_PATH": str(auth)}))
    profile.chmod(0o600)
    subprocess.run([
        ".venv/bin/med", "run", "my-study",
        "--model", "openai/gpt-6-astra", "--effort", "medium",
        "--harbor", str(Path(".venv/bin/harbor").resolve()),
        "--agent-env-file", str(profile), "--diagnostic",
    ], check=True)
```

This starts a model. Add `--preview` for validation without inference.

#### Failure checks

| Symptom | Check first |
| --- | --- |
| Missing key / 401 | Selected auth method and whether the solver can read the uploaded credential |
| Network unreachable | Compose isolation and whether an agent override replaced the sidecar proxy |
| Model rejected / metadata missing | Exact client version and route used by the failing attempt |
| Turn completes but no reward | Verifier image, test script and output permissions |

Retain execution errors and fix the failing layer before retrying. These errors
alone do not prove model failure or account-wide unavailability.

[Verified routing incident and evidence](../groups/lesion-localization/history/2026-09-23-codex-routing.md).

### Controls and interpretation

Diagnostic runs may precede controls. A model run without `--diagnostic` requires
an oracle pass and expected no-op failure for the exact task, and an assessment
other than `needs_review` or `invalidated`. These local checks do not certify
submission eligibility. Diagnostic origin remains visible after reassessment.

Control reuse also respects the supplying experiment's review state, including
reuse by a different experiment with identical task bytes. A questioned or
invalidated supplier needs explicit scoped reassessment before its controls become
eligible again. A neutral reset cannot clear an adverse assessment. Never-assessed
controls remain eligible when their current execution evidence and exact task
binding satisfy the checks.

The latest execution/result observation governs an attempt. A later incomplete,
erroneous or unbound observation does not fall back to an earlier passing result;
a separate valid control attempt may still satisfy the requirement. Saved-output
replays and comparative/trace reviews are separate observations. An operational
launcher failure retains its receipt and returns a nonzero CLI exit status; a
normally completed model attempt may have a failing scorer outcome without being
an operational command failure.

## Collect and inspect

`med collect EXPERIMENT RESULT.json ...` imports externally launched Harbor
outputs or collects after interruption. Repeated collection preserves attempt
identity and appends changed observations. Partial results and execution errors
remain distinct from scorer failure.

Collecting the unchanged latest result is a no-op. If the result changes and later
returns to earlier bytes, collection appends that return as a new observation;
the older observation remains intact.

```sh
uv run med show my-study
npm run frontend:build
uv run med present --serve
# Open http://127.0.0.1:8765
```

Reads parse known metadata and show stored status and timestamps. They do not poll
jobs, inspect Docker or rehash all raw evidence. An old running observation is not
proof of a live process. The [shared vocabulary](status-vocabulary.md) defines the
progress/assessment badges and the attention queue.

## Review conclusions

```sh
uv run med issue ATTEMPT_OR_EXPERIMENT --reason 'Specific reproduced defect' --evidence path/to/receipt.json
uv run med review EXPERIMENT usable --reason 'Narrower conclusion survives' --scope 'Cases and claims retained' --resolves ISSUE_ID --evidence path/to/reassessment.json
```

Issues name affected runs and flag the experiment and dependent summaries/exports.
Reviews record scoped assessments without changing old scores. Unassessed evidence
creates no review task; an acknowledged withdrawal may remain invalidated without
occupying the attention queue. A narrower conclusion needs explicit reassessment.

To reassess a diagnostic attempt against later controls, add
`--qualify-attempt ATTEMPT_ID` to a review. It checks the selected task binding,
unchanged inputs, completed scoring and matching controls. Reuse for submission
still depends on the target's requirements.

You may resolve an issue and qualify an attempt in the same scoped `usable`
review. The command checks the proposed resolution in memory and publishes the
review only if every requested qualification succeeds. It does not briefly expose
an optimistic usable assessment on failure.

Continue with [reproduction and presentation](reproduce.md) for saved-output replay,
views and media, use the [evidence explanation workflow](evidence-explanations.md)
for a pinned result/GT/trace explanation, or continue to
[exports and submission](submission.md) for a fresh package.
For code/docs changes, follow [contribution checks](../CONTRIBUTING.md). Neither
routine validation nor documenting a proposal authorizes an experiment.
