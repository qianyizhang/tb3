---
schema: 2
id: mixed-tissue-audit
title: Find foreign tissue inside a named mask
locale: en
purpose: Explain inspecting supplied named masks against CT, then reporting the host,
  included class and one physical witness.
scope: Retained BR-017 M02 CT and masks, three oracle-centred teaching crops from
  s1233. Injected-region reference and oracle witness are private task material, explicitly
  revealed to the reader. This is neither a blind search nor clinical contour adjudication.
recipe: mixed-tissue-v1
asset_pack: retained-mixed-tissue-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/anatomy-audit/presentation/briefs/tb3-mixed-tissue-audit.md
- docs/research-rounds/BR-017-absorbed-anatomy.md
- docs/evidence/br017-audit.json
- docs/evidence/br017-abdomen-m02-freeze.json
- docs/evidence/br017-abdomen-f01-freeze.json
- presentation/task-explorer/mixed-tissue/manifest.json
- scripts/build_mixed_tissue_assets.py
---

# Mixed tissue audit

## input

```beat
id: input
frames: 120
caption: CT is supplied; the proposed labels still need an audit.
narration: The real broad task supplies native CT, thirteen named masks and inspection
  tools. These three teaching crops were selected using the private reference point;
  they do not demonstrate independently finding the affected location.
visual: Show native axial CT without overlays, with the reference-centred teaching
  boundary visible.
channels:
  plane:
  - 0
  - 0
  overlay:
  - 0
  - 0
  reference:
  - 0
  - 0
  witness:
  - 0
  - 0
  conditions:
  - 0
  - 0
```

## masks

```beat
id: masks
frames: 144
caption: A named mask can contain tissue from another organ.
narration: Overlay the supplied duodenum object o327 in teal and the remaining pancreas
  o589 in blue. Names are proposed labels, not proof of pure contents. In M02 both
  names remain present, so counting missing labels cannot identify the inclusion.
visual: Fade in only the two solver-visible supplied mask outlines.
channels:
  plane:
  - 0
  - 0
  overlay:
  - 0
  - 1
  reference:
  - 0
  - 0
  witness:
  - 0
  - 0
  conditions:
  - 0
  - 0
```

## inspect

```beat
id: inspect
frames: 192
caption: Cross-check CT and mask contents in three physical planes.
narration: The axial, coronal and sagittal views retain the same physical LPS coordinate
  system, with positive axes left, posterior and superior. The task requires substantial
  foreign tissue, at least five millilitres. Ordinary thin contour differences and
  native overlaps are outside scope.
visual: Switch among three equal-scale native planes while the reference region and
  witness remain hidden.
channels:
  plane:
  - 0
  - 1
  overlay:
  - 1
  - 1
  reference:
  - 0
  - 0
  witness:
  - 0
  - 0
  conditions:
  - 0
  - 0
```

## reference-reveal

```beat
id: reference-reveal
frames: 168
caption: 'Reader reveal: 21.04 mL of source pancreas was reassigned.'
narration: Gold shows the exact injected-region lineage, taken from the private evaluator.
  It sits inside the supplied duodenum host while 38.38 millilitres of pancreas remains
  separately labeled. The CT is unchanged. This synthetic edit is not a documented
  clinical annotation error.
visual: Reveal the gold region over the supplied masks, clearly marked author-only
  reference.
channels:
  plane:
  - 1
  - 1
  overlay:
  - 1
  - 1
  reference:
  - 0
  - 1
  witness:
  - 0
  - 0
  conditions:
  - 0
  - 0
```

## witness

```beat
id: witness
frames: 144
caption: Report the host ID, included class and one LPS point.
narration: The white ring is the private oracle point, not an agent prediction. Report
  o327 as host and pancreas as included class. Localization accepts a point within
  three millimetres of an injected voxel centre. No contour reconstruction, exact
  volume estimate or disease diagnosis is required.
visual: Show the same reference witness across all three planes and display its physical
  coordinate.
channels:
  plane:
  - 1
  - 0
  overlay:
  - 1
  - 1
  reference:
  - 1
  - 1
  witness:
  - 0
  - 1
  conditions:
  - 0
  - 0
```

## conditions

```beat
id: conditions
cut: intentional-cut
frames: 192
caption: Whole, partial, unchanged and focused audits are distinct.
narration: M01 absorbs the whole pancreas and removes its label. M02 preserves every
  class name. N01 keeps the source masks unchanged and expects no findings. F01 uses
  the same M02 data but restricts the audit to the pair. These are different conditions,
  not pooled evidence or new trials.
visual: Hold the axial reference view and witness beside the four-condition contrast.
channels:
  plane:
  - 0
  - 0
  overlay:
  - 1
  - 1
  reference:
  - 1
  - 1
  witness:
  - 1
  - 1
  conditions:
  - 1
  - 1
```
