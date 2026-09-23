# Codex routing investigation — 2026-09-23

## Scope

- Source tasks: [investigation](codex://threads/01a0cc34-3a42-7243-aa18-c02bd8b0c2f3), [WSI experiments](codex://threads/01a0cbf7-5068-7001-90be-102123fff079).
- Current instructions: [launch rulebook](../../../docs/workflow.md#local-codex-launch-rulebook).
- Local proof: `.local/model-route-smoke-20260923/verification.json` and adjacent jobs/workbench.

## Findings

| Failure | Confirmed explanation |
| --- | --- |
| Missing API key | Harbor defaulted to API-key auth; the existing login was ChatGPT auth. |
| 401 after opting into ChatGPT auth | Upload retained host UID 501 and mode 0600. The solver dropped all capabilities, so container root could not read the file; login status reported permission denied. |
| Network unreachable after restoring an older profile | The direct proxy override replaced `http://transport:3128`; the isolated solver could not reach the upstream LAN address. |
| Conflicting host/container behavior | Host shell Codex was 0.147.0; the solver used 0.155.1. Host errors did not establish account-wide unavailability. |

## Verification

| Check | Result |
| --- | --- |
| Direct-route Astra/medium and Sol/xhigh toys | Completed `19 + 23` shell/file task; reward 1, no Harbor exception. |
| Direct-route CLI, `attempt-4b916c8a4a33420d` | Passed; frozen bytes unchanged. This did not cover the task's Compose restrictions. |
| Initial sidecar toys | Both models completed inference and saved exact `42\n`; toy verifier setup errors were retained separately. |
| Full sidecar CLI, `attempt-a354519f85d04d7e` | Same WSI solver image/Compose/capabilities, corrected separate evaluator: reward 1, no exception, frozen bytes unchanged. |
| HuBMAP retry, `attempt-8d9493603c6d4909` | Began shell calls and native slide-crop reads. Later medical results belong to the experiment record. |

The failed WSI attempts and interrupted proxy retry remain unchanged. Smoke results
establish runtime operation, not medical capability or independent provider-side model identity.

## Prior implementation references

The [longitudinal launcher](../../longitudinal-reading/methods/longitudinal-ct-image-only/run_condition.py)
and [dental launcher](../../anatomy-audit/experiments/dental-ct-only-astra-medium/authoring/launch.py)
already used a readable auth copy inside a private temporary directory. These are
provenance references, not prerequisites or launch commands for other studies.

Recheck when the image, client, Compose topology, credential permissions, proxy
or model access changes. Missing local proof requires recovery, not an assumed working route.
