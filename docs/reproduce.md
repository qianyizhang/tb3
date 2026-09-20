# Reproduce selected work

The [daily workflow](workflow.md) documents installed commands and dependency setup.
All 38 retained experiments have canonical records. The [migration inventory](migration/native-experiment-inventory.md)
states which operations are maintained and where recovery gaps remain.

For `anatomical-landmarks-br040`, the input manifest declares exact saved CT/MRI
tasks, truth and outputs. `med prepare` restores a selected task, `med replay`
rescores saved answers, and `med view` draws native planes. Six saved outputs
reproduce every retained metric exactly. This establishes saved-output replay,
not fresh Docker execution or repeatable model behavior.

The [MRI package recipe](../exports/recipes/landmarks-mri-v2.json) selects frozen
task files, source notices, two saved model outputs, oracle output and standalone
replay code. `med export` writes a fresh independent directory. Inside it, run
`python3.12 replay.py`, then verify with `med verify-package /path/to/package`.
No source checkout, NumPy, Docker, network or inference is needed for this replay.
The Docker image is still a historical mutable tag; dependency artifacts and
current submission requirements need separate assessment before promotion.

Other historical methods remain preserved source evidence under `probes/` and
linked protocols. Their old authoring runners are not supported daily interfaces.
The active BR-042 owner retains its exact runtime and closeout path until cutover.
New studies use group-owned task files and the installed common runner.

Tour regeneration restores retained derived inputs, then renders/optimizes them;
it does not claim to reconstruct every original raw dataset derivation. Scientific
source provenance remains in the retained snapshot. Static stories and 17 figures
are portable. `med check --assets` checks their exact extraction when needed.

Independent off-machine backup remains unverified. This migration does not delete
ignored raw runs or environments, certify clinical correctness, or promote a
package to submission-ready.
