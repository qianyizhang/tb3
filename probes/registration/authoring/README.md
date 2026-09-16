# BR-019 slice-to-volume registration pilot

[Protocol](../../../docs/research-rounds/BR-019-slice-registration.md) ·
[Completed results](../../../docs/research-rounds/BR-019-results.md).

Both frozen conditions passed Terra/high with matched oracle/nop controls.
They are retired as hard-task candidates. No Sol or cross-acquisition trials
were launched.

`build.py` uses retained, checksum-verified TotalSegmentator small v2.0.1
subject s0915 to create two local task images: a full oblique cardiac-region
view and a crop. The selected apex-side direction is a mask-based heuristic,
not an expert annotation. The other seven source CTs were visually screened;
s0965 has truncated cardiac coverage. Raw scans, task images, private poses,
traces and review graphics stay under ignored `runs/br019-registration/`.

`baseline.py` reads only public CT/target/geometry inputs. It initializes at
the supplied volume's physical centre with 64 broad orientation starts,
uses coarse-to-fine normalized cross correlation and refines with intensity
least squares. It does not read labels, the target pose or the generator.
This deliberately permits ordinary numerical registration to reveal whether
the proposed task is computationally easy.

`reslice.py` is the public forward renderer. `score.py` independently scores
physical point correspondence; no image correlation or submitted code enters
the verifier. `build.py` additionally checks 204 interpolated samples,
including the corners, using SciPy's independent RegularGridInterpolator.
It tests exact pose, no output, small/large shifts, wrong patient convention,
scale and mirrored columns. The public image contains neither masks nor pose
metadata; full-volume geometry is necessary input, not the target answer.

`run_trials.py` refuses existing jobs and changed snapshots. The delegated
supervisor invokes one oracle and nop (Harbor 0.18.0), then one Terra/high
diagnostic (Harbor 0.14.0) per condition. Ground truth and oracle are in the
separate verifier/solution build contexts. The existing local config provides
runtime credentials and proxy settings; never copy it into the authored record.

`collect.py` verifies frozen membership/hashes, matched checksums, runtime
model/effort records and the frozen user instruction, then replays final
matrices through the geometry grader. It retains safe receipts in
`docs/evidence/br019-*.json`. These are local research diagnostics.
`present.py` generates the local comparison figure and target/recovery overlay
review. It uses the host's Helvetica font and is not a task dependency.

For existing evidence only, with the pinned Python 3.12 environment:

```sh
.venv-br019/bin/python probes/registration/authoring/collect.py
.venv-br019/bin/python -m compileall -q probes/registration/authoring
```

Do not rebuild over or edit a frozen task. Starting another trial is a separate
research action. NumPy 2.2.6, SciPy 1.15.3, nibabel 5.3.2 and Pillow 11.3.0 are
the authoring dependencies. All data access is read-only; no source freezes
or the separate submission workspace are changed.
