# BR-014 results — inventory resolves the miss; fragments cost more work

**Both new Sol/xhigh attempts passed.** The exact present-label inventory
resolved the previous compact-pancreas error. Splitting the pancreas and
duodenum into four substantial fragments increased observed resource use but
did not produce a failure. These tested conditions are retired as hard Sol
candidates. The conditional Terra follow-up was not triggered.

[Declared protocol](BR-014-inventory-components.md) ·
[Measured results](../evidence/br014-results.json) ·
[Authored review](../evidence/br014-reviews.json) ·
[Component screen](../evidence/br014-component-screen.json) ·
[Authoring](../../probes/revisions/br014/authoring/README.md)

## One attempt per task

| Condition | Sol/xhigh outcome | Agent seconds | Total trial seconds | Output tokens |
| --- | --- | ---: | ---: | ---: |
| Historical A02: 11 intact objects, 13 possible classes | Miss, 9/11 | 157.58 | 213.57 | 5,015 |
| **I01: same objects, exact 11 present classes** | **Pass, 11/11** | **75.58** | **143.81** | **2,602** |
| Historical A01: ordinary scene, 13 intact objects | Pass, 13/13 | 73.36 | 138.55 | 2,035 |
| **F01: A01 source, 15 objects including four fragments** | **Pass, 15/15** | **222.65** | **285.33** | **6,620** |

Historical rows are retained BR-013 observations, not reruns. I01 changes only
the vocabulary, its contract sentence and task-routing name; geometry, object
IDs, renderings, loader and reference key remain unchanged. F01 also changes
IDs/order and explicitly permits repeated labels with an exact class inventory.
Its roughly 3.0× agent time and 3.3× output relative to A01 are descriptive
single-trial differences, not a causal estimate of fragmentation alone.

| New attempt | Input tokens | Included cached input | Included reasoning output | Estimated cost |
| --- | ---: | ---: | ---: | ---: |
| I01 | 216,133 | 183,040 | 1,136 | $0.258 |
| F01 | 478,510 | 411,520 | 4,231 | $0.565 |

Both completed normally, with no retries, within the unchanged 1,800-second,
four-CPU/4-GiB allowance. Total new model use: 298.23 agent seconds, 694,643 input
tokens including 594,560 cached, and 9,222 output tokens. Input includes repeated
context; output includes reasoning. Cost is a Harbor estimate, about $0.823
combined, not an invoice. Actual peak CPU/RAM was not measured.

Two oracle controls passed and two empty-answer controls failed as intended.
Every control/model pair shares a task checksum. Runtime sessions verify
Sol/xhigh, Codex 0.154.0, one fresh session and the exact frozen instruction.
Artifact replay and independent exact-set comparison agree. Model-answer
scoring took 1.56 ms for I01 and 0.57 ms for F01. Nine authored F01 scoring
controls passed, including duplicate/missing fragments and a plausible
pancreas/duodenum identity switch. Historical BR-013 task hashes remain unchanged.

## What was actually split

Starting with original 1.5 mm source masks from case 28, each target organ was
partitioned along its longest principal axis. F01 removes a 6 mm band around
the median plane and retains both sides in their original physical coordinates.
The gap-free variant is an author control only; it was not given a model trial.

| Source organ | Original volume | Retained fragment volumes | Omitted volume |
| --- | ---: | --- | ---: |
| Pancreas | 59.42 mL | o475: 26.90 mL; o919: 27.24 mL | 5.28 mL (8.89%) |
| Duodenum | 55.86 mL | o942: 26.79 mL; o165: 26.81 mL | 2.26 mL (4.05%) |

Each retained target fragment is connected under 26-neighbor connectivity.
An independent world-coordinate set comparison verifies every fragment is a
subset of its source organ, paired fragments do not share voxels, retained plus
omitted counts recover the source, and the other 11 organs are unchanged.
Original **cross-organ** overlaps are preserved.

The exact task is to label every retained object, allowing repeated classes.
It does not ask the model to detect an unspecified boundary error, reconstruct
hidden voxels, or distinguish surgery from disease. These exclusions define the
observable task, rather than hiding ambiguity inside the evaluator.

## What the component screen and solver show

Across eight retained patients, 5/16 pancreas/duodenum source masks have multiple
26-connected components. Some are tiny islands; their existence is neither
proof of correct anatomy nor a certified annotation defect. Component count
therefore cannot itself be the answer key for an error-detection benchmark.

A greedy nearest-surface pairing baseline, even told which four objects are
the target fragments, gets **0/2 pairs** in both gap conditions: some pancreas
and duodenum surfaces are closer than their same-organ counterparts. This is a
narrow baseline, not a general solver. A seam-aware algorithm could exploit the
paired planar cuts; that shortcut has not been measured independently.

**Sol F01** requested ten focused renderings and used a distance matrix and
voxel-overlap counts. After an unavailable SciPy import, it implemented the
calculation with NumPy. It correctly paired o919/o475 as pancreas and o942/o165
as duodenum, then assigned all other structures correctly. Its use of preserved
cross-organ overlap as an exclusion heuristic means this is not a pure test of
anatomical priors. The public trace supports successful grouping and useful
tool recovery; it does not establish clinically reliable recognition.

**Sol I01** focused on the compact central objects and their relation to the
vascular masks, identifying the pancreas within the duodenal loop. With exactly
the present class names available, its previous gallbladder/pancreas confusion
disappeared. This supports inventory uncertainty as a hypothesis worth keeping;
one fresh trial does not establish a general mechanism or a success rate.

## Current disposition

Both tested conditions are retired as hard Sol candidates. Exact inventory
resolved A02's confusion; substantial fragments increased observed work but
were all named correctly. The fracture task also exposes native-overlap and
planar-cut cues, so its pass should not be reduced to anatomical knowledge alone.

The [cross-round presentation and verdict](../anatomy-experiments.md) ranks
BR-017's broad partial-absorption miss first and the original open-inventory A02
miss second. The [trace walkthroughs](../anatomy-traces.md) show the I01
recognition and F01 NumPy fallback/grouping steps with their actual images.

No new Terra or Claude trial was run in BR-014. The original freezes and grades
remain unchanged; no additional fragment trial is queued.
