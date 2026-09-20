# Anatomy identity experiments — trace walkthroughs

> Retained trace walkthroughs. Current research lives in
> [Anatomy audit](../README.md). Local report links require
> retained artifacts; see [historical context](../../../docs/archive/README.md).

[Presentation and current verdict](br013-br017-summary.md) · [Offline visual report](../../../runs/anatomy-history-presentation/index.html)

High-level reconstruction from executed commands, returned images, public progress messages and final artifacts. Pseudocode summarizes observable work. Interpretations are hypotheses, not access to hidden reasoning.

Seven Sol/xhigh trials and one conditional Terra/max trial from BR-013/014/015. Images below are decoded from the exact returned payloads. The [trace index](../../../docs/evidence/anatomy-trace-index.json) records hashes and step anchors. No additional model trials were run for this retrospective.

## Shared approach

```text
Read vocabulary + spatial measurements
                  ↓
Identify obvious organs → isolate ambiguous groups
                  ↓
Inspect shape / neighborhood; optionally write numerical probes
                  ↓
Choose identities → validate JSON coverage and label constraints
```

The masks were provided. These are identity/audit tasks, not segmentation from raw CT. No specialist medical inference model or new training was invoked in the observed tools. A format check can pass even when the anatomical identities are wrong.

## BR-013 · A01 / Sol/xhigh — Ordinary anatomy

**Pass: 13/13. Position narrows the search; local views finish the assignment.**

Recognize all 13 ordinary abdominal structures from existing masks and physical coordinates. The answer is one label per object; CT is unavailable.

73.4 s · 5 images · 3 commands · 2,035 output tokens.

### Establish the scene

Read the vocabulary and helper-generated volumes, bounds and centroids; inspect the overview. The public assessment treats the large organs and long central vessels as well constrained. (Steps 7, 9, 10.)

### Isolate the ambiguous neighborhood

Generate four focused renderings: three angles on the central organs and a separate vascular/adrenal group. Identify a duodenal loop, the branching portal/splenic venous mask and pancreatic tissue anterior to it. (Steps 11, 12, 13.)

### Validate coverage

Write the 13 identities and check that every object appears once, each label is allowed and no label repeats. Independent grading confirms all 13 identities. (Steps 14, 15, 16.)

> the U-shaped inferior loop is duodenum, the thin branching transverse mask is the combined portal/splenic vein, and the compact elongated tissue just anterior to it is pancreas.

*Public message, step 13.*

```text
read vocabulary and object measurements
identify large organs and paired structures
render ambiguous groups from several angles
assign identities using shape and neighborhood
validate all 13 IDs and unique labels
```

**Interpretation.** A successful geometry-and-relationship workflow with little custom code. The ordinary scene does not support a difficult-task claim: the author’s simple geometry baselines also solved all 13 objects.

**Tool recovery.** No failed command was recorded.

[Actual returned image](../../../runs/anatomy-history-presentation/a01.png) · [Raw trajectory](../../../runs/br013-abdomen-a01-sol-xhigh-v1-20260915/abdomen-a01__mdEFsR5/agent/trajectory.json)

## BR-013 · A02 / Sol/xhigh — Atypical anonymous organs

**Miss: 9/11. Familiar silhouettes support a coherent but wrong assignment.**

The source scene has a compact 43.4 mL pancreas. Eleven objects must be assigned from 13 possible classes; unused classes are allowed. No mask voxels are altered and CT is unavailable.

157.6 s · 5 images · 7 commands · 5,015 output tokens.

### Concentrate on the central objects

Read physical measurements and view the overview plus four focused renderings. The public assessment identifies the venous tree and interprets the broad transverse mask as pancreas. That mask is actually the source duodenum. (Steps 7, 9, 10, 11, 12, 14.)

### Measure shape; leave the distance check unfinished

Compute principal axes and extents. Attempt nearest-surface distances with SciPy, but the import fails and no replacement distance calculation follows. Instead, print three binary-mask maximum projections as ASCII shapes. These collapse depth; they are not individual CT slices. (Steps 15, 16, 17.)

### Commit the wrong identity story

Call the compact o197 object gallbladder and o277 pancreas, then infer that duodenum and spleen are absent. Validate the schema successfully. Grading finds two wrong identities: the intact pancreas and duodenum. (Steps 18, 19, 20, 21.)

> that mask is a single obliquely elongated sac, while the neighboring mask has the transverse head-to-tail geometry of pancreas.

*Public message, step 18.*

```text
anchor obvious organs from geometry
interpret transverse object as pancreas
compute principal axes
attempt surface distances → missing SciPy; no fallback
inspect depth-collapsing mask projections
label compact pancreas as gallbladder → 9/11 correct
```

**Interpretation.** The visible failure combines silhouette-based interpretation, uncertainty about which classes are present and a self-chosen unfinished geometry check. Schema validity cannot validate the anatomical mapping. Later passes with exact inventory or CT weaken a broad anatomical-inability explanation.

**Tool recovery.** The session completed normally after the missing SciPy import, but the intended distance calculation was abandoned. No timeout or malformed-answer failure occurred.

[Actual returned image](../../../runs/anatomy-history-presentation/a02.png) · [Raw trajectory](../../../runs/br013-abdomen-a02-sol-xhigh-v1-20260915/abdomen-a02__zemQR6P/agent/trajectory.json)

## BR-013 · A02 / Terra/max — Terra on the same case

**Miss: 10/11. The duodenum is recovered, but the compact pancreas is still missed.**

One Terra/max trial was triggered after the Sol failure. It received the same task bytes and broad class vocabulary. This selected follow-up is not a model-ranking sample.

176.3 s · 12 images · 16 commands · 7,838 output tokens.

### Read the shared geometry

Inspect the overview, vocabulary and helper source, then read per-object measurements. Generate isolated renderings of all 11 objects. (Steps 7, 9, 10, 11, 12.)

### Inspect every object separately

View all 11 isolated images, including the true duodenum and compact pancreas. The final mapping gets the duodenum right but calls the compact pancreas gallbladder. The public assessment concludes that pancreas and spleen have no supplied masks. (Steps 13, 14, 15, 16.)

### Write a valid but partly wrong answer

Correct an answer-file patch mismatch, then validate object coverage, vocabulary and uniqueness. The source-key comparison yields 10/11: o197 is the sole identity error. (Steps 17, 18, 19, 20, 21.)

> the remaining unassigned labels are the spleen and pancreas, which have no supplied mask.

*Public message, step 16.*

```text
read object positions and class menu
render and view all objects individually
assign duodenum correctly
assign compact pancreas to gallbladder
validate complete mapping → 10/11 correct
```

**Interpretation.** The shared compact-pancreas confusion survives a different model and inspection strategy. It gives A02 more evidence than a solitary miss, but does not establish repeated Sol failure or prove that masks alone uniquely support the intended identity.

**Tool recovery.** No nonzero shell exit was recorded. An initial answer patch did not match the starter formatting; a corrected patch succeeded.

[Actual returned image](../../../runs/anatomy-history-presentation/terra.png) · [Raw trajectory](../../../runs/br013-abdomen-a02-terra-max-v1-20260915/abdomen-a02__JJc4VpZ/agent/trajectory.json)

## BR-013 · A03 / Sol/xhigh — Misleading proposed names

**Pass: 2 corrections; 0 false repairs. The agent overturns both supplied names using their relationship.**

Audit proposed identities on the same atypical geometry. The pancreas and duodenum names are exchanged; every voxel remains unchanged. Report corrections only.

88.8 s · 5 images · 6 commands · 2,306 output tokens.

### Check the proposed scene

Read the proposed assignments, vocabulary and measurements; view the overview. Narrow the audit to the central pancreas/duodenum/venous group after accepting the large-organ layout. (Steps 7, 9, 10.)

### Resolve enclosure and course

Generate front, side and oblique views of the central trio, plus an adrenal view. The public assessment identifies o277 as the C-loop and o197 as the enclosed pancreatic tissue. Both proposed names are rejected. (Steps 11, 12, 13.)

### Report only the swap

Recover from an answer-patch mismatch and unavailable xxd, then write the two corrections. Independent scoring confirms both and finds zero false repairs. (Steps 14, 15, 16, 17, 18, 19, 20.)

> `o277` forms the duodenal C-loop, while `o197` is the enclosed pancreatic tissue.

*Public message, step 13.*

```text
read proposed labels
focus on the central trio
match loop to duodenum and enclosed tissue to pancreas
replace the two wrong names
leave all other assignments unchanged
```

**Interpretation.** This is counterevidence to a simple anchoring story: the model can reject incorrect names. Proposed labels also expose the relevant category inventory, and the task changes from open recognition to correction, so the pass does not isolate a single naming effect.

**Tool recovery.** A formatting mismatch required a second answer patch. The missing xxd utility was replaced with od; final validation succeeded.

[Actual returned image](../../../runs/anatomy-history-presentation/a03.png) · [Raw trajectory](../../../runs/br013-abdomen-a03-sol-xhigh-v1-20260915/abdomen-a03__eywYzqa/agent/trajectory.json)

## BR-014 · I01 / Sol/xhigh — Exact class inventory

**Pass: 11/11. A smaller assignment space accompanies a clean recovery.**

Keep the A02 objects, IDs, renderings, loader and key unchanged. Supply exactly the 11 present class names instead of 13 possibilities. Each class must be used once.

75.6 s · 5 images · 10 commands · 2,602 output tokens.

### Read the constrained inventory

Read the 11-name vocabulary and physical measurements with the overview. Gallbladder and spleen are not candidate labels. The remaining uncertainty is concentrated in the compact central trio. (Steps 7, 9.)

### Use the local arrangement

Render the central trio at three angles and once with the major vessels. Publicly identify the branching venous mask, C-shaped duodenum and compact pancreas nestled inside the loop. (Steps 10, 11, 12.)

### Validate a full bijection

Write the mapping and require every object and every listed class exactly once. Recover an answer-file formatting mismatch. All 11 source identities are correct. (Steps 13, 14, 15, 16, 17, 18.)

> the C-shaped loop is the duodenum, and the compact tissue nestled within it is the pancreas.

*Public message, step 12.*

```text
read exact present-class inventory
resolve obvious organs
view ambiguous trio in vascular context
assign pancreas inside duodenal loop
check every object ↔ one distinct listed class
```

**Interpretation.** This is a narrow rescue of the earlier miss with unchanged geometry. Inventory uncertainty is a useful hypothesis; one new successful session does not prove a causal mechanism or reliable rescue rate. The exact-inventory version is retired as a hard Sol task.

**Tool recovery.** An answer-patch formatting mismatch was corrected. No failed shell command was recorded.

[Actual returned image](../../../runs/anatomy-history-presentation/inventory.png) · [Raw trajectory](../../../runs/br014-abdomen-i01-sol-xhigh-v1-20260915/abdomen-i01__ByXzTRu/agent/trajectory.json)

## BR-014 · F01 / Sol/xhigh — Fragmented pancreas and duodenum

**Pass: 15/15. Custom geometry helps group the pieces correctly.**

Split each ordinary-source pancreas and duodenum into two substantial fragments by removing a 6 mm central band. All fragments keep their physical coordinates. Name every retained object; reconstructing omitted tissue is not requested.

222.6 s · 11 images · 10 commands · 6,620 output tokens.

### View fragments and context

Read the exact class inventory and measurements, inspect the overview, then generate ten focused views. The pancreatic/duodenal region receives isolated and grouped views from different angles. (Steps 7, 8, 9, 10, 11, 12, 13, 14.)

### Recover a useful numerical check

After SciPy fails, implement chunked NumPy nearest-surface distances. Also map voxels to world coordinates and count pairwise overlaps. The measurements complicate nearest-neighbor grouping: some different-organ fragments are closer than the correct same-organ partners. (Steps 15, 16, 17, 18.)

### Combine anatomy with an exclusion heuristic

The public assessment groups o919/o475 as pancreas and o942/o165 as duodenum, using coherent shape and the overlap pattern to reject an alternative grouping. Write 15 assignments and validate coverage with repeated pancreas/duodenum names. All 15 are correct. (Steps 19, 20, 21, 22, 23.)

> Their overlap pattern also rules out treating all three lower masks as one organ.

*Public message, step 19.*

```text
inspect isolated fragments and neighboring organs
attempt nearest-surface distances → missing SciPy
compute chunked NumPy distance matrix
compute world-coordinate voxel intersections
combine shape and overlap exclusions to pair fragments
label all 15 objects, allowing repeated classes
```

**Interpretation.** This pass shows tool recovery and geometric evidence integration. Native cross-organ overlap became a useful exclusion clue, while artificial planar cuts may offer further shortcuts. It is not a pure test of anatomical knowledge. More fragments increased work in this observation but did not make a hard Sol case.

**Tool recovery.** The unavailable SciPy operation was replaced by working NumPy code. No unrecovered tool failure determined the outcome.

[Actual returned image](../../../runs/anatomy-history-presentation/fragments.png) · [Raw trajectory](../../../runs/br014-abdomen-f01-sol-xhigh-v1-20260915/abdomen-f01__9nEFduz/agent/trajectory.json)

## BR-015 · C01 / Sol/xhigh — Add the source CT

**Pass: 11/11. Tissue appearance and the surrounding loop support the correct identities.**

Retain all old A02 public members and the identity key; add original CT, previews and a reslicing helper. The vocabulary again permits absent classes.

136.2 s · 14 images · 10 commands · 5,150 output tokens.

### Inspect the new image evidence

Read geometry and view the 3-D and CT overviews, followed by eight per-object CT previews. The central pair, small glands and venous object get targeted attention. (Steps 7, 8, 10, 11.)

### Measure intensity and generate focused views

After a SciPy import fails, compute correctly registered CT intensity summaries with NumPy. The compact o197 object has median 65 HU and mean 62.5 HU. Generate three central 3-D views and an axial CT sheet. A coronal command fails argument parsing and is not rerun. (Steps 12, 13, 14, 15.)

### Assign the pair correctly

The public assessment identifies o277 as the duodenal sweep and o197 as solid pancreatic tissue inside it. Write and validate all 11 identities, leaving the two unused vocabulary names unassigned. (Steps 16, 17, 18, 19.)

> one object forms the C-shaped duodenal sweep (including its transverse segment), while the other is the solid pancreatic tissue inside that sweep.

*Public message, step 16.*

```text
view anonymous geometry plus source CT previews
map mask voxels into CT; summarize intensities
render central group and axial CT slices
identify solid tissue enclosed by the duodenal sweep
assign all 11 objects correctly
```

**Interpretation.** The pass is consistent with added image evidence resolving the mask-only ambiguity. CT arrived with previews, a helper and focus examples; these were not separated experimentally. The frozen failure is preserved, while this CT-supported condition is retired.

**Tool recovery.** The intensity computation succeeded without SciPy. The failed negative-position coronal command was left unrepeated; other returned views supported normal completion.

[Actual returned image](../../../runs/anatomy-history-presentation/ct.png) · [Raw trajectory](../../../runs/br015-abdomen-c01-sol-xhigh-v1-20260915/abdomen-c01__ytrARUt/agent/trajectory.json)

## BR-015 · V01 / Sol/xhigh — Eight abdominal veins

**Pass: 8/8. Ready previews are sufficient for the eight-way assignment.**

Name eight substantial source-labeled venous structures in a new patient, with surrounding veins and native venous-phase CT. All eight candidate names are supplied.

98.1 s · 10 images · 6 commands · 2,852 output tokens.

### Read the vocabulary and inspect every target

Read scene metadata and target IDs, view both overviews and all eight per-target CT previews. The public assessment separates major trunks from gastric tributaries. (Steps 7, 8, 9, 10, 11.)

### Use course and neighborhood

Read both helper sources and run their object-statistics function. Publicly map portal, splenic and mesenteric trunks, then identify the remaining routes by their relation to the stomach and splenic hilum. No new focused rendering, endpoint-distance or graph calculation is executed. (Steps 12, 13, 14.)

### Write the eight labels

Recover a starter-format patch mismatch and missing xxd. Validate all target IDs, eight distinct names and the exact schema. The final assignment scores 8/8. (Steps 15, 16, 17, 18, 19, 20.)

> The endpoint check is consistent: o185 is the portal trunk, o582 the superior mesenteric trunk, o597 the splenic trunk, and o425 the long left-sided inferior mesenteric tributary.

*Public message, step 14.*

```text
read exact vessel vocabulary and target list
view two overviews and eight target CT previews
read helper code and geometry statistics
assign names from anatomical course and neighborhood
validate eight unique IDs and eight unique names
```

**Interpretation.** The public phrase “endpoint check” records an assessment, not a measured endpoint algorithm. This pass demonstrates effective use of prepared views and named categories. A helper example grouped a relevant vessel neighborhood, providing a focus hint even though it was not executed.

**Tool recovery.** An initial answer patch missed the starter formatting. After unavailable xxd, the file was inspected with sed and the corrected patch validated successfully.

[Actual returned image](../../../runs/anatomy-history-presentation/veins.png) · [Raw trajectory](../../../runs/br015-abdomen-v01-sol-xhigh-v1-20260915/abdomen-v01__NKBATMu/agent/trajectory.json)

