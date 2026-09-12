# TB3 task workshop

Local setup, incident research, and inexpensive feasibility probes for [the assignment](docs/task.md). This is not a completed TB3 submission. The six final standard trials and two adversarial trials have not been run.

Docker runs through Colima on this Mac. The Codex CLI is repaired and retains its ChatGPT login. Harbor's trial and validation versions are installed separately and pinned to the inspected CI snapshot.

Docker controls and Terra/high trials pass for cache invalidation, nested Dremel assembly, Ninja dynamic dependencies, SQLite EXISTS optimization, and Clipper2 PolyTree hierarchy. These five snapshots are retired from difficulty selection. The geometry pickup completed in 8m15s; its controls, grading fixes and result are recorded in the [pickup](docs/pickup-20260912.md). A [numerical interpolation lead](docs/research-numerical-candidates.md) has a limited local reference check and still needs full public-API reproduction. No genuine Terra failure has been observed; Sol remains unused. Two earlier network failures are retained as infrastructure errors.

| Start here | Purpose |
| --- | --- |
| [Setup](docs/setup.md) | Install/recreate environments, start Docker, subscription commands. |
| [Ledger](docs/ledger.md) | Successful and failed attempts, evidence and remaining trial counts. |
| [Research](docs/research.md) | Initial firsthand sources and ideas. |
| [Harder screen](docs/harder-screen.md) | Broader incident research, measured trials, and promotion criteria. |
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
