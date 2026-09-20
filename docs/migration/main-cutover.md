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
is hash-verified. Both worktrees' original local runs and environments remain
intact. These same-disk copies do not establish independent backup.

The migration branch is absorbed and retired. The former migration checkout is
retained detached at the consolidated commit to preserve its local environments
and artifacts; it is not another development branch. No remote settings, history
or existing submission checkout are changed, and no push or publication occurs.

## Verification

The machine-readable [cutover receipt](main-cutover.json) records source hashes,
canonical mappings, local-copy accounting and final check results. Checks use an
existing Python 3.12 environment: automatic approval review rejected creation of
a fresh environment under the no-runtime-installation maintenance rule. No new
runtime or dependencies were installed.

The inherited replay/export proof remains scoped to its recorded selected
landmark cases. Integration verification does not certify new model behavior,
clinical correctness, all historical recovery paths or submission readiness.
