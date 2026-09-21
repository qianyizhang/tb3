# From CTA to a named vascular tree

**BR-042 · Final technical retrospective · 21 September 2026**

Technical ML / research audience · One public development case · Six fresh attempts · Seven saved outputs

[Interactive showcase](index.html) · [Machine-readable results](data.json) · [Input and output hashes](manifest.json)

## 1. What this study demonstrates

A general-purpose agent can inspect a native 3D coronary CT angiogram (CTA), write classical image-processing code, discover its own tracing controls, and produce a substantial named vessel inventory. On this case, the strongest recorded geometry is **95.5% of annotated coronary length within 1 mm** (Astra/medium, V3). That output correctly labels **79.3%** of reference length. No model output passes the complete coronary criterion.

The difficult transition is from finding bright tubular structures to producing a **complete, correctly connected and consistently named tree**. Small omissions affect both geometry and the numbering of later branches. More available time and higher reasoning effort did not reliably repair that transition in these attempts.

The strongest explanation for the resumed plateau is concrete: **the continuation retained all 15 prior coronary extraction specifications**, while expanding and cleaning up the broader vessel inventory. Its coronary coverage and label scores are exactly unchanged. Reconstructed candidate filters show two different failure mechanisms: D2 reached the review list but was withheld; OM1 fragments were removed by size and connection-distance gates.

These are observations about a small exploratory study, not a general model ranking or a causal test of inference-time scaling. Astra and Sol are the only model families with BR-042 outputs. Terra results from the predecessor BR-041 task are not comparable rows here.

## 2. The task: discovery, tracing, topology and identity

The agent receives a full native **ImageCAS case 1 CTA**, a source notice, a generic coronary taxonomy and an output contract. The volume is **512 × 512 × 275**, with **0.376953 × 0.376953 × 0.5 mm** spacing. No vessel masks, centerlines, seeds, endpoints, known branch-presence list or previous solution are supplied. A taxonomy tells the agent which names are legal; it does not tell it which vessels are present.

The requested scope is broad: identify clinically relevant visible vessels, discover their courses, reconstruct centerlines, assign anatomical names, and document method and uncertainty. This includes aorta, pulmonary vessels and veins as well as coronary arteries. Submitted geometry is a set of named polylines in **RAS millimeters** with per-point category codes. The task requires nonzero steps no longer than 1.5 mm. The agent must build its own useful views and processing tools using the available CPU image-processing environment.

| Component | Supplied to the solving agent? | Role |
| --- | --- | --- |
| Native CTA, affine and source notice | Yes | Original image evidence |
| Generic 14-code coronary taxonomy and output schema | Yes | Naming vocabulary and file contract |
| NumPy / SciPy / nibabel / Pillow / scikit-image and CPU tools | Yes | Building and running image-processing methods |
| Agent-written waypoints, crops, filters and review images | Created during the attempt | Intermediate decisions; not supplied seeds |
| ImageCAS-X coronary centerlines and labels | No; evaluator only | Frozen scoring reference |
| Case-specific annotations or prior solutions from elsewhere | Prohibited | Would invalidate the intended image-only inference boundary |
| Reference-guided branch focus in this demo | Post-hoc presentation only | Helps readers inspect a known failure; easier than blind discovery |

The key reasoning problems are separable. **Discovery** asks whether a branch is found. **Geometry** asks whether its course is close to the reference. **Connectivity** asks whether it joins the correct parent. **Identity** asks which anatomical category it belongs to. **Extent** asks where it should stop. Local tube enhancement and shortest-path tracing help with geometry, but do not determine anatomical identity by themselves.

![Original CTA in three linked native planes, with both overlays hidden](native-input.png)

*Static fallback: original CTA only. The corresponding interactive viewer supports linked native coordinates and independent overlay reveal.*

## 3. How performance is measured

The automated evaluator covers the annotated **coronary subset**, not the entire requested vascular inventory: 18 reference polylines, 11 present categories and **646.24 mm** of reference length. It uses dense arc-length sampling, with segment steps at most 0.25 mm, and a fixed nearest submitted geometry match independent of labels.

- **Geometry recall:** fraction of reference length within the tolerance of any submitted curve, including category 0.
- **Labeled recall:** fraction both covered and assigned the correct category by that same closest match.
- **Length weighting:** each millimeter contributes equally; long main arteries dominate.
- **Category mean:** each of the 11 present categories contributes equally; short branches matter as much as long main arteries.
- **Pass:** category mean at least 90% **and every present category at least 80%**, at 1 mm. Geometry and labeling are assessed separately. The 2 mm figures are sensitivity measurements, not alternate passes.

There is no precision or endpoint/length-ratio gate in V2 onward. Extra unannotated output is **unadjudicated**, not automatically false anatomy. Conversely, a large number of submitted courses does not establish anatomical correctness or clinical completeness. Coverage also does not by itself validate parent connectivity or lumen centrality.

Sources: [frozen scorer](sources/frozen-score.py), [reference](sources/reference.json), [V4 instruction](sources/instruction.md).

## 4. Results across models and settings

All percentages below use the common V3 geometry-first matching semantics at **1 mm**. The original submissions and verifier outcomes are preserved. V2's original labeled length score was 77.2%; under the common scorer it is 76.0%. This is a disclosed re-evaluation, not an edited original score.

| Saved output | State | Actual wall time | Geometry, length | Labeled, length | Geometry, category mean | Labeled, category mean | Courses |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| V2 · Astra / medium | Completed | 0:27:56 | 87.0% | 76.0% | 70.1% | 51.0% | 27 |
| V3 · Sol / xhigh | Completed | 0:41:36 | 26.2% | 19.4% | 15.8% | 8.6% | 16 |
| V3 · Astra / medium | Completed | 0:46:34 | 95.5% | 79.3% | 81.3% | 55.3% | 65 |
| V3 · Astra / xhigh | Timeout · partial | 1:00:00 | 91.8% | 68.3% | 72.0% | 48.2% | 33 |
| V4 · Astra / xhigh · 2h | Timeout · partial | 2:00:00 | 94.1% | 74.8% | 76.9% | 51.7% | 71 |
| V4 · Astra / xhigh · 6h | Transport stop · partial | 2:47:45 | 94.0% | 79.3% | 75.5% | 54.1% | 60 |
| V4 · Astra / xhigh · resumed | Completed continuation | 4:13:52 | 94.0% | 79.3% | 75.5% | 54.1% | 64 |


The resumed row reports **combined** wall time: 2h47m45s before the transport stop plus 1h26m07s of continuation. It is not an independent replicate. Wall time includes inference, tools and transport delays; it is not GPU compute or active reasoning time. Course counts measure output inventory, not validated vessels.

**The fairest available within-protocol comparison is the V3 subset.** Its three intended model settings share frozen task bytes and a one-hour allowance. Sol/xhigh and Astra/medium complete; Astra/xhigh times out, so its row is a valid saved partial output rather than a completed capability comparison. Two setup failures occurred before model execution and are excluded from these performance rows.

Sol's submitted LM, LAD and LCx have 0% geometry recall at 1 mm, despite its method report assigning these names. It recovers much of RCA. Astra/medium recovers substantially more of both trees, but misses the small D2/OM1 and misnumbers recovered branches. Higher effort and longer-budget variants do not exceed the completed medium result on this case. The tiny 79.31% versus 79.30% labeled-length difference between medium and the resumed output should not be interpreted as a meaningful advantage.

**Protocol history matters.** V1 was superseded before any model trial. V2 broadened the task and removed the precision gate. V3 clarified numbering and separated geometric matching from labels. V4 further clarified scope, shared categories and continuation, and added time-management instructions. The prepared V4 one-hour configuration was never run. V4 two-hour and six-hour attempts were fresh starts; only the six-hour continuation reuses prior state. Cross-revision comparisons are descriptive development evidence, not controlled compute scaling.

Sources: [common evaluation](sources/comparison.json), [V2 original review](sources/BR-042-results.md), [V3 study](sources/BR-042-v3-results.md), [resume evaluation](sources/evaluation.json).

![Comparison of geometric and correctly labeled reference-length recall](comparison.png)

*All saved outputs under the common scorer, 1 mm, weighted by reference length. Teal: geometry. Blue: correct label. The continuation is not a fresh attempt.*

## 5. What the agents actually did

These attempts combine image inspection and agent-written classical vision pipelines. They are not evaluations of a single pretrained segmentation network, and their saved extraction scripts are not general, seed-free solutions for arbitrary scans.

| Setting | Retained methodology | Main shortcoming |
| --- | --- | --- |
| V2 Astra/medium | Native slice inspection; physical-scale Hessian tube features; HU/vesselness-weighted paths between image-derived guide points; normal-plane centering and RAS export | Incomplete side-branch discovery, unresolved diagonal/marginal numbering, limited broad inventory |
| V3 Sol/xhigh | Multiscale Frangi vesselness, skeleton paths, image-derived waypoints and geodesics; smoothing/resampling | Major left-tree localization failure; plausible named output did not imply correct anatomical location |
| V3 Astra/medium | Blood-pool suppression, multiscale Hessian responses, skeleton pruning, constrained geodesics, cross-section centering, manual anatomical review by the agent | High overall geometry; tiny branches missed; downstream numbering and some right-system identities unresolved |
| V3 Astra/xhigh | Saved extraction refines reviewed voxel paths in normal planes, attaches nearby parent junctions and resamples to RAS; retained work includes vesselness and candidate-path exploration | Timeout and incomplete final documentation; D1/Ramus confusion and missing small branches |
| V4 Astra/xhigh | Physical-scale Hessian features, constrained HU/vesselness geodesics, image-derived controls, residual candidate review, broad-vessel expansion and validation | Hard candidate gates; rejected D2 hypothesis; OM numbering cascade; effort spent outside the scored coronary subset |

The methods are based on saved code, artifacts and model-authored method reports; a method report is evidence of claimed procedure, not proof that its anatomical claims are correct. V3/xhigh has no final `method.md`. The final resumed extraction rebuild takes **76.3 seconds**, but uses the case-specific controls discovered during the hours-long session. This demonstrates replay conditional on those controls, not repeated blind success.

Observed traces and method artifacts show classical image processing and local file work. Retained audits did not establish case-specific annotation retrieval or pretrained coronary-model use. This is an **observed-access statement**, not proof of an air-gapped environment or absence of public-case contamination in model training. Network availability, cached tokens and model configuration cannot establish those stronger claims.

Retained examples: [Sol method](sources/v3-sol-method.md), [Astra medium method](sources/v3-medium-method.md), [V3 xhigh code](sources/v3-xhigh-extract.py), [resumed method](sources/resumed-method.md).

## 6. Why the extra time did not resolve the result

### 6.1 The resumed work improved a different part of the deliverable

The continuation restored its own output and conversation without receiving GT, scores or case-specific reviewer advice. It added three pulmonary arterial courses and a superior RCA atrial branch, corrected pulmonary geometry, completed the inventory and documentation, and validated a full rebuild. Output grew from **60 to 64 courses**, from 7107 to 7430 points, and from 3134.6 to 3276.4 mm of submitted path.

All 15 pre-existing coronary extraction specifications are identical. Fourteen corresponding exported curves are identical; RCA has one inserted point for the new atrial junction. Across the complete inventory, 53 course objects are unchanged. The scored coronary metrics are exactly equal. This makes work allocation and unchanged accepted hypotheses a stronger explanation than an opaque failure of “more reasoning.”

The resumed trace contains 34 `exec` orchestration calls and 11 structured transport errors, then normal completion. Neither six-hour allowance was exhausted. Exact useful inference time and transport-delay cost cannot be recovered from elapsed time alone.

### 6.2 D2: candidate detected, reviewed and withheld

The saved candidate generator was independently reproduced with **zero added or missing candidate voxels**. In its default pipeline, 93.9% of reference D2 lies within 1 mm of the raw skeleton; **87.8% survives all candidate gates**. Candidate #3 has 87 voxels and is 1.69 mm from an existing path. Its component covers 100% of reference D2 at 2 mm.

The pre-resume trace generated views at this location, and the continuation listed it again. The final method withheld the candidate as a possible left-atrial-appendage/myocardial ridge. Final D2 geometry coverage is only **3.1%**, with 0% correctly labeled. Relative to the reference, this is principally an acceptance/identity failure after detection. An unordered candidate component still needs ordering, parent verification and arterial adjudication before it becomes a valid centerline.

### 6.3 OM1: local signal removed by the candidate filters

OM1 has weak local support: its reference-center median is about 121 HU. The raw skeleton covers **78.3%** at 1 mm; size filtering leaves **55.8%**; the parent-gap filter leaves **0%**. A 3-voxel fragment fails the 6-voxel minimum. A 13-voxel fragment survives that gate but sits 4.55 mm from an accepted path, beyond the 2.2 mm connection cutoff.

Lowering vesselness from 0.018 to 0.006 yields 100% raw-skeleton OM1 coverage, but most of it joins a **6586-voxel component**, which fails the 2499-voxel maximum. Accepted OM1 coverage remains zero and candidate count increases from 17 to 37. A lower threshold alone is not a demonstrated fix.

![Reference-assisted native OM1 inspection of the resumed output](OM1-inspection.png)

*Post-hoc OM1 focus. Orange: resumed output; cyan: evaluator reference. The crosshair location is reference-derived and was not supplied to the solver. All three views use the original native grid and affine. The 3D panel is a polyline projection.*

### 6.4 A discovery miss also changes later names

The final output covers 57.2% of GT OM2 but calls it OM1. It covers almost all the reference “Other” diagonal but calls it D2. Reference-assisted relabeling on unchanged geometry would raise labeled length coverage from **79.30% to 88.85%**, while category mean rises only to 68.34%. It still fails because missing branches remain missing.

D2, OM1 and the uncovered portion of OM2 account for **80.2% of missing reference geometry**. Small-branch discovery has a disproportionate effect on complete-tree scoring and on identities elsewhere in the tree.

Sources: [trace investigation](sources/trace-audit.md), [structured trace audit](sources/trace-audit.json), [candidate-stage measurements](sources/candidate-funnel.json). These diagnostics use GT after the run; they are not additional blind results.

## 7. Does the ground truth impose a ceiling?

**No general GT-imposed ceiling has been demonstrated. A narrower anatomical naming dispute remains open.**

The frozen verifier replays exactly. Reference geometry and labels score 100% against themselves, after adding required display names. This rules out a demonstrated internally contradictory conversion/scoring ceiling; it does not establish clinical correctness or attainable blind performance.

ImageCAS-X derives its final centerlines from corrected lumen masks and propagates segment labels through a shared annotation process. Mask/centerline agreement therefore is not independent anatomical adjudication. Its protocol is selective, including some additional diagonal/marginal branches and allowing multiple PDA/PLA courses. A broad all-vessel inventory need not map one-to-one to this taxonomy. [Primary source: ImageCAS-X methods and labeling protocol](https://arxiv.org/html/2608.30404v1#A2).

The concrete dispute is a course labeled R-PDA by GT and an inferior right-ventricular branch, category 0, by the agent. Relabeling that submitted course would add about **2.17 percentage points** to correct-label length coverage. With the diagonal/marginal renumbering above, it reaches 91.03% length coverage but only 71.12% category mean: still no pass. Even an optimistic perfect-label bound on the final geometry is only **75.53% category mean**.

The fixed closest-geometry rule also introduces label-boundary sensitivity. A permissive diagnostic allowing any correctly labeled submitted course within 1 mm gives 81.50% instead of 79.30% labeled length coverage. That alternative can reward overlapping guesses and is not substituted for the frozen score.

Reference-guided native and curved views show local signal near D2/OM1. Neither this investigation nor those images constitute a specialist ruling that every disputed annotation is anatomically correct. The current evidence does not justify invalidating D2/OM1 or attributing the entire performance plateau to GT error.

## 8. What to change next

These are **assistant recommendations**, not user-approved trials or demonstrated improvements.

| Failure addressed | Concrete method change | Evidence needed to establish improvement |
| --- | --- | --- |
| OM1 lost as fragments or giant merged components | Split skeleton graphs into branch paths before size filtering; use bounded, image-supported reconnection instead of a single parent-gap cutoff | Blind outputs across more cases; candidate precision and reviewed false paths as well as recall |
| D2 discarded after being detected | Persist accepted/rejected/uncertain candidate ledger with images and parent hypotheses; revisit consequential rejections before expanding low-priority inventory | Correctly connected, supported submitted branch without GT guidance |
| Discovery-order numbering | Decide numbering after candidate reconciliation; keep topology and anatomical name hypotheses explicit until review | Better category identity without duplicate guesses or forced presence |
| Broad task versus coronary-only feedback | Reserve a coronary completeness audit and report broad inventory quality separately | Predeclared coronary checks plus independently reviewed noncoronary accuracy |
| R-PDA and boundary ambiguity | Obtain appropriate anatomical adjudication and document scoring conventions prospectively | Expert/source resolution; new task revision if the contract changes |
| Uncertain time/effort conclusions | Matched prompts and environments, repeated attempts, complete execution accounting, multiple cases | Uncertainty estimates and comparable completed attempts |

A useful next experiment would change the discovery/review mechanism under a fixed protocol, rather than merely extending the same accepted reconstruction. No new trial, benchmark rewrite or clinical adjudication was performed for this report.

## 9. Reading and reproducing the evidence

The interactive page begins with **input only**. Reveal a saved model output and the evaluator reference separately. The three native planes preserve the full voxel grid and physical aspect ratio; the display uses a fixed HU window of −120 to 600, quantized to 8 bits for portability. The original source is unchanged. The 3D panel is a projected polyline view, not a CT volume rendering. Orange means submitted output; cyan means evaluator reference; color does not assert correctness.

Branch-focus buttons use GT locations for post-hoc inspection and are clearly marked. They were not solver inputs. All saved answers are copied byte-for-byte with SHA-256 receipts; display coordinates are rounded only for rendering. Original numeric metrics, exact centerline files, the scorer, prompt, source notice, licensing and investigation records accompany the demo. Private reasoning traces and credentials are excluded.

Use `manifest.json` to trace every packaged source. Rebuild using the adjacent source `README.md`; the builder reads retained artifacts and writes only to a fresh destination. It never imports historical trial-authoring modules or changes frozen answers.

**Attribution:** CTA from ImageCAS (Xu and collaborators), source listing Apache 2.0. Evaluator annotations from ImageCAS-X (Bransby et al.), CC BY 4.0. [Source notice](sources/SOURCE_NOTICE.md) · [License declarations](sources/DATA-LICENSE.txt). This local retrospective evaluates research artifacts from a public development case; it is not held-out clinical validation.
