# HiESD · classify annotated gastric tissue patches

Assign a histotype to each fixed target patch from one gastric ESD slide.

## Value

Patch labels can test recognition in regions where the source provides a class;
they do not establish whole-slide search or clinical margin assessment.

## Given

### Original data

One 39,887 × 28,702-pixel H&E SVS, `e4442edf…`, at 0.2458 µm/px.

### Supplied helpers

Twelve 256 × 256-pixel target crops and 1024 × 1024 context crops. A black and
white rectangle marks the target in each context. Fixed coordinates remove the
search step. The full slide and GT-free overview remain available.

### Callable tools

The packaged slide reader can inspect further native crops. No histotype model
or reference mask is supplied.

### Reference-only material

Six source XML classes and the chosen patch labels. The XML marks coarse,
sparse regions; blank tissue is not automatically normal.

## Task specification

Classify the central target in every named patch as chronic gastritis, complete
or incomplete intestinal metaplasia, lymphoid follicle, normal glands, or
well differentiated adenocarcinoma. Code 0 permits abstention. See the
[executable prompt](../../../../.local/wsi-agent-v2/hiesd/annotated-patches/task/instruction.md).

## Expected output

`labels.json`: `{"labels":[{"id":"patch_ID","class":1}, ...]}`. Every ID needs
one code from 0–6.

## Evaluation

Coverage, total correctness and per-class correctness on the 12 withheld labels.
The two patches per class are correlated selected locations from one slide.

## Visual explanation

### Workflow

- Fixed target and surrounding tissue → inspect morphology → one class per ID.

### Input

![GT-free target crop from the selected HiESD slide](../../../../.local/wsi-agent-v2/hiesd/annotated-patches/task/environment/data/patches/patch_01.png)

### Supplied helpers

![GT-free context crop with the target square outlined](../../../../.local/wsi-agent-v2/hiesd/annotated-patches/task/environment/data/patches/patch_01-context.jpg)

### Reference or output

**Reader-only reference example:** `patch_01 → class 5` (well differentiated
adenocarcinoma, tub1). The source XML label is withheld from the solver.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| Sol xhigh diagnostic | Fixed target/context crops, full slide | Six-class morphology judgment for each target |

## Difficulty

The fixed locations reduce navigation. Distinguishing metaplasia and gland
patterns remains a visual hypothesis to test, not a measured difficulty claim.

## Sources

- [HiESD source paper and annotation limits](https://pmc.ncbi.nlm.nih.gov/articles/PMC12311038/).
- [Sol diagnostic protocol](../../experiments/wsi-hiesd-patches-v2-sol6-xhigh/protocol.md).

## Coverage

One source slide, twelve GT-selected patches, six classes, one Sol condition.

## Gaps

No independent slide or pathologist re-review of the two rare-class patch pairs.
