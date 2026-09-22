# Comprehensive curation: broader inclusion, unchanged 3/22 recovery

The fresh Astra-medium attempt followed the broader inclusion policy for an uncertain finding, but did not improve total reference-lesion recovery. It gained one previously missed lesion and lost another. This is a behavioral change, not evidence that mission framing alone fixes the task.

## Task and comparison

The [exact instructions](../methods/longitudinal-ct-curation-v1/instruction.md) set the goal of a **comprehensive longitudinal tumor-candidate inventory for oncologic review and subsequent assessment of disease burden and lesion evolution**. They explicitly require every plausible candidate regardless of size, no RECIST-target restriction, benign-favored candidates when tumor remains plausible, a second review for omissions, separate distinguishable touching instances, and correspondence for all retained candidates. A sidecar records subjective tumor probability separately from inclusion.

The CTs, verified clinical-context paragraph, Astra-medium model/effort, tools, runtime image, resource/time ceilings, private GT and scientific scorer match the previous context-supplied condition. No source identity, organ distribution, lesion count, localization, GT event or previous output was supplied. A new private wrapper checks the extra sidecar and the predeclared probability subset.

Comparability is **endpoint_only**: shared scientific endpoints are unchanged, but goal, inclusion policy, review wording and uncertainty format changed together. One run cannot separate wording effects from stochastic variation. The [paper's annotation protocol](https://www.nature.com/articles/s41597-026-07466-y) includes all lesions deemed malignant without a minimum size, separately from RECIST target selection. Our plausible-candidate inventory is deliberately wider. The [release](https://fdat.uni-tuebingen.de/records/qe950-g4h94) also describes use of clinical reports, which remain unavailable for this patient.

## Frozen measurements

| Endpoint | Image only | Context supplied | Comprehensive curation |
|---|---:|---:|---:|
| Strict GT instances localized | 3/22 | 3/22 | **3/22** |
| Unmatched predicted instances | 0 | 0 | **2** |
| GT instances <=1 mL recovered | 0/11 | 0/11 | **0/11** |
| Equal-GT-instance Dice | 0.1073 | 0.1104 | **0.1055** |
| Foreground Dice, baseline / follow-up | 0.799 / 0.891 | 0.740 / 0.876 | **0.629 / 0.870** |
| Correct end-to-end links | 1/7 | 1/7 | **1/7** |
| Exact end-to-end event groups | 2/15 | 2/15 | **1/15** |
| Agent execution time | 17m02s | 12m27s | **21m11s** |

Strict localization uses one-to-one assignment with a prediction centroid inside GT or within 3 mm of a labeled voxel center. Mask Dice uses a separate optimal one-to-one overlap assignment; foreground Dice weights large lesions heavily. The 22 visit-level instances belong to one patient. New size-stratum recoveries are 0/11 at <=1 mL, 1/9 at >1–10 mL, and 2/2 above 10 mL. All <=1 mL GT regions have zero predicted foreground coverage.

The five retained candidates comprise three strict matches and two unmatched instances. The unmatched pair is a thigh plaque at both visits, explicitly benign-favored at `p_tumor=0.2`; it is retained as intended. The predeclared `p_tumor >= 0.5` subset removes those two candidates and yields 3 TP / 0 unmatched / 19 FN, still 3/22 recall. Unmatched does not mean clinically adjudicated false tumor; these probabilities are not calibrated.

All-candidate association has one correct and one unmatched link. The single eligible link between detected GT endpoints is correct. Among two eligible GT event groups, one is exact and one is unresolved. This is a permitted abstention, not a schema error, but does not match the definite reference `newly_appearing` event. Exact-event agreement does not judge whether clinical abstention was justified.

## Native result and reference inspection

![Native CT, GT and saved predictions](../../../.local/longitudinal-ct-curation-v1/analysis/curation-comparison.png)

Author-selected axial crops: cyan solid = GT, purple solid = previous context run, orange solid = new curation run. Native zero-based k, i right / j down; HU [0,150], 55 mm crops, no CT resampling before plotting. GT2 appears at both visits, followed by gained GT14 and lost GT13. These views were selected after execution and never reached a solver. [Figure sources, crops and hashes](../../../.local/longitudinal-ct-curation-v1/analysis/curation-comparison.json). Longitudinal-CT v3, FDAT, CC BY-NC 4.0. The rendered figure was visually inspected.

**Recovery changed identity, not count.** Large GT4 remains recovered at both visits. Follow-up GT14 is now separate, with Dice 0.6714 and tumor probability 0.7. Its event is unresolved because the agent cannot confidently exclude baseline visibility. Follow-up GT13, recovered previously, now has zero predicted coverage. GT2 remains absent at both visits; this run does not explicitly revisit the previous report's GT2 rejection.

**One omission is an explicit recognition disagreement.** The report excludes a vascular-appearing hepatic cross-section at follow-up native (125,208,528). That exact point lies inside GT13. The public report supplies the interpretation and the reference supplies the disagreement; this is stronger evidence than inferring recognition from a missing mask. It is not independent clinical adjudication. Other explicitly reported exclusion points lie outside GT and must not be used to explain GT misses.

**Review coverage increased without proving exhaustive perception.** The trace contains 111 literal image requests and 111 retained image observation blocks, including all 19 second-pass slab montages and both sagittal bone views. Every GT region intersects at least one explicitly generated standard view in the bounded coverage audit. Unlike the previous run, GT7 has generated bone-view intersections, but the follow-up intersection is only 10 GT voxels on a sampled sagittal plane. Sampling and downsampling remain consequential. The late sweep uses three-slice maximum-intensity projections and crops the y range; covering all axial indices is not native-resolution review of every voxel. A brighter voxel in a slab can suppress a low-attenuation feature in that projection. This is a possible representation limitation, not proven causality.

**Contours remain manually guided.** Saved `segment.py` uses selected slice guides, intensity thresholds, connected components, closing, hole filling and smoothing, plus a manually bounded plaque region. No learned global detector was used. More rendered views did not translate into more GT matches.

## Attribution and next diagnostic

The inclusion rule is explicit and demonstrably used for one benign-favored pair. Current misses cannot be explained by a written minimum-size or more-likely-malignant requirement. Deciding whether tumor remains plausible still requires recognition. GT13 supports a concrete interpretation disagreement; other omissions are not individually separable into search, attention and recognition failures. Small target size, image appearance and unavailable original clinical reports remain task/reference limitations.

This result argues against assuming that a stronger goal alone will unlock exhaustive curation on this case. It does not establish a causal null effect or a general model capability ceiling. A useful next diagnostic would supply standardized native-resolution candidate clips containing both GT targets and plausible mimics, blinded to labels, and assess recognition separately from longitudinal presence/event judgment. That would control search and presentation. No such follow-up was launched here.

## Execution and provenance

New attempt `attempt-e5fda20ed65a41b4`, freeze `7b4b2740a45157383bccd77af41ccf5635deb94c0bcc2b00fa3f07f952f681cb`. Comparators: image-only `attempt-92800845745342f4` and context-supplied `attempt-81ee755346d04be7`. All use `openai/gpt-6-astra`, medium, the same solver image and a two-hour ceiling. The new attempt completed normally with valid masks, events, sidecar and report; no terminal exception, retry or quota reset. The original scientific scorer SHA remains `c5dcbe1208592b5eeac93d06d80be571f1cab038d730edb289e736892fa145a6`.

Oracle/no-op controls behaved correctly; a synthetic check covered the probability boundary and missing sidecar. Live isolation passed, the complete frozen instruction was delivered verbatim, and independent replay matches all saved metrics exactly. Only model-transport traffic was allowed; auxiliary OpenAI-host requests were blocked and retained in the audit. No source lookup or private-reference request was observed. This does not measure unseen training knowledge or establish attention.

Review `review-c623ccd6a955467e` permits this exploratory reference comparison, without task qualification or clinical adjudication. Original freezes, GT and scores remain unchanged.

- [Checked record/artifact manifest](evidence/longitudinal-ct-curation-comparison.json)
- [Structured results, transitions, trace checks and figure provenance](evidence/longitudinal-ct-curation-results.json)
- [Predeclared protocol](../methods/longitudinal-ct-curation-v1/protocol.md)
- [Preparation and controls](../examples/longitudinal-ct-curation-preparation.json)
- [Local replay and all GT panels](../../../.local/longitudinal-ct-curation-v1/analysis/evidence.json)
