# BR-040 — Sol/xhigh on frozen CT and MRI

User-authorized follow-up to BR-038/039. This code never changes those tasks.

- `run_trials.py preflight`: verify every frozen file and matched successful oracle / failing nop controls; retain a plan with original hashes. Refuses to overwrite the plan.
- `run_trials.py ct-full`, `ct-partial`, `mri32-full`: copy each earlier Terra configuration privately, change only the job identity and model/effort to `openai/gpt-5.6-sol` / `xhigh`, and execute one attempt with no retries. Check task bytes again afterward and compare Harbor task checksums. Keep at most two runs active.
- `collect.py`: replay each frozen scorer without importing into or modifying the frozen directory; independently calculate world distances; include the earlier Terra results and trace/image audit.
- `report.py`: generate local side-by-side per-landmark overlays and the authored results table.

Use `.venv-br033/bin/python`; set `MPLCONFIGDIR=/private/tmp/br040-mpl` for report rendering. Docker and provider execution use the existing `.venv/bin/harbor`. Provider configs are local, mode 0600, and must not be printed or committed.

Raw runs: `runs/br040-*-sol-xhigh-v1-20260917/`. Plan/configs/comparison/review: `runs/br040-sol-landmarks/`. Historical Terra artifacts remain unchanged. This comparison changes model and reasoning effort together; MRI has no unavailable targets and therefore no hallucination endpoint.
