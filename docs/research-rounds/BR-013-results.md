# BR-013 results — compact pancreas mistaken for gallbladder

**Anonymous recognition produced a shared whole-organ identity miss.** Sol/xhigh
called the compact pancreas gallbladder and the duodenum pancreas. Terra/max,
tested conditionally on the same task, also called the pancreas gallbladder but
identified the duodenum correctly. Sol passed the ordinary scene and corrected
the proposed pancreas/duodenum swap on the altered scene.

This is a more useful lead than a tiny contour discrepancy: no mask voxel was
edited, and the failed identity belongs to an entire 43.4 mL source object.
Current judgment: retain it as a secondary diagnostic. Later Sol passes with
exact class inventory or CT weaken its promotion case. See the
[current verdict and presentation](../anatomy-experiments.md).

[Protocol and selection](BR-013-abdominal-direction.md) ·
[Frozen tasks](../evidence/br013-freeze.json) ·
[Measured results](../evidence/br013-results.json) ·
[Authored reviews](../evidence/br013-reviews.json) ·
[Authoring code](../../probes/revisions/br013/authoring/README.md)

## One attempt per condition

| Task | Model | Outcome | Agent seconds | Total trial seconds | Output tokens |
| --- | --- | --- | ---: | ---: | ---: |
| A01: ordinary, 13 anonymous objects | Sol/xhigh | Pass, 13/13 | 73.36 | 138.55 | 2,035 |
| A02: altered scene, 11 anonymous objects | Sol/xhigh | Miss, 9/11 | 157.58 | 213.57 | 5,015 |
| A03: A02 geometry, two proposed names swapped | Sol/xhigh | Pass, both corrections; zero false repairs | 88.85 | 145.70 | 2,306 |
| A02: conditional follow-up, identical bytes | Terra/max | Miss, 10/11 | 176.29 | 231.98 | 7,838 |

All four completed normally, within an unchanged 1,800-second allowance.
There were no retries. Three oracle controls passed; three empty-answer controls
failed as intended. Controls and models have matching per-task checksums.
Runtime sessions record the requested model and effort, one fresh session each,
and the exact frozen user instruction. Artifact replay and a separate exact-set
comparison agree with every grade. No Claude trials were run.

| Attempt | Input tokens | Included cached input | Reasoning output, included above | Estimated model cost |
| --- | ---: | ---: | ---: | ---: |
| A01 Sol | 150,334 | 124,288 | 985 | $0.195 |
| A02 Sol | 284,726 | 259,712 | 2,956 | $0.304 |
| A03 Sol | 256,829 | 222,848 | 1,054 | $0.271 |
| A02 Terra | 387,147 | 347,136 | 6,214 | $0.244 |

Token counts are Harbor counters, checked against matching runtime counters;
input totals include repeated/cached context. Total model use: 496.08 agent
seconds, 1,079,036 input tokens including 953,984 cached, and 17,194 output
tokens. Cost is a harness estimate, about $1.014 total, not an invoice. CPU/RAM
were limited to four CPUs/4 GiB; actual peak use was not measured. Each input
package is under 0.5 MB. Scoring itself took 0.47–0.63 ms per model artifact;
the separate verifier container took about 12 seconds per trial.

## What was missed

| Object in A02/A03 | Source identity | Sol recognition | Terra recognition | Sol audit |
| --- | --- | --- | --- | --- |
| o197, 43.4 mL | Pancreas | Gallbladder | Gallbladder | Corrected to pancreas |
| o277, 63.5 mL | Duodenum | Pancreas | Duodenum | Corrected to duodenum |

The public data retain full original 1.5 mm binary masks, independent overlaps,
and shared LPS coordinates. Lossless cropping removes only empty array margins.
No supplied object touches the original scan boundary. Empty source spleen and
gallbladder masks produce no objects, and the instructions explicitly allow
unused vocabulary classes. Their absence is not graded as an error or diagnosis.

Additional axial CT review supports the source identities. In mask views, the
compact pancreatic object occupies the concavity of the adjacent duodenal loop.
That relationship is consistent with the general anatomy described in
[Javed et al., section 2.2.1](https://pmc.ncbi.nlm.nih.gov/articles/PMC9317715/).
The paper does not adjudicate this patient. CT intensities helped author review
but were unavailable to the solvers and are not a justification for requiring
an otherwise unobservable judgment.

Inspect the [public-input neighborhood](../../runs/br013-abdomen/author/neighborhood-83.png)
and [additional author CT review](../../runs/br013-abdomen/author/source83-central-axial.png).
These local images are not bundled in a fresh clone. The interactive comparison
shown in the conversation switches names while keeping every geometric point
fixed; its preview is sampled, not a replacement for the full binary masks.

## What the trajectories establish

**Sol A01:** read measurements, viewed the overview and four focused renderings,
then correctly assigned the duodenal loop, pancreas and branching venous mask.
This retires ordinary major-organ recognition as the difficulty lead.

**Sol A02:** viewed the overview and four focused renderings, measured principal
axes, and inspected ASCII projections. It described a familiar transverse
pancreas silhouette and a sac-like gallbladder. A proposed nearest-neighbor
calculation failed because its chosen SciPy import was unavailable; it continued
without installing it or replacing that calculation. NumPy/Pillow availability
was correctly disclosed. This is a completed solver miss, but it combines
anatomical interpretation and tool-use decisions, not a pure visual-prior test.

**Terra A02:** read physical measurements and inspected isolated renderings of
all 11 objects. It got the duodenum right but still called the compact pancreas
gallbladder. It recovered from one answer-file patch mismatch and finished
normally. Both traces use the public local geometry; no external patient matching
or private reference-answer access was observed.

**Sol A03:** focused on the three central structures and explicitly recognized
the pancreatic object within the duodenal loop. It corrected both misleading
names and left all other objects unchanged. The proposed labels may have helped
it select the relevant categories. This is not evidence of an anchoring failure.

## Current disposition

Retain A02 as a compact historical identity miss: Sol 9/11 and Terra 10/11.
The proposed-name audit A03 passed. Subsequent [BR-014](BR-014-results.md) exact
inventory and [BR-015](BR-015-results.md) CT conditions also passed, preserving
the central geometry. These outcomes weaken a general anatomical-inability
explanation. A02 is a secondary diagnostic; BR-017 M02 is the current primary
lead. See the [cross-round verdict](../anatomy-experiments.md).

The [per-trial analysis](../anatomy-traces.md) includes all four runs, public
excerpts, actual image payloads and pseudocode. A02's ASCII outputs are maximum
projections, not individual CT slices. Its unavailable SciPy distance check was
not replaced. The observed error combines interpretation and tool-use choices.

Mask-only identifiability and clinical cause remain unresolved. Each condition
has one attempt; Terra was selected after Sol failed. Preserve the original
records without treating these selected outcomes as relative success rates.
