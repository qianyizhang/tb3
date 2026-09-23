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

All three Sol cases completed. [`tumor_091`](attempts/attempt-8d453145984a45c3.json)
and [`tumor_084`](attempts/attempt-9acd94eaa875417b.json) each produced a
valid empty answer, hitting 0/4 and 0/30 study-defined lesion groups.
[`normal_108`](attempts/attempt-927a18c8c21e4ec5.json) also produced an
empty answer, appropriate for its zero-lesion reference. On the positives,
the agent reviewed suspicious regions but judged them non-metastatic; explicit
native helper crops contained 2/4 and 11/30 oracle group points, respectively.
Direct pyramid reads prevent equating those counts with complete visual access.
Post-hoc source-centered crops did not show an obvious coordinate/GT defect,
but need specialist adjudication for pathology claims. Three selected public
training slides are not a population sensitivity or specificity estimate.
Grouping nearby polygons can still merge biologically separate foci. See the
[seven-condition synthesis](../../findings/wsi-sol6-xhigh-v2-diagnostic-synthesis.md).
