# BR-038 full-volume landmark coordinate retest

[Protocol](../../../../docs/research-rounds/BR-038-volume-landmarks.md).

- `audit_original.py`: immutable BR-036 tasks, exact full/crop arrays and independent
  SimpleITK/nibabel conversions and rescoring.
- `prepare.py`: full native source volumes, voxel-output contract, checked viewer,
  independently converted references and isolated scorer; freezes once.
- `volume_tools.py`: public helper, no reference coordinates; checks array equality,
  displays native voxel axes and converts arbitrary debugging coordinates.
- `score.py`: explicit voxel space; physical metric applied only in verifier.
- `run_trials.py ct-full` or `mri32-full`: oracle/nop then one Terra/high attempt.
  No overwrites or retries. Reuse existing Harbor transport without exposing auth.
- `collect.py`: verify frozen bytes; collect results; replay strict grader and
  independently compare transformed predictions against source-world references.
- `report.py`, `compare.py`: regenerate measured report and author-only panels.

Use `.venv-br033/bin/python`. Local data/jobs live under `runs/br038-*`.
Set `MPLCONFIGDIR` to a writable temporary directory when rendering on the host.
Runtime auth/configs, arrays and rendered panels remain ignored. Do not rerun
preparation/trials into existing paths. No clinical adjudication is implied.
