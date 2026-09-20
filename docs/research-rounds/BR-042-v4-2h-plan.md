# BR-042 V4 two-hour variant — Astra/xhigh

User authorized launch on 2026-09-20 with a two-hour agent time limit. The original unrun V4 one-hour freeze remains intact. This variant changes only the time allowance, midpoint wording and task version identifier; CTA, reference, evaluator, clinical scope, category instructions, resources and model settings remain unchanged. No case-specific feedback is supplied.

- Agent: `openai/gpt-6-astra`, `xhigh`; one attempt, no retries.
- Agent wall time: 7200 seconds, including computation, review and transport delays. Setup and verification are additional.
- Preliminary valid answer and method/inventory: midpoint, 60 minutes.
- Final review: approximately the last 10 minutes.
- Controls: fresh oracle and no-op must succeed on identical task bytes before model exposure.

Authorized launch command from repository root:

```bash
.venv-br030/bin/python probes/vessel-geometry/authoring/br042_v4_2h/run.py --run
```

Without `--run`, this performs offline readiness only. See the [V4 plan](BR-042-v4-plan.md) for scope, interpretation limits, local dependencies, safeguards and post-run review. This is a budget-changed, outcome-informed follow-up, not an isolated model comparison.

Local bundle: `runs/br042-all-vessels-v4-2h/`. Job names: `br042-all-vessels-{oracle,nop,astra-xhigh}-v4-2h-attempt1`. [Freeze](../evidence/br042-v4-2h-freeze.json), [public-input audit](../evidence/br042-v4-2h-input-audit.json). Preserve the local bundle, environments and raw evidence during restructuring. The launcher owns its event journal; this planning record does not claim an outcome.
