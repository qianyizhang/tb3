# HuBMAP whole-slide glomerulus inventory — Astra medium

Can `openai/gpt-6-astra` at medium inventory glomeruli by navigating one full PAS kidney image? This is one diagnostic public-training-sample pilot, not a generalization estimate.

The solver sees the native `aaa6a05cc` TIFF under a neutral name, physical pixel scale, a GT-free overview and a coordinate crop helper. The reference JSON, reference-derived crops and teaching overlays remain private. The agent returns deduplicated level-0 centers and confidence. There is no pretrained segmentation model in the runtime. The crop helper records calls, but direct TIFF reads are possible, so its ledger is descriptive rather than an enforced read budget.

The scorer matches one point per glomerulus polygon when the point is inside the polygon or within 50 µm of its edge. It reports recall, unmatched predictions and count error. Unmatched predictions are not automatically clinical false positives until annotation-valid tissue coverage and edge cases are reviewed. No contour/area scoring is attempted without a contour output contract. No-op and reference oracle controls check artifact handling; the oracle's answer is never solver-visible.

Use one 3600-second attempt, no automatic retry, Docker 4 CPUs/12 GiB/0 GPUs, and the existing restricted transport. Pin source hashes from `datasets/receipts/wsi-teaching-samples.json`, runtime image identities, a task preview and controls before model dispatch. Stop on source mismatch, privacy leakage, invalid controls or infrastructure failure. Apply the one-time quota preflight in `docs/workflow.md`; a lower-cost condition or shorter timeout requires user acceptance before launch. Review the trace and score separately; do not claim a population rate from this slide.

## Operational status — 2026-09-23

The user switched this diagnostic condition to Astra medium after two Sol 6 attempts ended before image analysis. The native task, private reference, source hashes and exact-task oracle/no-op controls are unchanged. A host `gpt-6-astra` medium smoke test passed; isolated Harbor execution still requires a verified auth route.

The first full-slide Astra launch, `attempt-f1b7827a5e544517`, used an explicit Harbor agent environment after a base-runtime toy passed. The WSI task's transport-isolated container instead returned repeated `Network unreachable` errors before image analysis. The launch was interrupted after about two minutes; its frozen task bytes remained unchanged and its execution observation is `no_verdict`. The exact WSI sidecar/auth route must pass a tiny verification before a bounded retry.

### Diagnostic result — 2026-09-23

With the unchanged WSI sidecar and a private temporary auth copy, `attempt-8d9493603c6d4909` completed in Harbor with no exception and frozen task bytes unchanged. Its `reward=1` verifies the answer artifact contract only. The private scorer matched 86 of 99 reference polygons to 114 submitted level-0 points using one-to-one inside-polygon or 50 µm edge tolerance: recall 0.869, 13 unmatched reference polygons, 28 unmatched predictions, and absolute count error 15. `precision_within_reference=0.754` is the scorer's matched-point fraction, not an adjudicated clinical precision estimate. The crop helper recorded 22 calls, but direct slide reads were possible, so this is not an enforced search budget. The inspected 14 shell commands showed no explicit access to the private `tests/` or `solution/` paths. One selected public training slide cannot establish population performance; unmatched predictions need annotation-domain and morphology review before being called false positives. Raw evidence is in `observation-e86a9102f526e7c5ebc39c9e` and its local Harbor trial.

## Question and method

## Inputs and reference

## Findings and limits
