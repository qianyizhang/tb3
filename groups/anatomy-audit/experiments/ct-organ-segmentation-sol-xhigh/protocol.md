# CT-only ten-organ segmentation: Sol/xhigh comparison condition

This is one fresh `openai/gpt-5.6-sol` / `xhigh` attempt requested by the user to
compare with the completed Astra/xhigh pilot. It reuses the exact frozen task at
digest `fcf7827f7100d1ca54be84f6bc14fb320d27ca546fd5352ac45cb40b04110ab6`.
The CT, taxonomy, instruction, evaluator, source case, reference and runtime are
unchanged. The source and reference qualification, finite ten-organ scope,
controls, scoring rules and limitations remain those documented in the
[original protocol](../ct-organ-segmentation-astra-xhigh/protocol.md).

The attempt receives only the frozen solver-visible CT and `labels.json`. It does
not receive the Astra/xhigh output, trace, score, finding, review images, hidden
reference, source identifiers or comparison plan. It runs in a new Codex context
and a new native attempt directory. This is a foundation-model reasoning
condition with ordinary scientific libraries; additional pretrained segmentation
weights remain unavailable.

The fixed allowance is 7,200 agent seconds, four CPUs, a configured 12 GiB memory
cap and no GPU. The host may provide less usable memory than the configured cap.
There is one dispatch and no inference retry, continuation or post-result task
change. Existing oracle/no-op controls apply because native preview must reproduce
the identical task digest. A fresh shared-quota receipt with more than 25%
remaining is required immediately before dispatch. Run it before Astra/medium so
the two new solvers do not contend for the Docker host.

The native command is:

```sh
.venv/bin/med run ct-organ-segmentation-sol-xhigh \
  --model openai/gpt-5.6-sol --effort xhigh --harbor .venv/bin/harbor
```

Preserve normal failures, partial work and infrastructure failures distinctly.
Comparison across the three single attempts is descriptive and cannot establish
a population ranking or isolate model from reasoning-effort effects.
