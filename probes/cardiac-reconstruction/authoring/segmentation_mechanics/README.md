# Segmentation to mechanics (BR-035)

The [prospective protocol](../../../../docs/research-rounds/BR-035-segmentation-mechanics.md)
owns the two authorized Sol/xhigh conditions and clinical transfer. Source data,
frozen Docker tasks, submitted models and viewer remain under ignored `runs/`.
This directory owns no prior cardiac experiment and changes no frozen BR-029,
BR-031 or BR-034 artifact.

- `prepare.py` creates independent per-phase binary wall masks and matching
  ultrasound on a calibrated 1.5 mm Cartesian grid. It separately freezes a
  clinical cavity sequence. Source vertex identities and regional labels never
  enter either public input. The clinical volume/EF quantization is audited.
- `geometry.py` contains independent tetrahedron rasterization, point location
  and finite kinematics. `validate.py` checks rigid and affine fields, permutation
  invariance, exact membership, and identical-shape/different-strain ambiguity.
- `score.py` scores any valid submitted topology. Shared material probes are
  reference tetrahedron centroids. Barycentric interpolation evaluates motion,
  and the containing element's F evaluates strain at the probe. Coverage is
  volume weighted and reported independently; regional strain is conditional on
  covered reference locations, with per-region coverage retained.
- `package.py` freezes both conditions before either attempt, including source
  references in separate verifier containers. Local source-motion and static
  controls pass/fail as expected; the source oracle is privileged, not a legal
  solution. Task F/E/J tolerances are numerical, not clinical tolerances.
- `run.py CONDITION controls|sol-xhigh` uses the existing local Harbor harness.
  Controls run Harbor 0.18, model trials 0.14, as in prior rounds. Task checksum
  identity, separate verifier execution, runtime model/effort, and input-image
  inventory are checked. Each model receives 30 minutes; automatic retries are
  disabled. Conditions run sequentially on the 4 CPU/8 GB Docker host.
- `audit_image.py CONDITION IMAGE` checks that the image contains only frozen
  public data and no verifier/solution directories. Harbor may delete the image
  during cleanup; rebuild the frozen environment Dockerfile for clinical replay.
- `collect.py CONDITION` independently regrades retained artifacts and records
  runtime/trace provenance. External-command candidates require author review;
  their absence does not establish unknown pretraining exposure.
- `replay.py CONDITION` executes unchanged code on the frozen clinical inputs,
  with no network, 4 CPUs/8 GB and five minutes. Failure receipts are retained.
- `build_review.py` uses `.venv-br034/bin/python` (scikit-image/matplotlib) to
  render models and scientific figures. Other author scripts use the existing
  `.venv-dynamic-heart/bin/python`. Strain colors are independently recomputed
  principal Green–Lagrange strain; they are disabled for a cavity domain.

Geometry reward and simulator-material diagnostics are intentionally separate.
No count of mesh vertices, smooth colors, or mask overlap can establish true
myocardial correspondence. Analytic fields validate calculations, not inferred
patient mechanics. The real cavity transfer cannot validate myocardial strain.
