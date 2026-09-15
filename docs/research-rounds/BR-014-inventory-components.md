# BR-014 — Label inventory and fragmented organ identity

Historical selection/protocol record. [Current presentation and verdict](../anatomy-experiments.md) · [Trace analysis](../anatomy-traces.md).

**Status: complete; two Sol/xhigh passes.** See [results](BR-014-results.md).
Authorized on 2026-09-15. The user said
"good progress, continue" and proposed breaking pancreas/duodenum annotations
into components through missed labels or omitted parts. The message is retained
in this conversation; its individual ID was not captured.

## Questions declared before new model results

1. **I01, exact inventory:** copy BR013-A02 and change only the vocabulary and
   its explanatory sentence to supply the 11 classes actually represented.
   Preserve all object IDs, masks, views, tools, scoring and resource allowance.
   Does anonymous recognition still miss the compact pancreas when gallbladder
   is no longer an available label? Compare to retained BR-013 observations;
   no repeat of the historical broad-vocabulary task.
2. **F01, fragment identity:** screen a bounded two-piece split of pancreas and
   duodenum in the ordinary source-28 scene, which Sol previously identified
   correctly. Keep shared physical coordinates and all surrounding organs.
   Ask for the anatomical label of every retained fragment, allowing repeated
   labels. Source lineage supplies an exact ID-to-label key. Do not ask to
   reconstruct an unknowable omitted boundary or diagnose a patient.

Component screening first measures natural disconnectedness (6- and 26-neighbor
connectivity), then a lossless split and a split with a small explicit gap.
Report fragment sizes, omitted volume and cheap proximity/reassembly baselines.
No single-voxel islands are promoted as difficulty. Reject tiny or ambiguous
fragments and treat artificial cutting cues as a limitation. A bounded split
may be run as a diagnostic calibration even if cheap methods solve it; it must
not then be described as a hard anatomical benchmark.

Freeze each admitted task separately before its controls/trials. Use one fresh
Sol/xhigh attempt, 1,800 seconds, four CPUs, 4 GiB RAM and the same NumPy/Pillow
tools. Zero retries. After reviewing a valid Sol miss, allow one Terra/max
follow-up on identical task bytes; no Terra follow-up on a clean Sol pass.
Record outcome, identity accuracy, input/cache/output tokens, agent/total time,
grading time and model provenance. Keep historical freezes/results untouched.

## What fragmentation can and cannot establish

Changing object containers without removing voxels tests grouping and identity;
it does not create missing anatomy. Removing connecting tissue tests recognition
with less evidence, but a gap alone cannot distinguish omission, pathology,
surgery or valid source fragmentation. Those are different tasks. Actual QA of
boundary omission would need CT or other independently sufficient evidence and
an accepted tolerance region, not exact recovery of an author's hidden cut.

Pancreas segmentation research does document confusion with adjacent duodenum
and inconsistent segmentation of unusual anatomy, but that does not establish
that a synthetic mask-only fragment puzzle reproduces those clinical errors.
Primary lead: [human-in-the-loop pancreas validation](https://pmc.ncbi.nlm.nih.gov/articles/PMC12701807/).
No clinical frequency or diagnosis is inferred from this pilot.
