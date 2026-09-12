# Cache calibration: useful controls, no observed reasoning failure

Analysis recorded 2026-09-12 from local trial artifacts and the existing
[experiment ledger](../../docs/ledger.md). Scope: the seven cache-probe attempts.
Subsequent candidates have their own snapshots and denominators.

| Observation | Evidence | Interpretation |
| --- | --- | --- |
| The final nop receives reward 0: five cases pass and five fail. | [Verifier cases](../../runs/cache-nop-final-20260912/cache-invalidation__Zqobefz/verifier/test-stdout.txt) | The initial runner already handles several invariants. Failure clusters around declared input changes, not basic execution. Nop is a control, not a model. |
| The final oracle receives reward 1; all 10 cases pass. | [Oracle result](../../runs/cache-oracle-final-20260912/cache-invalidation__gKJsM5U/result.json) | The frozen calibration task has a working reference solution. |
| Terra/high receives reward 1; all 10 cases pass, with no execution exception. | [Model result](../../runs/cache-terra-high-proxy-20260912/cache-invalidation__5V4Z43m/result.json), [cases](../../runs/cache-terra-high-proxy-20260912/cache-invalidation__5V4Z43m/verifier/test-stdout.txt), [submitted runner](../../runs/cache-terra-high-proxy-20260912/cache-invalidation__5V4Z43m/artifacts/app/build_runner.py) | The missing input fingerprint was repairable in this diagnostic. Keep the probe for calibration; this run offers no evidence that the task is difficult for Terra or Sol. |
| First model attempt has `NonZeroAgentExitCodeError`, no completed agent execution, no verifier, and no reward. The ledger records Debian DNS failure. | [Attempt result](../../runs/cache-terra-high-20260912/cache-invalidation__QCGrLrt/result.json), ledger P04/S12 | Exclude from model outcomes. Its displayed job mean of zero is not a failed verifier. |
| Retry has `CancelledError`, no verifier, and no reward. The ledger records repeated direct ChatGPT transport timeouts and cancellation. | [Retry result](../../runs/cache-terra-high-retry-20260912/cache-invalidation__YzLdAvE/result.json), ledger P05/S14 | Exclude from model outcomes. An execution timer or trajectory file does not prove a completed model trial. |

The final oracle, nop, and successful Terra trial share recorded Harbor
`task_checksum` `5b6007a79b86f7fb539b175438e5a6a9cfccc5994e7f833aa2a883b3b990e418`.
The two earlier controls share a different checksum and remain separate columns
in the matrix. The freeze document's `task_sha256` uses a different algorithm.

The successful job's `proxy` suffix describes an HTTP network proxy. It is an
actual Docker/Harbor/Codex run, not mirrored evaluation by another agent.

For these seven attempts: **one completed model pass, zero completed model
non-passes, two excluded execution errors, and four control trials**. This
supports retaining cache invalidation as a setup fixture and directing the next
diagnostic toward the interacting behaviors in Dremel assembly or Ninja.
It does not establish a model failure rate or satisfy final qualification.

Next action for the excluded attempts: retain them as separate attempts, preserve
their original artifacts, and use the already documented DNS/proxy setup for
future trials. Their recovery is evidenced by the later completed Terra pass;
there is no reason to relabel or erase the earlier failures.
