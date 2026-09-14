# E03 author record

Hypothesis: an agent may repair an eigenvector derivative rather than the
invariant projector, passing distinct spectra and failing repeated internal
eigenvalues despite a separated selection boundary. This is a speculative
cheap pilot, not a benchmark-backed Terra failure.

[PyTorch documentation](https://docs.pytorch.org/docs/2.8/generated/torch.linalg.eigh.html)
warns about eigenvector derivatives at repeated spectra. That numerical issue
motivates the experiment but does not establish model difficulty.

Twenty-four matrix/upstream pairs cover distinct spectra, repetition in the
selected cluster, repetition in its complement, and near repetition. Each
family includes a trace/zero-gradient control. Matrices use dimensions 4, 8,
16, different k and rotated bases. Three public pairs show the advertised
issue. Upstream matrices are generally nonsymmetric; the public B-to-symmetric-A
expression fixes the derivative convention.

Truth is manufactured from known eigensystems before assembly of A. It sums
only selected/complement contributions. A separately written PyTorch custom
VJP and NumPy central finite differences cross-check it. The validation uses
five random symmetric directions per case at three step sizes, and a complete
coordinate finite-difference VJP baseline. Actual assembled spectral norms and
selection gaps are checked, not just the intended diagonal values.

The naive eigenvector derivative, zero gradient and blind nan_to_num controls
must fail. Finite differences are explicitly permitted and must pass the
published accuracy bar; no performance constraint is added to defeat them.
A clean model pass retires this snapshot. If a failure occurs, distinguish
nonfinite gradients, an incorrect factor for symmetric perturbations, and a
changed forward operator from the specific invariant-subspace hypothesis.
