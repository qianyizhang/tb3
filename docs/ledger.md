# Findings and experiment ledger

All entries dated 2026-09-12. Research claims and ranked alternatives live in [research.md](research.md); acceptance rules in [requirements.md](requirements.md). Append outcomes, including failures. No model difficulty claims without completed verifiers.

| ID | Attempt / finding | Result | Evidence / next action |
| --- | --- | --- | --- |
| S01 | Initial host inventory | Docker, Colima, Podman and Apple container absent; no Docker socket. macOS arm64. | User subsequently authorized install/repair. |
| S02 | Global `codex --version` | Failed: missing optional package `@openai/codex-darwin-arm64`. | Same-version reinstall restored the runtime; CLI 0.147.0 and ChatGPT login verified. See codex-repair.md. No model trial occurred. |
| S03 | Upstream fetch in restricted shell | Failed connecting to configured localhost proxy; escalated public clone succeeded. | `.cache/terminal-bench` at `e2995b9`; no upstream changes. |
| S04 | Upstream sanity audit by Terra/high | Completed source/config review; found stale CONTRIBUTING network example and split Harbor versions. | requirements.md and configs/upstream-lock.json. |
| S05 | Workspace Harbor installation | 0.14.0 in `.venv`; 0.18.0 in `.venv-validation`. Version commands pass. | Separate dependency lock files in configs/. |
| S06 | Docker install | Homebrew installed colima 0.10.3, docker CLI 29.8.0, Compose 5.5.1, Lima 2.2.0. | Engine 29.5.2 started in Colima; `hello-world` pulled and ran successfully. |
| I01 | Incident-backed shortlist | Four ranked ideas; external-input cache repair selected for one small probe. | research.md contains sources, inference, estimates and rejected ideas. Difficulty unproven. |

| S07 | Docker Compose integration | Plugin initially not discovered; added Homebrew plugin directory preserving Docker config. `docker compose version` now passes. | Compose 5.5.1. |
| S08 | Native Docker smoke | `docker run --rm hello-world` completed, reward not applicable. | Image sha256:5e23090353324d887c48ad5e5c56d294eab81588df9605b07d1afe895f9cc8f8; arm64. |

| S09 | Docker image-build tooling | Installed Buildx 0.37.0 after detecting the missing Compose build prerequisite. | Plugin uses the same configured discovery path. |
| I02 | Independent Terra/high verifier review | Found fake-hit loophole, missing cases and timeout/read hazards in initial probe. | Fixed before running; findings and fixes retained in probe authoring/review.md. |

| S10 | Static runner child Python | Initial 10 failures included 9 Python3.9/tomllib tool errors; fixed child PATH to the explicit .venv Python3.12. | Historical manifests retained; not counted as task/model failures. |
| S11 | Static verifier parent-dir check | Runtime mkdir already worked, but CI requires literal RUN mkdir. Split the Dockerfile line; now 21/22 static checks pass. | runs/static-20260912T051959761015Z; only intentionally absent human README sections fail. |
| P01 | Docker Harbor0.18 oracle, v1 | Reward 1, 0 exceptions, 25s including build/teardown. | runs/cache-oracle-20260912; final snapshot revalidation passed in P03. |
| P02 | Docker Harbor0.18 nop, v1 | Reward0, 0 exceptions, 24s; five stale-input cases fail as expected. | runs/cache-nop-20260912. |

| P03 | Final frozen Docker controls | Oracle1 and nop0, both 0 exceptions, approximately 24s each. | runs/cache-{oracle,nop}-final-20260912; freeze.json. |
| P04 | First Terra/high Harbor attempt | **Infrastructure failure before model execution**: apt could not resolve Debian; NonZeroAgentExitCodeError. No verifier. | runs/cache-terra-high-20260912. Do not count its displayed mean0 as a model failure. |
| S12 | Compose DNS diagnosis/repair | Default bridge resolves; custom bridge lacked upstream DNS. Explicit 8.8.8.8 resolved and fetched HTTPS200; persisted tested DNS in Colima docker configuration. | Custom network now resolves normally and fetches HTTPS200 after restart; see docs/evidence/docker-compose-network.txt. Retry retained separately. |

| S13 | Unchanged static scripts inside Linux Docker | **21/22 passed**; only absent human-authored README sections fail. | runs/static-20260912T053102084122Z; docs/evidence/static-linux-summary.json. |
| P05 | Second Terra/high attempt after DNS repair | Codex installed; direct ChatGPT requests repeatedly timed out. Stopped with SIGINT after 337s; no verified model result. | runs/cache-terra-high-retry-20260912; infrastructure-only, not a model failure. |
| S14 | Host proxy connectivity | Existing proxy at VM host 192.168.5.2:10808 reaches ChatGPT (HTTP403 anonymous response instead of timeout). | Explicit per-agent proxy passed for next attempt; does not modify task or host auth. |

| P06 | Terra/high via existing proxy, frozen task | **Reward 1; all 10 verifier cases pass; zero exceptions.** 145s total (rounded), 84.943s agent execution, 12.542s verifier phase including container overhead. | runs/cache-terra-high-proxy-20260912; docs/evidence/trial-summary.json and terra-verifier.json. |
| I03 | Cache-probe disposition | Successful setup/calibration, insufficient difficulty for final submission. No Sol/Opus runs on this toy. | Source-linked research downgraded to feasibility-only; seek authentic multi-step work before promotion. |
| S15 | Completion checks | Docker daemon, Compose, Buildx and both Harbor versions work; 10 runner unit tests passed; no trial containers left running. | docs/evidence/doctor.json; root README. |
| S16 | Cost metadata warning | LiteLLM could not refresh its remote cost map because optional socksio is absent; used local map. Run/verifier completed. | Subscription usage is not an API invoice; do not treat estimated cost as actual billed spend. |

## Denominators

Completed early model diagnostics: **1 valid Terra/high pass**, plus **2 infrastructure-only attempts**. Docker controls: **2 oracle passes and 2 nop failures** across the documented Dockerfile syntax revision. These are calibration controls, not final-task qualification.

Required final standard trials: **0/6**. Required final adversarial trials: **0/2**. No final task selected or submission approved. Setup probes and Terra research reviews do not increase these counts.
