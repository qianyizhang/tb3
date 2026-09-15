# Findings and experiment ledger

Initial entries are dated 2026-09-12; later rounds carry their own dates. Research claims and ranked alternatives live in [research.md](research.md); acceptance rules in [requirements.md](requirements.md). Append outcomes, including failures. No model difficulty claims without completed verifiers.

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
| G08 | Terra/high geometry diagnostic | **Completed pass**, reward 1, no exception; 494.711s total, 421.371s agent, 23.042s verifier. All four semantic queries and 14 historical diagnostics pass. | runs/clipper-terra-high-v3-20260912; matching final control/model checksum. Retire snapshot from difficulty selection; Sol remains unused. |
| G09 | Numerical source screen | SciPy/ForwardDiff leads recorded. A limited execution of historical SciPy numerical blocks confirms an incremental-update sign inconsistency; no full-package reproduction or model trial. | [Numerical candidates](research-numerical-candidates.md); SciPy full public-API reproduction ranks next; limited reference-check outputs and source hashes are retained in docs/evidence/. |

## Denominators

Completed local pilots so far: **16 valid Terra/high passes, 4 Sol/max passes, 4 Astra/max passes, 0 genuine model failures**, plus **2 infrastructure-only model attempts** from initial setup. Authoring oracle failures are separate controls and never model failures. Six Terra passes predate BR-001; six are in the [completed BR-001 round](research-brainstorm-experiments-20260914.md). Four further Terra passes belong to [BR-003](research-rounds/BR-003-work-history.md). The eight Sol/Astra passes belong to [BR-002](research-rounds/BR-002-results.md); different tasks and protocols are not pooled into a model ranking. Detailed earlier controls and snapshot revisions remain preserved in [initial summary](evidence/trial-summary.json), [harder summary](evidence/harder-trial-summary.json), [geometry summary](evidence/clipper-trial-summary.json), and [homology summary](evidence/homology-trial-summary.json).

Required final standard trials: **0/6**. Required final adversarial trials: **0/2**. No final task selected. Completed local rounds are indexed in the [round register](research-rounds.md).

## Diverse short-horizon screen

| ID | Attempt / finding | Result | Evidence / next action |
| --- | --- | --- | --- |
| D01 | User narrowed research scope | Explicitly stay away from security tasks; favor hard but less complex, short-horizon work. Eight fields/task directions screened; seven new idea records. Historical HTTP framing lead parked. | [AGENTS.md](../AGENTS.md), [survey](research-short-horizon.md). |
| D02 | Compact homology certificate prototype | One Python interface; independent exact determinant/rank/identity verifier. Six focused mutation/acceptance tests passed. Custom canary/category metadata corrected before controls. | probes/homology-basis and [static summary](evidence/homology-static-summary.json). |
| D03 | Matching Docker controls | Oracle 1, 43/43 cases, 29.951s; nop 0, 37/43 cases fail, 24.536s; no exceptions and matching checksum. | [Freeze](evidence/homology-pilot-freeze.json), [commands](evidence/homology-evaluation-plan.sh). |
| D04 | Homology Terra/high | **Completed pass**, 43/43 cases, no exception; 399.743s total, 340.514s agent, 12.735s verifier phase. | [Trial summary](evidence/homology-trial-summary.json), [trajectory review](../catalog/analyses/homology-calibration.md). Retire; no failure-confirmation or Sol trial. |
| D05 | Numerical public-class follow-up | Both unchanged historical modules loaded with actual NumPy/SciPy helpers. Incremental linear output is 0.8 instead of 0.5 in the published patch; high-degree constructor fix works. | [Result](evidence/barycentric-public-api.json). Full historical module API witness, not a historical full-package build or model trial. Independent complete repair oracle is next. |
| D06 | Repository validation | Staged artifact gate and 61 offline tests pass on Python 3.12.13. Local probe static sanity 21/22; human-authored task README absent. | runs/short-horizon-make-check.log. No final qualification claimed. |

## Sequential brainstorm round (2026-09-14, complete)

The user requested design and trials one by one from “Brainstorm New Tasks”.
All six original pilots completed once under Terra/high with 1,800 seconds
available. Each had matching healthy oracle 1 / nop 0 controls. Published
source receipts are calibration evidence and remain distinct from this ledger.

| ID | Diagnostic | Result | Evidence |
| --- | --- | --- | --- |
| B01 | MR frame association | Pass 36/36; 150.284 agent seconds; retired | [Summary](evidence/mr-trial-summary.json) |
| B02 | Quadrilateral face-flux reconstruction | Pass 72/72; 34.529 seconds; retired | [Summary](evidence/quad-trial-summary.json) |
| B03 | Spectral projector gradient | Pass 24/24; 102.691 seconds; retired | [Summary](evidence/projector-trial-summary.json) |
| B04 | Clamped instrument calibration | Pass 20/20; 48.682 seconds; 42 measurements; retired | [Summary](evidence/instrument-trial-summary.json) |
| B05 | Physical stress/virial conversion | Pass 36/36; 27.022 seconds; retired | [Summary](evidence/stress-trial-summary.json) |
| B06 | Collision-event derivative | Pass 24/24; 46.887 seconds; retired | [Summary](evidence/collision-trial-summary.json) |

The [round receipt](evidence/brainstorm-round-summary.json) verifies sequential
model timestamps and unchanged frozen bytes. There were no model exceptions,
repeats, Sol/Opus runs or genuine failures in this round. Two superseded MR
draft controls and a corrected pre-freeze extxyz package build are retained;
neither is a model failure. The proposed compact failure mechanisms were not
observed. Final submission counts remain 0/6 standard and 0/2 adversarial.

## BR-002 capability pilots (2026-09-14, complete)

The user authorized testing the four newly organized designs. The
[predeclared plan](research-rounds/BR-002-execution.md) calls for Sol/max then
Astra/max on each natural task, with 1,800 seconds available and identical
task bytes/access. All eight model runs completed normally and passed. No
repeat or ablation was triggered; all four snapshots are retired.

| Scoped ID | Diagnostic | Sol/max | Astra/max | Evidence |
| --- | --- | --- | --- | --- |
| BR-002/D02 | RF wave composition | 32/32, 203.718 agent seconds | 32/32, 214.608 seconds | [Summary](evidence/br002-rf-summary.json) |
| BR-002/D04 | Score sounding events | Exact 96/96 events, F1 1.00, 849.882 seconds | Exact 96/96 events, F1 1.00, 195.167 seconds | [Summary](evidence/br002-score-summary.json) |
| BR-002/D03 | Actuator memory | 12/12 histories, 68.715 seconds | 12/12 histories, 96.648 seconds | [Summary](evidence/br002-actuator-summary.json) |
| BR-002/D01 | Moving-frame velocity | 24/24, 132.703 seconds | 24/24, 184.816 seconds | [Summary](evidence/br002-frame-summary.json) |

The [round receipt](evidence/br002-round-summary.json) verifies unchanged frozen
bytes, matching healthy oracle/nop checksums, model/effort/CLI settings and
sequential timestamps. Eight final-snapshot controls and four superseded
pre-freeze score/actuator controls are retained separately from model attempts.
The [result analysis](research-rounds/BR-002-results.md) links submitted-artifact
inspections and the source 041/047 audit. H-D01–H-D04 are unsupported on these
snapshots; one pair per task cannot estimate a population capability gap.

## BR-003 work-history prototypes (2026-09-15, complete)

Nine selected historical conversations supplied recurring PDF crop and Tavern
lifecycle evidence. Later user messages added anatomy inference and SVG physical
planes. These source reports are distinct from the four original controlled
Terra/high diagnostic attempts. All model runs completed normally; all passed.

| Scoped ID | Diagnostic | Result | Evidence |
| --- | --- | --- | --- |
| BR-003/H01 | PDF table lineage | 4/4 checks; 146.066 agent seconds; retired | [Probe](../probes/pdf-table-lineage/instruction.md), [controls](evidence/br003-pdf-author-controls.json) |
| BR-003/H02 | Durable chat recovery | 22/22 traces; 197.254 agent seconds; retired | [Probe](../probes/chat-round-recovery/instruction.md), [controls](evidence/br003-chat-author-controls.json) |
| BR-003/H03 | Anatomical DICOM annotation QA | 5/5 packets; 293.135 agent seconds; retired | [Probe](../probes/dicom-label-audit/instruction.md), [controls](evidence/br003-audit-author-controls.json) |
| BR-003/H04 | Patient-coordinate SVG | 12/12 views, all 72 Dice comparisons 1.0; 217.431 agent seconds; retired | [Probe](../probes/dicom-triplanar-svg/instruction.md), [controls](evidence/br003-svg-author-controls.json) |

Eight matching Docker controls passed oracle=1/nop=0. Four sequential model
trials had no exceptions and no retries. [Receipts](evidence/br003-round-summary.json)
retain exact historical checksums, source freezes, raw output hashes and timings.
[Inspection](../catalog/analyses/br003-work-history.md) records successful repairs
and fixed-cohort limits. A local report-server preview was rejected before
execution because its proposed directory also contained private history exports;
a file preview was used instead. This is not a model or task failure.

Final qualification counts remain 0/6 standard and 0/2 adversarial. The source
selection lessons and parked vector-diagram lead belong to the
[round record](research-rounds/BR-003-work-history.md).

## BR-005 scaffolding correction and retest (2026-09-15, complete)

The [frozen plan](research-rounds/BR-005-scaffolding-retest.md) removes the central
supplied ingredients from five previously passing packages. Original snapshots,
grader inputs, tolerances and 1,800-second budgets are preserved. Six sequential
model runs complete normally; ten matching oracle=1/nop=0 controls are healthy.

| Scoped condition | Model / effort | Result | Agent seconds |
| --- | --- | --- | --- |
| BR-005/collision-vjp | Terra/high | Pass 24/24; revised snapshot retired | 88.072 |
| BR-005/extxyz-stress | Terra/high | Pass 36/36; revised snapshot retired | 48.421 |
| BR-005/quad-face-flux | Terra/high | Pass 72/72; revised snapshot retired | 85.350 |
| BR-005/actuator-memory | Sol/max | Pass 12/12 histories; revised snapshot retired | 139.551 |
| BR-005/actuator-memory | Astra/max | Pass 12/12 histories; revised snapshot retired | 103.305 |
| BR-005/clipper-polytree | Terra/high | Genuine semantic failure on `holes5`; retained for separately scoped follow-up | 513.989 |

The Clipper author replay matches three of four semantic cases. The failed
case has four roots/one hole instead of three roots/two holes, independently
confirmed by exact rectangular-cell topology. The worker's final 392-test
library pass omits its failed historical PolyTree diagnostics. No private
answer reads, online solution fetches or delegation are observed in the six
traces. There are no model exceptions, retries or extra model attempts.

[Results and limits](research-rounds/BR-005-results.md),
[round receipt](evidence/br005-round-summary.json) and
[failure audit](evidence/br005-clipper-failure.json) preserve the evidence.
This adds five passes and one reviewed genuine failure to the preceding
24-pass cohort. It is a package comparison with one attempt per model/condition,
not a repeatable failure rate or a prompt-only causal ablation. No final standard
or adversarial qualification run was performed.


## BR-004 localized anatomical audit (2026-09-15, inconclusive)

The user authorized an eight-patient subtle-error test and one fresh Terra/max
attempt. The frozen task has 86 focus-label decisions, four unmodified controls
and five altered labels across four patients. Exact labels and 3-mm-tolerant
spatial witnesses give deterministic grading. Author geometry/truth checks and
matching normal Harbor oracle 1 / nop 0 controls passed.

**Terra/max reached the 1,800-second limit with AgentTimeoutError.** The answer
artifact equals the empty starter byte-for-byte. Its reward 0 and 4/8 passing
cases are unfinished-artifact checks, not anatomical accuracy. This round adds
one excluded timeout, zero completed model accuracy results and zero genuine
failures. It does not change the counts of healthy completed model trials.

All frozen bytes remain unchanged. V1 is parked; a smaller one-family batch and
complete source-region adjudication are proposed before another trial. No
confirmed postoperative history or specialist clinical certification is claimed.
See the [round](research-rounds/BR-004-dicom-annotation-revisit.md),
[receipt](evidence/br004-anatomy-round-summary.json), and
[authored analysis](../catalog/analyses/br004-anatomy-audit.md).

## BR-007 Clipper topology coverage (2026-09-15, complete)

The [predeclared study](research-rounds/BR-007-clipper-sol-xhigh.md) expanded the
reference-removed source repair to 18 base layouts and 144 transformed/order
variants, with independently computed contour truth. Matched Harbor controls
returned oracle 1 / nop 0. Native controls reject the BR-005 Terra artifact on
72 cases; removing persistence updates alone passes and is not a detected bug.

**Sol/xhigh passes 144/144**, completing normally in 1,315.843 of 1,800 seconds.
The source replay matches. The 55-call trace shows a substantive boundary
normalization/containment repair, with no observed private-reference read,
online solution fetch or delegation. No retry or post-answer test change.
The requested Sol difficulty target was not reached; retire this exact condition
for Sol while preserving BR-005's distinct Terra failure. One diagnostic is not
a failure rate or final qualification.

[Results and trace anchors](research-rounds/BR-007-results.md),
[round summary](evidence/br007-round-summary.json),
[freeze](evidence/br007-clipper-freeze.json), and
[controls](evidence/br007-author-controls.json) retain the evidence.

## BR-004 single-patient resource screen (2026-09-15, complete)

One fresh Terra/max attempt on each of eight unchanged patient subsets,
sequentially, with zero retries and the normal 1,800-second allowance.
**All eight completed normally: five raw passes, three raw misses.** Matched
oracle/nop controls and independent re-scoring agree; all frozen task bytes,
patient files, protocol and builder remain unchanged.

Review retains **two genuine controlled-defect misses** (cases 83 and 32), four
solved controls (74, 19, 28, 95), and two source holds (46 raw pass, 61 raw miss).
Case-61 reported unadjudicated original-source regions and did not locate the
planted omission; it is not counted as a genuine overall task failure.
Case-46's hold was declared before testing. Keep all eight resource rows.

**Case-32 leads:** 10.21 agent minutes, 23,713 output tokens, 98,915 uncached input
tokens, estimated $0.857. Its 63-voxel kidney extension was missed despite
reviewed views covering the region. Compared with case-83, it used 35.9% less
time and 27.6% fewer output tokens. No reliable failure probability follows
from one observation. Reduced anatomical focus and a supplied viewer are
proposed next contrasts; no additional model run was launched.

Total model resources: 117.80 agent minutes, 262,186 output tokens, 1,624,554
uncached input tokens and estimated $13.257. The sequential benchmark took
136.22 minutes including controls/setup; this is separate from the earlier
batch timeout. No specialist clinical or final submission qualification is
claimed. See the [analysis](../catalog/analyses/br004-single-patient.md),
[frozen protocol](research-rounds/BR-004-single-patient-benchmark.md),
[summary](evidence/br004-single-patient-summary.json), and
[case reviews](evidence/br004-single-patient-reviews.json).
