# Historical records

[Current documentation](../README.md) · [Git recovery guide](../../archive/README.md)

These are dated sources, not a second task queue. “Active”, “next”, commands and
status counts inside a retained document describe its capture date. Research
session closeouts and retrospectives have one canonical convention:
`groups/<group>/history/<scope>-<topic>.md`, with navigation from each group README.
New medical work and current assessments live with the semantic groups. Original
protocols, freeze receipts and outcomes remain at their recorded paths.

## Group research history

| Retained source | Current owner and presentation |
| --- | --- |
| [Anatomy experiments](../../groups/anatomy-audit/history/br013-br017-summary.md), [trace walkthroughs](../../groups/anatomy-audit/history/br013-br017-traces.md) | [Anatomy audit](../../groups/anatomy-audit/README.md) |
| [Registration session](../../groups/registration/history/br019-br028-synthesis.md) | [Registration](../../groups/registration/README.md) |
| [Cardiac session](../../groups/cardiac-motion/history/br025-br035-closeout.md) | [Cardiac motion](../../groups/cardiac-motion/README.md) |
| [Landmark session](../../groups/anatomical-landmarks/history/br036-br040-closeout.md) | [Anatomical landmarks](../../groups/anatomical-landmarks/README.md) |
| [Round register](../research-rounds.md) and [round files](../research-rounds/README.md) | All groups; BR numbers are historical provenance, not unique experiment IDs |
| [Evidence receipts](../evidence/README.md) | The experiment citing each receipt |

The old `site/` and `site_med/` links in these retained sources refer to retired
presentations. Build the current index with `uv run med present --serve`; use
[reproduction](../reproduce.md) for native views and tours. Old `runs/` links require
local artifacts. Do not regenerate evidence to make an old link work.

## Earlier investigation and cross-domain lessons

The ledger, mixed-domain brainstorm, specification audit, operating notes and
2026-09-17 trace-audit viewer are retired. Their exact files and the completed
migration records are indexed in the [recovery manifest](../../archive/manifest.json);
see [documentation pruning](../../archive/README.md#documentation-pruning--2026-09-22).
Applicable current lessons live in [research design](../research-design.md).

- [Medical-agent repository survey](../../presentation/external-tasks/sources/repository-survey-2026-09-20.md): dated source research accompanying the maintained external-task collection.
- [Retired report figure provenance](../../archive/report-figure.json): original figure hashes, attribution and licensing; raw images remain local.
- [Migration decisions](../migration/README.md): retained design choices and interface recovery locators.

## Reproduction baseline

The [2026-09-21 backfill receipt](../evidence/experiment-support-backfill-20260921.json)
retains the checked scope, hashes, controls and replay counts for the dated
38-experiment inventory and eleven selected core records. Current operations
belong in the [reproduction guide](../reproduce.md) and group method indexes;
separate copies of the baseline tables are no longer maintained.

## Retired guidance and recovery

Obsolete guides have been removed from the active tree without redirect pages.
Their original bytes are indexed by path, commit and SHA-256 in
[archive/manifest.json](../../archive/manifest.json):

| Original path | Disposition |
| --- | --- |
| `docs/requirements.md` | Closed assignment profile from 2026-09-12; current promotion guidance is [exports and submission](../submission.md). |
| `docs/submission.md` at `f5b2ced` | Superseded case-32 handoff; the current page describes research exports and ownership. |
| `docs/geometry-review.md` | Completed nonmedical Clipper/PolyTree review. |
| `docs/research-next-candidates.md` | Closed GoAWK/Zstandard candidate queue. |
| `docs/research-sourcing-methodology.md` | Old 100-card source-screening method; applicable lessons now live in [research design](../research-design.md). |

These five originals use source commit
`f5b2ced2d85e13e325bf535d444b574fedd9dd39`. The manifest also retains original
versions of the five medical history reports listed above at that commit, so
old receipt paths and hashes remain recoverable after the move. Current source
indexes cite the group-owned navigation editions. The redundant `docs/archive.md`
navigation page was removed; this directory owns historical navigation.

The same manifest indexes the old catalog, original assignment, interview
publication and retired nonmedical families. Historical links to removed files
remain provenance; look up their repository-relative path in that manifest.
Neither retaining nor restoring a source authorizes resuming archived research.
