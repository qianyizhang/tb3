# Anatomy audit

How do agents recognize anatomical identity, omissions and tissue assigned to the wrong label?

Supplied-mask auditing differs from segmentation from scratch. Inventory and image context can change an outcome; broad and focused audits are separate conditions.

Use `uv run med list --group anatomy-audit` from the repository root. The group owns the current research entry point; original protocols and frozen evidence remain at their recorded paths.

[Capability story](presentation/story.md) · [Working contract](AGENTS.md)

[Data sources](sources.json) · [Retained examples](examples/README.md) · [Methods](methods/README.md)

[CT-only organ segmentation comparison](findings/ct-organ-three-condition-comparison.md):
three fresh model/effort conditions, per-organ results, trace methodology and
matched-plane visuals. This is distinct from supplied-mask identity auditing.

## Research history

Dated session conclusions and trace accounts live in `history/`. They retain
their original findings and limits; current assessments belong to the experiment
and group findings, and current presentation belongs to the capability story.

- [BR-013–017 retrospective](history/br013-br017-summary.md)
- [Trace walkthroughs](history/br013-br017-traces.md)
