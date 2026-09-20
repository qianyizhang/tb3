# BR-041 — CTA-only named coronary tracing

See the [predeclared plan](../../../../docs/research-rounds/BR-041-image-only-centerline.md).

- `prepare.py` creates the image-only task from unchanged BR-030 bytes, tests local positive/negative controls and freezes every task file. Refuses overwrite.
- `run_trials.py` runs Docker oracle/no-op and one Terra/high attempt, with no model retries; requires the existing private runtime configuration and Docker access. Do not rerun a completed round.
- `collect.py` verifies the freeze and equal task checksums, replays saved artifacts and independently checks distances using a dense pairwise matrix.
- `plot.py` writes local comparison projections after collection.

Use `.venv-br030/bin/python` from the repository root. Raw data, private configuration and outputs stay in ignored `runs/` paths. No source acquisition or clinical validation is performed by these scripts. The prepared task's inherited TOML description mentions the old geometry workflow; its actual instruction, delivered files and standalone verifier govern this tracing-only pilot.

S01 comparison: `run_sol.py` runs one fresh Sol/xhigh attempt on unchanged task bytes, reusing verified controls. `collect_sol.py` writes a separate comparison receipt preserving the original Terra receipt; `branch_sol.py` checks the alternate released branch after completion, and `plot_sol.py` shows both branch references. Do not rerun the completed model job.

A01 comparison: `run_astra.py` runs one fresh Astra/xhigh attempt on unchanged task bytes. `collect_astra.py` preserves earlier receipts and compares all five runs; `branch_astra.py`, `audit_astra.py`, and `plot_astra.py` diagnose branch/extent disagreement without changing the submitted artifact or score. The runtime reference-assisted truncation diagnostic is not a model success.
