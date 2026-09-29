# FeEcho4D BR-027 local teaching assets

Actual FeEcho4D Patient001 source images, supplied anchors and saved author outputs.
Source: https://feecho4d.github.io/Website/ . Research-use terms apply; this pack
is for the user's local noncommercial interpretation. No public redistribution
right is asserted. Keep source-derived images and geometry local.

Source images are downsampled from 485 x 464 to 243 x 232 for display. Boundary
overlays are native binary contours widened to two native pixels then scaled by
nearest neighbor. The one/two-anchor output masks are retained saved predictions;
withheld plane-8 cyan sections are projected from retained saved radius profiles.
Gold source boundaries are reader-only evaluator material, never solver input.
The dense volume comparator uses all 36 source directions, including evaluation
views; it is annotation fit rather than independent three-dimensional truth.

The 0/45/90/135-degree pose model is assumed. This viewer replays arrays and
does not run tracking, interpolation, fitting, scoring or a model attempt.
The mesh wire view samples eleven polar rings and twenty-four azimuth points
per ring directly from each retained saved mesh, rounds them to 0.001 mm for
display, and uses one fixed oblique projection and scale over all frames.
Rebuild only to a fresh local directory with scripts/build_cardiac_anchor_assets.py.
