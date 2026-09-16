# Real ultrasound case study (BR-032)

This directory owns a separate no-reference case requested by the user.
[Protocol](../../../../docs/research-rounds/BR-032-real-echo-case.md) and
[source/contamination notes](../../../../docs/research-rounds/BR-032-source-notes.md)
explain the evidence boundary. No prior source, task snapshot or model artifact
is changed. Raw images, task packages, runs and generated media stay local.

From the repository root:

1. `fetch.py` uses the normal repository Python and an official GitHub release.
   It reads ZIP byte ranges to fetch one deterministically selected scan, plus
   source-format documentation. Downloaded code is inspected, not executed.
2. `decode.py` uses the existing `.venv-br003/bin/python` (pydicom, NumPy) to
   decode the documented Philips private format. It exports image arrays and
   allowlisted geometry/timing only; no patient identifiers enter the task.
3. Other scripts use `.venv-dynamic-heart/bin/python`. `prepare.py` defines
   public/review planes, exports 72 input PNGs and calibration, and checks
   coordinate transforms. `package.py` creates the frozen Harbor task.
4. `run.py controls` runs a static procedural shape and no-output control.
   The Harbor phase named `oracle` is ONLY a format control: its shape does not
   use the images and must never be called anatomical truth. The deliberate
   control passes to demonstrate the narrow meaning of the automatic reward.
5. `run.py sol-xhigh` runs one fresh 30-minute attempt, no automatic retries.
   Source scans, withheld images and author code are absent from its initial
   image. `audit_image.py IMAGE` verifies the allowed inventory. The solver can
   use installed libraries; observed external/source retrieval is audited in
   traces, not assumed impossible solely from prompt instructions.
6. `collect.py` independently checks outputs and runtime provenance; `review.py`
   recomputes mesh intersections against eight image planes. Its brightness
   contrast diagnostic is not segmentation truth. `replay.py pose` and `static`
   rerun the submitted executable in a network-disabled container with altered
   input; these test input response, not pretraining contamination.

The viewer uses the original image frames, submitted surfaces and alternatives,
and independently computed slice intersections. It does not add a decorative
pulse or paint tissue strain. Cavity volume is obtained by signed triangle
integration, with the submitted basal cap and assumptions retained. Positive
volume and edge closure do not rule out every possible self-intersection.

Anatomical accuracy, material correspondence, strain, calibrated uncertainty,
clinical EF accuracy, flow and pathology lack independent truth here. This
case is descriptive evidence, not a benchmark qualification or clinical result.
