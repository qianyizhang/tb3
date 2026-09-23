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

The working host is an Apple Silicon Mac with Docker Desktop. Harbor runs the
Codex CLI inside the selected Linux solver image. The desktop app, shell `codex`
and container `codex` are different clients and can have different versions,
credentials and routes. Check the exact executable/image used by the failing
attempt before inferring model availability.

**Use the existing working runtime profile explicitly.** On this Mac it lives at
`.local/runtime/codex-agent-env.json` (ignored, mode 0600). It contains a flat JSON
object of string environment values: `CODEX_FORCE_AUTH_JSON` set to `"1"`,
`http_proxy`, `https_proxy`, `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY`. Harbor
then injects the existing `~/.codex/auth.json` and the container-reachable proxy
settings. For a different approved credential location, use
`CODEX_AUTH_JSON_PATH` instead of assuming the default cache. Keep credentials
and machine-specific proxy addresses in local files, not tracked instructions.

```sh
uv run med run my-study --model openai/gpt-6-astra --effort medium \
  --agent-env-file .local/runtime/codex-agent-env.json \
  --harbor .venv/bin/harbor --diagnostic --preview
# After the route and authorized condition are verified, omit --preview to launch.
```

`--agent-env-file` resolves relative to the workbench root and accepts a flat JSON
object with valid environment-variable names and string values. Preview validates
the file and shows variable names only; it does not authenticate or contact a
model. Launch passes these values as Harbor `agents[].env`. Values stay in the
private local runtime configuration, not authored attempt/evaluation records.
Harbor may also retain them in raw logs/configuration under the private attempt
directory. No environment file means no explicit agent environment is supplied;
do not assume a host shell's proxy variables will reach the container. Harbor's
default auth path uses `OPENAI_API_KEY`; an existing ChatGPT login requires the
explicit opt-in above. Reuse a successful run's environment when recovering a
missing local profile, without printing secrets or executing historical launchers.
Tasks with a declared transport sidecar or stricter network policy keep their
declared route; do not replace it with this WSI profile.

Before a new or repaired route runs a medical task:

1. Inspect active ownership, usage reserve, the selected image/CLI version and
   auth method; preserve the requested model and effort.
2. Run one bounded, no-retry toy through that same Harbor runtime and environment.
   Verify a completed model turn, an actual shell-produced answer and a passing
   verifier. A host-only reply does not verify Docker/Harbor transport.
3. If it fails, inspect the first auth/transport/model-discovery error and fix
   that layer. Retain the failed attempt as an execution error. Do not repeat the
   same invocation or equate a 401/missing key/stale-client error with model failure
   or account-wide unavailability. A route repair does not change prior scores.
4. Resume the already authorized experiment condition with the verified profile.
   A runtime smoke pass proves execution plumbing, not medical capability.

On 2026-09-23, the new WSI launches omitted the previously successful BR-041
`agents[].env`. One invocation had no API key; the ChatGPT-auth attempt reached
`api.openai.com/v1/responses` without usable authentication. The shell CLI was
0.147.0; the WSI image had 0.155.1. Restoring the prior explicit auth **and** proxy
environment in the same image made both `gpt-6-astra`/medium and `gpt-6-sol`/xhigh
complete a `19 + 23` shell/file toy with reward 1 and no Harbor exception. No
client upgrade was needed. This verifies the restored combination; it does not
isolate every proxy/backend mechanism or attest provider-side model identity.

Local proof: `.local/model-route-smoke-20260923/jobs/gpt-6-astra-medium/` and
`.local/model-route-smoke-20260923/jobs/gpt-6-sol-xhigh/`, with the task and configs
alongside them. Source discussions:
[WSI experiments](codex://threads/01a0cbf7-5068-7001-90be-102123fff079) and
[routing investigation](codex://threads/01a0cc34-3a42-7243-aa18-c02bd8b0c2f3).
Recheck when image, client, login, proxy, model access or host networking changes;
missing local artifacts require recovery rather than an assumed working route.
The repaired `med run --agent-env-file` path also passed the same toy in the
isolated `.local/model-route-smoke-20260923/workbench/`, attempt
`attempt-4b916c8a4a33420d`, with unchanged frozen bytes and a collected passing
observation. Earlier auth usage was recorded in historical launch-scope receipts
and local configurations, but was missing from this daily launch guide.

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
