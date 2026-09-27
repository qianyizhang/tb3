# Locate named anatomy and detect unavailable targets

Find named landmarks in native CT or MRI, return physical locations under the
specified coordinate contract, and distinguish visible, outside-scan and absent
targets. A supplied name is not a supplied location.

## Value

Separates anatomical localization from availability judgments. A point on a real
vertebra can have the wrong level name; avoiding outside-scan detections can still
miss a visible vertebra. These selected exploratory cases do not establish clinical
or population performance.

## Given

### Original data

Three source subjects under four historical protocols: PDDCA 1.4.1 head/neck CT
0522c0001, AFIDs SNSX T1 MRI sub-C001 from OpenNeuro ds004470, and VerSe sub-verse823
CT. Full and cropped conditions reuse their subject's native pixels; they are not
independent patients. Inputs are volumes, not the reference-centred teaching panels.

PDDCA is 512×512×107 at approximately 1.12×1.12×3 mm, with positive native axes L/P/S.
AFIDs is 224×342×342 at approximately 0.700×0.702×0.702 mm, with R/A/S axes. VerSe is
512×512×1214 at 0.71875×0.71875×0.700012 mm, with L/A/S axes. NIfTI affines map native
indices to RAS millimetres; RAS orientation does not imply MNI/template alignment.

### Supplied helpers

All conditions supply target names and semantic definitions. BR-036 supplies
NIfTI and requests RAS world coordinates. BR-038/039/040 additionally supply an
intensity-identical native `volume.npy`, geometry JSON, and public slice/point
inspection helpers; they request zero-based `[i,j,k]`. These helpers do not supply
target detections. A requested cyan crosshair is an inspection location.

BR-040 MRI used permitted generic AFIDs/MNI atlas assistance: an affine proposal
followed by manual review. This is not unaided localization. No retained evidence
shows retrieval of the target subject's private labels. The exact runtime atlas
image bytes are missing locally; the retained archive contains an annex pointer,
not that image. Its assistance cannot be reconstructed as an audited intermediate.

### Callable tools

Image rendering, array processing and ordinary code tools are allowed in the
frozen container. General anatomical references and software were permitted;
target-subject annotations and prior solutions were forbidden. Each protocol
retains its precise network and execution contract. BR-036 used a 30-minute limit;
BR-038/039/040 used 60 minutes with two CPUs and 4 GiB. No new execution is implied.

### Reference-only material

Private PDDCA manually placed bone points, AFIDs three-rater consensus fiducials,
and VerSe centroids/availability labels are used only for evaluation and explicit
reader reveals. VerSe C1 denotes the ring centre; other levels denote body centres,
not the centroid of the complete vertebral mask. Reference-centred panels and
diagnostic segmentation masks are not solver inputs. The source supplement records
24 presacral vertebrae for subject 823; T13/L6 absence follows that source convention,
not missing centroid rows alone. Variant numbering remains untested here.

## Task specification

Inspect the volume, identify each named target and return every required key.
Preserve the native coordinate system and the condition's exact unavailable-target
semantics. Fractional voxel coordinates are valid; screenshot pixels are not voxel
coordinates. World conversion is `p_RAS = A × [i,j,k,1]`.

For BR-039/040, choose `observed`, `out_of_fov`, `absent` or `uncertain`. An observed
point must lie in the scan. `absent` and `uncertain` require null coordinates. An
explicit outside estimate must actually be outside. Uncertainty avoids inventing a
detection but does not earn a correct absent/outside decision.

## Expected output

BR-036: each required name mapped to an RAS-millimetre triple; crop tasks also accept
null/empty responses for outside targets. An explicit outside estimate must be
outside the actual voxel-cell FOV and within the separate 10 mm hidden-reference
tolerance. BR-038: `space: voxel_ijk_zero_based` and a complete finite `landmarks`
map. BR-039/040: the same declared voxel space with a complete name-to-status/point
map. The frozen instructions own JSON spelling and validation; formats must not be
interchanged across rounds.

## Evaluation

**Physical location.** Compute `||A[:3,:3] × (prediction_ijk − reference_ijk)||` in
millimetres. Native voxel centres span indices 0 through shape−1; the voxel-cell
FOV extends half a voxel beyond the centres. BR-036/038 use 5 mm for CT and 3 mm for
MRI. BR-039/040 CT reports 5/10/20 mm endpoints; MRI also reports 3/5/10 mm.

**Denominators.** Localization fractions use all visible targets, including omitted
ones. Mean error uses only returned visible points and must show that denominator.
Report false observed claims on outside targets separately from absent targets,
correct rejection and visible-target misses. Frozen all-correct rewards require
every specified endpoint; they are not clinical readiness scores.

**Retained observations.** BR-040 and its matched task predecessors have these
saved results; each cell represents one attempt at that condition:

| Condition | Terra/high | Sol/xhigh |
| --- | --- | --- |
| Full VerSe CT, within 5/10/20 mm | 2/24; 7/24; 9/24 | 1/24; 13/24; 23/24 |
| Partial VerSe CT, within 5/10/20 mm | 1/13; 2/13; 5/13 | 4/13; 8/13; 12/13 |
| Partial CT false observed outside | 1/11 (T4) | 0/11; visible T5 missed |
| Partial CT false observed absent | 0/2 | 0/2; T13 uncertain, L6 absent |
| Full MRI, within 3/5/10 mm | 3/32; 8/32; 20/32 | 14/32; 23/32; 32/32 |

Sol's partial CT mean of 7.44 mm is over **12 returned visible points**, while its
4/13 within-5-mm fraction includes missed T5. Terra's T4-labelled point lies 2.14 mm
from the source T5 centre: a wrong-level claim on real bone. Full CT mean error
improves from 24.77 to 10.24 mm although the within-5-mm count falls. MRI mean falls
from 9.40 to 3.87 mm with atlas assistance; the anterior commissure is a local
counterexample to aggregate improvement. MRI has no unavailable-target test.

**Earlier conditions.** BR-036 full CT has 1/4 within 5 mm and full MRI 0/8 within
3 mm. Its CT crop accepts 2/4 responses, both outside-target nulls; neither of its
two visible targets is localized within tolerance. Its MRI crop accepts 0/32 and
handles 0/7 outside targets correctly. BR-038 PDDCA CT localizes 2/4 within 5 mm;
the two condyle errors are 32.07 and 35.15 mm. Representation, helpers and MRI query
inventory changed between BR-036 and BR-038, so this is not a controlled causal
test of coordinate guidance.

**Reference limits and replay.** The source audit verifies all eight unique frozen
input volumes, native affines, reference coordinates and 30 saved score records.
Regrading stored outputs is not fresh inference. Source rater maxima around the
AFIDs consensus exceed 3 mm at IDs 22 (3.59 mm) and 27 (3.14 mm); this contextualizes
the tolerance without changing the original references or scores. Native-coordinate
consistency does not rule out a local axis mistake or wrong-structure selection by
an agent. The complete runtime atlas image remains a recovery gap.

## Conditions

| Condition | Given and remaining work |
| --- | --- |
| BR-036 full/crop | World RAS output; four PDDCA points or eight full MRI points; MRI crop expands to all 32. CT native k=68:107 removes chin/dens; MRI k=145:342 removes seven fiducials. Locate visible targets and handle the separate outside contract. |
| BR-038 complete volumes | Same PDDCA subject, all 32 MRI targets; native NPY/geometry/helper assistance and voxel output. Both cases are entirely visible. |
| BR-039 complete/partial VerSe | 26 requested names C1–C7, T1–T13, L1–L6. Full: 24 visible, zero outside, two absent. Native k=0:920 crop: 13 visible, 11 outside, two absent; cranial counting anchors are removed. |
| BR-040 matched inputs | Exactly the BR-039 CT and BR-038 MRI task bytes; model and effort both change to Sol/xhigh. MRI additionally uses generic atlas assistance in its saved method. |

## Difficulty

Names require anatomical search and numbering in three dimensions. Projection can
make an incorrect point appear close in one plane while it is far away in depth.
Cropped scans remove counting anchors. A source-confirmed absent level, a target
outside the acquisition, a visible miss and a wrong-level point require distinct
judgments. Local success and qualified partial improvement remain informative.

## Coverage

Four experiments retain **11 fresh model attempts**: eight Terra/high and three
Sol/xhigh, plus 16 distinct oracle/no-op control executions. Thirty stored score
records include three repeated records of earlier attempts; they are not 30 model
trials. BR-040 provides a 71-file reproduction manifest. Earlier frozen tasks and
raw outputs remain available locally. Model, effort and selected methods vary;
there is one attempt per condition and no population, causal or clinical claim.

MedPelvis was excluded before these CT trials because its documented coordinate
mapping failed anatomical overlays. That source-screen exclusion is not a model
failure. The rejected source, current reviewed datasets and atlas recovery gap
remain separate provenance records.

## Sources

- [BR-036 protocol](../../experiments/br036/protocol.md)
- [BR-038 protocol](../../experiments/br038/protocol.md)
- [BR-039 protocol](../../experiments/br039/protocol.md)
- [BR-040 protocol](../../experiments/br040/protocol.md)
- [Availability and localization finding](../../findings/landmarks-availability-and-localization.json)
- [Named-landmark source audit](../sources/named-landmark-audit.json)
- [Verified source terms and AFIDs CC0 correction](../sources/named-landmark-source-terms.json)
- [Retained panel provenance](../sources/landmark-provenance.json)
- [Variant-numbering idea and reopening conditions](../../ideas/variant-vertebral-numbering.md)
