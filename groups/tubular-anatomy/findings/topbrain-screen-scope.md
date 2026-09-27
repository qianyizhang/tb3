# TopBrain screening admitted no brain repair trial

**Five retained development predictions yielded no admitted hard brain task and
zero coding-agent trials.** The small R-SCA gap remains geometric calibration;
three PCA–SCA contacts retain reference ambiguity; two selected artery variants
are already preserved. This is a source-curation result, not an agent failure.

The [resumption receipt](../../../docs/evidence/br033-brain-resumption.json) and
[protocol](../../../docs/research-rounds/BR-033-brain-resumption.md) retain the
original decision. The [new read-only audit](../presentation/sources/topbrain-screen-audit.json)
reproduces selected measurements without inference, optimization or clinical adjudication.

## Condition and source boundary

- **Images:** public training/development MRA 004, 007, 012, 006 and 011. The last
  two were acquired after reference-assisted selection for third-A2/A3 variants.
  Five predictions are not five coding-agent attempts.
- **Prediction:** the released TA36 ResEncM fold-4 component; checkpoint SHA-256
  `64371519d5d9374f60f132f27dd0f6b212bd2f70ac47f6c81ebd84031e78013d`.
  Released preprocessing/sliding-window predictor, MPS, 0.5 tile step, Gaussian
  blending, disabled checkpoint mirroring. No reference crop, synthetic defect,
  official three-model ensemble or pruning postprocessing.
- **Author references:** version-2 TA36 36-class masks. The earlier TopBrain
  modality-specific 40/42-class inventories are different schemes. References
  assist selection and scoring; retained inference reads image values only.
- **Future solver condition:** a natural labeled error, enough parent/target context,
  an editable region and valid unchanged controls. No such packet or independent
  brain verifier was frozen. The separate airway pilot does not fill that gap.

The official [model record](https://zenodo.org/records/21959166) identifies the
TA36 release, LPS input prerequisite and training-data source. The exact
[retained data terms](../../../presentation/task-explorer/topbrain-screen/DATA-LICENSE.txt)
permit noncommercial use with source attribution; commercial use requires owner
permission. Model-page metadata does not replace the dataset's license.

## Development measurements

Dice is computed per nonbackground label present in either prediction or
reference, then averaged with equal class weight. It is not whole-volume Dice,
a clinical endpoint or a held-out estimate.

| MRA | Labels compared | Mean label Dice | Interpretation |
| --- | ---: | ---: | --- |
| 004 | 32 | 0.9388 | Selected gap calibration and contact review |
| 006 | 31 | 0.9161 | Third-A2/A3 already preserved |
| 007 | 32 | 0.9440 | Contact and reference-parent review |
| 011 | 33 | 0.9422 | Preserved variant and contact review |
| 012 | 32 | 0.9447 | Development source screen |

The audit reproduces all **160** class counts and Dice values from full native
arrays. This verifies retained arithmetic, not anatomical correctness.
The historical [interior-region list](../../../runs/br033-brain-routing/predictions-resencm-v1/review-regions.json)
contains 16 candidates under a 0.5 mm reference-interior threshold, component size
at least ten voxels and at most four regions per class. That selective rule is
not exhaustive for thin vessels. It was not rerun as a new candidate search.

## Why candidates were not admitted

| Candidate | Observed evidence | Supported disposition | Unresolved condition |
| --- | --- | --- | --- |
| 004 distal R-SCA | Saved geometry-only bridge restores parent reachability with two additions | Geometric calibration | One addition is reference background; hard anatomical discrimination unestablished |
| Three PCA–SCA contacts | Predictions gain face contacts; references touch under 26-neighbour connectivity | Reference-convention ambiguity | Anatomical connection needs adjudication; neither adjacency rule resolves it |
| 006/011 third-A2/A3 | All variant voxels reach R-ICA in prediction and reference | Potential preservation controls | No adjudicated true-absence case or accompanying hard repair |
| 007 reference L-MCA | 1,479/11,322 L-M2 voxels lie outside the parent component | Reference-fitness concern | Fragmentation alone establishes neither missing anatomy nor model error |

**Contact units matter.** These count PCA voxels neighboring SCA, not touching
face pairs or unique vessel connections. They reproduce the retained convention audit.

| Candidate | Prediction: 6 / 26 neighbours | Reference: 6 / 26 neighbours |
| --- | ---: | ---: |
| 004 L-P1P2 / L-SCA | 4 / 20 | 0 / 8 |
| 007 R-P1P2 / R-SCA | 2 / 2 | 0 / 1 |
| 011 L-P1P2 / L-SCA | 1 / 18 | 0 / 13 |

The selected native sections show proximity and differing label boundaries.
They do not establish whether the anatomical vessels connect. Neither a
projection nor a new face adjacency supplies an independent topology oracle.

**Parent chains are explicit.** Both variants use only R-ICA-C6-C7 → R-A1A2 →
third-A2/A3 with 26-neighbour connectivity; no collateral Circle-of-Willis route
is needed. Prediction/reference third-A2 counts are 1496/1572 (006) and 1159/1248
(011); third-A3 counts are 820/843 and 1510/1517. Every counted variant voxel
reaches the parent. The reference L-MCA chain is L-ICA-C6-C7/L-M1/L-M2/L-M3:
four components, with L-M2 parent coverage 86.94%. These are label-chain measures,
not clinical identity or absence adjudication.

## Saved geometric calibration

The inspected [author method](../../../probes/brain-routing/authoring/gap_calibration.py)
chooses nearest points between R-SCA components, rounds the bridge on the original
voxel lattice, then traces within the repaired BA/R-SCA union using inverse-radius
cost. MRA supplies subsequent CPR signal; it does not choose the repair.
References enter after output construction. Selection itself is reference-assisted.

- **Edits:** exactly native IJK `(190,306,79)` and `(191,307,79)`, background → R-SCA.
  No deletion or other full-volume edit. The 247-voxel distal fragment reconnects
  to its selected basilar parent; nearest original centres are 0.939 mm apart.
- **Reference disagreement:** one addition matches reference R-SCA, one matches
  background. Connectivity recovery does not imply exact annotation recovery.
- **Route:** 344 saved RAS+ points, 85.5667 mm. Nearest distance to the saved
  reference route is p95 0.2983 mm, max 0.4494 mm. Both routes use the same
  author-selected endpoints; this is not independently adjudicated route truth.
- **CPR:** eight angles at 45° intervals, 51 offsets from −5 to +5 mm at 0.2 mm.
  All **140,352** stored signal samples reproduce original-MRA trilinear sampling
  within float32 tolerance: max difference **0.000101698 signal units**.
  Coordinates, radial offsets and cumulative arc agree. MRA signal is not HU.
  No new source pixels are sampled for the teaching display.
- **Mesh:** the saved BA-plus-R-SCA PLY is finite, watertight and one connected
  component. This limited surface does not claim whole-brain repair.

Earlier three-voxel exports remain in historical v1/v2 directories. The final
retained export uses the native lattice and two additions. This was author
calibration before any frozen brain task; no score is retroactively corrected.

## Re-audit and teaching scope

The [builder](../../../scripts/build_topbrain_screen_assets.py) verifies **108
retained data members**, **314 model/source members**, the complete model/source
layer, five images/predictions and selected calibration artifacts against retained
fingerprints. It reproduces class scores, selected contacts/attachments,
full-volume edits and CPR/route checks. It never loads the checkpoint as executable
code, imports historical authoring modules, optimizes a route or writes raw evidence.

Views retain native pixels, affine vectors, source bounds, fixed per-view signal
windows and physical pixel aspect. MIPs collapse a named axis. Contact views are
three native planes per candidate. Source, prediction and reader reference remain
labeled; crop selection is author/reference assisted. Uniform-arc CPR rendering
interpolates only saved signal rows and retains the original row rasters. The
[notice](../../../presentation/task-explorer/topbrain-screen/NOTICE.md) records
colors, derivation and terms. Selected views support this explanation; they do
not constitute exhaustive anatomical review of all five volumes.

**Reopen with:** a substantial reference-supported natural branch error, reliable
parent/target identity, intact or adjudicated absence controls, and a frozen
independent verifier. The screen does not establish that TopBrain cannot supply
such a case. This assistant audit preserves the original outcome and grants no
new trial authorization.
