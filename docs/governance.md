# Artifact ownership and retention

Research is closed; [the final report](report.html) owns the synthesis and
[the archive index](archive.md) owns reader navigation. Historical next actions
do not authorize new work. The clean submission has [separate ownership](submission.md).

This policy preserves the small authored record while keeping local execution
outputs out of commits. It does not delete files or move frozen task inputs.

| Location | Owner and treatment |
| --- | --- |
| `scripts/`, `tests/`, `configs/` | Workshop implementation, executable contracts, dependency pins and artifact policy; track. |
| `probes/<id>/environment`, `tests`, `solution` | Task and verifier inputs, including vendored source, licenses, locks and required archives; track after review. |
| `probes/<id>/authoring` | Provenance, reviews and concise controls; track. |
| `docs/report.html` and report provenance | Authored interview presentation, including attributed embedded illustration; track. |
| `docs/` and `docs/evidence/` | Source-linked research, decisions, frozen plans and concise evidence; track, retaining historical failures. |
| `catalog/ideas`, `reviews`, `analyses` | Authored candidate decisions and append-only reviews; track. |
| `catalog/trials` | Allowlisted imports from raw evidence; track deliberately after review. |
| `runs/`, `jobs/` | Raw logs, trajectories, submissions and generated HTML; local, ignored. |
| `.cache/`, `.venv*`, compiler/debug outputs | Rebuildable local material; ignored. |

The [round register](research-rounds.md) owns brainstorm chronology and handoffs;
round documents retain source provenance, proposed experiments and dispositions.
They link candidate cards, plans, freezes and ledger evidence without replacing
those authorities. Raw conversation exports stay local. Capturing a round does
not establish its hypotheses or change the submission requirements.

## Commit gate

`make hygiene` reads blobs and policy from the Git index, not the working files.
It rejects forced additions of runtime directories, credentials by filename,
compiler/debug output, symlinks, submodules and unresolved merges. It parses
first-party JSON/TOML and rejects binary files or files larger than 1 MiB unless
an exact path, SHA-256 and reason appear in `configs/artifact-policy.json`.
Vendored directories skip first-party syntax checks only; artifact checks still
apply. The gate is a filename/size/content-format check, not a general secret
scanner or full catalog schema/evidence validator.

Known required large inputs are recorded explicitly: SQLite's amalgamation and
shell fixtures, and Clipper's verifier archive used by Docker `ADD`. Each entry
links its provenance or authoring note. Entries can precede a probe's first
commit; absent entries do not require an unfinished probe to be staged. When a
retained input changes, inspect its source/license and dependent Docker/verifier
usage, then deliberately update the digest. Do not blanket-ignore archives,
JSON, text evidence, vendored source, or dependency lockfiles.

Ignore rules protect normal staging; the independent gate catches forced
staging. If intentional new fixture names conflict with a blocked artifact
pattern, review and update both the ignore rules and artifact policy explicitly.
Never force-add a runtime output merely to make evidence links exist in CI.
Historical raw `runs/` links are expected to be unavailable in a fresh clone.

## Evidence and cleanup

Before removing anything, establish its owner, active writer, retained copies,
and references from task freezes, Dockerfiles, verifiers, catalog records and
research notes. Disposable caches may be recreated; raw trial evidence often
cannot. There is no age-based cleanup, scheduled deletion, or `git clean -fdx`
automation. `make artifacts` is an inventory only. Run catalog sync explicitly
after a completed trial; CI and hooks must never mutate catalog evidence.

Repository CI runs only the artifact gate and synthetic unit tests on Python
3.12. It does not install Harbor, execute submitted code, build probe images,
run models, regenerate freeze hashes, or certify upstream static checks. Actual
trial and submission validation remains governed by `requirements.md` and the
owning experiment plan.

## Concurrent work and semantic commits

Check Git status and task ownership before staging. A hygiene task owns its
policy, documentation, hooks, checks and workflow; an active experiment owns
its probes, freezes and outcome records. Commit explicit paths or selected
hunks. Validate the committed tree in a temporary archive when the main
checkout has unrelated changes. Report local validation separately from hosted
CI and distinguish committed work from remaining unstaged experiment files.
