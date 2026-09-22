# Second CT case: source-driven selection and one isolated attempt

[Selection review](../../examples/longitudinal-ct-case02-selection.md) ·
[Protocol](../../experiments/longitudinal-ct-case02-astra-medium/protocol.md)

This method owns new data under `.local/longitudinal-ct-case02/`. Original case
freezes, outputs, source receipts and scores remain unchanged. The selected test
keeps the exact v2 prompt and v1 scorer. The change is the patient and its private
reference. Read the protocol before any intentional fresh generation.

Preparation sequence, using existing runtimes only:

1. `screen.py` verifies 300 cached v3 CSVs by ZIP size/CRC, deduplicates event
   destinations, records criteria/candidates and chooses a patient. It requires
   the retained v3 ZIP index and metadata; no model output is read.
2. `acquire.py` rechecks the live pinned release identity and retrieves just seven
   selected ZIP members with bounded HTTP 206 ranges, size/CRC and SHA-256 checks.
   It can safely reuse matching downloaded members without rewriting old receipts.
3. `review_case.py` checks native geometry, source IDs/volumes, inter-label contact,
   connectivity and edges, then renders author-only CT/GT views. Author inspection
   is recorded in `review/acceptance.json`; it is not clinical adjudication.
4. `prepare.py` verifies source hashes and acceptance, cleans CT text/extensions,
   proves voxel/affine identity, copies unchanged prompt/scorer, and creates new
   private reference/oracle files. It refuses existing tasks. Its base-image tag
   must first be verified against `RUNTIME`; this is a local precondition.
5. Build the two local images with `docker build --pull=false`, using the existing
   `tb3-longitudinal-runtime:validated-v1`. Pin resulting image identities in
   `task.toml` and `image-identities.json` before `preflight.py`. The preflight
   checks exactly two image inputs, private-path absence and blocked external
   egress, then saves the task manifest.
6. Run new native `med run ... --agent oracle` and `--agent nop` controls. Save
   the preview digest in `study.json` and obtain fresh ordinary-usage clearance.
   `run_condition.py` dispatches the authorized Astra-medium condition once,
   records live isolation/transport and refuses automatic retry or another
   concurrent task container. Never invoke it as a maintenance check.
7. `audit.py` and the saved-output analysis read terminal evidence only. Independent
   scorer replay and declared size strata do not dispatch models or alter scores.

`profile.py` regenerates the native-volume profile from the retained geometry
receipt. It is an author-only illustration, never a solver input.

No runtime or pretrained model was installed. `.venv-br037` supplies existing
NumPy, SciPy, nibabel, requests and Matplotlib; `.venv` supplies the common CLI.
A Git clone alone does not contain raw CTs, images, freeze or results. These local
recovery dependencies and the acquisition procedure are explicit; fresh-machine
portability was not established. The full 51 GB archive MD5 is unverified because
only selected members were downloaded. A preliminary Dockerfile base-reference
syntax failure occurred before controls and was corrected using the verified
local tag; it is an author setup event, not a model outcome.

## Completed evidence

The single model attempt `attempt-92800845745342f4` completed normally on the
recorded digest. `analyze.py` replayed its frozen scorer exactly, computed the
predeclared size strata, and rendered all 22 reference-region comparisons.
It refuses an existing output directory and never changes task or answer bytes.
[Result and bounded trace interpretation](../../findings/longitudinal-ct-case02-astra-medium.md).
The observable report's exclusion coordinates were checked directly on native GT;
exact points, source hashes and survey requests are retained in the result evidence.
All original task/reference/result artifacts remain local and immutable.
