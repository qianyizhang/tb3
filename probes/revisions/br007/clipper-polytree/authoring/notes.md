# BR-007 ownership and verification

This is a new frozen condition of the historical source repair. BR-005 and
original Clipper snapshots remain untouched. The source and license come from
the BR-005 stripped package. No new source defect is injected.

The crux remains horizontal joining and contour ownership. Coverage expands
from three base geometries to 18 base layouts, four integer affine transforms
and two input-order/ring-start variants: 144 semantic cases. Seven base layouts
derive from the bundled rectilinear historical regressions; eleven are original
ladders, depth-four/depth-six nesting, signed cancellation, difference,
intersection and empty-output controls. No geometry is selected after a model
run. The corpus generator records the full pre-run layout inventory.

`arrangement.py` evaluates the winding-based Boolean operation on exact
elementary cells, extracts oriented boundaries, and reconstructs containment.
Integer affine transforms preserve these independently computed contours.
The private verifier contains baked expected trees, not a working Clipper
implementation. Full contour/hierarchy equality is invariant to sibling order,
ring start, winding, duplicate endpoints and intermediate collinear vertices.
Parent indices, levels, hole parity and repeated API execution are checked.

The agent gets the public driver/checker and four examples, including an
explicit empty interface-compatible output where relevant. The private corpus,
arrangement generator, oracle and previous model artifacts are outside the
agent build context. Existing historical tests retain their legitimate source
context; their fixture paths and Cargo registration are repaired for usability.
The legacy `Tests` directory is packaged as `fixtures`, with the PolyTree suite
registered under lowercase `tests`; this also works on case-insensitive hosts.

The full repair passes all 144 cases. Unmodified source fails 80, the prior
Terra artifact fails 72, reverting registration fails 80, and reverting ordering
fails 72. Removing persistent scan-position updates alone passes all 144. That
last control is retained as a passing simplification; the experiment does not
claim those updates are semantically required. No case was removed to obtain
these results, and no model has run during authoring.

The private source archive is a packaging copy of the stripped agent Rust
snapshot, Cargo files and licensed fixtures, not the removed C++ reference.
It supplies immutable build scaffolding around the transferred `src` directory.
Submitted code runs under an unprivileged account separate from the root
grader and expected trees. This is ordinary verifier separation, not a security
research task.
