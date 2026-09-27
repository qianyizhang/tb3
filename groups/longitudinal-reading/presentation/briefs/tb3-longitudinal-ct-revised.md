# Track CT lesions — Revised inclusion and instance contract

Find tumor instances across two full native CT volumes, make uncertain inclusion decisions explicit, and link complete events. Three retained Astra medium attempts test revised generic wording on two selected pairs, with broad clinical context added to the second pair in one condition.

## Value

Separates **discovery, inclusion, instance partition, contour quality and temporal association**. Useful foreground masks can coexist with many missed instances; perfect conditional event scores can cover only a small eligible subset.

## Given

### Original data

Full native baseline and follow-up CT volumes, named neutrally. The first pair has 261/274 slices at 3 mm spacing; the second has 615/743 slices at 2.0/2.5 mm spacing. Preserve each volume's own grid and affine. Visits are not registered by this explanation.

### Supplied helpers

- **Inclusion:** include findings judged more likely tumor than normal/benign, even without diagnostic certainty. Exclude findings judged more likely normal/benign; uncertainty alone is not an exclusion rule.
- **Partition:** distinguishable touching lesions receive separate local IDs. Voxel connectivity alone does not establish one confluent instance.
- **Uncertainty:** record native location, included/excluded decision and short reason in the report.
- **Context condition only:** released age 44, recorded sex female, 121-day interval; cohort background of metastatic melanoma, systemic therapy and staging/therapy-response assessment. The age field's reference date is unspecified. No individual clinical report, regimen, surgery dates or target hints are supplied. Cohort information is not an individual history. Separate context-inference output was never passed in.

### Callable tools

The frozen image provides CPU Python image/numerical tools and shell access. No pretrained medical weights or external dataset lookup are supplied. The three linked protocols retain the exact environment and restrictions; each attempt uses `openai/gpt-6-astra`, medium effort and a two-hour bound.

### Reference-only material

Source instance maps, lesion tables, correspondence/event groups, source patient identity and private scorer are evaluator material. No lesion locations, counts, anatomic hints, masks, links or previous outputs are given to the solver. The reader story separately reveals actual saved outputs and source references. Its selected crops remove search and are not solver inputs.

## Task specification

Search both complete volumes. Produce distinct native tumor instances, infer correspondence and type events as persistent, merging, newly appearing, disappearing or unresolved. Persistent means identity continuity, not stable size. Check coverage before interpreting absence. Every positive local mask ID belongs to exactly one group; unresolved groups assert no links.

## Expected output

- `baseline_instances.nii.gz` and `followup_instances.nii.gz`: exact native shape and affine; integer background 0 and local IDs 1–65535, at most 4096 per visit.
- `events.json`: schema 1; complete local-ID membership and event cardinalities. Persistent is 1→1, merging ≥2→1, new 0→1 and disappearing 1→0.
- `report.md`: method, uncertainty, native candidate coordinates, inclusion decisions/reasons and representative filename plus zero-based native-slice evidence. Retain useful scripts/views under the work directory.

There is **no probability sidecar** in this revision. Empty masks with an empty event list may satisfy the mechanical contract; this does not establish scientific success. The later comprehensive-candidate task is separate.

## Evaluation

The same original private scorer is retained in all three freezes. Detection uses one-to-one assignment from predicted centroids to reference masks with the frozen 3 mm tolerance. Foreground Dice ignores instance partitions; GT-macro instance Dice retains missed references as zeros. Report links and exact typed events end to end, alongside conditional scores and eligible/total reference denominators.

| Retained condition | Localized visit instances | Foreground Dice baseline / follow-up | GT-macro Dice | Correct links / events |
| --- | --- | --- | --- | --- |
| First pair, revised image only | 3/6 | 0.685 / 0.764 | 0.335 | 2/4 · 0/2 |
| Second pair, revised image only | 3/22 | 0.799 / 0.891 | 0.107 | 1/7 · 2/15 |
| Second pair, broad context supplied | 3/22 | 0.740 / 0.876 | 0.110 | 1/7 · 2/15 |

Fresh saved-output replay reproduces every original parsed score field. This is verifier replay, not new inference. All three have zero **instance** false positives, which does not imply no excess segmented tissue.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| First pair revised | Full CT pair and revised generic instructions | Discover targets, partition touching instances and infer events |
| Second pair revised | Different selected full CT pair, identical revised prompt | Discover all targets; infer persistent and new events |
| Second pair with context | Same second-pair images plus the verified broad context block | Use priors without supplied locations or instance identities |

Only `instruction.md` changes from original to revised first-pair freeze and from second-pair image-only to supplied-context freeze. The first-pair original Astra comparator localized 2/6 instances and 1/4 links, with 0/2 exact events. The revised output has two baseline IDs, but still misses the separate B3/F3 focus and the complete merger. Fine-instance/confluence review remains open; two wording changes plus one fresh attempt do not isolate a prompt effect.

## Difficulty

The second pair has seven baseline and fifteen follow-up reference instances: seven persistent and eight new groups. It has no merging or disappearing reference event and no touching distinct labels under six-connectivity. One identity contributes **84.6%/94.9%** of baseline/follow-up reference tumor volume. Both conditions localize **0/11** instances ≤1 mL, **1/9** above 1 through 10 mL and **2/2** above 10 mL. The two large annotations are one lesion at two visits.

Both second-pair conditions recover exactly B4, F4 and F13. Conditional link **1/1** and event **2/2** correctness have eligibility only **1/7** and **2/15**. Saved contours differ, without a gained detected identity. Both reports accept F13 despite a benign alternative. The context report also explicitly excludes points (190,199,406) and (182,165,524), favoring a benign cyst-like/vascular explanation; both lie inside source GT2 and have zero context-mask coverage. This establishes a report-reference disagreement, not clinical adjudication.

## Coverage

Two purposively selected public-source pairs and one attempt per condition support a diagnostic comparison, not population accuracy, a model ranking or causal context benefit. Changing the patient changes the case. Broad context is not the clinical reports available to source annotators. Prompt delivery is verified; its effect on reasoning is not. Public-source training exposure cannot be ruled out. Localized recognition, context inference and comprehensive curation remain separate catalogue entries.

## Sources

- [Revised image-only protocol](../../experiments/longitudinal-ct-v2-astra-medium/protocol.md) and [retained finding](../../findings/longitudinal-ct-v2-and-localized.md).
- [Second-case protocol](../../experiments/longitudinal-ct-case02-astra-medium/protocol.md), [selection account](../../examples/longitudinal-ct-case02-selection.md) and [retained result](../../findings/longitudinal-ct-case02-astra-medium.md).
- [Supplied-context protocol](../../experiments/longitudinal-ct-context-supplied-astra-medium/protocol.md), [actual context block](../../methods/longitudinal-ct-context-v1/context-block.md) and [context comparison](../../findings/longitudinal-ct-context-hypothesis.md).
- [Source and replay audit](../sources/longitudinal-ct-revised-audit.json), [canonical story](../stories/longitudinal-ct-revised.story.md) and [asset attribution](../../../../presentation/task-explorer/longitudinal-ct-revised/NOTICE.md).
- [Longitudinal-CT source release](https://fdat.uni-tuebingen.de/records/qe950-g4h94), CC BY-NC 4.0. Native source labels, one-voxel satellite and original scores remain unchanged.
