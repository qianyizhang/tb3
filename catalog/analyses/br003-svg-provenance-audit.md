# BR-003/H04: Terra launch and solution-leakage audit

Audited 2026-09-15 at the user's request after the reported Dice 1.0 result.
Scope: the completed SVG trial `dicom-triplanar-svg__hoWg6JJ`. No new model trial
was launched, and no frozen task inputs or original results were changed.

**Finding: no private solution or generation-code retrieval is observed.** The
recorded model constructs a renderer from the public inputs. However, this is
a strongly specified conversion of existing segmentation masks into SVG. The
result does not establish difficult anatomical drawing or broad medical reasoning.
The task remains retired. [Machine-readable audit](../../docs/evidence/br003-svg-provenance-audit.json)
contains source hashes, call coordinates, prompt comparison and artifact lineage.

## How Terra was launched

The parent used Harbor 0.14.0 to start Codex CLI in a fresh Docker container,
with a fresh `/tmp/codex-home`. It did not spawn a conversation-forked worker.
The core invocation was:

```sh
.venv/bin/harbor run -p probes/dicom-triplanar-svg \
  --env docker --agent codex --model openai/gpt-5.6-terra \
  --ak reasoning_effort=high --ae CODEX_FORCE_AUTH_JSON=1 \
  --n-attempts 1 --n-concurrent 1 -o runs \
  --job-name br003-svg-terra-high-v1-20260915
```

The actual command also supplied the existing HTTP/HTTPS proxy and NO_PROXY
environment settings recorded in the local run config. Auth setup copied only
the configured authentication file; no credential contents were read for this
audit. The harness then invoked `codex exec --model gpt-5.6-terra --json
--enable unified_exec -c model_reasoning_effort=high`, with its standard
approval/sandbox bypass inside the Docker container and the task instruction
as the prompt. The 1,800-second task allowance remained in force.

The [trial log](../../runs/br003-svg-terra-high-v1-20260915/dicom-triplanar-svg__hoWg6JJ/trial.log)
records this command at line 14. Run config, result metadata and raw turn context
agree on Terra/high; CLI version is 0.154.0. This establishes consistency of
the local records, not independent attestation of the provider's backend.

## What the model saw

The raw session contains 86 records. Line 9 matches the frozen public instruction
apart from terminal newlines. Line 6 is the CLI's generic plugin/environment
message. There are no subsequent user hints and no parent conversation in the
recorded task prompt. Other developer messages contain generic CLI instructions.
Custom skills, MCP servers, extra instruction paths and extra mounts are empty.

The agent Docker build context is only `environment/`. Its Dockerfile installs
the libraries and copies the empty starter, driver, requests, source notices,
licenses and input archive. It does not copy `solution/`, `authoring/` or `tests/`.
The archive contains 91 CT instances, one SEG object and the label vocabulary:
93 files, with no Python source or expected-mask NPZ. The trace's initial `/app`
listing and subsequent starter read agree with this construction.

The grader uses a separate image built from `tests/`; it receives the submitted
`/app/answer`. Harbor's default agent mounts include the **same trial's** agent
logs, verifier logs and artifact directory. Thus "no mounts" would be inaccurate:
there are no configured extra mounts or host-repository mount, but ordinary log
mounts exist. Verification started after the agent finished, and no recorded
command reads verifier logs or a private reference. Other oracle trials have
different trial directories. The recorded original container was removed; no
surviving matching named image was found for a direct historical filesystem
inspection. This boundary assessment uses frozen build inputs, run config,
observed initial files and installed harness code, not a preserved image dump.

## Complete recorded tool sequence

The [raw session](../../runs/br003-svg-terra-high-v1-20260915/dicom-triplanar-svg__hoWg6JJ/agent/sessions/2026/09/14/rollout-2026-09-14T17-35-36-01a0a0fd-18f5-77d0-8cc9-c1d58074cb71.jsonl)
has eight tool calls and eight paired outputs. The model used shell/Python and
patch application; no delegation, additional model call, web search or private
answer fetch appears in the recorded calls.

| Call / output lines | Recorded action |
| --- | --- |
| 15 / 18 | List `/app`, read the public driver and input names. |
| 24 / 27 | Read the five-line empty SVG starter, DICOM metadata and requests. |
| 33 / 36 | Inspect segment labels/source references and geometrically order CT positions. |
| 44 / 46 | Attempt a complete renderer replacement; patch tool rejects duplicate delete/add targets. |
| 50 / 53 | Apply a successful full update to the empty starter. |
| 57 / 60 | Compile and execute the renderer for the four public requests. |
| 64 / 67 | Check its own geometry/counts and render its SVG locally with CairoSVG. |
| 75 / 78 | Attempt Git inspection (Git absent), then inspect its own loaded grid. |

The successful patch at line 50 reconstructs the final archived `renderer.py`
**byte for byte**. Its removed lines match the frozen empty starter. This ties
the submitted artifact to the model's recorded edit, rather than merely trusting
the final reward. All eight original evidence hashes checked against the round
receipt still match.

The model and reference use different source structures. The reference builds
one Boolean volume per organ and writes SVG rectangles. Terra caches CT/SEG
metadata, constructs a categorical volume for requested labels and writes
horizontal-run SVG paths grouped by color. Their shared DICOM affine and sampling
operations follow the same public specification. They are not identical files;
source differences alone would not prove absence of copying, so the access and
edit trace is the stronger evidence here.

## Why exact Dice is attainable

The input already contains the labeled 3-D organ voxels. The prompt explicitly
supplies LPS display axes, pixel-center formulas, the nearest-voxel rounding rule,
color mapping and grading convention. The required work is to decode DICOM,
associate sparse frames correctly, transform coordinates and emit exact-color
SVG. Correct deterministic resampling can match every target pixel exactly.
The 12 views are four requests on one source case, not 12 independent tasks.

The earlier summary should therefore be read as **exact mask-resampling/rendering
agreement on this specified fixture**. It should not be read as independent
reconstruction of anatomy from raw CT or freehand anatomical drawing. No solution
leak was found in the available evidence; the more substantive weakness is the
limited, strongly specified task design. Hidden provider behavior and training
provenance are outside what this local trace audit can establish.
