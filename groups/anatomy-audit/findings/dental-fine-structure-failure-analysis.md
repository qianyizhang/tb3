# F002 pulp and canal failure mechanisms

At the user's request, the saved reference-assisted attempt
`attempt-36ee0d66d0a64d55` was examined beyond final scores. This is author-side
diagnosis, with no new inference, changed output or replacement score.
Source task: codex://threads/01a0c3e5-6fb0-7321-a930-a7251047e7ad.
It supplements the [paired comparison](dental-reference-example-comparison.md).

The low fine-structure scores have multiple causes, with direct measured evidence:

- **Pulp intensity-rule transfer failure.** The same fixed rule (smoothed CT
  below 1250 and more than two voxels inside a tooth) scores pooled Dice 0.809
  on F008's true masks, or 0.765 on its matching 22 tooth IDs. On F002 it scores
  0.299 even with true target tooth masks, and 0.287 with predicted masks.
  These oracle-mask diagnostics precede the agent's later filters; they are
  distinct from the recorded final pulp macro 0.315. The cutoff rejects 42.5%
  of target GT pulp voxels and also selects substantial non-pulp tissue.
- **A remaining pulp annotation convention gap.** GT labels 116 and 131 have
  838/858 and 331/333 voxels above intensity 3000; most are at the scan maximum
  3220. The example lacks this appearance. The agent explicitly avoided calling
  saturated contents empty pulp. V2 defines internal chambers but does not settle
  occupied/treated/calcified spaces. The mismatch is observed; material identity,
  clinical correctness and the intended dataset convention remain unadjudicated.
  Excluding those two IDs diagnostically raises pooled pulp Dice only 0.364→0.417.
- **Hard exclusion against inaccurate transferred anatomy.** For tooth 14,
  rejecting pulp farther than 1.05 mm from the transferred prior deletes 440
  of 443 correctly placed voxels, leaving 3. This exact deletion reproduces
  voxel for voxel from saved inputs and code. Whole-pulp transferred geometry
  scores 0.395, then 0.316 after intensity processing, and 0.364 after final edits.
- **Canal paths are misplaced and undersized.** Only 19.8%/43.6% of main-canal
  path samples are inside their GT masks. Of missed main-canal GT voxels, 98.6%
  already lie outside the uncut tubes; final assembly is not the cause. Increasing
  both radii by 1.2 mm yields only diagnostic Dice 0.269/0.326. The final local
  search is limited to 0.75 mm per perpendicular direction for main canals and
  0.3 mm for small canals, with a penalty against movement.
- **Small canals have different failures.** Left incisive Dice 0.306 includes
  useful placement but low coverage; a fixed 0.6 mm radius expansion gives 0.549.
  The right incisive path has zero overlap and remains poor under expansion.
  Lingual Dice 0.075 includes missing a separate 69-voxel GT component; its raw
  transferred label had better Dice 0.302 before later path replacement.

Simple overlap sensitivity is insufficient to explain the result: a one-voxel
translation of main-canal GT yields mean Dice about 0.900, and 0.803/0.811 for
incisive canals. The actual errors are larger. Both native output validity and
original metric replay passed; the reference run finished in 49m04s of its
two-hour allowance without a terminal exception.

**Interpretation:** the reference supplies spatial and intensity guidance, but
neither a reliable target fine-structure detector nor the missing filled-chamber
convention. This qualifies the earlier statement that annotation rules had been
addressed: the occupied-pulp edge case was not resolved. It does not establish
clinically wrong GT, impossible anatomy, or a population-level model limitation.

**Assistant recommendation, not a new user decision:** adjudicate occupied/treated
pulp labels and review an example demonstrating that convention before a further
trial. For canals, distinguish target localization from tube width and annotated
extent. More normal examples alone do not directly address the identified gap.

The [full local report](../../../.local/dental-reference-ablation-20260921/fine-structure-diagnosis/report.md)
contains source-linked methods, native CT overlays, gate counts, intermediate
scores, fixed-radius sensitivity and reproducible commands. The
[compact evidence](evidence/dental-fine-structure-failure-analysis.json) retains
measurements, input hashes and limitations. Author-only code:
[diagnostics](../methods/dental-reference-ablation/diagnose_fine_structures.py),
[rendering and prior-clipping verification](../methods/dental-reference-ablation/render_fine_diagnosis.py).
