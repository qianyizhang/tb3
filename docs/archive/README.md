# Historical records

[Current documentation](../README.md) · [Git recovery guide](../../archive/README.md)

These are dated sources, not a second task queue. “Active”, “next”, commands and
status counts inside a retained document describe its capture date. New medical
work and current assessments live with the semantic groups. Original protocols,
freeze receipts and outcomes remain at their recorded paths.

## Medical syntheses and traces

| Retained source | Current owner and presentation |
| --- | --- |
| [Anatomy experiments](../anatomy-experiments.md), [trace walkthroughs](../anatomy-traces.md) | [Anatomy audit](../../groups/anatomy-audit/README.md) |
| [Registration session](../research-registration-session.md) | [Registration](../../groups/registration/README.md) |
| [Cardiac session](../research-cardiac-session.md) | [Cardiac motion](../../groups/cardiac-motion/README.md) |
| [Landmark session](../research-landmark-session.md) | [Anatomical landmarks](../../groups/anatomical-landmarks/README.md) |
| [Round register](../research-rounds.md) and [round files](../research-rounds/README.md) | All groups; BR numbers are historical provenance, not unique experiment IDs |
| [Evidence receipts](../evidence/README.md) | The experiment citing each receipt |

The old `site/` and `site_med/` links in these retained sources refer to retired
presentations. Build the current index with `uv run med present --serve`; use
[reproduction](../reproduce.md) for native views and tours. Old `runs/` links require
local artifacts. Do not regenerate evidence to make an old link work.

## Earlier investigation and cross-domain lessons

- [Ledger](../ledger.md): dated observations and denominators from the closed investigation.
- [Brainstorm experiments](../research-brainstorm-experiments-20260914.md): mixed-domain pilot history, including medical source context.
- [Specification/scaffolding audit](../research-specification-audit-20260915.md): retained evidence for task-design lessons, now summarized in [research design](../research-design.md).
- [Operating records](operations.md): old setup/geometry pickup and the former round template. Use `med new` for current authoring.
- [Trace audit](../audit/agy-0917.md) and [local audit viewer](../audit/index.html): retained analysis, not general current status.
- [Migration history](../migration/README.md): the pivot decisions, phased closeouts, inventories and verification receipts.

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
`f5b2ced2d85e13e325bf535d444b574fedd9dd39`. The redundant `docs/archive.md`
navigation page was removed; this directory owns historical navigation.

The same manifest indexes the old catalog, original assignment, interview
publication and retired nonmedical families. Historical links to removed files
remain provenance; look up their repository-relative path in that manifest.
Neither retaining nor restoring a source authorizes resuming archived research.
