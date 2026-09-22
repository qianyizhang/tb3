# Retained examples

The [Longitudinal-CT sample review](longitudinal-ct-review-20260922.md) records
four downloaded CT pairs, explicit lesion correspondence GT, three illustrated
examples and one facial image/reference concern. The
[proposed Task Brief](../presentation/briefs/longitudinal-ct-correspondence.md)
frames marked-target correspondence without authorizing a model trial. Its
local interactive reader and raw inputs have recovery instructions in the review.

The [BR-037 protocol](../../../docs/research-rounds/BR-037-longitudinal-reading.md)
and [retained reading review](../../../docs/research-rounds/BR-037-results.md)
describe the three cases and four attempts. Full examinations remain local; the
review distinguishes reference measurements from unadjudicated clinical interpretation.

Use `python3.12 scripts/med new longitudinal-reading NEW-ID --title TITLE` to start
a disabled scaffold. Copy a case only after selecting its source, truth, license
and solver/evaluator boundary; do not import an old authoring module to get a sample.
