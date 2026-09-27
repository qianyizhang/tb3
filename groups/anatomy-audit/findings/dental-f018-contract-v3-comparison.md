# F018 v3: annotated-reference comparison

Both user-authorized fresh Astra-medium attempts completed normally with valid
outputs, unchanged frozen tasks, exact independent scoring replay and no observed
forbidden data access. Original macro Dice was 0.71084 without an example and
0.82395 with the original F008 CT/annotation. One repeated development-case pair
supports descriptive findings, not a population effect or an isolated estimate of
the instruction revision's benefit.

Source: codex://threads/01a0c3e5-6fb0-7321-a930-a7251047e7ad.
[Fixed protocol and fairness decisions](../methods/dental-f018-contract-v3/README.md),
[common instructions](../methods/dental-f018-contract-v3/instruction.md), and
[dataset-contract caveats](dental-dataset-contract-audit.md).
Original target/GT and scoring formulas remain unchanged. No extra tools, weights,
retries, extensions, or feedback were supplied. Both controls passed before inference.

| Measure | No example | F008 example |
|---|---:|---:|
| Overall macro Dice | 0.71084 | 0.82395 |
| Whole-tooth matched geometry Dice | 0.78523 | 0.92613 |
| Correctly identified detected GT teeth | 29/29 | 29/29 |
| Tooth-tissue macro Dice | 0.77406 | 0.91771 |
| Pulp macro Dice | 0.69887 | 0.80387 |
| Main-canal macro Dice | 0.36062 | 0.47882 |
| Small-canal macro Dice | 0.14324 | 0.18527 |
| Jawbone macro Dice | 0.83329 | 0.85835 |
| Sinus macro Dice | 0.92042 | 0.94789 |
| Pharynx Dice | 0.96395 | 0.97710 |

The no-example solver constructed image-selected tooth territories and canal paths
with intensity/morphological refinement. The reference solver fitted affine and
dense registration, corrected tooth correspondences, transferred example masks,
then refined them using the target. Saved code and arrays verify actual example
use, beyond its two initial permitted read commands.

Pulp improved for 20/29 labels. Pooled precision rose 55.5% to 74.6%, recall 87.6%
to 89.7%, and pooled Dice 0.67967 to 0.81442. However, pulp 127 fell from 0.75759
to 0.18608: its transferred prior had zero initial overlap, and local refinement
recovered only 115/827 GT voxels. Spatial restrictions in the code support poor
registration and constrained recovery as a mechanism, without proving a unique cause.

Incisive canals remain mostly missed: IDs 103/104 score 0/0 without the example
and 0.06658/0 with it. Reference-run ID 104's centroid is 11.18 mm from GT and
average surface distance 8.64 mm. Main-canal ID 4 improves Dice while HD95 worsens
3.09 to 7.32 mm. These are substantive geometry/extent disagreements; a group
average conceals them. No missing classes, invalid files or global FDI reversal
explain these residual failures.

Agent elapsed was 23m48s / 28m59s; output tokens 36,510 / 46,941. Gross input,
cache and uncached counts are separated in the receipt; dollar cost is unavailable.
Both finished well before the two-hour limit. No further inference is authorized.

Restoration classes are absent in GT and both outputs, and occupied treated pulp
was not confidently identified by either solver. This case does not test those
conventions. Clinical laterality and original annotation semantics remain under
review. Correct dataset tooth IDs do not clinically adjudicate the image headers.

The [full local report](../../../.local/dental-f018-contract-v3-20260922/comparison/report.md)
contains split metrics, pseudocode, a process diagram, actual native-coordinate CT
overlays, canal projections, methods and limits. See the
[compact evidence](evidence/dental-f018-contract-v3-comparison.json) and
[reproducible analysis](../methods/dental-f018-contract-v3/analyze_comparison.py).
Figures are explicitly post-hoc diagnostic selections, with matching legends;
raw evidence and media remain local. Original scores are preserved.

## Explainer source audit — 2026-09-28

The [reader-source audit](../presentation/sources/dental-v3-audit.json) rechecks
341 pinned files, both freezes and six saved evaluations. Original outputs/scores
remain unchanged. The retained pulp and canal refinement math reproduces exactly
for all 29 pulp and five canal labels; no historical solver program is executed.
The [expanded brief](../presentation/briefs/tb3-dental-v3.md) and
[reader asset notice](../../../presentation/task-explorer/dental-v3/NOTICE.md)
provide native views, selection rules and reference boundaries. This source review
does not yet accept a canonical story or playback.

| Post-hoc operation check | Observed limit | Evidence locator |
| --- | --- | --- |
| Pulp 127 before additional refinement | 28/827 GT voxels in the saved initial pulp; 345/827 in its whole-tooth object | Assisted `teeth.npy`, `teeth.py:6–29`; trace line 116 |
| Pulp 127 expansion | Retained mask plus geometric eligibility contains 128/827 GT voxels; intensity/component filtering retains 115/827 | Assisted `pulp.py:6–11`, `teeth_final.npy`; trace line 136 |
| Canal 104 search crop | Prior bounds plus four voxels contains 0/355 GT voxels; 189 prior voxels become 203 final voxels | Assisted `canals.py:5–17`, `canals.npy`; trace line 144 |
| Saved example transfer | All 168,100 atlas and warped-CT voxels at k=55 reproduce from saved affine/regional fields | Assisted `composite2.py:4–16`, `atlas.npy`, `warpct.npy`; trace line 95 |

Locators refer to attempt `attempt-72c26b83987d4409`, trial `task__irqdozr`,
`artifacts/app/work/` and line-numbered `agent/codex.txt`; hashes are in the audit.
The pulp constraints overlap and their exclusions must not be summed. The
historical six-voxel prior-distance diagnostic is not the canal algorithm's
search radius. These checks establish a specific operation's limited reach;
they do not establish a unique upstream cause or clinically adjudicate the GT.
