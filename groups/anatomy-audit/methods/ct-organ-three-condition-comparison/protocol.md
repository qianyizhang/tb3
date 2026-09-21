# CT organ segmentation: fixed three-condition comparison

The user requested two additional fresh solvers on the exact CT-only ten-organ
task after the completed Astra/xhigh pilot. The comparison matrix is fixed before
the new results:

| Order | Experiment | Model | Effort | Status before dispatch |
| --- | --- | --- | --- | --- |
| retained | `ct-organ-segmentation-astra-xhigh` | `openai/gpt-6-astra` | `xhigh` | completed |
| 1 | `ct-organ-segmentation-sol-xhigh` | `openai/gpt-5.6-sol` | `xhigh` | fresh |
| 2 | `ct-organ-segmentation-astra-medium` | `openai/gpt-6-astra` | `medium` | fresh |

All conditions use frozen task digest
`fcf7827f7100d1ca54be84f6bc14fb320d27ca546fd5352ac45cb40b04110ab6`.
Native preview must report that digest for each new experiment before launch. The
solver task bytes, image, taxonomy, scoring, reference and runtime are identical;
only model/reasoning condition and fresh stochastic execution differ. Existing
same-digest oracle/no-op controls remain the pre-launch controls.

Each new run has a 7,200-second agent limit, four configured CPUs, a 12 GiB memory
cap, no GPU, no inference retry and no score-conditioned changes. The runs are
sequential: Sol/xhigh must be terminal before Astra/medium is dispatched. Each
gets a separate native attempt, output tree, transport log and live container
isolation receipt. The launcher requires an explicit parent-review receipt and
uses exclusive per-condition dispatch markers. It also waits for a fresh quota
receipt immediately before each condition; Sol clearance cannot authorize the
later Astra/medium dispatch.

Preview commands:

```sh
.venv/bin/med run ct-organ-segmentation-sol-xhigh \
  --model openai/gpt-5.6-sol --effort xhigh --harbor .venv/bin/harbor --preview
.venv/bin/med run ct-organ-segmentation-astra-medium \
  --model openai/gpt-6-astra --effort medium --harbor .venv/bin/harbor --preview
```

After parent review and fresh first-condition quota clearance, run the non-launching
runner check. It verifies the clearance hash, images, native previews, idle host and
next-condition quota without creating a dispatch marker:

```sh
.venv/bin/python \
  groups/anatomy-audit/methods/ct-organ-three-condition-comparison/run_comparison.py \
  --check-only
```

Then start the bounded sequential operator once:

```sh
nohup .venv/bin/python \
  groups/anatomy-audit/methods/ct-organ-three-condition-comparison/run_comparison.py \
  > .local/ct-organ-comparison/operator-console.log 2>&1 &
```

The operator writes `.local/ct-organ-comparison/operator-state.json` plus one
subdirectory per condition. It refuses active `task__` containers, verifies the
pinned solver and transport images, detects the new native attempt, captures the
transport container log, and inspects the live main container for the expected
image, internal network, log-only per-attempt bind mounts, capability drop,
no-new-privileges, CPU/memory caps and lack of GPU device requests. A failed
isolation assertion terminates that condition rather than allowing it to continue.
Any nonzero native exit, isolation/operator error, missing successful live-
isolation receipt or incomplete native execution stops the sequence before the
next solver. A normal scientific failure still permits the second condition.

Before each dispatch, the parent writes a separate receipt named
`.local/ct-organ-comparison/quota-clearance-<condition>.json` with this shape:

```json
{
  "approved": true,
  "condition": "sol-xhigh",
  "task_digest": "fcf7827f7100d1ca54be84f6bc14fb320d27ca546fd5352ac45cb40b04110ab6",
  "checked_at": "2026-09-21T12:00:00+00:00",
  "remaining_percent": 75.0
}
```

The condition and digest must match, the check must be no more than ten minutes
old, and remaining shared quota must be greater than 25%. Missing, stale or low-
quota receipts leave the operator in a durable waiting state without creating a
dispatch marker. The Astra/medium receipt must be refreshed after Sol is terminal.

No prior solver artifact is mounted or mentioned in the task. The main service
has no repository, source, GT or Docker socket mount. Allowlisted model-service
transport and absence of observed retrieval do not prove absence from foundation
model training.

After both runs are terminal, collect and independently replay each saved answer.
Compare semantic macro Dice, matched macro Dice, semantic-geometry gap, positive-
overlap identity assignment, foreground precision/recall, every per-organ Dice,
wall time and retained token counts. Keep trace/method differences descriptive.
One case and one attempt per condition cannot establish general ranking or
clinical performance.
