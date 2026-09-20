# Main-branch cutover

On 2026-09-21 the user requested absorption of the completed experiment and the
pending repository pivot into one clean `main` branch. Source task:
codex://threads/01a0c002-3428-7311-8dec-1c05b815cdb2.

The integration combines the native workbench (`7177822`, `f5b2ced`), the docs
and group-history cleanup (`3f4d79f`, `4ca6dc4`), and the experiment owner's
completed closeout (`c31e660`). Original commits remain in history. No redirect
pages, old CLI wrapper or dual metadata reader is restored.

## Completed experiment

The two new BR-042 execution records keep their stable identities. The first
ended with a transport error; the second is its completed resumed continuation,
not an independent trial. The original imported classifications, rewards, metric
dictionaries and evidence hashes are preserved. Canonical status fields describe
execution separately from the unchanged scorer's outcome.

The resumed review is now discoverable through `med show` and the shared index.
Its original report remains byte-identical under `resume1/evaluation.json`;
the canonical observation links that source digest and explicitly limits its
failing outcome to the frozen coronary scorer. Broader anatomy and disputed
reference identity remain unadjudicated. The experiment is closed; migration
alone does not assign a new evidence assessment or qualify a submission.

The historical one-shot adapters and protocols remain source evidence. Their old
launch and monitoring instructions are marked historical; new work uses the
[current workflow](../workflow.md). No model, Harbor, Docker or historical authoring
script was run by this cutover.

## Concurrent work and local artifacts

The completed trace audit is retained byte-for-byte, with a canonical source-linked
observation and its appended idea-card finding. It carries no new scorer verdict.

The Task Explorer source collection and BR-043 explanation follow-up are absorbed
with their ownership and decision provenance. Its commands use `med brief
new|build|check`; the normal native check validates its catalogue. Two discussion
records use the canonical schema, without importing task payloads as research
metadata. Existing source receipts and user-approved vocabulary are retained.
The obsolete staged `scripts/check_medical.py` change is integrated into `med check`.

Local landmark inputs, prepared task copies, the verified MRI draft package,
review figures and retained tour inputs are copied from the migration worktree
into the original checkout without overwriting differing files. Each copied file
is hash-verified. At the initial cutover, both worktrees' original local runs and environments
remained intact. These same-disk copies do not establish independent backup.

The migration branch is absorbed and retired. The former migration checkout was initially
retained detached at the consolidated commit to preserve its local environments
and artifacts; the follow-up below completes its removal. No remote settings, history
or existing submission checkout are changed, and no push or publication occurs.

## Verification

The combined tree passes `make check PYTHON=python3.12`: 44 tests (43 passed,
one existing optional SciPy-dependent skip), 2,036 indexed files, metadata, 153
source measurements and Ruff checks. The original checkout now reads 571 records
across 38 experiments, with all 284 catalogue entries linked and six illustrated
briefs available without missing local media. All six saved CT/MRI replay metric
dictionaries still match exactly after local-input absorption; the copied MRI
draft package verifies all 25 files. Browser interaction verified the closed
BR-042 record, resumed observation and Task Explorer case selection.

The machine-readable [cutover receipt](main-cutover.json) records source hashes,
canonical mappings, local-copy accounting and final check results. Checks use an
existing Python 3.12 environment: automatic approval review rejected creation of
a fresh environment under the no-runtime-installation maintenance rule. No new
runtime or dependencies were installed.

The inherited replay/export proof remains scoped to its recorded selected
landmark cases. Integration verification does not certify new model behavior,
clinical correctness, all historical recovery paths or submission readiness.

## Worktree removal follow-up

Later on 2026-09-21, the user explicitly requested removal of the fully absorbed
worktree. Its detached head (`d258eb6`) was verified as an ancestor of `main`,
with no uncommitted source changes. All 5,102 ignored files (3,105,056,049 bytes,
plus preserved symlink targets) were matched to hash-verified copies in this
checkout before the old worktree was removed. Only the main checkout remains
registered with Git.

Previously unabsorbed generated files, logs, caches and the original environment
are retained under `runs/native-cutover-20260921/worktree-residual`; the local
`worktree-removal-manifest.json` maps every original file to its preserved copy.
The existing Python environment was also relocated to `.venv-medical`, with
launcher and editable-source paths updated. `.venv-medical/bin/med` resolves
this checkout, its imports and Ruff work, and the preserved Playwright package
loads from `node_modules`. No dependencies were installed. The original runtime
snapshot remains unchanged for provenance.

The active Task Explorer follow-up was allowed to finish before removing the
old environment path. Its source changes retain their separate ownership.
