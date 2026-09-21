Source: `docs/research-rounds/BR-024-neighborhood-plan.md`; original SHA-256: `cde3c211eef881e258fcaae43dd8788ea990faa6bcea7ab847267b5a96848e50`.
Repository source locators below are provenance; they are not required runtime inputs.

# BR-024 — final bounded feasibility rescue for patient 2

Fixed after both prior author methods missed all three patient-2 views, while
the already admitted patient-3 Sol trial is running. No patient-3 model outcome
informs this method. This is the final author rescue in this round.

Reuse the unchanged local-affine patch matcher on a deterministic 10-pixel grid
within 36 pixels of the original queries, retaining nodes with source-patch
standard deviation at least 20 HU. Fit a local displacement plane around each
query, using a 20-pixel Gaussian distance weight, NCC confidence and eight
robust-regression iterations with a 3 mm residual scale. Nodes, starts, matching,
weights and output decisions use only the public images and geometry.

Keep the original query match if it lies within 5 mm of the neighborhood
prediction. Otherwise use the neighborhood prediction and refine its translation
within 3 mm on each world axis, with fixed local basis from the fitted field and
10/16/25 mm patches weighted 0.4/0.35/0.25. Record all intermediate results.
The accompanying code hash fixes remaining implementation details before runs.

Run the unchanged ranked patient-2 candidate list, stopping at the first whole
answer passing the original tolerances. Grading occurs only after each isolated
public-input execution. No label-based choice between alternative per-query
answers, initialization, parameter tuning or further author rescue is allowed.
If all three fail, retain patient 2 as unqualified and finish with the admitted
patient-3 trial. A failed author solver is not a Sol failure.
