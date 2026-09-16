# Clinical adaptation case (BR-034)

This separate experiment responds to the user's request for a clearer clinical
scan and a model-driven functional assessment. It preserves all BR-025–BR-032
inputs and results. Read the frozen [protocol](../../../../docs/research-rounds/BR-034-pathological-echo.md)
and [supplementary preserved-function control amendment](../../../../docs/research-rounds/BR-034-preserved-control-amendment.md).

Authoring uses the isolated `.venv-br034` Python 3.12 environment. The frozen
Harbor environment uses the pinned dependencies in its Dockerfile. Clinical
archives, prepared arrays, trial logs and generated report stay under ignored
`runs/br034-pathological-echo*`; no data or site has been published.

- `fetch.py` reads public archive byte ranges for the first case's metadata.
  `bulk_fetch.py` retrieves the bounded screens recorded in source JSON, checks
  publisher LFS SHA-256 values, and extracts annotation metadata. Source code is
  inspected as documentation, not executed.
- `screen.py` records reference surface-derived EF for every screened case.
  It does not assign a disease cause. Duplicate annotation/volume recording
  pairs are not counted as separate patients.
- `prepare.py` decodes selected native frames with Zarr, applies the publisher's
  mesh-to-render convention, aligns actual timestamps, and exports a Cartesian
  volume plus only the initial reference surface for the solver. `validate.py`
  checks archive/decoder consistency, geometry, closed mesh topology, and
  independently draws reference intersections for inspection.
- `package.py` freezes inputs, independent references, scoring and controls.
  `run.py controls` runs exact-reference and no-output controls; the local
  static-initialization control also must fail. `run.py sol-xhigh` runs exactly
  one authorized fresh attempt with no automatic retries or reviewer feedback.
- `audit_image.py IMAGE` verifies the public input inventory and absence of
  `/tests`, `/verifier` and `/solution`. Harbor cleanup can remove every tag
  of its image. If this happens, rebuild the frozen Dockerfile using cached
  layers, record the infrastructure event, and audit the rebuilt replay image.
- `collect.py` checks completed receipts, independently regrades the output,
  verifies runtime model/effort and instruction provenance, and records observed
  external/source/delegation tool-use candidates. Such trace review does not
  establish the pretraining corpus or hidden provider behavior.
- `replay.py original|patient|preserved|static|shift` executes the unchanged
  submission in a network-disabled, read-only container with 4 CPUs/8 GB and
  a five-minute limit. Artifacts are hashed. The hidden clinical cases retain
  their own initial surfaces and calibration; no model feedback is supplied.
- `build_review.py` generates the local interactive viewer, independent
  intersections and static scientific comparison. Its rendering keeps spatial
  scale fixed through each beat and uses lighting, not invented strain colors.
- `finalize.py` verifies frozen inputs and completed receipts, then writes the
  final evidence record once. Read the [results](../../../../docs/research-rounds/BR-034-results.md)
  for the clinical comparisons and the limits of this single attempt.

All physiological comparisons concern the LV endocardial cavity. Dense clinical
surfaces are not material trajectories. The pilot does not validate force,
myocardial strain, hemodynamics, disease etiology or patient-care decisions.
