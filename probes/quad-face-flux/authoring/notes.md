# E02 author record

This is a new planar RT0 reconstruction task, not the published spherical
Parcels task 036. The audited Sol source miss produces NaN near the north pole;
it does not establish failure of a contravariant Piola reconstruction. The
requested pilot tests that proposed crux directly with open mathematical
semantics and correct supplied geometry helpers.

Reference: [DefElement RT](https://defelement.org/elements/raviart-thomas.html).
The public contract fixes the reconstruction space, flux units, orientation,
map and both acceptance criteria. No algorithm, library, or direct formula is
prohibited. A successful formula implementation retires this snapshot.

Eight base cells, three flux patterns and three rigid transformations yield
72 cases. Each has 16 interior points and 8 Gauss points per edge. These are
cases within one trial, not independent model attempts. Three public examples
cover a square, skew parallelogram and non-affine cell. The geometry generator
manufactures expected values at known reference coordinates; it does not use
the supplied inverse helper. A direct reference implementation uses that helper
and independent NumPy determinant/matrix operations.

Pre-freeze validation checks inverse residuals, corner Jacobian determinant and
condition bounds, plus edge quadrature at orders 4, 8 and 16. For a convex
bilinear quadrilateral the determinant is affine in reference coordinates;
the chosen mild cells stay far from degeneracy. Norm/adjugate bounds can also
bound conditioning throughout using the four corners. The verifier integrates
candidate velocities with physical edge tangents/normals, independently of the
manufactured pointwise expected values.

Targeted controls omit the mapping, omit its determinant, reverse outward signs,
or use one cell-centre Jacobian. Distinguish a sign mistake from H02's predicted
component-interpolation error. A supporting H02 result needs successful square
controls and reproducible transformed/non-affine misses with normal execution.
Fixtures/expected outputs and all task code are original; no source repository
or benchmark private test is copied.
