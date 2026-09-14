# E06 author record

The brainstorm's collision-gradient reserve is an original numerical probe.
It has no audited model-failure result. Motivation comes from
[differentiable rigid-body simulators](https://arxiv.org/abs/2305.00092),
[DiffTaichi](https://arxiv.org/abs/1910.00935), and the
[TOI discussion](https://docs.taichi-lang.org/zh-Hans/blog/improving-gradient-computation).
The source's wider simulation and optimization setup is not reproduced.

The fixed profile has two equal disks, one nongrazing elastic collision and
an eight-coordinate initial state. Masses, radius and restitution are fixed
physical constants; the only requested derivative is with respect to initial
state at fixed final time. This removes parameter bookkeeping from the
reference's broader proposed API. No runtime or library restriction is used
to create difficulty. Removing the two incorrect detach operations is a valid
repair if it produces the correct derivative, as are explicit formulas and
complete finite differences.

Eight canonical collisions and three rotations yield 24 cases, not 24 model
trials. Expected trajectories are constructed at a known contact time and
normal before the initial state is serialized. The private Jacobian uses the
implicit contact equation n·(dr+t dw+w dt)=0 and the corresponding normal and
impulse differentials. A separate exact-quadratic-root autograd reference and
coordinate finite differences must agree. Five directional differences per
case at each of three step sizes also test the gradient. Public cases cover
head-on and oblique geometry; private cases include zero and conserved-total-
momentum upstream controls.

The starter must pass every forward check while missing derivatives, isolating
H06 from collision detection or trajectory bugs. Pre-freeze validation also
checks contact distance, energy, momentum, rotation equivariance and margins
from grazing/event boundaries. The public profile and acceptance tolerate
ordinary float64 and central-difference errors. H06 requires a healthy,
independently reproduced derivative miss tied to event/normal dependence.
A clean pass retires the snapshot without more bodies or event transitions.

All code and fixtures are original; no source benchmark tests are copied.
