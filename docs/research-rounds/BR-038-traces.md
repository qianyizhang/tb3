# BR-038 — coordinate audit and remaining localization errors

[Measured results](BR-038-results.md) · [Setup audit](BR-038-volume-landmarks.md) ·
[Native voxel-axis overlays](../../runs/br038-volume-landmarks/review/index.html)

Both fresh Terra/high attempts completed normally, ran the supplied coordinate
check, used the supplied viewer and submitted valid tagged voxel coordinates.
Four matched Docker oracle/nop controls behaved as expected. Host replay matches
the verifier exactly. A separate calculation maps predictions to source RAS and
compares directly to original manual coordinates: discrepancies from the voxel
metric are below 3e-14 mm. No web calls are recorded in either new attempt.

| Complete volume | Fixed tolerance | Accepted | Mean / maximum error | Agent time |
| --- | --- | --- | --- | --- |
| CT, 4 landmarks | 5 mm | 2/4 | 18.094 / 35.146 mm | 488 s |
| MRI, 32 landmarks | 3 mm | 3/32 | 9.402 / 28.235 mm | 265 s |

The CT predictions for chin and dens are within 2.724 and 2.436 mm. Both condyle
predictions are wrong by 32.072 / 35.146 mm. The right condyle was placed 20.48 mm
anterior and 24 mm inferior to the reference, with a smaller lateral error.
This is not a uniform image-origin offset applied to all four points. The agent
used many orthogonal views, then threshold/component checks, but the final
selected condylar positions remained wrong. Calling the exact mistaken structure
requires anatomical adjudication; no such independent review was performed.

The MRI AC error is 0.716 mm: the earlier cropped-run origin assumption is absent
from this output. Splenium (1.555 mm) and right anterolateral temporal horn
(2.616 mm) also pass. The genu is 23.866 mm away, largely posterior to the source
protocol's most anterior callosal point. The voxel-labelled overlay makes this
error visible without interpreting a physical coordinate convention. Large
errors remain at occipital-horn and ventricular queries. The attempt rendered
native views and used the provided helper, but did not achieve uniformly precise
subject-specific landmark placement.

For the eight queries shared with the earlier **full-volume** MRI run, the new
attempt passes 2/8 versus 0/8 originally. [Pointwise overlap](../evidence/br038-mri-overlap.json)
records the comparison. The larger query set, changed representation, explicit
coordinate cautions, viewer scaffold and fresh sample all prevent a one-factor
causal conclusion. The CT success count improves 1/4 -> 2/4 while its mean error
worsens because the new attempt misses both condyles more severely.

## What was and was not resolved

The earlier inputs were 3D arrays: full volumes or truncated volumes, never
supplied 2D patches. The agent could read the full arrays programmatically and
render arbitrary slices; visual model inputs were those generated 2D images.
This is a coding-agent workflow, not direct inference by a native 3D medical
vision model on an image tensor. Raw original sessions contain structured image
payloads, and independent geometry checks find no scoring-coordinate defect.

The new experiment removes the requirement for the agent to convert its chosen
voxels to physical RAS coordinates. It supplies one explicit native index
contract, verified slice mappings, axis labels and examples. Both outputs obey
that contract; several points are accurate, while others remain far from their
references. This rules out an evaluator-wide RAS/LPS/index mismatch in these
runs. It does not prove that the agent never misread an image axis, misidentified
a structure, or misapplied a local anatomical definition.

These remain two-subject, single-attempt pilots. Source reference annotations
are not independently clinically adjudicated; one MRI rater is slightly beyond
3 mm for a point. That caveat matters at a boundary but does not account for all
large errors. No population accuracy, repeatable difficulty, or clinical
capability claim is supported. Original data/results are preserved and no
additional trial is queued.
