# TB3 task workshop

Local setup, incident research, and inexpensive feasibility probes for [the assignment](docs/task.md). This is not a completed TB3 submission. The six final standard trials and two adversarial trials have not been run.

Docker runs through Colima on this Mac. The Codex CLI is repaired and retains its ChatGPT login. Harbor's trial and validation versions are installed separately and pinned to the inspected CI snapshot.

The [benchmark-backed survey](docs/research-benchmark-backed.md) is the current selection authority. It inspects Terminal-Bench-Science's 70-task inventory, five compact tasks with Terra 0/3, and their public trial evidence, alongside Harbor-Index and other research benchmarks. Baseline-free damage localization is the strongest current lead: one function returning a coordinate, three valid but inaccurate Terra submissions, and fast verification. These are external published results, not new local trials or original submissions.

The [100-card broad task bank](docs/research-broad-task-bank.md) expands this into 23 broad directions, including CAD, hardware, SQL, spreadsheets, compilers, typography, GIS and media. It adds six completed Terra/max CAD observations, records HN/Reddit leads and counterexamples, and gives every candidate a small deliverable, proposed verifier and easy-baseline exclusion. These are research candidates, not 100 runnable tasks or demonstrated Terra failures. Search the catalog for `broad-bank-100`.

Six local frozen snapshots completed valid Terra/high passes and remain retired: cache invalidation, nested Dremel assembly, Ninja dynamic dependencies, SQLite EXISTS optimization, Clipper2 PolyTree hierarchy, and integral homology bases. The [earlier short-horizon screen](docs/research-short-horizon.md) and [interpolation reproduction](docs/research-numerical-candidates.md) are retained. The local denominator remains six passes, zero genuine failures, and two infrastructure-only attempts; no local Sol/Opus trial has run.

Current research scope explicitly excludes security tasks and favors hard but less complex, short-horizon work: one conceptual crux, a small deliverable and fast independent verification. See [AGENTS.md](AGENTS.md) for the durable scope instructions.

| Start here | Purpose |
| --- | --- |
| [Setup](docs/setup.md) | Install/recreate environments, start Docker, subscription commands. |
| [Ledger](docs/ledger.md) | Successful and failed attempts, evidence and remaining trial counts. |
| [Research](docs/research.md) | Initial firsthand sources and ideas. |
| [Harder screen](docs/harder-screen.md) | Broader incident research, measured trials, and promotion criteria. |
| [Short-horizon survey](docs/research-short-horizon.md) | Eight diverse directions, explicit non-security scope, homology pass and numerical follow-up. |
| [Benchmark-backed survey](docs/research-benchmark-backed.md) | Current shortlist: published failures, task-level audit, compactness, fairness concerns and source-selection decisions. |
| [100-card broad task bank](docs/research-broad-task-bank.md) | Diverse experiment candidates, corrected CAD receipts, community anecdotes, evidence labels and preparation queue. |
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
