# E06: clean pass; retire

Terra/high passed all 24 trajectory/VJP cases with normal completion,
reward 1 and no exception in 46.887403 agent seconds. Matching oracle/nop
controls returned 1/0 and all three runs share Harbor checksum
`b30bbc55f5db0ec5db40b9ffc70aac4e47c1208b46af5968538894fad6946900`.
The current task bytes still match the pretrial workshop freeze.

The agent removed the two detach operations on impact time and normal, keeping
both in the autograd graph. Its own directional finite-difference check agrees
to about 2.2e-10; the private analytical derivatives also pass. This is the
direct permitted repair and H06 is not supported. Retire without additional
contacts, grazing cases, tighter tolerances or restrictions on autograd.

The author controls agree between a known-contact implicit Jacobian,
exact-quadratic-root autograd and complete coordinate finite differences.
The unchanged starter passes all forward values but only 6/24 VJPs, isolating
the derivative defect. Energy, momentum, contact-distance, rotation and
event-margin checks pass. Linux repeats the same acceptance/rejection counts.
The 24 cases are eight collisions with three rotations, not separate trials.

Evidence: [freeze](../../docs/evidence/collision-pilot-freeze.json),
[summary](../../docs/evidence/collision-trial-summary.json),
[controls](../../docs/evidence/collision-author-controls.json).
This is the twelfth valid local Terra pass and completes the requested six-idea
round. Static sanity is 21/22, with final human-authored README material absent;
final submission gates remain open.
