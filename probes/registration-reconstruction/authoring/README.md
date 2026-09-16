# BR-020 reconstruction-kernel registration

[Protocol](../../../docs/research-rounds/BR-020-reconstruction-registration.md) ·
[Results](../../../docs/research-rounds/BR-020-results.md).
Terra/high passed with matched oracle/nop controls; this snapshot is retired.
The task pairs real NLST B30f/B50f reconstructions with matching patient-space
geometry. Raw DICOM, private target reconstruction, pose keys, generated task
snapshots and runtime traces stay under ignored `runs/br020-registration/`.

Authoring uses Python 3.12, NumPy 2.2.6, SciPy 1.15.3, Pillow 11.3.0 and
pydicom 3.0.1 in `.venv-br020`. `fetch_source.py` downloads only the selected
public pair, retains its original license and records hashes. `inspect_source.py`
checks all DICOM slice coordinates and native HU conversion. Missing acquisition
times are a stated provenance limit.

`build.py` creates the new task without modifying BR-019. It reuses BR-019's
public renderer and geometry grader by explicit source imports. The baseline
is also the unchanged BR-019 script, executed against public inputs; both its
64-start misses and 512-start recoveries are retained. The latter additionally
passes inside a disposable public-only container with no network or host mount.
The baseline itself is never supplied to the benchmark agent.

`freeze.py` checks preparation hashes, input boundaries, interpolation and
acceptance controls before writing the immutable task manifest. `run_trials.py`
runs matched oracle/nop and one Terra/high diagnostic with zero retries. It
asserts the complete frozen file membership before and after each job. The
separate verifier receives only the answer artifact; hidden pose and oracle
files are outside the solving image. Local runtime configs are never retained
in authored evidence.

`collect.py` verifies hashes, runtime context and frozen instructions, and
replays submitted matrices through the geometry scorer. `present.py` makes
a local target/reconstruction comparison after a submitted pose is available.
Do not rebuild over existing tasks or rerun model jobs as a side effect of
documentation/verification work.
