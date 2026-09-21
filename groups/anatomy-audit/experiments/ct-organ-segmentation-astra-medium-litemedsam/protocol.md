# Astra medium with LiteMedSAM: CT organ segmentation

The user explicitly requested one fresh Astra/medium attempt with the LiteMedSAM
skill enabled, following the [local calibration task](codex://threads/01a0c423-5d0a-7ee3-97b4-66939a8c9e20).
Authorization and supervision belong to
codex://threads/01a0c38d-fcff-7670-9ac7-80d0ca352c35. This condition is separate
from the three completed standalone-agent attempts. Parent owns preparation and
execution; the previous Sol helper is errored and has no live writer.

## Fixed task and changed capability

Use the same CT, ten target definitions, original reference bytes, scorer and
separate evaluator as the [original protocol](../ct-organ-segmentation-astra-xhigh/protocol.md).
The comparison baseline is frozen Astra/medium attempt
`attempt-6979f136149c4e17`, semantic macro Dice 0.7341910610035614. Preserve all
existing freezes and results. The new task has a new digest because the image,
task-bound skill, and neutral availability instruction change. Do not claim byte
identity of the complete task or a pure tool-only causal contrast.

Supply only the canonical LiteMedSAM skill and adapter, minimal inference source,
the pinned checkpoint, and Linux CPU dependencies. The agent chooses every box,
slice, crop, window and semantic assignment from the supplied CT. The skill
provides its generic image/box contract and coordinate cautions; neither the
instruction nor runtime contains case-specific prompts. The solver may choose
whether and how to use the available tool. Record actual use separately from
availability, including any modified or directly imported inference code.

Pin upstream LiteMedSAM commit `b0fab476e54e631dd412b25e0db9fdf2a2b0f54c`
and checkpoint SHA-256
`79d8c9dca6db4d69d3f905579e5250af05e859fff9c1f543e89a513c3028ce76`.
Retain the upstream Apache-2.0 license with the runtime. The checkpoint was
previously downloaded from the upstream-linked Google Drive object
`18Zed-TUTsmr2zc5CHUWd5Tu13nb6vq6z`; copy the existing exact bytes, not a fresh
download. The main image derives from baseline solver image
`sha256:e7f0c11c5c8991896e1f9058fc6f5a6943808dea5c3077e471a946d3f6cce52d`.
Only this pretrained segmenter is authorized. No GPU, TotalSegmentator runtime,
other weights, dataset cache or network downloads during the agent run.

## Leakage, controls and execution

Exclude GT-derived calibration boxes and slice choices, benchmark scripts,
findings, source identifiers, old solutions, traces, scores and reference masks
from the solver payload. The private scorer and GT remain in the evaluator-only
task subtree. Do not copy the whole host calibration directory or macOS venv.
The solver uses the same internal-only network plus model-service allowlist proxy
as the baseline. Inspect the final image inventory and live mounts/networks/caps.

Before inference, validate one synthetic image+box call in the actual CPU image,
verify weight and adapter hashes, compare solver data/reference/scorer hashes to
the original task, and run fresh exact oracle=1 and no-op=0 controls on the new
task digest. Retain failed infrastructure invocations rather than replacing them.
No live trial is implied by preparation or by the local calibration result.

One fresh `openai/gpt-6-astra`, `medium` attempt; 7,200 agent seconds, four CPUs,
12 GiB configured memory ceiling, no GPU. The Docker VM has about 7.74 GiB total,
so that ceiling is not guaranteed available RAM. Wait for unrelated Docker trials
to finish. Use one exclusive dispatch marker, fresh quota clearance (>25% at
launch), and retain at least 20% account quota throughout; never redeem resets.
No automatic inference retry, continuation, feedback or time extension. Bounded
pre-inference repairs are allowed with exact failure records and parent review.

## Outcome and interpretation

After terminal state, collect the original answer, independently replay every
verifier field, inspect per-organ semantic and matched geometry Dice, foreground
coverage, identity matching, time/token usage and the full trace. Retain actual
tool calls, prompt/image mappings, receipts and inference timing when available.
Compare per-organ changes to the original Astra/medium baseline; retain the other
two conditions as context. Use matching-color/line-style legends for overlays.

This is a single-case, single-attempt descriptive comparison of agent + skill +
segmenter versus a standalone agent. The local tool calibration used this case
with GT-derived prompts; its evidence supports provisioning but is never exposed
to this solver. LiteMedSAM training overlap with this public CT has not been
established or excluded. Neither a gain nor a loss establishes general efficacy,
clinical accuracy, unseen-case generalization or a causal tool effect. Do not
revise frozen scores to fit a qualitative explanation.
