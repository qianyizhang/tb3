Extract and anatomically label all clinically relevant vessels you can identify in the CTA at `/app/data/image.nii.gz`, including coronary arteries and other visible major arteries and veins. Discover their locations, connections and courses from the image alone. No mask, seed, landmark, centerline, target branch or patient-specific presence list is provided. Work within the actual field of view; vessels may end at the scan boundary. This is exploratory image geometry, not diagnosis.

OBJECTIVE AND PRIORITIZATION

Produce image-supported vessel courses with accurate anatomical names and as complete a visible vessel inventory as possible within the scope below. First reconstruct both coronary arterial trees, including visible side branches regardless of whether they have a dedicated benchmark category. Then cover the major noncoronary arterial and venous trunks and their major named branches within the scan. A long, accurately traced main vessel does not substitute for discovering its side branches.

Exhaustive tracing of fine peripheral pulmonary arborization, tiny unnamed tributaries and terminal twigs is not required. Record conspicuous unresolved candidates in the inventory. These omissions define the workload boundary; they do not establish that those vessels are clinically irrelevant. The benchmark vocabulary is an output coding system, not a patient-specific presence list or a limit on discovery.

Use your preferred extraction method. Organize your review around three separate questions:
1. Discovery: Which vessels and branch connections are visible?
2. Geometry: Does each submitted course continuously follow the central lumen?
3. Identity: Do its anatomical name and benchmark label agree with its origin, parent vessel and course?

Revisit earlier decisions when later tracing reveals an inconsistent connection or branch identity. Do not assume that a plausible shortest path, bright structure or smooth curve establishes vessel identity.

ANATOMICAL NAMES AND BENCHMARK LABELS

Every submitted polyline needs a specific anatomical `vessel_name`. The integer `labels` field is a separate mapping to this benchmark vocabulary:

1 LM — left main
2 LAD — left anterior descending
3 LCx — left circumflex
4 D1 — first diagonal
5 D2 — second diagonal
6 OM1 — first obtuse marginal
7 OM2 — second obtuse marginal
8 IM — ramus intermedius
9 RCA — right coronary artery
10 R-PDA — right posterior descending
11 R-PLA — right posterolateral
12 L-PDA — left posterior descending
13 L-PLA — left posterolateral
14 Other — additional diagonal or obtuse marginal branches

Label 14 is NOT a catch-all for every other coronary artery. Use label 0 for vessels outside the listed categories, including coronary branches outside this taxonomy as well as noncoronary arteries and veins. Retain their specific anatomical names. Such vessels remain part of the requested output and human review.

Assign branch numbers from anatomical branch order along the parent vessel, not the order in which your algorithm discovers them. Before assigning a first or second branch, inspect the upstream parent course for earlier branches. Do not infer absence merely because a branch was not extracted.

The vocabulary defines anatomical categories, not a checklist of individual vessels. A category may be absent or represented by multiple distinct courses. Do not assume one polyline per category.

A geometric bifurcation does not by itself establish a change of anatomical category. Determine continuation and branch identity from origin, parent connection, anatomical course and supplied territory, not size or path continuity alone. Split geometry where useful while retaining the appropriate category.

Multiple courses may share a category when each independently satisfies its anatomical definition. Conversely, attachment to a named vessel alone does not make every daughter part of that category. Use label 0 for a genuinely out-of-vocabulary vessel, preserving its specific anatomical name. Record uncertain segment boundaries rather than treating your chosen boundary as certain.

Not every category is necessarily present. Do not invent vessels to fill the vocabulary. For ambiguous identity, submit one best-supported label and describe the alternative, parent connection and decisive image evidence in `method.md`. Do not duplicate the same geometry under several alternative labels. Do not use label 0 merely to avoid committing to a difficult in-vocabulary assignment.

COMPLETENESS AND IMAGE-SUPPORT REVIEW

Before submission, review both coronary trees systematically from their origins through their visible bifurcations and distal courses. Check whether any visible side branch was skipped, merged into its parent, given an inconsistent name or omitted after an early failed extraction.

For uncertain courses, inspect consecutive native slices or complementary views rather than relying on a single projection. Check for transitions into adjacent vessels, chambers, myocardium or lung. Retain image-supported distal continuation even when its endpoint is uncertain; do not extend a vessel simply to increase output length.

In the vessel inventory, distinguish:
- traced;
- visible or suspected but not confidently traced;
- identity or extent uncertain.

An untraced or unrecognized vessel is not established to be anatomically absent. Keep this review concise and within the available task allowance of 7200 seconds (two hours).

TIME MANAGEMENT AND SUBMISSION

You have 120 minutes, including computation, inspection and reporting. Save a valid preliminary submission and concise method/inventory by the midpoint (60 minutes), then update them incrementally. This checkpoint is a deliverable requirement, not evidence that reconstruction is complete.

Reserve approximately the final 10 minutes for checking coordinates, continuity, duplicate trunks, anatomical assignments and output validity. During this period, prioritize completing and documenting existing work over beginning another vessel family or optional visualization.

An incomplete but valid, clearly documented reconstruction is preferable to leaving required outputs unfinished. Record remaining candidates and uncertainties rather than silently omitting them.

OUTPUT

Write `/app/answer/centerlines.json` as:
{"centerlines": [{"id": "unique name", "vessel_name": "anatomical name", "points_ras_mm": [[x,y,z],...], "labels": [integer,...]}, ...]}

Provide one integer label per point. Split at bifurcations when practical; coronary labels may change along a polyline. Export continuous central lumen courses without repeatedly exporting shared trunks. Each polyline must contain 2–20000 finite points with nonzero steps <=1.5 mm; approximately 0.5 mm spacing is preferred. Submit at most 200 polylines.

Coordinates are RAS millimeters, using the NIfTI affine on zero-based XYZ voxel indices. The image retains native HU values and its original field of view.

Write `method.md` with your vessel inventory, anatomical connections supporting the assignments, uncertain identities and boundaries, untraced candidates, method, external assistance and compute used. Save executable extraction code in the answer directory. Optional segmentation and figures are welcome; CPR and mesh are not required.

EVALUATION

Ground truth is available only for annotated coronary centerlines. Geometry and anatomical labeling are evaluated separately against this reference.

Geometry coverage measures reference centerline recovered within 1 mm, ignoring submitted labels. Correctly labeled coverage additionally requires the geometrically matched submitted course to carry the reference category. A fixed label-independent nearest-geometry correspondence is used for both; labels cannot change which course is matched. All submitted courses, including label 0, are candidates for geometry matching. Missing geometry and incorrect labels remain distinguishable.

Report both coverages per reference category, as an equal-category mean, and as an overall reference-length-weighted mean. Report separate geometry-coverage and correctly-labeled-coverage pass decisions: each requires an equal-category mean >=90% and every present reference category >=80%, within 1 mm. Each present category contributes equally, including small branches. Also report coverage at 2 mm, and label accuracy conditional on geometrically matched reference length.

Evaluation uses arc-length-weighted samples of line segments at intervals no larger than 0.25 mm. For a segment whose endpoint labels differ, the label changes at its midpoint. Equal-distance matches use a deterministic rule independent of the labels. These numerical conventions do not supply anatomical landmarks or segment boundaries.

Extensions beyond annotation endpoints do not automatically fail. Reference agreement of submitted length and unmatched length are review diagnostics; there is no precision, endpoint or length-ratio pass gate. Portions of vessels without reference annotations are not automatically false positives and will be visualized on the source CTA for human inspection. Their anatomical names are not independently validated by benchmark category agreement.

Broader vessel reconstruction is also an explicit review outcome: image support, anatomical connections, names and useful visible extent will be inspected on the source CTA. Completion, reproducibility and uncertainty reporting are assessed separately from coronary reference coverage. There is no exhaustive ground-truth completeness score for the broader vessel inventory.

Coverage alone cannot establish central-lumen accuracy, correct connections or clinical completeness. Submit image-supported courses rather than unsupported paths designed to satisfy the coverage metric. No reference annotations will be available to you for validation.

TOOLS AND SOURCE RESTRICTIONS

NumPy, SciPy, nibabel, Pillow, scikit-image and trimesh are installed. Use ordinary tools and general methods. Do not retrieve this case's annotations, masks, centerlines or previous solutions, or use pretrained coronary weights with unknown training overlap. See `/app/SOURCE_NOTICE.md`. No previous answers or case-specific feedback are supplied.
