# Cardiac capability stages

[Prospective protocol](../../../../docs/research-rounds/BR-031-cardiac-agent-levels.md).
This directory owns BR-031 only. BR-029 input/reference bytes are read-only.
Raw tasks, model logs, arrays and generated reviews stay under
`runs/br031-cardiac-levels/` and separately named Harbor job directories.

The first screen has two input conditions: complete supplied motion (L0), and
four calibrated videos with an exact initial mesh (L1). L1's geometry/motion
reward and its mechanics score are separate. Later levels are conditional,
and EF/flow/diagnosis are not generated without appropriate references.

The [prospective volume contrast](../../../../docs/research-rounds/BR-031-volume-contrast.md)
adds L1V only if both sparse-view agents miss complete acceptance. It supplies
native 3D images with all mesh/scoring bytes unchanged. The four formerly
withheld evaluation planes then become visible through the volumes, so their
score must be described as off-plane agreement rather than generalization.

## Reproduction

Use `.venv-dynamic-heart/bin/python` from the repository root. `package.py l0`
and `package.py l1` prepare and hash tasks and run local controls. Preparation
refuses to replace task directories or freezes. The actual frozen tasks and
receipts are local; reproducing a new model attempt requires a new explicitly
named experiment version, not overwriting an existing job.

`run_trial.py l0 controls` runs Docker oracle/nop controls. The corresponding
`terra-high` phase runs one fresh model session. After a normal L0 pass, repeat
for L1; `sol-xhigh` is the conditional comparison on the first valid miss.
Thirty minutes are available per model attempt and automatic retries are off.
The runner uses the already configured local Harbor authentication/proxy
configuration without copying it into authored evidence. Version 0.18.0 runs
controls and the existing 0.14.0 Codex trial environment runs models; verifier
task bytes and checksums must match. This is not a claim of identical wrapper
versions. Both use separate verifier containers.

`collect.py STAGE PHASE` independently regrades saved outputs and audits runtime
model/effort and the exact instruction. It retains candidate external commands
only in local logs for manual review. `audit_image.py STAGE PHASE IMAGE` checks
that the initial task image has exactly the allowed input hashes and no verifier
or solution directories. `build_review.py` renders a local report and adds actual
agent predictions to a copy of the workbench. Its default playback becomes an
agent submission as soon as one is available; original workbenches are untouched.

## Independent evaluation

`kinematics.py` uses reference edge systems and determinant ratios; the author
oracle uses inverse edge matrices and a separate implementation. L0 additionally
executes the submitted solver on rigid, affine, shear and missing-axis examples.
Absolute field tolerance is 1e-5. Those mathematical definitions are specified
in the task, not hidden conventions.

`score_l1.py` recomputes geometry/mechanics from point trajectories. Cross sections
are unions of tetrahedron-plane polygons; observed and four fixed withheld plane
masks are scored separately. Surface distance uses boundary vertices and triangle
centroids, not exact continuous Hausdorff distance. Volumes refer to the entire
myocardial tissue body. Strain is reference-volume weighted on valid LV axes;
unknown RV directions remain excluded. Region-level timing accepts reference
extrema within 0.5 pp as ties and uses frame distance, not invented seconds.

The known source passes all gates; empty and static outputs fail. BR-029 affine
and tissue fits are scored as permitted-method comparisons, not agent outcomes.
A further small interior perturbation preserves the rendered surface and remains
within the frozen strain tolerances; its passing result is retained honestly.
It does not establish that the gate detects every visually hidden local defect.
Analytic section controls cover rigid coordinate changes and tetrahedral interior
and exterior membership. A local macOS NumPy matmul warning was checked against
einsum: arrays were finite and distances exactly matched. Frozen scoring code
and metrics were preserved; Linux controls passed.

One healthy simulated case and one attempt per condition are insufficient to
estimate a general agent frontier. Oracle success validates the scorer/output
contract, not identifiability from sparse images. The author knew the case and
has source access; model attempts are fresh and receive only the declared inputs.
