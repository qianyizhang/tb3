# Image-only paired CT: detection, segmentation and correspondence

2026-09-22 · [User request](codex://threads/01a0c4d1-741f-76e3-9023-1064e5a9a0c5)
· [Generic solver instruction](../methods/longitudinal-ct-image-only/instruction.md)
· [Preparation and controls](../examples/longitudinal-ct-image-only-preparation.json)

Neither attempt recovered the complete task on this first CT pair. Astra medium
captured the dominant abdominal region but missed a separate reference lesion at
both visits and used a coarser baseline partition. Sol xhigh submitted empty masks
after concluding that no definite tumor was visible. Both finished normally with
valid artifacts; neither result is a timeout or infrastructure exclusion.

[Interactive native reader](http://127.0.0.1:8770/) ·
[Exact scores, replay and trace evidence](evidence/longitudinal-ct-image-only-comparison.json).
The standalone reader is `.local/longitudinal-ct-image-only-v1/review/index.html`.

Follow-up analysis: [trace methodology and failure attribution](longitudinal-ct-trace-attribution.md)
distinguishes under-separation from absent lesion coverage, audits candidate
rejection and coordinate pairing, and identifies instruction changes to test.

## Task and information boundary

Each agent receives two full native CT volumes, marked only baseline/follow-up,
and a concise instance-mask/event-file contract with an invented JSON example.
No masks, target locations, lesion counts, disease history, dataset name, source
patient ID or reference events are supplied. IDs are independent between visits.
The solver may inspect images, write code and construct masks with installed
NumPy/SciPy/nibabel/skimage/Pillow. No pretrained weights, GPU or external data are
available. Each attempt has a two-hour ceiling; attempts run sequentially because
the Docker host has four CPUs and about 7.74 GiB physical RAM.

Outputs are two native NIfTI instance masks, `events.json` and a short report.
The private verifier scores only after the agent finishes, in a separate image.
Harbor reward means valid artifacts, not scientific success. Oracle/no-op controls
and synthetic error controls passed before the first model started. The task digest
is `f2aa2fb2f71acd930e927d581a2513c31dd6c5a03f1f0387ff64e00f098eea24`.

## Results

All original verifier fields were reproduced **exactly** by independent local
replay. The original verifier used NumPy 2.2.6/SciPy 1.15.3/nibabel 5.3.2; replay
used the existing NumPy 2.5.3/SciPy 1.18.1/nibabel 5.4.2 environment. No score or
reference was changed. No composite scientific pass threshold was introduced.

| Endpoint | Astra medium | Sol xhigh |
| --- | ---: | ---: |
| Valid output contract | Yes | Yes |
| GT instances localized, both visits | 2/6 | 0/6 |
| Detection TP / FP / FN | 2 / 0 / 4 | 0 / 0 / 6 |
| Detection precision / recall / F1 | 1.000 / 0.333 / 0.500 | undefined / 0 / 0 |
| Baseline foreground Dice | 0.68480 | 0 |
| Follow-up foreground Dice | 0.77921 | 0 |
| GT-macro instance Dice, all six instances | 0.23445 | 0 |
| Baseline / follow-up GT-macro Dice | 0.15159 / 0.40015 | 0 / 0 |
| Correct cross-visit edges | 1/4 | 0/4 |
| End-to-end link F1 | 0.400 | 0 |
| Correct exact typed event groups | 0/2 | 0/2 |
| Conditional link recovery | 1/1 eligible edge | No eligible edges |
| GT edge eligibility | 1/4 | 0/4 |
| Complete GT event-group eligibility | 0/2 | 0/2 |
| Agent execution time | 17m 05s | 41m 11s |
| Total trial time | 17m 51s | 42m 10s |
| Image observation blocks (montages count as one) | 51 | 77 |

The two point-localization matches are Astra's single abdominal instance at each
visit, assigned to source B4 and F4. Its one corresponding edge is correct under
that mapping. Thus the weak end-to-end link result is upstream of, and does not
by itself demonstrate, failure to link already-localized lesions. Neither output
provides a complete detected GT event group for an isolated event assessment.

![Separate endpoints](../../../.local/longitudinal-ct-image-only-v1/review/score-comparison.png)

Astra's baseline/follow-up foreground precision is 0.58947/0.69831 and recall is
0.81691/0.88131. The overlap loss therefore includes both omitted tumor voxels and
extra labeled tissue, beyond the fine-instance convention question. At IoU gates
0.10, 0.25 and 0.50, its detection sensitivity is retained in the exact receipt;
the frozen primary centroid-based rule is not retuned after these outputs.

![Native GT and saved predictions](../../../.local/longitudinal-ct-image-only-v1/review/native-comparison.png)

These six rows use each GT instance's maximal-area axial plane and a 150 mm crop;
all four columns in a row share the same source CT, orientation and window. Cyan
is GT, orange is Astra, pink is Sol; a solid contour and faint fill share each
legend color. Local IDs do not establish identity across outputs. Both models have
zero predicted overlap with source B3/F3. The full-volume reader supports slice
inspection and mask toggling; selected crops are not exhaustive visual QA.

## What the traces show

Astra visually specified native axial polygons, interpolated signed-distance
fields, applied vessel/fat exclusions and retained the dominant connected region.
It described one confluent retroperitoneal lesion at each visit and called that
identity persistent. Its report separately mentions thyroid nodularity that it
did not confidently attribute to tumor. That prose does not establish that it
correctly recognized the nearby source lymph-node target; the target masks were
omitted in both visits.

Sol reviewed axial and orthogonal soft-tissue/lung/bone views, resampled follow-up
onto the baseline grid using affines, inspected fusion views and estimated some
image-based shifts. It generated candidate breast/axillary masks, rejected them
and other candidates as normal-appearing anatomy, then deliberately submitted two
all-zero masks and no groups. It explicitly distinguished a negative annotation
from a clinical assertion that malignancy was absent. Interim candidate masks
remain in raw work artifacts but are not substituted for its final submission.

Each solver's initial prompt lacks the dataset name, source patient identifier,
melanoma, lymph-node and retroperitoneal case terms. Source IDs/references were not
found in tool requests. Live image/mount/network checks passed; captured proxy
connections allowed only `chatgpt.com:443`. These observations support the intended
isolation boundary; they do not rule out opaque prior training exposure.

Native token counters accumulate across model calls: Astra reported 2,999,112
input tokens (2,728,704 cached) and 23,587 output tokens; Sol reported 13,399,846
input tokens (13,133,312 cached) and 46,341 output tokens. These are neither unique
case-text lengths nor an estimate of actual account charges.

## Reading the endpoints separately

Detection uses one-to-one centroid-to-GT-mask matching, accepting a centroid inside
a GT region or within 3 mm of its voxel centers in physical space. Precision,
recall, F1 and TP/FP/FN are retained by visit; matching sensitivity at IoU 0.10,
0.25 and 0.50 is also retained. These are fixed exploratory rules, not a clinical
acceptance threshold.

Foreground Dice evaluates the union of lesion voxels. GT-macro instance Dice uses
best one-to-one mask assignments and gives missed GT instances zero. Their difference
shows why a large-region overlap score cannot stand in for finding and separating
all lesions. Localization-anchored and detected-only Dice remain separate fields.

Link scores compare cross-visit edges after localization-based ID matching.
End-to-end recall includes missed lesions; conditional link scores count only
GT edges whose endpoints were detected and report eligible/total GT denominators.
Exact event scores require the entire typed group to agree. If no whole GT event
group is detected, conditional event recall is not assessable; a numeric frozen
F1 with zero eligible groups must not be presented as a useful isolated event test.

## Instance convention remains under review

The source has four baseline and two follow-up instances: B1+B2+B4 merge into F4,
while B3 persists as F3. Baseline labels 1, 2 and 4 touch in the voxelized masks.
Our generic instruction says a confluent region is one instance. This can affect
how a model partitions the baseline mass and therefore the exact event it can
express. Connectivity alone does not establish radiologic confluence or invalidate
expert labels. See the [scoped review](../examples/longitudinal-ct-instance-boundary-review.md).

Both experiments carry that open review. Astra had already started before the
question surfaced; Sol runs the identical task with diagnostic origin because it
was known before Sol's dispatch. No task bytes or model outputs are altered, and
Sol receives no first-run findings or feedback. The original fine-instance scores
remain descriptive; do not use this case alone to claim isolated merging-reasoning
failure or a reference error.

## What to do next

Keep the user's image-only setting. Before another trial, clarify the generic
instance rule: distinguishable touching nodules may remain separate instances;
connected foreground alone is insufficient to declare merging. This supplies a
labeling convention without revealing any case-specific finding. Review the
selected reference partitions appropriately before using exact merge groups as
a decisive endpoint. A new task revision and new attempts are required for any
changed wording; this comparison stays frozen.

The next independent pair should probe smaller persistent/new lesions. The reviewed
lung-disappearance case still needs coverage adjudication; the defaced facial case
remains held out. One selected pair and one attempt per model provide no population
accuracy estimate or general model ranking. No additional trials are authorized
or launched by this recommendation.
