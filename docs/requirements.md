# TB3 requirements and evidence boundaries

Checked 2026-09-12 against terminal-bench commit `e2995b93b0a46edee7bc9942ea5622411a6d5bb9`. The assignment is [task.md](task.md). This document records rules, not completed checks.

## Source of truth

| Authority | What it governs |
| --- | --- |
| [Contribution call](https://www.tbench.ai/news/tb3-contribution-call) | Public contribution goals; its historical May merge window is not a verified current deadline. The seven-day delivery requirement comes from task.md. |
| [Contributing guide](https://github.com/harbor-framework/terminal-bench/blob/e2995b93b0a46edee7bc9942ea5622411a6d5bb9/CONTRIBUTING.md) | Task format, authoring and submission requirements. Four task README explanations must be human-written; do not fabricate experience or present generated prose as human-authored. |
| [Proposal rubric](https://github.com/harbor-framework/terminal-bench/blob/e2995b93b0a46edee7bc9942ea5622411a6d5bb9/docs/prompts/task-proposal.md) | Realistic paid work, essential difficulty, complete specification, efficient outcome verification. Fast execution can coexist with hard reasoning. |
| [Review guide](https://github.com/harbor-framework/terminal-bench/blob/e2995b93b0a46edee7bc9942ea5622411a6d5bb9/docs/REVIEWING.md) | Human review of instruction, verifier, solution and environment; rubric is a first-pass signal. |
| [Automation guide](https://github.com/harbor-framework/terminal-bench/blob/e2995b93b0a46edee7bc9942ea5622411a6d5bb9/docs/TASK_REVIEW_AUTOMATION.md) | Static/rubric/validation, trial analysis and maintainer slash commands. |
| [Run defaults](https://github.com/harbor-framework/terminal-bench/blob/e2995b93b0a46edee7bc9942ea5622411a6d5bb9/.github/harbor-run-defaults.yml) and workflows | Exact executable settings below. Prefer workflow behavior over stale examples in prose. |

## Frozen trial plan

| Stage | Harbor | Agent/model | Attempts | Acceptance evidence |
| --- | --- | --- | ---: | --- |
| Early sanity | 0.14.0 | codex / openai/gpt-5.6-terra, high | 1 | Diagnostic only; success means the environment/task works. |
| Oracle | 0.18.0 | oracle | 1 | Completed verifier, reward 1, no infrastructure exception. |
| Nop | 0.18.0 | nop | 1 | Completed verifier, reward 0. |
| Standard | 0.14.0 | codex / openai/gpt-5.6-sol, xhigh | 3 | All three genuine task failures under the assignment. |
| Standard | 0.14.0 | claude-code / anthropic/claude-opus-5, max | 3 | Same; set CLAUDE_CODE_MAX_OUTPUT_TOKENS=128000. |
| Adversarial | 0.14.0 | Both standard configurations | 1 each | Each completed verifier must return exactly zero, using the pinned hack prompt. |
| Trial analysis | 0.14.0 | sonnet | per completed job | Inspect specification, reward hacking, difficulty crux, refusal and low-timeout analysis. |

Upstream `/run` and `/validate` default to **Modal**. Local Docker is an explicit backend override permitted by the assignment, not identical infrastructure. Local subagents are weaker **mirror proxies**, never official Codex CLI trials or independent security isolation. Sol/Opus trials are reserved for a mature candidate, not this setup pass.

The current review workflow uses **Harbor 0.18.0 `harbor exec`**, stages the candidate and implementation rubric into an ephemeral Ubuntu task, uses `claude-code -m sonnet`, and validates every criterion in the resulting verdict JSON. `harbor check` is an advisory local shortcut, not that exact CI review. No review, trial artifacts or code should be uploaded automatically by our local scripts.

## Implementation gates

Run the exact 22 checks listed in `.github/workflows/static-checks.yml` from `scripts/checks/`. Fail on missing inputs/check scripts and retain tool errors separately. macOS BSD tools are not identical to Ubuntu CI; run the unchanged scripts on Linux for authoritative static results.

Required separate verifier: `environment_mode="separate"`; top-level `artifacts`; `tests/Dockerfile` owns `/tests` and pre-creates artifact parents. Bake verifier tools/dependencies into the image. Transfer only deliverables. Never copy tests or oracle into the agent image. When executing submitted code, isolate it from verifier/reward permissions too.

Use `network_mode="public"`; **omit `allow_internet`**: the live static checks reject explicit true as well as false despite an older CONTRIBUTING example. Do not disable Internet to manufacture difficulty. Use portable base images, pinned pip versions, unpinned apt versions with update/cleanup, no bare nproc, and no host bind mounts in task Compose files. Use canaries, absolute artifact paths, a task package name, complete metadata, a short slug, and the exact instruction timeout trailer.

## Classification and remaining submission work

Record frozen task tree, upstream commit, package versions, full command/configuration, elapsed time, raw result, verifier output and trajectory for every attempt. A zero with agent crash, API/rate-limit failure, container failure, timeout or missing verifier is **not a model failure**. A completed easy pass is evidence against the candidate's difficulty; do not discard it or add arbitrary constraints to force failure.

This workspace's probes are feasibility experiments. A final submission still needs a selected sufficiently hard original task, human-authored sections/experience, author metadata, complete static/rubric/oracle/nop gates, six standard trials, two adversarial trials, and failure analysis. Maintainer proposal feedback is recommended before major implementation; no messages, PRs or public repository have been sent by this setup work.
