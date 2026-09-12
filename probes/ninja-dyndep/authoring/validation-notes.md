# Pre-trial authoring corrections

The separate verifier builds and runs all submitted C++ as an unprivileged user. Compilation has a generous 120-second cap, separate from six-second graph commands. Harbor enters /tests/test.sh; the artifact parent is created by a literal RUN mkdir instruction.

Pinned static checks also require the exact instruction suffix and canonical canary in supported text files under tests/. The vendored trusted build scaffold preserves upstream licensing and behavior; 61 files received comment-only canaries before the frozen Docker controls. These are authoring corrections, not model failures.

The first real Docker oracle returned zero because sanitizing file modes removed inline.sh executable permission. The verifier now preserves execute bits while keeping compilation unprivileged. The failed control is retained as ninja-oracle-20260912, not a model trial.

The second Docker oracle exposed another fixture-only permission fault: cp inherited the protected input mode (0444), making generated outputs unwritable on the next build. Producer commands now use shell redirection from cat, which creates ordinary writable output files. The scheduling contract is unchanged; ninja-oracle-final-20260912 records this excluded authoring control.
