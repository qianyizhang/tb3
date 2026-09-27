# Analyze a single-view registration failure

Explain why repairing one code defect did not rescue the selected BR-021 case-one
registration miss, while preserving the two fresh BR-022 attempts and their mixed outcomes.

## Value

Separates transform composition, search support and image-matching objective.
This is a retrospective author analysis with privileged references, not a new solver task.

## Given

### Original data

The original solver received a complete 171 × 118 exhalation CT section, a complete
192 × 192 × 208 inhalation target CT, eight fractional-pixel queries, 1.25 mm
in-plane spacing and the known source pose. No full source volume was supplied.
Coordinates are dataset-world millimetres; native patient LPS/RAS is not asserted.
The author additionally retained source code, final answers and reconstructed stages.

### Supplied helpers

The postmortem recovered the original trace and fitted transforms. The original
trial image had been removed; historical replay used an identical-Dockerfile image
with pinned packages and matching task bytes. Its maximum final-coordinate drift
was 6.30 × 10⁻⁹ mm. Today’s explainer reads these retained results without rerunning
a solver, optimizer or model.

### Callable tools

The historical solver used the frozen Python imaging environment. The author
protocol fixed replay, transform/search interventions, a context-by-flexibility
control and exactly two fresh Terra/high sessions. Presentation generation uses
only local retained artifacts and deterministic measurements.

### Reference-only material

Manual target landmarks, reference-centred CT patches, point errors and diagnostic
searches are author/reader references. The original and fresh agents did not receive
this postmortem. Public annotation availability remains an exposure limitation.

## Task specification

Check that replay preserves the final coordinates before interpreting intermediate
stages. Compare B(x) against the original A(B(x)), distinguish a search box’s best
possible geometric error from optimization failure, and inspect the recorded
patch objective at manual and submitted points. Keep author controls separate from
fresh blind attempts.

## Expected output

A source-linked attribution report and reader explainer with separate observed
defects, controlled comparisons, counterexamples and unresolved alternatives.
The underlying solver output remains eight ordered `query_ids` and finite XYZ rows
in `points_world_mm`, saved to `/app/answer/points.json`.

## Evaluation

The frozen task requires **RMS ≤ 3 mm and maximum ≤ 5 mm** over all eight points.
The selected original scored **12.641 / 23.796 mm**. Two predeclared fresh attempts
scored **24.905 / 34.165 mm** and **2.021 / 4.646 mm**; oracle/no-op controls passed/failed.
These scores remain unchanged. The analysis is not another autonomous outcome.

## Difficulty

Minimal composition repair still scores **12.410 mm RMS** at seed 17 and ±9 mm.
q04 lies **18.994 mm** outside that original box. Widening to ±30 mm includes all
targets but the fixed finite searches still fail. q01/q06 already lie inside the
box; their recorded objective scores are higher at the submitted points than at
the manual targets. A small numerical patch also appears in the successful fresh
agent, which used broader candidate search, visual/stability checks and orientation
refinement. No single component is established as a universal cause.

## Coverage

Fourteen retained transform/search variants and four author context controls are
diagnostic interventions. The original miss was selected after its outcome;
the two fresh sessions are the predeclared repeat cohort. One case and eight sparse
points establish neither population performance nor a validated dense deformation.
The exact snapshot was retired as a reliably difficult Terra candidate after the pass.

## Sources

- [BR-022 — systematic analysis of the BR-021 single-view failure](../../experiments/br022/protocol.md)
- [Attribution finding and source fitness](../../findings/respiratory-failure-mechanisms.md)
- [Retained source views and derivation](../../../../presentation/task-explorer/registration-analysis/NOTICE.md)
