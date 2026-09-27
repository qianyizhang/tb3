# Study geometric shortcuts in mask reasoning

An author study of what geometry already solves, and what the retained evidence
cannot establish. This entry is supporting research, not a solver task or trial.

## Value

Screen inexpensive baselines before claiming that a mask-only task requires a
hard anatomical relation. Preserve useful successes and unresolved alternatives.

## Given

### Original data

Eight retained, unmodified TotalSegmentator source-label arrays in their physical
LPS frames: cases 19, 28, 32, 46, 61, 74, 83 and 95. The author screen uses original
masks, not the earlier BR-004 planted edits. BR-010 separately audits seven
historical Terra/Sol tool trajectories.

### Supplied helpers

For the ordering screen, the author baseline knows each lumbar or left/right rib
family and its proposed-label multiset. For the organ classifier, seven other
patients supply labeled training examples for each held-out patient. These are
different assistance conditions; I2 prototype solvers do not receive that training set.

### Callable tools

The retained NumPy method computes full-mask centroids, volumes and bounding-box
extents, then sorts physical superior coordinates or compares standardized feature
vectors with median class templates. No parameter search or one-to-one assignment
was performed. Historical authoring modules are inspection sources, not importable
presentation helpers.

### Reference-only material

Original identities, retained baseline predictions and post-hoc source comparisons
are author references. The teaching view reveals them explicitly for the reader;
it must not become a blind solver packet. Source-label agreement is not independent
clinical adjudication or proof that identities are inferable from masks alone.

## Task specification

Audit the strategy evidence, measure simple geometric baselines, and state which
candidate designs remain admissible questions. Do not convert residual errors into
model failures or select a partial-coverage case merely because a baseline fails.

## Expected output

A provenance-backed author assessment with exact baseline predictions, counterexamples,
solver/reference boundaries and reopening conditions. No model answer file is requested.

## Evaluation

The retained ordering screen recovers **23/24 groups** across eight patients. All
lumbar groups pass. In case 74, left ribs 8/9 reverse centroid order; coverage and
anatomical review are still required. Ordinary label permutations of the solved
groups are not supported as difficult leads.

The leave-one-patient-out organ baseline agrees on **109/131 nonempty identities**,
with **0/8 complete scenes** correct. Its seven features are normalized centroid
coordinates, log physical volume and three log box extents; training standard
deviations scale nearest-median-template distances. Instances are clustered by
patient. The case-32 example mislabels spleen as stomach. These are author-screen
results, not Sol/Terra scores, causal evidence or clinical performance.

## Difficulty

BR-010's seven targeted trajectories already contain quantitative and relational
checks. Terra's solved rib exchange is counterevidence to a blanket reasoning
weakness. Sol's numeric signal followed by an empty report leaves interpretation,
contract and clinical-significance alternatives unresolved. A mask alone may not
distinguish a genuinely short organ from an omitted pole.

## Coverage

I1 audits proposed identities; I2 infers anonymous identities; I3 separates identity,
annotation quality and verified unusual anatomy. I1/I2 need matched geometry and
assistance for comparison. I3 needs source context and adjudication from only the
solver-visible inputs. Check unique assignments and unchanged controls before
freezing any trial. The separate I2 prototype entry demonstrates representation;
it does not establish difficulty.

The integrated story shows selected source-derived point samples from case-32 and
case-74 left ribs and case-32 organs. Full occupancy determines centroids and
features; sampled points discard detail and have no mesh faces. Each scene retains
shared position and scale; different patients are independently fitted, not registered.
The dashed centroid guide illustrates ordering, not anatomical attachment.

## Sources

- [BR-010 — From boundary inspection to anatomical consistency](../../experiments/br010/protocol.md)
- [Seven-trajectory retrospective audit](../../../../docs/evidence/br010-mask-reasoning-audit.json)
- [BR-011 — Author screens and distinct identity/quality hypotheses](../../experiments/br011/protocol.md)
- [All retained baseline predictions and source hashes](../../../../docs/evidence/br011-author-screen.json)
- [Display derivation, source checks and terms](../../../../presentation/task-explorer/mask-screen/NOTICE.md)
