# Artifact ownership and retention

The medical workbench is active for user-authorized work. The original interview
and selection queue are historical. The [existing submission](submission.md)
remains independently owned. Start with [current documentation](README.md);
[migration history](migration/README.md) records the pivot and integration boundary.
The [workflow](workflow.md) explains the supported interface.

| Location | Authority and treatment |
| --- | --- |
| groups/ | Semantic ownership: ideas, decisions, methods, experiments, findings, presentation. Small source records are tracked. |
| groups/<group>/history/ | Dated research closeouts, retrospectives and trace accounts. Current findings and presentation remain separate; narrative navigation may be maintained without changing scientific outcomes. |
| datasets/ | Source explanations, selected samples, pinned receipts, task links and access/recovery gaps; no implicit downloads or trial authorization. See [dataset contracts](../datasets/README.md). |
| discussions/ | Local notes and artifacts are ignored by default. Exact exceptions retain important design histories and stable records under records/. Maintained Task Explorer content lives in presentation/external-tasks/. |
| src/tb3_medical/, scripts/, tests/, configs/ | Common interfaces, adapters, executable checks and artifact policy. |
| presentation/ | Shared read-only renderer, media tools and portable publication support. |
| exports/ | Pinned recipes and lineage records. Generated destinations have explicit ownership; never overwrite them. |
| probes/ and docs/evidence/ | Retained medical task/source snapshots and concise historical receipts. Original bytes stay immutable. |
| docs/research-rounds/ | Historical protocols/outcomes and active writers' handoffs. Round numbers are historical provenance, not lookup aliases. |
| archive/README.md and manifest.json | Recovery locators, exact hashes and retirement reasons. Payload under archive/legacy/ is ignored. |
| runs/, jobs/, .local/, .cache/, .venv*/ | Local raw outputs, credentials, environments and caches. Do not delete as cleanup. |
| presentation/tours/data/, presentation/tours/web/, presentation/tours/exports/ | Local derived media; retain source provenance and static fallbacks in Git. |

Attempts identify executions. Evaluations identify observations or replays.
Reviews assess experiment conclusions; they do not alter original scores. Groups,
findings and exports cite experiments directly. An unresolved issue flags that
experiment and its summaries for review, retaining the affected run list.
Acknowledged withdrawal and narrower reassessment remain explicit historical
events. Missing local inputs are an operation-specific availability issue, not a
scientific verdict. Reads use stored state and timestamps, never a live audit.

The Git-index artifact gate rejects runtime roots, credentials by filename,
compiler output, symlinks, submodules and unresolved merges. First-party JSON and
TOML must parse. Binaries and files over 1 MiB require exact path, SHA-256 and
reason entries in configs/artifact-policy.json. This is not a general secret
scanner or a clinical/task qualification certificate. The discussions policy keeps
local working artifacts out of Git; it does not exempt allowlisted records from
validation. Elsewhere, do not blanket-ignore docs, probes, JSON, archives or license
files to bypass the gate.

Archive only an enumerated, verified scope. Keep the original Git commit and a
verified bundle; record required local artifacts separately. A same-disk copy is
recovery convenience, not independent backup. No scheduled deletion, history
rewrite or `git clean -fdx`. CI never starts Docker, inference or authoring scripts
that overwrite historical evidence. Stage only your owned changes, then run
Python 3.12 checks and inspect a clean tree before committing.
