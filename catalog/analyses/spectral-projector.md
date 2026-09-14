# E03: clean pass; retire

Terra/high passed all 24 private matrix/upstream pairs with normal execution,
reward 1 and no exception. Agent execution was 102.690817 seconds. Both
controls and the model share checksum
`83dfb4912e62761da4fecd00631f3e716c1d11366258a0c9f6eab25393dbe536`;
the pretrial workshop hash is unchanged.

The submitted custom autograd function saves an eigensystem for the forward
projector. Backward symmetrizes the upstream derivative, divides only the
selected/complement block by its open eigenvalue gaps, and symmetrizes the
result. It does not divide by internal eigenvalue differences or perturb the
operator. The trajectory records public, rotated/repeated, finite-difference
and identity-upstream checks. This directly addresses the proposed conceptual
crux; H03 is not supported by this trial. Retire the snapshot without larger
matrices, stricter runtime or a ban on numerical differentiation.

The author controls also accept complete coordinate finite differences. Linux
CPU oracle/nop returned 1/0. A host NumPy BLAS warning during matrix assembly
was eliminated by explicit contraction before the freeze; finite results were
independently checked through eigenvalue bounds, directional differences and
orthogonal equivariance. It was not a model failure.

Evidence: [freeze](../../docs/evidence/projector-pilot-freeze.json),
[summary and runtime packages](../../docs/evidence/projector-trial-summary.json),
[controls](../../docs/evidence/projector-author-controls.json).
Raw submission and trajectory are linked through the summary/catalog trial.
This is the ninth valid local Terra pass. Static sanity is 21/22, with only
the final human-authored README absent; final submission gates remain open.
