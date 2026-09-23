# HiESD annotated patch classification — Sol 6 xhigh

## Question and method

Can `openai/gpt-6-sol` at xhigh classify tissue histotype in annotated gastric
ESD regions when the output matches the source annotation granularity? The user
selected patch labels on 2026-09-23. Run one 3600-second diagnostic attempt,
no automatic retry, with 4 CPUs, 12 GiB, no GPU and the pinned isolated
transport route. Require exact-task oracle pass and no-op contract failure.
This is a new task type, separate from the [Astra coarse-map diagnostic](../wsi-hiesd-map-astra-medium/protocol.md).

## Inputs and reference

The solver receives 12 fixed 256×256 level-0 target patches from source slide
`e4442edf-05b0-431b-bf61-ccf2d8cdebb6`, each with a 1024×1024 context crop,
plus the complete slide and GT-free overview for optional wider reading. The
center patches were selected by eroding each of the six source XML-derived
class regions on the 64x grid by two grid cells, requiring at least 80% tissue
in the GT-free thumbnail neighborhood, then taking a deterministic farthest
pair per class. IDs are shuffled without class cues. Labels and the
selection mask remain evaluator-only. The output is one class 0–6 per patch;
0 is an explicit abstention. Scoring reports coverage, total correctness and
per-class correctness. Only annotated target regions enter the denominator.

## Findings and limits

The completed [Sol attempt](attempts/attempt-d1bd0aecea104412.json) labeled
12/12 patches and got 8 correct (66.7%). Classes 3 and 4 were 2/2; classes
1, 2, 5 and 6 were 1/2. The four errors include one tub1-to-incomplete-
metaplasia confusion and the reverse. These 12 patches from one slide are
correlated: rare classes may contribute two locations from one source region.
Their GT-selected locations remove autonomous WSI search, and the XML regions
do not establish precise gland boundaries, invasion depth, margins or labels
for unannotated tissue. The [HiESD source paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC12311038/)
recommends patch classification over exact boundary segmentation. See the
[seven-condition synthesis](../../findings/wsi-sol6-xhigh-v2-diagnostic-synthesis.md).
