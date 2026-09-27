---
schema: 2
id: tiger-context
title: From tissue context to an immune-cell density
locale: en
purpose: Explain tissue segmentation, merged immune-cell points, coordinate transforms
  and calibrated compartment densities in the proposed TIGER task.
scope: Three source-defined ROIs from one public JB training slide. Source-reference
  worked examples only. Retained pilots submitted points and compartment labels, not
  evaluated tissue contours or density summaries.
recipe: tiger-context-v1
asset_pack: retained-tiger-context-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/lesion-localization/presentation/briefs/wsi-tiger-context.md
- groups/lesion-localization/presentation/briefs/wsi-tiger-context.en.md
- groups/lesion-localization/presentation/sources/tiger-context-audit.json
- datasets/receipts/wsi-teaching-samples.json
- groups/lesion-localization/experiments/wsi-tiger-context-astra-medium/protocol.md
- groups/lesion-localization/experiments/wsi-tiger-context-v2-sol6-xhigh/protocol.md
- groups/lesion-localization/methods/wsi-agent-v2/score.py
- scripts/build_tiger_context_assets.py
---

# Tissue context determines the denominator

## Start with three supplied regions

```beat
id: inputs
scene: inputs
frames: 192
caption: Start with three supplied regions
narration: Three source-defined H and E regions come from one public training slide.
  Known locations remove whole-slide search. Each region uses local pixels with x
  right and y down. Source labels and cell counts remain hidden.
visual: Three actual source ROI images at correct aspect, labeled with both pilot
  and COCO IDs.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 0
```

## Separate the assistance conditions

```beat
id: conditions
scene: conditions
frames: 192
caption: Separate the assistance conditions
narration: The joint proposal asks for tissue regions and immune-cell locations. Supplying
  an integer tissue mask creates a separate assisted condition. Historical pilots
  returned point locations and compartment codes only; they did not evaluate tissue
  contours or density summaries.
visual: Compare explicit solver inputs and output scope without showing reference
  labels.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Reveal the compartment reference

```beat
id: tissue
scene: tissue
frames: 216
caption: Reveal the compartment reference
narration: Reveal the source tissue mask separately. Code six is inflamed tumor-associated
  stroma with high lymphocyte density. Code zero is unknown, so exclude it from density
  denominators. Codes three and five exist in the schema but are absent in these selected
  regions.
visual: Colored source mask on COCO 940 with matching code legend; unknown domain
  stays explicit.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 1
cut: intentional-cut
```

## A marker box is not a nuclear outline

```beat
id: cells
scene: cells
frames: 192
caption: A marker box is not a nuclear outline
narration: The source merges lymphocytes and plasma cells. Yellow dashed boxes mark
  source points using a fixed eight-by-eight-micrometre convention. Their area is
  not nuclear area. This dense teaching crop was selected with references and is not
  recorded agent navigation.
visual: Native source crop with source fixed-size cell boxes, shown only after reference
  reveal.
channels:
  view:
  - 0
  - 0
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Choose which center reads the tissue mask

```beat
id: assign
scene: assign
frames: 240
caption: Choose which center reads the tissue mask
narration: A constructed shift of two pixels right and three down crosses a source
  tissue boundary. The original center is in invasive tumor; the shifted center is
  in stroma. Revised pilots report both source-centered and submitted-centered labels.
  No historical score is rewritten.
visual: White source circle and black constructed shifted circle move over actual
  source pixels and mask.
channels:
  view:
  - 0
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Carry the ROI origin into the output

```beat
id: coordinates
scene: coordinates
frames: 216
caption: Carry the ROI origin into the output
narration: A teaching-crop point adds the crop origin to reach ROI coordinates. Add
  the ROI origin again to reach the full-slide level-zero frame. Label every row with
  its frame and region identity. A point from a different ROI cannot share the same
  origin.
visual: Highlight one actual source point and show ROI-local plus crop-origin arithmetic
  leading to slide coordinates.
channels:
  view:
  - 0
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Measure the annotated denominator

```beat
id: area
scene: area
frames: 216
caption: Measure the annotated denominator
narration: Code two covers three hundred twenty-four thousand one hundred forty-six
  pixels in this region. Square the physical pixel spacing and convert micrometres
  to millimetres to get zero point zero six seven six zero seven square millimetres.
  Unknown and zero-area domains cannot provide a density denominator.
visual: Actual compartment mask beside pixel area, squared spacing and physical area
  calculation.
channels:
  view:
  - 0
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Pool counts and areas together

```beat
id: density
scene: density
frames: 240
caption: Pool counts and areas together
narration: 'Code two has forty-five source cells and code six has one hundred twenty-nine.
  If the protocol combines them, divide their summed count by their summed area: about
  two thousand forty-nine cells per square millimetre. An average of the two densities
  would be wrong.'
visual: Reference cell points over source tissue plus separate and pooled count-area-density
  rows.
channels:
  view:
  - 0
  - 1
  reference:
  - 1
  - 1
cut: intentional-cut
```

## Join cells, regions and summary rows

```beat
id: output
scene: output
frames: 192
caption: Join cells, regions and summary rows
narration: The proposed output links a cell CSV, compartment geometry and a summary
  CSV. They must share the same coordinate and class policy. Source masks demonstrate
  the regional domain here; no submitted contour file or evaluated density result
  is being shown.
visual: Three proposed output files with fields and explicit coordinate-frame relation.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```

## Keep the untested contract visible

```beat
id: limits
scene: limits
frames: 216
caption: Keep the untested contract visible
narration: Retained pilots match points one to one within twenty pixels and report
  both compartment conventions. A joint tissue-and-density trial still needs its own
  frozen evaluator. These three selected training regions cannot establish full-slide
  counts, clinical stromal TIL area percentage or population performance.
visual: Retained point-only contract and remaining joint-task evaluation boundaries.
channels:
  view:
  - 0
  - 0
  reference:
  - 0
  - 0
cut: intentional-cut
```
