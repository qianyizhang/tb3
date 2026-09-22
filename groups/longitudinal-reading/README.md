# Longitudinal reading

Can agents compare examinations with reproducible measurements and source-grounded interpretations?

Mechanical contract success is not a clinical pass. Sequence selection, measurement definition and reference units must be stated.

Use `uv run med list --group longitudinal-reading` from the repository root. The group owns the current research entry point; original protocols and frozen evidence remain at their recorded paths.

[Capability story](presentation/story.md) · [Working contract](AGENTS.md)

[Data sources](sources.json) · [Retained examples](examples/README.md) · [Methods](methods/README.md)

[Longitudinal-CT data/GT review](examples/longitudinal-ct-review-20260922.md) ·
[Proposed lesion-correspondence task](presentation/briefs/longitudinal-ct-correspondence.md)

[Image-only Astra-medium / Sol-xhigh pilot](findings/longitudinal-ct-image-only-comparison.md):
separate detection, segmentation and correspondence scores with native image
review; exact merging interpretation remains under review.

[Trace methodology and failure attribution](findings/longitudinal-ct-trace-attribution.md):
separates lesion acceptance, instance partitioning, boundary construction and
upstream effects on links/events using saved actions and quantitative diagnostics.

[Revised Astra medium and localized recognition](findings/longitudinal-ct-v2-and-localized.md):
strict localization improves from 2/6 to 3/6, but exact center cues do not rescue
the remaining separate focus; both indicated structures are explicitly rejected
as normal/benign. Recognition relative to GT and clinical adjudication are distinct.

[Second case selection](examples/longitudinal-ct-case02-selection.md): source documentation,
300-patient metadata screen, and a new liver-dominant pair with persistence and
new lesions; the revised image-only contract is retained.

[Second-case Astra result](findings/longitudinal-ct-case02-astra-medium.md):
3/22 instances and 2/15 exact events despite foreground Dice 0.799/0.891;
one reported vessel exclusion falls inside a missed new reference lesion.

[Clinical-context study](findings/longitudinal-ct-context-hypothesis.md): supplying
verified broad context recovers the same three instances; explicit recognition
disagreement and incomplete rendered coverage remain distinct explanations.

[Comprehensive curation](findings/longitudinal-ct-curation-comparison.md): an explicit
all-size inventory goal and permissive candidate policy retain additional
uncertainty, but recovery stays 3/22. One target is gained and another rejected
as vascular; exact events fall to 1/15 because the gained target is unresolved.
