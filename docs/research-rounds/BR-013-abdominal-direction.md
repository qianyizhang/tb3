# BR-013 — Prioritize upper-abdominal identity reasoning

Historical selection/protocol record. [Current presentation and verdict](../anatomy-experiments.md) · [Trace analysis](../anatomy-traces.md).

**Status: pilot complete: two Sol passes, one Sol identity miss; conditional
Terra follow-up repeats the pancreas-to-gallbladder error.** See the
[results and limits](BR-013-results.md).
On 2026-09-15 the user replied "proceed" to the recommendation below, authorizing
curation, controls and one Sol/xhigh attempt per admitted task, with Terra/max
only following a reviewed valid Sol failure. The user previously asked what to recommend next and whether
abdominal organs deserve more attention. The message remains in this conversation;
its separate message ID was not captured. No new model result is claimed here.

## Recommendation

Pause additional spine authoring. Prioritize anonymous upper-abdominal organ
identification, then test whether proposed wrong identities anchor judgment.
Use real variations in organ shape and arrangement, retain useful surrounding
structures and orientation, and score exact object-to-label assignments.
Treat unusual anatomy as a later preservation control. A disease-versus-error
verdict needs evidence beyond a surprising shape.

## Evidence for selection

The [abdominal subset receipt](../evidence/br013-abdominal-screen.json) filters
the existing BR-011 predictions without retraining or running inference. Among
nine abdominal organ classes, the geometry-only template classifier gets 56/69
identities correct; excluding the previously flagged partial-coverage patient
74 gives 52/60. Predictions still compete against the original 17-class
thoracoabdominal vocabulary. These are clustered observations from eight
patients, not new model trials or an abdomen-only benchmark.

| Source organ | Correct / available |
| --- | --- |
| Stomach | 3/8 |
| Gallbladder | 4/7 |
| Spleen | 5/6 |
| Left kidney | 6/8 |
| Pancreas | 7/8 |
| Liver | 7/8 |
| Right kidney | 8/8 |
| Each adrenal gland | 8/8 |

This supports investigating particular confusions; it does not establish weak
Sol/Terra anatomical knowledge. Duodenum and detailed abdominal branches were
not included in this baseline. Pancreas and adrenal identities should not be
called hard merely because the structures are difficult to segment from CT.

A [pancreas segmentation study](https://pmc.ncbi.nlm.nih.gov/articles/PMC12084540/)
reports recurring confusion around adjacent bowel and vessels. Those are
specialized CT segmentation results, not mask-only recognition outcomes.
Giving a clean mask has already removed much of the boundary-identification
problem. The proposed difficulty instead concerns combining shape, neighborhood
and the full scene into consistent identities.

## Bounded next round — authorized

Start with existing local source masks, retaining their available original
resolution. Curate approximately 10–15 objects per complete upper-abdominal
scene: liver, spleen, stomach, gallbladder, pancreas, duodenum, kidneys, adrenals,
and available major vessels. Do not include every class just to increase workload.

1. **BR013-A01, recognition:** one typical complete scene, anonymous instance
   IDs, fixed vocabulary, shared coordinates, ready viewer and loader. Exact
   identity assignment is the deliverable.
2. **BR013-A02, recognition under altered arrangement:** a source-verified scene
   with substantial natural displacement/deformation but sufficient context.
   Require identities, not an unsupported diagnosis. Reject partial-FOV tricks.
3. **BR013-A03, identity audit:** reuse one accepted scene in a separate fresh
   context with a small number of plausible wrong proposed names and unchanged
   geometry. Return exactly the affected IDs and corrected identities. This is
   a paired condition, not another independent patient.

Author-screen ordinary centroid/volume/extent matching, then a one-to-one
assignment baseline before spending model trials. Inspect source masks against
CT and check mask-only identifiability. Correct missing context rather than
accepting a planted key as sufficient ground truth. Preserve source defects as
holds. Do not add geometry errors, postoperative diagnoses or rare diseases in
this first recognition round.

Once admitted, use one fresh Sol/xhigh attempt per task. Retire clean passes;
review failures for source/evaluation faults. Use Terra/max on a retained valid
failure to examine whether it reproduces. This conditional follow-up cannot
estimate comparative model success rates across all cases. Record task success,
per-object accuracy, missed corrections/false repairs, wall time, input/output
tokens and grading time. Use the existing Harbor/Docker harness, 1,800-second
agent allowance, four CPUs and 4 GiB RAM, one attempt and zero retries. Freeze
inputs before controls and trials. A normal scene may be retained explicitly
as a calibration control even if the geometric baseline solves it; it will not
be advertised as a difficult residual. Baseline residuals receive no automatic
semantic-validity credit. Altered arrangement means observed source geometry,
not a certified pathology or surgical history.

If the compact local pool is insufficient, [PanTS](https://github.com/MrGiovanni/PanTS)
is a promising primary-source lead: it includes pancreatic substructures and
surrounding anatomical annotations. Its full external cohorts are not all
directly downloadable. Inspect a small accessible subset and its annotation
protocol/license; the large dataset headline is not evidence of difficult or
fair mask-only tasks. No PanTS data were acquired here.

## Ultimate condition

After recognition is calibrated, add a verified unusual-anatomy scene and test
preservation separately from annotation error detection. For surgery, provide
minimal verified operative context when geometry cannot distinguish resection
from a missing mask. For disease, score observable structural patterns unless
the allowed evidence supports a unique diagnosis. Require a macroscopic
relational or instance-assignment contradiction before injecting an error.

The next useful result is a small executable, interpretable pilot. More source
curation without a bounded admission/retirement decision would not establish
the hypothesized model blind spot.

## Frozen pilot selection, before model execution

The [original-mask screen](../evidence/br013-original-mask-screen.json) uses
13 abdominal classes, original 1.5 mm individual masks, and scene-relative LPS
centroids instead of the earlier scan-relative coordinates. All six scenes
with 13 nonempty masks are solved by the injective assignment baseline,
including the held limited-coverage case 74. This is a different baseline,
not a causal estimate of the benefit of one-to-one matching alone.

* **A01 / source 28:** 13 objects; ordinary calibration. Both baselines 13/13.
* **A02 / source 83:** 11 objects; no exported mask touches a scan boundary.
  Independent matching 9/11; injective matching 8/11, confusing pancreas,
  duodenum and portal/splenic vein. The source has a compact pancreas mask and
  empty spleen/gallbladder masks. The vocabulary allows absent classes; their
  cause is neither inferred nor graded. No surgical or disease diagnosis is
  claimed. This is a bounded residual pilot, not certified difficult anatomy.
* **A03 / source 83:** same geometry, IDs and render as A02; proposed pancreas
  and duodenum names exchanged. Object count and proposed-label multiset do
  not reveal the error. Exact correction IDs/labels are graded.

The [source review](../evidence/br013-source-review.json) records inspected
CT/mask overlays and its limits. The [freeze](../evidence/br013-freeze.json)
records all exported task hashes, exhaustive voxel/affine round trips and
25 author scoring controls. Whole individual masks preserve overlaps; there
is no merged-label priority overwrite and no planted geometry defect. Public
data include a label-free loader, statistics and selectable multi-view renderer.
The review is authored, without independent specialist adjudication. Any model
disagreement requires renewed identifiability review.
