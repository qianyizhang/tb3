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

## Harder screen (active)

| ID | Attempt / finding | Result | Evidence / next action |
| --- | --- | --- | --- |
| H01 | Broader primary-source research | Actual Ninja and SQLite source regressions selected; nested decoder extracted as a fast internal-reader task. Two miniature DataFusion engines rejected; Clipper2 port history under executable review. | [Harder screen](harder-screen.md) and linked domain ledgers. |
| H02 | Dremel authoring review | Fixed missing repeated-group metadata, zero rows, reward entry point, canaries and privilege handling before evaluation. | probes/dremel-assembly/authoring/notes.md; no model failure. |
| H03 | Frozen Dremel Docker controls | Oracle1 and nop0, zero exceptions, about24s each. | runs/dremel-{oracle,nop}-20260912. |
| H04 | Dremel Terra/high | **Completed pass**, reward1; 320.557s total, 255.573s agent. | runs/dremel-terra-high-20260912; retired from difficulty selection, Sol unused. |
| H05 | Cold Ninja Docker packages | Old authoring build clients kept non-proxy APT work alive. Confirmed owners stopped; no-cache proxy build56.851s, Ninja10.1s; portable warmbuild0.084s. | runs/ninja-network-diagnostic-* and ninja-warm-after-cleanup.log; infrastructure only. |
| H06 | First Ninja Docker oracle | Reward0: verifier removed executable mode from inline.sh. | runs/ninja-oracle-20260912; authoring fault fixed, no model run. |
| H07 | Second Ninja Docker oracle | Reward0: cp propagated read-only fixture permissions onto generated outputs. | runs/ninja-oracle-final-20260912; producer uses ordinary writable redirection, contract unchanged. |
| H08 | Corrected Ninja Docker controls | Oracle1 and nop0, zero exceptions,49s/37s including rebuild. | runs/ninja-oracle-v3-20260912 and ninja-nop-20260912. |
| H09 | First SQLite Docker oracle | Reward0: image lacked patch utility used by solve.sh. | runs/sqlite-oracle-20260912; same upstream correction now applied using checked Python. |
| H10 | Corrected SQLite Docker controls | Oracle1 and nop0, zero exceptions,37s/36s. | runs/sqlite-{oracle-final,nop}-20260912. |
| H11 | SQLite Terra/high | **Completed pass**, reward1;204.778s total,133.447s agent. Focused optimizer guard accepted. | runs/sqlite-terra-high-20260912; retired from Sol selection. |
| H12 | Ninja Terra/high | **Completed pass**, reward1;379.766s total,308.716s agent. Legitimate cross-file repair accepted. | runs/ninja-terra-high-20260912; retired from Sol selection. |
| H13 | Clipper2 historical source controls | Broken parent fails9/14 PolyTree tests; corrected source passes14/14. First Rust compile29.87s. | Geometry research and authoring evidence; these are source controls, not model failures. Semantic verifier review underway. |

## Non-security pickup

| ID | Attempt / finding | Result | Evidence / next action |
| --- | --- | --- | --- |
| G01 | Resume stopped source task | User excluded security tasks; geometry selected. Docker had no active containers or experiment writers. Prior saved results preserved. | [Pickup](pickup-20260912.md); source task `01a093fe-a6bb-7ef0-a1ca-da3b39e5aee2`. Platform research flags are not benchmark results. |
| G02 | Pre-trial geometry review | Fixed order-sensitive grading and duplicate-closing-vertex normalization; added tree consistency assertions and documented Cargo registration. | [Geometry review](geometry-review.md); 10 focused tests, 47 total tests pass. |
| G03 | Superseded first oracle | CancelledError, no accepted verifier reward; excluded control. No model run. | runs/clipper-oracle-pickup-20260912; preserved v1 freeze. |
| G04 | Revised v2 reference control | Oracle 1, no exception, 49.757s. Static check then required absolute paths in the local test command. | runs/clipper-oracle-v2-20260912; preserved v2 freeze. |
| G05 | Final v3 Docker controls | Oracle 1 / nop 0, matching Harbor task checksums, no exceptions; 49.916s / 26.597s. | [Freeze](evidence/clipper-pilot-freeze.json), [trial summary](evidence/clipper-trial-summary.json), [commands](evidence/clipper-evaluation-plan.sh). |
| G06 | Final local static sanity | 21/22 pass; only deliberately absent human-authored task README remains. macOS sanity, not Linux CI qualification. | [Static summary](evidence/clipper-static-summary.json); final submission remains incomplete. |
| G07 | Model launch approval review | First launch rejected before execution over export scope; inspected public source build context and explicit OpenAI subscription destination, then approval accepted. | [Launch scope](evidence/clipper-launch-scope.json); not a model attempt or failure. |
| G08 | Terra/high geometry diagnostic | Running on frozen v3, one attempt, 1800s agent allowance. | runs/clipper-terra-high-v3-20260912; inspect completed result and trajectory before classification. |
| G09 | Numerical source screen | SciPy/ForwardDiff leads recorded. A limited execution of historical SciPy numerical blocks confirms an incremental-update sign inconsistency; no full-package reproduction or model trial. | [Numerical candidates](research-numerical-candidates.md); SciPy full public-API reproduction ranks next; limited reference-check outputs and source hashes are retained in docs/evidence/. |

## Denominators

Completed early model diagnostics so far: **4 valid Terra/high passes**, **0 genuine model failures**, plus **2 infrastructure-only model attempts** from initial setup. Authoring oracle failures are separate controls and never model failures. Detailed controls and snapshot revisions are preserved in [initial summary](evidence/trial-summary.json) and [harder summary](evidence/harder-trial-summary.json).

Required final standard trials: **0/6**. Required final adversarial trials: **0/2**. No final task selected. See [harder screen](harder-screen.md) for active runs and the predeclared follow-up rule.
