# TB3 task workshop

Local setup, incident research, and inexpensive feasibility probes for [the assignment](docs/task.md). This is not a completed TB3 submission. The six final standard trials and two adversarial trials have not been run.

Docker runs through Colima on this Mac. The Codex CLI is repaired and retains its ChatGPT login. Harbor's trial and validation versions are installed separately and pinned to the inspected CI snapshot.

The [benchmark-backed survey](docs/research-benchmark-backed.md) is the current selection authority. It inspects Terminal-Bench-Science's 70-task inventory, five compact tasks with Terra 0/3, and their public trial evidence, alongside Harbor-Index and other research benchmarks. Baseline-free damage localization is the strongest current lead: one function returning a coordinate, three valid but inaccurate Terra submissions, and fast verification. These are external published results, not new local trials or original submissions.

The [100-card broad task bank](docs/research-broad-task-bank.md) expands this into 23 broad directions, including CAD, hardware, SQL, spreadsheets, compilers, typography, GIS and media. It adds six completed Terra/max CAD observations, records HN/Reddit leads and counterexamples, and gives every candidate a small deliverable, proposed verifier and easy-baseline exclusion. These are research candidates, not 100 runnable tasks or demonstrated Terra failures. Search the catalog for `broad-bank-100`.

The [first screening pass](docs/research-screening-20260912.md) now records decisions for all 100: **2 advance to bounded reproduction, 50 hold, 48 reject**. It deepens 29 source audits, including local calculations or fixture checks for 14 cards, and corrects easy tasks, faulty references and unsupported extractions. The [sourcing methodology](docs/research-sourcing-methodology.md) records search strategy, provenance, exclusions and evidence gates. Search the catalog for `screen-advance`, `screen-hold` or `screen-reject`; this pass ran no model trials.

The [round-two search](docs/research-candidate-search-r2-20260912.md) adds **12 exact records: 9 hold, 3 reject** across circuits, netlists, linguistics, NMR and further science tasks. It records 24 actual queries, independent small checks and nine external Terra receipts (seven completed misses, two excluded timeouts). Search `candidate-search-r2`; the original 100-card snapshot and local trial ledger are unchanged.

The [sequential brainstorm experiments](docs/research-brainstorm-experiments-20260914.md) completed all four primary ideas and both reserves: MR frame association, quadrilateral flux, spectral-projector gradients, clamped-instrument calibration, stress conversion and collision derivatives. Each passed one Terra/high diagnostic with matching oracle/nop controls; all six are retired. The smaller original tasks did not inherit the published source failures.

Together with the six earlier retired snapshots, the local denominator is now **twelve valid Terra/high passes, zero genuine failures, and two historical infrastructure-only attempts**. The [earlier short-horizon screen](docs/research-short-horizon.md) and [interpolation reproduction](docs/research-numerical-candidates.md) are retained; no local Sol/Opus trial has run.

Current research scope explicitly excludes security tasks and favors hard but less complex, short-horizon work: one conceptual crux, a small deliverable and fast independent verification. See [AGENTS.md](AGENTS.md) for the durable scope instructions.

| Start here | Purpose |
| --- | --- |
| [Setup](docs/setup.md) | Install/recreate environments, start Docker, subscription commands. |
| [Ledger](docs/ledger.md) | Successful and failed attempts, evidence and remaining trial counts. |
| [Sequential brainstorm experiments](docs/research-brainstorm-experiments-20260914.md) | Six completed original pilots, independent controls, frozen snapshots and clean Terra passes. |
| [Research](docs/research.md) | Initial firsthand sources and ideas. |
| [Harder screen](docs/harder-screen.md) | Broader incident research, measured trials, and promotion criteria. |
| [Short-horizon survey](docs/research-short-horizon.md) | Eight diverse directions, explicit non-security scope, homology pass and numerical follow-up. |
| [Benchmark-backed survey](docs/research-benchmark-backed.md) | Current shortlist: published failures, task-level audit, compactness, fairness concerns and source-selection decisions. |
| [100-card broad task bank](docs/research-broad-task-bank.md) | Diverse experiment candidates, corrected CAD receipts, community anecdotes, evidence labels and preparation queue. |
| [Sourcing methodology](docs/research-sourcing-methodology.md) | Search method, query examples, provenance, exclusion and screening rules. |
| [100-card screening](docs/research-screening-20260912.md) | Every decision, 14 bounded calculation/fixture checks, source corrections and next gates. |
| [Round-two candidate search](docs/research-candidate-search-r2-20260912.md) | 12 new exact records, 24-query search log, completed-failure audits and rejected long/ambiguous formulations. |
| [Catalog](docs/catalog.md) | Searchable idea/trial records and local browser report. |
| [Requirements](docs/requirements.md) | Frozen CI/defaults, discrepancies, human-authored submission requirements. |
| [Codex repair](docs/codex-repair.md) | Diagnosis, repair command and checks. |
| [Cache probe](probes/cache-invalidation/README.md) | Small setup/calibration task; difficulty remains unproven. |

From this directory:

```bash
bash scripts/bootstrap.sh
.venv/bin/python scripts/tb3.py doctor --backend docker
.venv/bin/python scripts/tb3.py static probes/cache-invalidation
.venv/bin/python scripts/tb3.py plan probes/cache-invalidation --backend docker \
  --agent-proxy http://192.168.5.2:10808
```

`plan` only prints commands; it never starts a model or uploads results. The raw static-check results are retained even if checks fail. The probe deliberately lacks final human-authored submission material; a green runtime check alone cannot make it submission-ready.

Raw `runs/` files stay local and are ignored by Git; concise checked-in evidence is under `docs/evidence/`. Inspect raw trajectories before publishing them. No GitHub remote or public submission was created.

Use Terra/high for initial diagnostics. Reserve Sol/xhigh and Opus/max for a frozen candidate that warrants their cost. Failed infrastructure, timeouts and mirrored subagent runs never count as genuine model failures. The explicit network proxy used by real Harbor runs does not change their Docker execution scope.
