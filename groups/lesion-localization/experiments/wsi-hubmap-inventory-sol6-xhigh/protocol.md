# HuBMAP whole-slide glomerulus inventory — Sol 6 xhigh

Can `openai/gpt-6-sol` at xhigh inventory glomeruli by navigating one full PAS kidney image? This is one diagnostic public-training-sample pilot, not a generalization estimate.

The solver sees the native `aaa6a05cc` TIFF under a neutral name, physical pixel scale, a GT-free overview and a coordinate crop helper. The reference JSON, reference-derived crops and teaching overlays remain private. The agent returns deduplicated level-0 centers and confidence. There is no pretrained segmentation model in the runtime. The crop helper records calls, but direct TIFF reads are possible, so its ledger is descriptive rather than an enforced read budget.

The scorer matches one point per glomerulus polygon when the point is inside the polygon or within 50 µm of its edge. It reports recall, unmatched predictions and count error. Unmatched predictions are not automatically clinical false positives until annotation-valid tissue coverage and edge cases are reviewed. No contour/area scoring is attempted without a contour output contract. No-op and reference oracle controls check artifact handling; the oracle's answer is never solver-visible.

Use one 3600-second attempt, no automatic retry, Docker 4 CPUs/12 GiB/0 GPUs, and the existing restricted transport. Pin source hashes from `datasets/receipts/wsi-teaching-samples.json`, runtime image identities, a task preview and controls before model dispatch. Stop on source mismatch, privacy leakage, invalid controls or infrastructure failure. Apply the one-time quota preflight in `docs/workflow.md`; a lower-cost condition or shorter timeout requires user acceptance before launch. Review the trace and score separately; do not claim a population rate from this slide.

## Operational status — 2026-09-23

The exact-task oracle passed and no-op failed in Harbor. Two model invocations were retained as `execution_error` with `no_verdict`: `attempt-4f9625ac511d4eea` used an absent `OPENAI_API_KEY`; `attempt-6b34b0a98f284ce8` used Harbor's supported ChatGPT auth-file path but received 401 without a bearer header. An independent host CLI smoke check reported that `gpt-6-sol` is unsupported through this ChatGPT account. Both attempts ended before image reasoning and produced no answer. No further model dispatch is authorized until the route is verified; the task, reference and controls remain unchanged.

### Routing clarification — 2026-09-23

A tiny Harbor task using the same WSI runtime completed with `gpt-6-sol` xhigh when ChatGPT auth and proxy variables were explicitly passed to the container agent. The older host CLI's rejection was not an account-wide model-access verdict. The two earlier HuBMAP attempts retain their execution-error/no-verdict records. The user subsequently selected Astra medium for pending WSI runs, recorded in a separate experiment; no Sol WSI rerun is currently scheduled.

## Question and method

## Inputs and reference

## Findings and limits
