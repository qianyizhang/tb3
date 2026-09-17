# BR-036 semantic landmark pilot

[Protocol and shortlist](../../../docs/research-rounds/BR-036-semantic-landmarks.md).
All downloaded volumes, source annotations, overlays and immutable trial tasks
are local under `runs/br036-semantic-landmarks/`. Do not commit native volumes or
runtime credentials. Curation/freeze receipts are retained under `docs/evidence`.

- `prepare.py`: first source-order CT/MRI selection; native coordinate conversion,
  three-rater MRI audit, scorer controls and frozen isolated task construction.
- `score.py`: strict named RAS-mm points; finite coordinates, per-point distances,
  all-point threshold and descriptive 3/5 mm counts.
- `render_review.py`: author-only reference overlays, never agent inputs.
- `run_trials.py`: matched oracle/nop controls then one Terra/high trial per case.
  Refuses overwrite; errors/timeouts are infrastructure exclusions, never misses.
- `collect.py`: immutable task verification, result import and host rescoring of
  saved submissions. Credentials are not imported.

Use the existing `.venv-br021/bin/python` runtime. `prepare.py` and `run_trials.py`
are one-time operations, not report regeneration commands. Completed evidence
can be re-collected with `collect.py`; do not rerun into the same trial names.

Sources: original PDDCA 1.4.1 part 1 archive and pddca.odt from ImagEngLab;
OpenNeuro ds004470 sub-C001 T1w volume, consensus and three individual rater FCSV
files from the public OpenNeuro S3 bucket. Exact paths and hashes are in the
curation receipt. MRI git-annex hashes independently match downloaded bytes.
CT NRRD is LPS; FCSV uses Slicer RAS. Physical errors use RAS millimetres.

The host curation environment uses SimpleITK for NRRD decoding and nibabel for
NIfTI output; an independent SimpleITK physical-coordinate check and an exact
native intensity comparison are saved locally in `independent-checks.json`.
The pilot is small and reference-based; it does not establish clinical accuracy,
independent human adjudication, or an agent-failure benchmark.

User-authorized expansion: `expand.py` freezes all 32 MRI points with seven
outside an inferior crop, plus paired four-point cropped CT.
`score_visibility.py` supports null/[] or bounded outside estimates.
`run_expanded.py` runs those two new conditions. `fetch.py` verifies original
source hashes; `collect.py`, `report.py`, `audit_completed.py` and `compare.py`
regenerate derived evidence and review panels without model calls.

[Completed interpretation](../../../docs/research-rounds/BR-036-traces.md).

## Completed follow-ups

[Session report](../../../docs/research-landmark-session.md) indexes BR-038
coordinate checks, BR-039 expanded CT and BR-040 Sol comparison. Each subdirectory
has its own README. No further trial is queued. Presentation imports live in
`scripts/import_landmark_figures.py`; they never rerun inference.
