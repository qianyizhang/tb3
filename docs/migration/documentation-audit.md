# Documentation audit — 2026-09-21

Source task: [Audit and update repository docs](codex://threads/01a0bf80-a83a-74e0-a3f5-25fdcc60a161).
The audit began with 398 tracked files under `docs/`: 276 evidence files, 83 round
files, 20 root files, 15 migration records, three trace-audit files and one operating
archive. Current interfaces were checked against package code and CLI help.

Implementation audited at `f5b2ced2d85e13e325bf535d444b574fedd9dd39` on
`codex/native-medical-workbench`. The tree was clean before this documentation work.
At inspection, main had BR-042 follow-ups `d16ebfd` / `76bd053` absent here, plus
seven dirty paths owned by other tasks. No branch integration is part of this audit.

## Findings and disposition

| Finding | Change |
| --- | --- |
| No current docs entry point; operational guidance mixed with dated results | Added a docs hub, repository map and dedicated historical/round/evidence indexes. |
| Failure-first sourcing and the closed assignment read as current purpose | Consolidated applicable lessons into medical research design; retired the obsolete requirements and nonmedical queue/review/method. |
| Case-32 handoff stood in for current submission policy | Rewrote the page around research drafts, promotion and separate ownership; retained the exact former handoff. |
| Replay, views, media setup and export instructions were scattered | Workflow owns author/run/collect/review; reproduction owns input recovery/replay/presentation; submission owns export/qualification. |
| Archive recovery called a removed launcher | Replaced it with Git inspection/extraction and explicit per-entry origin/hash verification. |
| First-pass closeout and review appeared to describe current defects | Added phased migration navigation and dated/superseded notices without rewriting the recorded findings. |
| Historical summaries link to removed sites, raw runs or old scripts | Indexed their current group owners and recovery context; retained source text, frozen outcomes and evidence bytes. |

The user explicitly requested **no shims**. Four obsolete guides and the redundant
`docs/archive.md` navigation page were removed outright. The former case-32
handoff page was rewritten as substantive export/ownership guidance. The five
guidance originals have exact Git origins, SHA-256 values and ignored local copies
in `archive/manifest.json`; current links point directly to maintained guides or
the historical index. No redirect page, alias, compatibility command or runtime
dependency was introduced.

The retained medical syntheses, ledger, cross-domain specification audit, round
protocols and evidence receipts remain source records at their original paths.
Direct-entry historical summaries now carry notices pointing to their current
groups and guides; the source text underneath is unchanged. The local-link scan
also identified 191 unresolved historical link occurrences, chiefly ignored runs
and retired sites/catalog/probes. These are recovery references, explicitly outside
the current-command documentation surface. Removing or rewriting their historical
links would hide provenance and can break evidence references; recover that context rather than treating them as runnable guides.

## Scope and verification

Validation passed:

- 126 current-guide/notice local links, including section anchors, resolve. Retained
  historical-body links were classified separately rather than silently rewritten.
- All 17 CLI subcommand help pages load. BR-040 preparation and diagnostic-run
  previews return without execution. Implementation inspection confirms the
  documented scaffold, collection, assessment, replay and export behavior.
- All five retired originals match their Git bytes and ignored copies. The Git
  recovery examples restore the requirements snapshot and all 29 archived site
  files with matching manifest hashes, without executing restored code.
- All 1,701 pre-existing probe/group/round/evidence files in the preservation scope
  are byte-identical. Eight historical summaries have only an added navigation
  notice; their original text underneath is unchanged. All seven pre-existing
  dirty files in the original checkout are unchanged.
- `make check PYTHON=python3.12` with the project environment active passes:
  1,826 staged/tracked files; 38 tests run with one optional imaging-runtime skip;
  562 records, seven groups, 38 experiments and 153 source-measurement checks;
  Ruff lint and formatting. The staged tree contains only this task's 34 paths.
- `git diff --cached --check` passes. No implementation code, frozen outcome or evidence
  receipt changed; this audit does not claim fresh scientific replay or model results.

No model trial, runtime installation, dataset download, scientific reassessment,
external requirements refresh or publication belongs to this change.

Reopen documentation maintenance when a supported command or ownership boundary
changes, when the original checkout completes cutover, or when new maintained
methods change reproduction coverage. New research belongs to a group rather than
another shared candidate queue.

## Follow-up: canonical research history

The user pointed out that indexing loose “Historical session closeout” pages did
not give them a canonical home. On 2026-09-21, this follow-up establishes
`groups/<group>/history/<scope>-<topic>.md` for dated research narratives. Each
group README links its history; the shared historical index is navigation only.
Repository implementation closeouts remain in `docs/migration/`. No redirect
pages or runtime path aliases are retained.

| Former path under `docs/` | Canonical path |
| --- | --- |
| `anatomy-experiments.md` | [groups/anatomy-audit/history/br013-br017-summary.md](../../groups/anatomy-audit/history/br013-br017-summary.md) |
| `anatomy-traces.md` | [groups/anatomy-audit/history/br013-br017-traces.md](../../groups/anatomy-audit/history/br013-br017-traces.md) |
| `research-cardiac-session.md` | [groups/cardiac-motion/history/br025-br035-closeout.md](../../groups/cardiac-motion/history/br025-br035-closeout.md) |
| `research-registration-session.md` | [groups/registration/history/br019-br028-synthesis.md](../../groups/registration/history/br019-br028-synthesis.md) |
| `research-landmark-session.md` | [groups/anatomical-landmarks/history/br036-br040-closeout.md](../../groups/anatomical-landmarks/history/br036-br040-closeout.md) |

The source tree before this follow-up is `3f4d79f8967f5ab3d7874a07eaaabed0a1c59071`.
Moved narrative bodies change only in relative Markdown link destinations. Current
indexes and dataset citations point directly to their new locations. Three dataset
source digests still cited pre-notice report versions after the first docs pass;
they now identify the moved navigation editions. Exact original report bytes and
their former hashes are retained at `f5b2ced` in the archive manifest, including
the registration publication's historical citation. No old receipt was rewritten.

Frozen/source records under `probes/`, `docs/evidence/` and `docs/research-rounds/`
remain byte-identical. Old paths inside those records describe their recorded Git
context and use explicit archive recovery; they are not compatibility interfaces.

Follow-up verification: all five old paths are absent; report text is unchanged
when only Markdown destinations are normalized; 180 links resolve or retain their
exact historical target. The 29 existing local/archive gaps in the reports were
not converted into new claims of availability. All five original Git/archive
snapshots and three current/original dataset citations match their hashes. All
1,029 protected source files and the original checkout's dirty files are unchanged.
`make check PYTHON=python3.12` passes with the project environment active: 38 tests
run, one optional imaging skip, 562 records and 153 source-measurement checks,
plus staged artifact policy and Ruff. The staged diff has no whitespace errors.
