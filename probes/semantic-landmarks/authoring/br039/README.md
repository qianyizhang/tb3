# BR-039: expanded CT landmarks

Reproducible author-side pipeline. Raw sources, task packages, configs (which can contain provider credentials), runs and generated review stay under ignored `runs/`. Do not print or publish configs.

1. `fetch_ct.py` acquires one original VerSe CT with bounded HTTP ranges and ZIP CRC validation. Source centroid/mask/supplement inputs are the retained BR-012 source files; exact paths are in `prepare.py`.
2. `prepare.py` checks lossless intensity conversion, affine and source centroid orientation, mask membership (excluding the atlas-ring centre), SimpleITK/nibabel agreement, renderer axes, scoring controls and explicit extrapolation. It freezes full and partial CT packages and refuses to overwrite an existing freeze.
3. `run_trials.py ct-full` and `run_trials.py ct-partial` each run matched oracle, nop and one Terra/high attempt. A run exception is an infrastructure exclusion; no automatic retry. This runner reuses the existing local Harbor provider configuration privately.
4. `collect.py` checks frozen bytes, replays scores and independently recomputes physical distances using world points.
5. `report.py` creates an offline review with every prediction/status and three-plane overlays.

Use `.venv-br033/bin/python` and `MPLCONFIGDIR=/private/tmp/br039-mpl` for author scripts. Harbor/Docker need the user's existing Colima runtime. The request set is C1-C7, T1-T13 and L1-L6; source subject 823 has 24 presacral vertebrae under the published source convention. The partial condition keeps native k=0:920. Labels are never provided to the solver.

Scoring differentiates observed, outside FOV, absent and uncertain. Explicit out-of-bounds estimates are allowed only when tagged outside FOV. Primary hallucination denominator includes every unavailable request; errors and visible omissions are separate. Report missing/invalid submissions as invalid, never as zero hallucinations.

The MedPelvis acquisition remains local as a rejected source candidate: documented coordinates failed anatomy overlays. It was not repaired heuristically or used in a model trial. See [round plan](../../../../docs/research-rounds/BR-039-ct-landmarks.md).
