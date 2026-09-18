# Medical showcase: editorial evidence workspace

Status: six content chapters and six guided tours complete; index synthesis and legacy HTML refresh deferred.
User direction, 2026-09-18: focus on content, structure and flow; additional
research, evidence and drawings may be collected or rebuilt locally. The eventual
publication destination is the user's Astro blog. No migration is performed here.

## Content package

- Keep narrative in portable Markdown, structured measurements in JSON, and
  illustrations in separate files with captions and source records.
- Use stable chapter/figure IDs and relative package paths. Resolve links to
  original experiment evidence separately from links between article pages.
- Preserve editable diagram sources and plotting/rendering commands alongside
  exported figures. Label conceptual drawings as illustrations, not scan evidence.
- For every figure, retain source, attribution, applicable terms, derivation,
  caption, alternative text, and whether it was shown to the model or produced
  afterward for readers. Carry existing source restrictions through migration.
- Keep interactive data independent of the current HTML shell. Each interaction
  needs a useful static figure and caption. Astro components can be chosen later.
- Inventory existing local material before copying it. Native scans, raw sessions,
  meshes and restricted source archives are not automatically blog assets.

`evidence-map.json` inventories existing local sources with current hashes. It is
an editorial retrieval index, not a replacement for frozen trial manifests or a
claim that each source or asset has been independently validated.

## Corrections that the rewrite must carry

| Chapter | Source-backed correction |
| --- | --- |
| Overview | The removed legacy overview mislabeled the recorded model IDs as Claude/GPT-4o. The wider round register is not 40 controlled medical trials. Rebuild resources from measured receipts. |
| Segmentation | Audit supplied masks; do not describe segmentation from scratch. Score an interior point near included tissue, not an exact centroid. Broad inspection already included targeted views of the affected pair. |
| Aneurysm | N01/N02 derive from sub-013/sub-022; N03 matches sub-000. Reference regions are weak localization annotations. N03 is an allowed source-assisted answer. |
| Registration | Use Learn2Reg LungCT provenance. Retain frozen numerical failure separately from later user visual acceptance. Do not invent a radiologist panel. Recompute tables from receipts. |
| Vessels | BR-030 uses an unchanged natural model-prediction gap. The distance-axis error belongs to the submitted output, not the verifier. BR-033's airway agent is Terra. |
| Cardiac | Keep synthetic material truth, supplied segmentation, raw-image reconstruction and clinical cavity transfer separate. BR-032 has no reference clinical EF. The cylinder example proves ambiguity; it does not establish the exact cause of an agent's error. |
| Landmarks | Preserve all-visible-target denominators. Model and reasoning setting both differ in the comparison. Atlas use is observed assistance, not an isolated causal explanation for the score difference. |

## Comparisons to recover before adding literature scores

- Registration: retained 2D author method, 2.133 mm RMS / 3.416 mm maximum;
  both author and agent methods have information and development-history caveats.
- Coronary geometry: image-guided and geometry-only author methods both pass;
  image guidance improves local overlap and reduces edits on this fixture.
- Airway routing: image-guided author baseline and Terra pass; tested geometric
  shortcuts fail. Detached-fragment controls do not establish whole-tree repair.
- Cardiac: oracle/static controls and masks-only/masks-plus-ultrasound conditions;
  primary construction checks are separate from material-motion diagnostics.
- Segmentation: unchanged, whole-absorption and focused-scope conditions are
  contrasts, not measured human-performance baselines.
- Aneurysm and landmarks: no human score should be manufactured from the fact
  that a source contains human annotations.

Published scores, if added, must retain cohort, input, output, metric, test split
and assistance context. Do not rank unlike published tasks against these pilots.

## Reproduction levels

1. Read the article and inspect portable figures.
2. Recompute reported scores from retained outputs, where available.
3. Rebuild visualizations from original inputs and recorded scripts.
4. Run a new model attempt under the frozen protocol; this is not guaranteed to
   reproduce an identical response and is not authorized by editorial collection.

State local-only dependencies explicitly. A link that works in this workspace is
not sufficient for a reader of the future blog. The initial audit found 110 machine-local links in the old Markdown. The current
articles use relative package/evidence links; runtime-only targets are documented
as local dependencies rather than promised as clean-checkout assets.

## Confirmed editorial decisions — 2026-09-18

- Lead with agent capability. Develop the index's current-state synthesis,
  remaining problems and future outlook together with the user next.
- Serve readers with technical or clinical backgrounds; explain the other
  domain's essential terms in the main narrative.
- Keep literature search light and comparisons proportionate.
- Use an anchor experiment per domain and supporting contrasts where useful.
- Target a 3–5 minute main read; link deeper methods, traces and reproduction.
- Keep material local and portable for eventual Astro migration. Do not change
  legacy HTML/CSS or migrate to the blog during the content pass. The subsequent
  user-authorized media work adds a separate local tour player.

## This content version

The Markdown chapters and source-linked task cards are authoritative for this
editorial version. The two old hardcoded content generators are retired. The
unchanged legacy HTML builder is not validated by the content checks. The root
README is now a directory guide; the former inaccurate overview survives only in
Git history. Cross-task synthesis remains deferred.

Static figures are exact exports of retained scientific images. Mermaid blocks
are new conceptual explanations and remain editable in the chapters. Each asset
has a manifest record, caption and provenance. Five guided tours now share a
renderer and export tool, with English/Chinese copy, configurable pacing and music,
and landscape/portrait output. Existing full viewers are preserved. Generated
geometry, compressed assets, movies and verification receipts stay local and are
ignored by Git; the player, storyboards, locales, presets and tools are tracked.

A source discrepancy is retained rather than rewritten into historical evidence:
BR-030 prose gives 484.14 agent seconds, while its ledger and raw execution
interval give 464.141901 seconds. The new chapter uses rounded full-job time.

The [original brief](brief.md) is retained for context; the confirmed decisions
and current package guides describe the completed scope.
