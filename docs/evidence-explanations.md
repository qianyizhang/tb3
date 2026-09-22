# Evidence explanations

Use evidence explanations to connect a task, frozen measures, result/GT inspection,
trace evidence and calibrated interpretation. The deterministic CLI collects and
pins evidence; an agent performs the explanation. Neither layer changes historical
scores or turns a diagnostic observation into a qualified result.

```text
workbench records + frozen artifacts
              |
              v
    med evidence collect/check       model-free identity and availability
              |
              v
 evidence manifest + generated index
              |
              v
  explaining agent                   comparability, interpretation, views
              |
              v
 finding JSON + report + figures     durable, review-aware analysis
```

## Record model

`finding` remains the first-class record. Existing result reports, comparisons,
trace analyses and group syntheses already use that lifecycle and inherit experiment
review flags. Do not create a parallel `analysis` record kind.

The optional `analysis_kind` makes the report role queryable:

| Value | Use |
| --- | --- |
| `result` | Explain one experiment or condition. |
| `comparison` | Compare multiple runs, conditions or task revisions. |
| `trace_analysis` | Explain consequential intermediate work and failure attribution. |
| `audit` | Examine data, GT, scorer, instructions or methodology. |
| `synthesis` | Combine findings without pooling incompatible endpoints. |

New scaffolds always set it. Legacy findings without the field remain valid and
appear as `unclassified_legacy` in evidence manifests until deliberately backfilled.

## Model-free commands

```sh
# Print a manifest without writing.
uv run med evidence collect FINDING_OR_EXPERIMENT_ID

# Write only to the explicitly named new file.
uv run med evidence collect ID --output .local/explanations/ID.json
uv run med evidence check .local/explanations/ID.json

# Render a factual Markdown inventory. This is not the explanation.
uv run med evidence build .local/explanations/ID.json \
  --output .local/explanations/ID-index.md

# Explicitly create a finding/report/manifest scaffold owned by one group.
uv run med evidence new GROUP ANALYSIS_ID TARGET_ID... \
  --title 'Title' --analysis-kind comparison
```

Collection follows the selected record to experiments, attempts, evaluations,
freezes, reviews, issues and dependent findings. It records exact record hashes;
classifies frozen task files as input, instruction, reference, evaluator or
environment; summarizes run conditions; and selects high-signal result, report,
score and trace pointers. Missing local raw artifacts remain explicit.

`check` rejects changed or missing pinned records. The manifest does not copy raw
patient data, infer clinical meaning, declare GT wrong, select a causal explanation,
or decide that equal/different task digests are scientifically comparable.

## Agent-authored explanation

Use the `explain-medical-evidence` skill. Keep these layers visibly separate:

1. **Contract:** solver-visible inputs, output, evaluator and reference boundary.
2. **Measure:** exact frozen metric and denominator.
3. **Interpretation:** what the measure does and does not mean.
4. **Inspection:** actual source/result/GT view with coordinates and derivation.
5. **Mechanism:** consequential trace or intermediate artifact.
6. **Attribution:** observed failure, competing explanations and confidence.
7. **Limits:** GT, data, instruction, condition and generalization caveats.

Task changes are not normalized away. For every comparison, declare one of:
`matched`, `endpoint_only`, `diagnostic`, or `not_comparable`, with a reason.
Same task bytes do not remove model/runtime confounders; different task bytes do
not automatically make every endpoint unusable.

Follow the [visual explanation rulebook](visual-explanations.md). Prefer a compact
overview plus expandable evidence over a long chronological narrative.
