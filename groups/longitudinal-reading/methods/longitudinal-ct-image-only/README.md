# Image-only paired CT pilot

Authoring and review tools for the two user-authorized attempts. They are not
solver inputs. Raw CTs, reference masks, isolated images, freezes, credentials and
saved outputs remain local. No extra runtimes or pretrained models are installed.

The [instruction](instruction.md) is the complete task. Each model receives only
`baseline.nii.gz` and `followup.nii.gz`, plus this generic output contract. The
private [scorer](score.py) independently measures localization, mask agreement,
cross-visit edges and exact event groups. Its scalar Harbor reward measures only
artifact validity. [Synthetic checks](check_score.py) test those distinctions.

Current source/reference suitability has a scoped [instance-boundary question](../../examples/longitudinal-ct-instance-boundary-review.md).
Original task bytes and scores remain unchanged. This pilot is not task promotion.

## Recovery and execution

- `prepare.py` requires the exact previously downloaded members and their reviewed
  hashes. It refuses to overwrite an existing task. It scrubs input free-text
  metadata, verifies unchanged image values/geometry and separates reference files.
- Solver/evaluator Dockerfiles use a local runtime tag. Before building, that tag
  must resolve to image `sha256:3de5f01c3d98a0ed47c9c6ac2ef202807e2761e0ece826d0b514c994f033f107`.
  The recorded first build failed because Docker interpreted a bare image ID as a
  registry name. Tagging the already-present image fixed preparation; no model ran
  in that failed build and no new runtime was installed.
- `finalize.py` verifies the runtime identity, pins built images in the task,
  checks the data-only filesystem and transport boundary, and records file hashes.
  It is a preparation command, not a historical replay command. Do not rerun it
  against a frozen task; native freeze records are the final authority.
- Native `med run` produced oracle/no-op controls before the first model. The
  `run_condition.py` operator dispatches one named condition at most once, checks
  host idleness and image identities, copies existing authentication to a temporary
  protected directory, captures live isolation and transport, and removes that
  temporary credential copy afterward. Credentials are never part of task data.
- The operator reads a fresh quota receipt before each launch. User authorization
  covers exactly these two conditions, one attempt each with 7200 seconds; no
  automatic retry or reset-credit redemption is authorized. Sol's diagnostic flag
  records the convention question known before its dispatch; it changes no task
  input and conveys no first-model result.
- `analyze.py` runs only the frozen private scorer against saved outputs, requires
  equal discrete outcomes and floating-point agreement within 1e-12 (with exact
  equality and any numerical differences recorded), and builds a new local comparison reader
  and static figures. Run with the existing `.venv-br037/bin/python`, setting
  `MPLCONFIGDIR=.cache/matplotlib`. It refuses to overwrite an existing review.
  It never launches a model.

Protocols: [Astra medium](../../experiments/longitudinal-ct-image-only-astra-medium/protocol.md)
and [Sol xhigh](../../experiments/longitudinal-ct-image-only-sol-xhigh/protocol.md).

For future studies, author a new task revision and fresh experiment; do not reuse
these single-dispatch markers, regenerate old freezes or edit historical outputs.
