# BR-004 — One trial per patient task

## Authorization and contrast

The user requested one trial per task and a benchmark of success, tokens, time
and related costs to identify difficult tasks that use fewer resources. Here a
task is **one of the eight existing patients**, with its full original focus
list. This is a follow-up condition of BR-004, not a retuning of defect severity.
Source: [current conversation](codex://threads/01a0a248-241a-76b0-8ecf-15e259df9734),
2026-09-15; message UUID unavailable in supplied context.

The earlier eight-patient run timed out without submitting and remains excluded.
Split patient DICOM bytes, taxonomy, focus lists, decoder, label truth, spatial
regions, grader, tool/network access and 1,800-second allowance remain unchanged.
Each new task receives a fresh Terra/max context and one attempt. No earlier
trajectory, clean reference, mutation recipe or result is supplied to the solver.

## Frozen execution

- Eight tasks, in original case order: 74, 19, 83, 46, 28, 61, 95, 32.
- `openai/gpt-5.6-terra`, `reasoning_effort=max`, Harbor 0.14.0/Codex/Docker.
- One attempt per task, zero retries, model trials sequential to avoid deliberate
  within-round resource contention. Other host activity and API latency remain
  potential timing confounders.
- 4 CPU, 4 GiB RAM, public network, ordinary image/tool access; 1,800 seconds each.
- Matching Harbor 0.18.0 oracle and nop controls precede each model attempt.
  Oracle must pass. Nop must fail altered cases and **pass clean cases**, where
  the empty finding list is correct. A separate author flag-every-label control
  must fail every task. Never treat the clean-case nop pass as verifier failure.
- Freeze all task bytes before starting any model. Preserve raw exceptions and
  partial artifacts. No adaptive retries, altered defects or additional hints.

## Metrics and interpretation

Retain one row per task, including zero scores and timeouts:

| Field | Meaning |
| --- | --- |
| Execution | Normal completion, timeout, or other execution error |
| Raw success | Exact affected labels and valid spatial witnesses; reward 0/1 |
| Findings | Planted labels named/located, missing labels, extra labels, bad points |
| Validity | Whether a completed miss can support the anatomy hypothesis; keep source ambiguity separate |
| Tokens | Reported total input, cached input, uncached input (= input minus cache), output |
| Time | Agent time, total time, setup and verifier time separately |
| Cost | Harbor-reported estimate if available, never represented as an invoice |
| Tools | Trace tool wrappers and image-review wrappers, with loop-count caveats |

Cached tokens are a subset of input tokens, not added to them. Do not invent a
reasoning-token split when the harness does not expose it. Missing usage is
unavailable, not zero. Timeout time is capped/censored; an unchanged starter is
not a considered answer. A clean task may legitimately finish with the starter
unchanged, so this check must be interpreted alongside normal completion.

Compare resource use among **normally completed, valid** outcomes. A useful
candidate is a genuine semantic miss with little agent time and few tokens;
timeouts, unresolved source errors, cheap clean passes and incorrect controls
cannot establish that result. Show time and token tradeoffs directly rather than
inventing one weighted hardness score. One trial supplies an observation, not a
reliable pass probability or an optimized task. Keep the prior batch's capped
resource use separate from the sum of eight independent attempts.

## Predeclared source-truth limitation

Case-46 has an unresolved small anterior L2 component noted in the earlier trace
review. Its anatomical interpretation is **provisional before this trial**;
resource/operational results remain usable, but a disputed source finding must
not be called a genuine model failure. Any newly alleged source defect in other
cases also requires review. The split preserves all inputs to isolate batch
size; it does not claim to resolve clinical ground truth by copying files.
No certified postoperative cohort or specialist clinical validation is claimed.

The split builder and [freeze](../evidence/br004-single-patient-freeze.json)
retain patient-file hashes and author controls. Results, trace reviews and the
resource comparison will be recorded after the authorized attempts complete.
