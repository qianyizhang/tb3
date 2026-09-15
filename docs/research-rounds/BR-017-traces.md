# BR-017 — How Sol worked through each case

[Experiment summary](BR-017-results.md) · [Interactive presentation](../../runs/br017-absorption/review/index.html)

High-level reconstruction from completed commands, returned images, public progress messages and final answers. Stage summaries and pseudocode describe observable work, not hidden reasoning. Interpretations are explicitly separated from observations.

Generated from the [authored analysis](../../probes/revisions/br017/authoring/presentation.json). Step numbers refer to each frozen trajectory; the [trace index](../evidence/br017-trace-index.json) records paths and hashes.

## The shared workflow

The agent was supplied with existing segmentations, proposed organ names, physical coordinates, full CT and rendering helpers. It combined Python measurements with image inspection and anatomical assessments, then wrote a small JSON answer. No specialist medical inference model or new training was invoked in these traces. The source masks were already provided.

```text
Supplied masks + CT + proposed names
                ↓
Python measurements ⇄ targeted image sheets
                ↓
Anatomical assessment → further checks or revision
                ↓
Host + included organ + interior point (or empty list)
```

Measurements answer questions such as “is this connected?” or “is this subset larger than 5 mL?” They do not establish which organ owns the tissue. That judgment appears in the agent’s image-based assessments.

## M02 · Partial absorption · Miss

**Extensive inspection ends in a false negative.** 21.04 mL of source pancreas is reassigned to the duodenum mask. A 38.38 mL pancreatic remnant remains separately labeled. The CT is unchanged.

404 s · 27 images · 10,593 output tokens.

### Establish plausibility

Read the proposed labels and view the whole scene, then all 13 dedicated CT previews. The first public assessment is that the gross anatomy looks plausible. (Steps 7, 9, 10, 15, 16, 17.)

### Measure and inspect the relevant pair

Map cropped masks into CT coordinates; compute intensity distributions, volume, six-neighbor connected components and pairwise overlap. Request additional axial, coronal and sagittal sheets containing pancreas, duodenum and stomach. The enlarged duodenum remains one connected component. (Steps 18, 19, 20, 21, 23.)

### Accept the local appearance, expand the sweep

The public assessment accepts the pancreatic head-to-tail course as consistent with its label. Inspection then moves through liver, vessels, stomach, kidneys, spleen and adrenals. No included pancreatic region is reported. (Steps 24, 25, 26, 27, 28.)

### Write an empty answer

Explicitly conclude that no inclusion meets the 5 mL threshold, write an empty findings list and validate its format. The grader fails detection; point localization is never reached. (Steps 30, 31, 32, 33.)

> So far, the gallbladder’s low attenuation and the pancreas’ head-to-tail course are consistent with their labels; neither is an obvious mixed-organ error.

*Public message, step 24.*

```text
read labels; view overview and every target
measure volume, components, CT intensity, overlap
view pancreas + duodenum in three planes
record local appearance as plausible
inspect the remaining anatomy
write findings = []  # false negative
```

**Interpretation.** The trace is consistent with accepting plausible labels without resolving the ownership error at their interface. It does not support an explanation based on never viewing the affected organs: all three CT planes were inspected. A single run cannot identify the internal cause of the miss.

**Tool recovery.** Recovered from missing SciPy and an attempt to index full CT with a cropped mask. Subsequent calculations used NumPy/Python and coordinate transforms.

[Actual returned image sheet](../../runs/br017-absorption/review/trace-m02.png) · [Raw trajectory](../../runs/br017-abdomen-m02-sol-xhigh-v1-20260915/abdomen-m02__YQZJHca/agent/trajectory.json)

Final answer:

```json
{
  "findings": []
}
```

## M01 · Whole absorption · Pass

**A missing label prompts an anatomical search.** The separate pancreas mask is removed and its tissue is incorporated into duodenum: 59.35 mL newly added. Both the missing-class clue and the larger abnormal extent differ from M02.

349 s · 26 images · 15,102 output tokens.

### Generate leads

Notice the absent pancreas label and an unusual upper aortic loop. Explicitly treat absence as a reason to search neighboring masks, rather than a finding by itself. Review every target preview and screen geometry and CT intensity. (Steps 9, 10, 12, 13, 14, 15, 16, 17.)

### Identify two anatomies in one mask

Targeted CT sheets show an upper part of o327 following the pancreatic gland while the lower duodenal C-loop remains. The public report identifies this as the inclusion. Later views compare the suspect tissue with stomach and splenic-vein context. (Steps 20, 21, 24, 26, 27, 30.)

### Quantify a substantial region

Count mask voxels in selected physical-coordinate regions. For example, the subset at z ≥ 357 mm and x ≥ 5 mm contains 13.932 mL. This measures the selected mask region; interpreting it as pancreas still depends on the anatomical review. (Steps 25, 28, 29, 30.)

### Choose and validate a witness

Use erosion and local CT statistics to select a point inside the suspected gland. Check mask membership, CT coordinates and JSON format. Return one pancreas-in-duodenum finding, with no extras; the reference accepts the point. (Steps 28, 31, 32, 33, 34.)

> The duodenum host is a confirmed concern: its superior component follows the solid pancreatic gland across several slices, while its inferior C-shaped bowel remains present.

*Public message, step 21.*

```text
notice pancreas absent → search adjacent hosts
trace o327 through CT slices
identify pancreatic gland plus duodenal loop
measure a substantial suspect subset
check other masks for additional findings
select interior point; write one finding
```

**Interpretation.** This pass combines a useful search cue, relative anatomical position and continuity across slices, followed by numerical localization. It is not a label-count-only solution. The comparison cannot separate the effect of an absent class from the effect of a larger, more recognizable inclusion.

**Tool recovery.** Recovered from unavailable ImageMagick and SciPy. Used the ready images, supplied rendering helper and NumPy/Python geometry instead.

[Actual returned image sheet](../../runs/br017-absorption/review/trace-m01.png) · [Raw trajectory](../../runs/br017-abdomen-m01-sol-xhigh-v1-20260915/abdomen-m01__jmaLeZe/agent/trajectory.json)

Final answer:

```json
{
  "findings": [
    {
      "object_id": "o327",
      "included_label": "pancreas",
      "point_lps_mm": [
        23.611,
        -195.389,
        369.7
      ]
    }
  ]
}
```

## N01 · Unchanged control · Pass

**Two asserted errors are withdrawn after further checks.** Original source masks are retained. The correct output is an explicit empty findings list. This tests false alarms under the same broad audit instructions.

453 s · 31 images · 11,864 output tokens.

### Investigate unusual appearances

Review all target previews, then additional pancreas, gallbladder, stomach and liver sheets. Compute connected components and spatial summaries. The pancreas/duodenum pair and large vessels initially attract attention. (Steps 9, 11, 12, 13, 14, 20, 22, 24.)

### Assert two provisional errors

A public progress message states that the pancreas includes duodenum and the gallbladder follows liver tissue. These claims would be false positives against this unchanged-source key. They are not the final answer. (Steps 25.)

### Gather counterevidence

Measure CT intensity in correctly registered masks and along their slice-wise course; view pancreas and duodenum together in all three planes; compute cross-mask face adjacency. Gallbladder mean intensity is 9.9 HU versus liver 56.9 HU. These are supporting measurements, not an anatomical classifier by themselves. (Steps 26, 27, 28, 29, 30.)

### Revise and clear the case

Finish the vessel and solid-organ sweep. The final public assessment says the suspicious gastrointestinal shapes resolve as normal adjacent structures. Write and validate an empty findings list. Both earlier claims are absent from the final answer. (Steps 31, 32, 33, 34, 35, 37, 38, 39.)

> The initially suspicious gastrointestinal shapes resolve as normal adjacent structures in multiplanar views; I’m finalizing the decision file now.

*Public message, step 35.*

```text
inspect unusual geometry
provisionally assert pancreas/duodenum and liver/gallbladder errors
measure CT intensity; inspect paired planes and adjacency
finish the remaining-organ sweep
revise the assessment to normal neighboring anatomy
write findings = []  # correct negative
```

**Interpretation.** The successful negative result came after a visible revision, not uniform confidence throughout. Additional checks preceded that revision, but the public record does not specify which single observation caused it. This was the longest run and returned the most images; more work did not mean a harder positive case.

**Tool recovery.** Recovered from missing SciPy and incompatible cropped-mask shapes; subsequent calculations aligned masks in the common physical/grid coordinate system.

[Actual returned image sheet](../../runs/br017-absorption/review/trace-n01.png) · [Raw trajectory](../../runs/br017-abdomen-n01-sol-xhigh-v1-20260915/abdomen-n01__aTnyAWY/agent/trajectory.json)

Final answer:

```json
{
  "findings": []
}
```

## F01 · Focused partial audit · Pass

**Plausible whole organs trigger a closer interface check.** Every M02 image, mask, CT sample, helper and reference-key byte is retained. The prompt narrows the audit to o327 (duodenum) and o589 (pancreas); other anatomy remains context. This follow-up was declared after the initial positive-case results.

351 s · 17 images · 12,009 output tokens.

### Examine the two targets together

Read the metadata and four ready previews. Compute target components and overlaps, then request three-plane CT sheets and four rotated 3-D views. The early public assessment still calls the large-scale shapes coherent. (Steps 7, 9, 10, 12, 13, 15, 16, 17, 18, 19.)

### Continue past global plausibility

Explicitly inspect the shared interface at finer spacing. Render each mask separately at 4.5 mm axial steps, inspect all-mask context, tabulate 2-D components slice by slice, and request tighter three-plane interface views. (Steps 19, 20, 21, 22, 23, 24, 25.)

### Localize the wrongly assigned gland

The final public finding identifies pancreatic head/uncinate tissue inside o327 while accepting the remaining o589 tissue as pancreas. Count selected suspect regions, including a central upper subset of 9.993 mL; use erosion depth to choose an interior voxel. (Steps 26, 27, 28.)

### Verify the point and return one finding

Check that the selected point lies inside o327 and outside o589, and map it to a CT voxel. Return [-22.9, -199.9, 324.7] LPS mm. Independent scoring places it 0.016 mm from an included source voxel centre. (Steps 29, 30, 31, 32.)

> I’m now checking their shared interface at finer slice spacing, where a ≥5 mL exchanged chunk would be most likely to hide.

*Public message, step 19.*

```text
inspect the target pair and surrounding anatomy
record plausible global shapes
zoom to the shared interface anyway
trace separate contours and slice-wise components
identify pancreatic tissue inside the duodenum mask
measure candidate region; choose deep voxel; write finding
```

**Interpretation.** The observable distinction is continued inspection of tissue ownership after the overall shapes looked plausible. This weakens a claim of general inability to recognize the anatomy. Scope provides a localization hint, and fresh-run variation remains possible; the contrast does not prove an attention mechanism.

**Tool recovery.** Recovered from missing SciPy by implementing connected-component and erosion operations with NumPy/Python.

[Actual returned image sheet](../../runs/br017-absorption/review/trace-f01.png) · [Raw trajectory](../../runs/br017-abdomen-f01-sol-xhigh-v1-20260915/abdomen-f01__dmBoEbU/agent/trajectory.json)

Final answer:

```json
{
  "findings": [
    {
      "object_id": "o327",
      "included_label": "pancreas",
      "point_lps_mm": [
        -22.9,
        -199.9,
        324.7
      ]
    }
  ]
}
```
