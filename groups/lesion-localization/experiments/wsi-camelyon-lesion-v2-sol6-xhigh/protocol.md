# CAMELYON lesion localization — Sol 6 xhigh

## Question and method

Can `openai/gpt-6-sol` at xhigh search a whole lymph-node slide for metastasis,
including a sparse positive and a negative, under a **lesion-group** endpoint?
The user accepted the revised endpoint and added cases on 2026-09-23. Run one
3600-second diagnostic attempt per case, sequentially, with no automatic retry,
4 CPUs, 12 GiB, no GPU and the pinned isolated transport route. Require an
oracle pass and no-op contract failure for each exact task. This new task is
not directly comparable to the [Astra polygon-hit diagnostic](../wsi-camelyon-search-astra-medium/protocol.md).

## Inputs and reference

The three cases are `tumor_091` (original teaching positive), `tumor_084`
(many small tumor polygons) and `normal_108` (negative). Their native TIFFs,
GT-free 64x overviews, physical scale and crop helper are solver-visible;
the XML is evaluator-only. The publisher's README identifies neither positive
slide as an annotation exception and lists normal slides as negative. The new
TIFFs match the publisher's MD5 manifest and have pinned SHA-256 receipts in
[the case receipt](../../../../datasets/receipts/wsi-agent-v2-camelyon-cases.json).

The study groups source Tumor polygons that touch after each side is dilated by
about 25 µm on a 16x downsampled raster. This is a prespecified **50 µm study
grouping**, not the official CAMELYON challenge FROC implementation. It produces
4 groups from 6 polygons on `tumor_091`, and 30 from 54 on `tumor_084`; the
negative has zero. A point inside a non-excluded polygon hits its group. The
scorer counts group recall, duplicate points and false-positive points on each
fully annotated slide. Confidence supports a later free-response curve across
the three cases. For the source challenge's separate official methodology, see
[CAMELYON16 evaluation](https://camelyon16.grand-challenge.org/Evaluation/).

## Findings and limits

Pending model attempts. Three selected public training slides are not a
population sensitivity or specificity estimate. Grouping nearby polygons
addresses the original equal-weight polygon mismatch but can still merge
biologically separate foci within its tolerance. Read-helper logs do not
enforce a search budget because direct TIFF reads remain possible. Keep the
case-level outputs and confidence thresholds visible before drawing conclusions.
