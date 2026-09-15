# BR-015 results — CT and vessel identity both pass

**No new hard Sol case was established.** Adding source CT resolved the earlier
atypical-organ miss. A new specialist-labeled abdominal vessel case also passed.
Both conditions are retired. The [cross-round presentation](../anatomy-experiments.md)
includes their trace walkthroughs and the current candidate verdict.

[Declared protocol](BR-015-clinical-evidence.md) ·
[Measured results](../evidence/br015-results.json) ·
[Authored review and source checks](../evidence/br015-reviews.json) ·
[Authoring and reproduction](../../probes/revisions/br015/authoring/README.md)

## One attempt per task

| Sol/xhigh condition | Exact result | Agent seconds | Total trial seconds | Output tokens |
| --- | --- | ---: | ---: | ---: |
| C01: BR013-A02's 11 objects / 13 possible classes, plus original CT | Pass, 11/11 | 136.16 | 192.75 | 5,150 |
| V01: eight intact venous structures, surrounding veins and same-phase CT | Pass, 8/8 | 98.12 | 156.96 | 2,852 |

| Condition | Input tokens | Included cached input | Included reasoning output | Estimated cost |
| --- | ---: | ---: | ---: | ---: |
| C01 | 289,818 | 258,304 | 3,201 | $0.332 |
| V01 | 327,531 | 299,904 | 1,362 | $0.288 |

Total new model use: 234.29 agent seconds, 617,349 input tokens including 558,208
cached, and 8,002 output tokens including 4,563 reasoning tokens. Input includes
repeated context. Cost is a Harbor estimate, approximately $0.620 combined,
not an invoice. Neither trial retried. Both retained the 1,800-second,
four-CPU/4-GiB allowance; actual peak CPU/RAM was not measured.

Two oracle controls passed and two empty-answer controls failed as expected.
Task checksums match within each three-run group. Runtime records establish
Sol/xhigh, Codex 0.154.0, one fresh session per model task and the exact frozen
instruction. Scorer replay and an independent exact-set comparison agree.
Answer scoring took 0.50 ms and 1.67 ms respectively. These are diagnostic
single attempts, not estimates of a population success rate.

## What the task evidence establishes

**C01 preserves the prior problem and adds evidence.** Every old public member
and the identity key are byte-identical to BR013-A02. All original CT samples
are retained with their physical-coordinate transform. Sol inspected focused
central-organ views, CT slices, statistics and HU samples; it correctly assigned
both the compact pancreas and its surrounding duodenum. It recovered from an
unavailable SciPy import. One negative-coordinate coronal command failed because
of the helper's argument parsing; `--positions=-195,-185` works. The frozen
helper remains unchanged and the issue did not prevent completion.

The historical mask-only A02 yielded 9/11 for Sol and 10/11 for Terra. An exact
present-class inventory subsequently yielded 11/11 for Sol in BR014-I01. C01
restores the broader class vocabulary and also passes with CT. These observations
make inventory/evidence uncertainty more plausible than a broad anatomical-prior
deficit. They do not isolate CT from the supplied previews and focus examples,
or establish a causal effect from one attempt.

**V01 uses real intact vessel masks.** The first patient in the inspected
ColonVessels archive, pat_016, had named multilayer segmentations. Eight substantial
venous structures were selected before model results: portal, splenic, superior
and inferior mesenteric, left gastric, right gastro-omental, short gastric veins,
and a source-named connecting vessel. Volumes span 1.89–26.90 mL and maximum axis
extents 57.4–219.1 mm. Exact terminology and an eight-name inventory were supplied.
The connecting-vessel name describes its course; no rare disease was asserted.

The [dataset](https://zenodo.org/records/17407158) is CC BY 4.0. Its
[data paper](https://doi.org/10.1038/s41597-026-07303-2) describes surgeon-authored
annotations verified by a senior colorectal surgeon. Arterial and venous phases
are not registered, so V01 uses only the native venous phase. Existing Slicer
in-progress tags are retained as a source-review caveat. The publication
supports source identities, not independent success on our anonymous packet.

Only selected ZIP members were fetched, with range-size and ZIP CRC checks;
the 24.6 GB archive was not downloaded. The author screen retained 28 nonempty
arterial and 24 nonempty venous sublabels from one patient; the empty Henle-trunk
label was excluded. Source mask voxels, overlaps and native coordinates remain
intact. CT was cropped to the supplied venous extent plus 20 mm without
resampling. Independent post-trial comparisons cover all eight targets, the
surrounding-vein context and every CT sample in the crop. They verify decoding
against the compressed NRRD source, not just a builder-generated reference.

**Sol used the ready images effectively.** It viewed the two overviews and all
eight per-target CT previews, read both helper sources and object statistics,
then assigned all identities correctly. No new focused render, reslice,
endpoint-distance calculation or graph metric was executed. Its public mention
of an endpoint check is therefore not evidence of a measured connectivity
analysis. A patch mismatch and missing `xxd` command were recovered. No private
key access or external patient matching was observed.

A public example groups the connecting vessel with its two neighboring routes.
Although it supplies no class mapping and Sol did not execute it, this is a
focus hint. No full learned geometric or graph baseline was tested. The pass
supports successful solving of this scaffolded condition, not unaided discovery
or clinical competence.

## Current disposition

Both conditions pass and are retired as difficult Sol tasks. C01 resolves the
compact-pancreas miss with additional CT evidence; V01 succeeds using prepared
views without a new endpoint or graph calculation. See the
[per-trial trace analysis](../anatomy-traces.md).

BR-017 subsequently tested substantial tissue absorbed into a neighboring mask.
Its broad partial-absorption miss is the current primary lead. Original A02
remains a secondary identity diagnostic; the [current verdict](../anatomy-experiments.md)
accounts for all completed contextual follow-ups.

Historical source leads were [postoperative pancreas segmentation](https://pubmed.ncbi.nlm.nih.gov/41307673/)
and a [multi-reader pancreas study](https://pmc.ncbi.nlm.nih.gov/articles/PMC12701807/).
Full case-level inputs were not obtained from those leads, and neither produced
a task or Sol/Terra trial in this round. Their published results concern other
segmentation models.

Source-label identity is graded here. Clinical cause, contour quality and
clinical performance were not established. The original source receipts,
answer-free viewer, freezes and raw outcomes remain retained; no further trial
is queued by this retrospective.
