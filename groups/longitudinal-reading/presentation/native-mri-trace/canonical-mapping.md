# Longitudinal MRI: retained P03 neutral trace mapping

**Mapped 2026-10-12:** `attempt-6c8ee6d062c12e5b435afa42`, BR-037 P03 neutral,
Terra/high (`openai/gpt-5.6-terra`), run
`runs/br037-p03-neutral-terra-high-v1-20260917/p03-neutral__dydf8YF`.
All 122 supplied NIfTI files and all 134 frozen task files match their retained
SHA-256 pins. This is a read-only mapping: no historical module, scorer, trial,
image regeneration, download, installation or browser review ran.

The entry `tb3-longitudinal-mri` has an existing
[brief](../briefs/tb3-longitudinal-mri.md),
[story](../stories/longitudinal-mri.story.md),
[source audit](../sources/longitudinal-mri-audit.json), and
[residual-extent idea](../../ideas/residual-breast-extent.md). Keep their three-case
scope, source-selected crop warning, measurement-unit limits and forecast baseline.
This mapping adds a single observed workflow; it does not replace the other attempts
or promote a clinical result. [BR-037 protocol](../../experiments/br037/protocol.md)
and [historical design](../../../../docs/research-rounds/BR-037-longitudinal-reading.md)
own condition and solver/reference boundaries.

## Source pins

`T = runs/br037-longitudinal-reading/tasks/p03-neutral/`

`R = runs/br037-p03-neutral-terra-high-v1-20260917/p03-neutral__dydf8YF/`

Every hash and byte count below was recomputed from current retained bytes. The
existing audit `sources` map and P03 neutral freeze receipt provide exact pins for
all 122 input volumes, avoiding a duplicate 122-row inventory here. Their own hashes
are pinned below. The frozen P03 neutral task checksum is
`22a4578aab38a10291feb5c7dd7757e90c00834ff74c1b7dc0427c479b4739b3`;
it is task identity, not a clinical score.

| Role | Exact repository-relative file | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Frozen instructions | `runs/br037-longitudinal-reading/tasks/p03-neutral/instruction.md` | 3,328 | `d90339323bc278e7c3c8a119d2029b4959a0243008745712167312501fbde284` |
| Whole-input series/frame metadata | `runs/br037-longitudinal-reading/tasks/p03-neutral/environment/data/manifest.json` | 110,201 | `5421d46323573a8d254a020b264761ae224edd1e081332ffae09a5a2ed6615c0` |
| Supplied generic viewer (read only) | `runs/br037-longitudinal-reading/tasks/p03-neutral/environment/view.py` | 1,590 | `d54a5c300328493308d17b8a5b9f5836fcc68bf96bcee186af72561e60896c36` |
| Evaluator manifest | `runs/br037-longitudinal-reading/tasks/p03-neutral/tests/manifest.json` | 110,201 | `5421d46323573a8d254a020b264761ae224edd1e081332ffae09a5a2ed6615c0` |
| Mechanical scorer (read only) | `runs/br037-longitudinal-reading/tasks/p03-neutral/tests/score.py` | 2,862 | `c3bfde846fc37d5e9059c24ef307f79bcf52fb545083092ce8d0ded2da394976` |
| Selected attempt identity | `groups/longitudinal-reading/experiments/br037/attempts/attempt-6c8ee6d062c12e5b435afa42.json` | 279 | `a105fee8a9d08aa7b8fd8270f86930eedf4cbd84bb09b406933ff412d164538e` |
| Actual tool trajectory | `runs/br037-p03-neutral-terra-high-v1-20260917/p03-neutral__dydf8YF/agent/trajectory.json` | 5,953,052 | `c2ba84e2246687284f8fc43654a691d0cb849115b1ef4f224ac1e898dcc8f62c` |
| Original trial result | `runs/br037-p03-neutral-terra-high-v1-20260917/p03-neutral__dydf8YF/result.json` | 4,033 | `c679dea31ba5b7d2ed676b8eeb632cfade7859d72166535dacec91ca677f85b7` |
| Saved assessment | `runs/br037-p03-neutral-terra-high-v1-20260917/p03-neutral__dydf8YF/artifacts/app/answer/assessment.json` | 5,534 | `b03263099e1783bf318ce0a3bb78e4dce90c9ff560748f4d7cf44741672c4533` |
| Saved report | `runs/br037-p03-neutral-terra-high-v1-20260917/p03-neutral__dydf8YF/artifacts/app/answer/report.md` | 1,576 | `94055947a476c20f07e3db4f05ddbc7bf97235262a823d09e5a4baa9d514aa74` |
| Saved final method code (read only) | `runs/br037-p03-neutral-terra-high-v1-20260917/p03-neutral__dydf8YF/artifacts/app/answer/analyze_mri.py` | 6,340 | `78d3a8a8c153cbcbd750262f9b3ea7eada6b9bddd144efccfd2db4451396af92` |
| Saved measurement summary | `runs/br037-p03-neutral-terra-high-v1-20260917/p03-neutral__dydf8YF/artifacts/app/answer/measurement_summary.json` | 818 | `a0aa59ef14fedc02dd01133e34a6fce89d9db17ac8853acf9514819a07706966` |
| Frozen mechanical result | `runs/br037-p03-neutral-terra-high-v1-20260917/p03-neutral__dydf8YF/verifier/contract.json` | 96 | `2126b9c72fa93ea755b255133595264a3bfc1da01cd086feaf7dd06f4ed62df7` |
| Frozen reward | `runs/br037-p03-neutral-terra-high-v1-20260917/p03-neutral__dydf8YF/verifier/reward.txt` | 2 | `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865` |
| Freeze receipt, all 134 files | `runs/br037-longitudinal-reading/p03-neutral-freeze.json` | 14,419 | `1ec5e22a5f354a69accee2059e7d027ebb2022c1f96e452f3ca3bac7d8ccd54f` |
| Existing source/method audit | `groups/longitudinal-reading/presentation/sources/longitudinal-mri-audit.json` | 64,796 | `63c61f7f82b70d75ea19804610b19b485dac7eebc0c73c18e2cccb4a1dbc5c5f` |
| Existing post-hoc measurement audit | `runs/br037-longitudinal-reading/measurement-audit.json` | 1,704 | `da8c08f6bfda532ed6df4eef476199894e9cb724ca98d1c0d76549e9d443feb7` |
| Source curation | `docs/evidence/br037-curation.json` | 13,506 | `eab3c15f8826a6a0c09021527a1dcf2b4a0cadd3adffb570df53f2ea6257c0b3` |
| Original collection/terms snapshot | `runs/br037-longitudinal-reading/source/ispy2.html` | 326,424 | `0bcbf84bf91748cbc9f1df90851a4d1f245f9e90b130c46079369a2eda8cc69c` |
| Reader-only measurement workbook | `runs/br037-longitudinal-reading/source/measurements.xlsx` | 132,946 | `f714c7784b1e57daa74d7cfb20db71cd432b4e4596b9b4eacdd5a76b7f8a58dc` |

## Whole input to selected series

**Given:** V1 day 0 and V2 day 34, 61 volumes each, **122 volumes / 1,930 source
frames / 522,225,010 compressed bytes**. Each visit includes 51 separately framed
scouts, one WATER:IDEAL and one FAT:IDEAL volume, plus baseline and seven dynamic
VIBRANT acquisitions. Full reconstructed input was available, not just selected
screenshots; no raw k-space was supplied. Source VOLSER analysis products, target
VOIs, outcome fields, source identity, later visits and surgical pCR were withheld.

- **Scouts:** V1 S01–S51 and V2 S62–S112 are 256×256×1 per-plane volumes with
  RAS/PIR/LIP axis groups. Preserve each affine; do not combine them into a fictitious
  contiguous 3D stack.
- **Other volumes:** V1 S52/S53 and V2 S113/S114 are WATER/FAT IDEAL,
  512×512×45, in-plane spacing 0.6641/0.6445 mm respectively and 5 mm through-plane.
  Step 11 checks selected files exist, but the retained custom method uses only the
  sixteen dynamic volumes below. This is not evidence of exhaustive review of all
  122 volumes.
- **Dynamic ordering:** ordinals 0..7 below are the solver's baseline-plus-Ph1..Ph7
  sequence interpretation. Every file is 3D: every saved `assessment.json` citation
  has **phase=0**, including S61/S122. Do not translate ordinal 7 into phase index 7
  of a 3D file. All supplied per-file acquisition-offset lists are `[0]`; ordinal
  ordering does not supply contrast-injection time or elapsed inter-series timing.

| Visit / series | Dynamic ordinal | File under T `environment/data/` | Bytes | SHA-256 |
| --- | ---: | --- | ---: | --- |
| V1 / S54 | 0 | V1_S54.nii.gz | 27,238,756 | `1b105b906a17ca79b70eb51d3a21f607863ab414ec68840782d94bf6c4963edb` |
| V1 / S55 | 1 | V1_S55.nii.gz | 28,148,212 | `6df67557f40f3c183242a73778f22cbdb111c1fcefddc0c55e6adae04c505fe8` |
| V1 / S56 | 2 | V1_S56.nii.gz | 28,536,625 | `f0cfbc507d6c966887883faa1086812168bc708ce454ccdfab5519cc25c4b85d` |
| V1 / S57 | 3 | V1_S57.nii.gz | 28,732,916 | `2c816e53dc3e523fd8eb8ce8c852354032d33f39aef3d8fca557955a9e280719` |
| V1 / S58 | 4 | V1_S58.nii.gz | 28,805,462 | `57f98731b7e5e6298870ebec26e20ac4ee6057511859765059fd123004e7aa36` |
| V1 / S59 | 5 | V1_S59.nii.gz | 28,810,703 | `0e7d9716652bf3743d13fe3c1f57b7d72e393143ae8e4f78eebe0b1a5de716d6` |
| V1 / S60 | 6 | V1_S60.nii.gz | 28,877,404 | `894c8a0be6b667cd19be31474e775a5f53a0af56aa88c403aaf813c62884a281` |
| V1 / S61 | 7 | V1_S61.nii.gz | 28,910,794 | `0fd9aa33bc342965574f846be24946dc76c13e2599625f66b4c5fe23be920030` |
| V2 / S115 | 0 | V2_S115.nii.gz | 28,690,426 | `f7ee66bec501e07b929edfe4d2db69f6a1093362df1328aabf4a0cb7638d15f5` |
| V2 / S116 | 1 | V2_S116.nii.gz | 29,830,999 | `7ad714b9201fa79162ceabde70e86203f078deb0edf281bfc02e6a94c707d5e1` |
| V2 / S117 | 2 | V2_S117.nii.gz | 30,197,606 | `e98749dc589e3bfe754a773d0fe6cba8096afd94c03ada2db4aaf49ea26f913e` |
| V2 / S118 | 3 | V2_S118.nii.gz | 30,271,272 | `2813339e5c79be56d4a150fdefdf47975af8165a4101767f609b53ccc6ffbd3c` |
| V2 / S119 | 4 | V2_S119.nii.gz | 30,382,089 | `924675fcd5cd7ebb89f62781554cbe5b54430a52f2c5178a872c77b682f294b3` |
| V2 / S120 | 5 | V2_S120.nii.gz | 30,371,080 | `7d66459788e11b45d87912c63476e1efb820722b96e8c7890609fe6c033353d3` |
| V2 / S121 | 6 | V2_S121.nii.gz | 30,413,115 | `9508487e100cbc62602e55b12701071f9c392601b278455012130fbe5d453cf9` |
| V2 / S122 | 7 | V2_S122.nii.gz | 30,405,877 | `0b06b67164c2b577a87927e4eb2cd476842e4c82cd679f78c41996223ad63f2c` |

**Native frames:** all selected dynamic arrays use zero-based `[i,j,k]`, axes R/A/S.
Within each visit their shapes and affines agree; between visits they differ and are
not registered. Manifest affines are rounded; use retained NIfTI affine precision
for overlays/world positions, retaining the manifest as supplied metadata.

| Native dynamic grid | V1 S54–S61 | V2 S115–S122 |
| --- | --- | --- |
| Shape | 512×512×106 | 512×512×100 |
| NIfTI spacing, mm | 0.6640999913215637, 0.6640999913215637, 2 | 0.6445000171661377, 0.6445000171661377, 2 |
| RAS origin, mm | −180.3939971923828, −138.53900146484375, −105 | −163.5989990234375, −150.72000122070312, −116.1709976196289 |
| Mapping | diagonal spacing × native index + origin | diagonal spacing × native index + origin |

Recorded step-19 candidate centres are V1 `[390,270,60]` → rounded RAS
`[78.6,40.8,15.0]` mm and V2 `[386,302,64]` → `[85.2,43.9,11.8]` mm.
Saved citations instead use V1 `[391,270,60]` and V2 `[386,301,64]`; preserve this
one-voxel distinction. These are solver-selected inspection/citation points, not
source VOI centres or registered correspondences.

## Actual operations and delivered images

The trajectory has **30 steps**. Consequential operations are discrete, not a
continuous recording or private reasoning account.

| Steps | Recorded operation | Source-volume relationship / boundary |
| --- | --- | --- |
| 7, 9–11 | Inventory files, inspect manifest and native shapes | Entire supplied packet → choose dynamic series; no source-case lookup in these calls. |
| 13–15 | Write/run custom method; open dynamic overview | Early subtraction S55−S54 / S116−S115; four axial k slices chosen by 99.5th-percentile slice scores. Retained figure labels V1 k=51,50,49,52; V2 k=49,48,50,46. Baseline, ordinal-7 and peak-subtraction panels use first selected k. Despite a comment about a three-slice slab, executed code displays single axial slices. |
| 16–18 | Add/run/open anterior early-subtraction MIPs | Max over k=15:96 (V1), 15:90 (V2); i=20:256 and 256:492, j=120:490. Step-18 image predates the laterality-label correction. |
| 19 | Smooth local early subtraction and print candidate centres | Actual ROI i=280:480, j=180:460, k=10:96 (V1), 10:90 (V2); sigma=(2,2,1) voxels. The comment calls it left breast, but positive-R centres and later correction identify right. Do not endorse the old label. |
| 20–22 | Correct projection laterality; add/run/open phase close-ups | V1 centre `[390,270,60]`, V2 `[386,302,64]`; i/j ±45 voxels, half-open 91×91 windows at fixed k, ordinals 0,1,2,4,7. Red cross denotes solver-selected focus, not GT. |
| 23–24 | Compare threshold components/curves and recheck geometry | Early subtraction Gaussian sigma=1 voxel; test local-peak fractions 0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.6. Native local boxes V1 `[330:450,200:340,40:85]`, V2 `[330:450,230:370,40:90]`; recorded centre curves at citation points. |
| 26–27 | Save assessment/report; check format | Four native citations and qualified interpretation/forecast. Format validation does not establish clinical correctness. |
| 28–29 | Save final method extension and rerun | Component containing local peak at 30% threshold; save inclusive bbox, voxel spans and mm summary. Step 29 prints summary then reports `git: command not found`; measurement output remains present. This shell tail error is not a clinical verdict. |

Every delivered image is located by `step_id`, then
`observation.results[result].content`, decoded item. Exact delivered bytes were
hashed in memory without creating extraction files:

| Step | Requested figure | Result/item | PNG dimensions | Decoded bytes | PNG SHA-256 |
| --- | --- | --- | --- | ---: | --- |
| 15 | `dynamic_overview.png` | 0/1 | 1600×1600 | 2,687,800 | `bd0dde1637698d1f164473fd2b4d581c98983a76af22da9761017e9a3431a40a` |
| 18 | `breast_early_subtraction_mip.png` | 0/1 | 2048×1024 | 686,420 | `ace35d019a226a1eb147a10b2f7df9e07b4753af947aa60fd757d5ff75407187` |
| 22 | `right_breast_focus_phases.png` | 0/1 | 2048×819 | 1,011,128 | `43762cfa527ab8b8fae3331588662a05abdab6bafc44603c1969cf5589b8cc55` |

Saved final figure files under R `artifacts/app/answer/` have separate pins:

| Saved filename | PNG dimensions | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| `breast_early_subtraction_mip.png` | 2400×1200 | 759,478 | `f89557da5fabe98a48e986f11e5a4ef8bb149d4c05bb30498c5d520bc5443f0a` |
| `dynamic_overview.png` | 2400×2400 | 4,571,084 | `cc73abd4b4691fb7cf7ce9aa827a489b648657c0c42145da5188375f149a8030` |
| `right_breast_focus_phases.png` | 2700×1080 | 266,126 | `d6d8c46784e8102619c5de22b323f4119ef6d69fa2184f0a1d3a85b00f20c386` |

**Delivery differs from saved artifact:** none of the three embedded PNG hashes
matches its final saved PNG. Dimensions differ, and step 18's displayed projection
labels were subsequently changed at step 20. Package exact embedded bytes as
observations and final saved figures as saved artifacts; never substitute one and
call it delivered. The corrected projection was rerun and saved, but no later
projection `view_image` is recorded. The final script and three PNGs exist locally;
intermediate on-disk script/PNG versions are not separately retained. Their changes
remain in tool-call patches and exact delivery observations.

## Measurements and existing reproduction limits

The saved method uses first-post minus baseline, Gaussian sigma=1 voxel, a local
30% peak threshold and the connected component containing the local maximum.
It measures the largest axis-aligned **voxel-edge bbox span**, not a clinically
adjudicated longest diameter. Inclusive extrema become half-open cell bounds by
adding 1 to each maximum; physical edges use native affine at index−0.5.

| Neutral result | V1 | V2 |
| --- | --- | --- |
| Inclusive extrema, ijk | `[376,253,54]` .. `[397,284,63]` | `[375,285,58]` .. `[391,315,67]` |
| Bbox voxels | 22×32×10 | 17×31×10 |
| Saved mm spans | 14.610,21.251,20.000 | 10.957,19.980,20.000 |
| Saved numeric maximum / report | 21.251 mm / 21.3 mm | 20.000 mm / 20.0 mm |
| Existing audit, full precision | 21.25119972229004 mm | 20.0 mm |

The existing audit reproduced **−5.887666%** change. V2's true maximum span is
k=20.0 mm, slightly exceeding j=19.9795 mm; the saved assessment's description
“31 j voxels × 0.6445 = 20.0” is rounded shorthand. Preserve numeric summary and
text separately. The code selects the component containing the local peak;
assessment prose describes a component containing the cited voxel. This mapping
has not rerun a connected-component membership check.

- **Already reproduced, not repeated here:** existing audit reports neutral −5.9%
  and cue −27.2%. Cue uses a different postcontrast phase, 50% threshold, no
  smoothing and voxel-centre spans. Method differences prevent causal cue
  attribution from one pair. Cue output/trajectory must not become an intermediate
  state of this neutral attempt.
- **Reader-selected crop is separate:** audit `measurement_reproduction` bounds
  `[330,210,120,120]` / `[330,240,120,120]` and k=58/63 are presentation crops,
  not the recorded 3D computational boxes or phase close-up centres above.
  Source-reference selected crops remove search and remain reveal-only.
- **Geometry evidence:** previous audit selected DICOM samples found zero pixel
  differences and micrometre-scale origin rounding differences. This is retained
  audit evidence, not verification of every acquired instance or a fresh DICOM
  audit. This mapping read only selected NIfTI headers and current file hashes.

## Reader reference and roles

**Input:** two visits, series/phase ordering, complete available reconstructed
volumes, relative days and native affine metadata. **Observed:** recorded tool
calls, exact delivered images and printed candidates/curves/component spans.
**Saved:** final code/figures/assessment/report/measurement summary.
**Reader reference:** source patient identifier, workbook, regional VOIs, later
visits and pathological response, plus the prior engineering reproduction.

Keep private reference assets hidden from input/observed chapters. Separate
source-origin identifiers/VOIs from neutral packet identifiers in UI and manifests.
No source-selected lesion crop should masquerade as a solver's initial input.
Neither raw MR signal nor separate visit positions are calibrated/registered.

Frozen `contract.json` says `contract_pass=true`, `errors=[]`, and clinical
accuracy **“Not scored by this program”**; `reward.txt` is **1**. There is no
`verifier/metrics.json` or `details.json`. Do not manufacture clinical metrics.

The existing reader audit's P03 source FTV trajectory is
3.2133359→5.5835413→1.6494477→0.38547287 cc; source diameter raw values are
2.4→2.0→1.0→0.8 with **unresolved workbook units**; pCR=0. Source early FTV
change is +73.7615%, raw-diameter change −16.6667%. These endpoints do not
validate the solver's component-box diameter or its diagnostic claim. The saved
forecast is “smaller,” confidence 0.43. All three neutral next-visit source
raw-diameter directions decreased, so an always-smaller baseline also matches
3/3; this neutral attempt cannot establish forecast benefit or generalization.

## Potential discrete chapters

Proposed seven 168-frame holds at 24 fps (**1,176 frames / 49 s**), subject to
readability review. This is presentation timing, not agent elapsed time. No
interpolated lesion motion, registration, phase timing or private reasoning.

| Chapter | Actual steps / reader evidence | Native state and role |
| --- | --- | --- |
| Receive full packet | 7,9–11 | V1/V2 series inventory, whole selected dynamic grids and other series inventory; no target marks. |
| Choose dynamic inspections | 13–15 | Early-subtraction axial montage and exact selected k slices within both native grids. |
| Project and correct orientation | 16–20 | Exact step-18 MIP, logged region bounds and explicit laterality correction; retain old image label caveat. |
| Inspect the selected focus | 20–22 | Actual native close-up centres/windows, ordinal series 0/1/2/4/7, exact delivered phase panels. |
| Define component extent | 23–24,28–29 | Real local computational boxes, tested thresholds, chosen bbox spans and printed curves; reader box overlays are derived and labelled. |
| Save qualified account | 26–29 | Four exact citations, native-frame distinctions, persistent-finding interpretation and low-confidence conditional forecast. |
| Reveal source/limits | Existing audit/workbook; saved state retained | FTV versus component-span versus source diameter; units unresolved, future direction/baseline, cue-method confound and mechanical/clinical boundary. |

## Integration gaps and recovery boundary

**Next bounded action:** author a fresh reader-only preparation recipe for this P03
neutral attempt. Package two native-grid context previews, all three exact embedded
deliveries, selected series/ordinal metadata, logged view/ROI states, saved citations
and bbox spans, with a separate reader-reference projection from the existing P03
audit. Pin source/derivative receipts and inspect geometry/reference hiding before
proposing an MRI adapter or catalogue binding. No cue attempt, new trial or clinical
score is needed for that preparation.

- **Adapter needed:** typed two-visit series inventory and per-series native
  geometry; explicit dynamic ordinal versus citation phase; selected plane/slab/ROI
  states, exact deliveries, saved bbox/citation/forecast projection, and separately
  gated source references. Current rigid CT pose, vessel masks and named-landmark
  statuses do not represent these MRI operations.
- **Derivatives not created:** no compact native preview, image-extraction bundle,
  receipt, static fallback or draft story was generated by this mapping. A fresh,
  source-pinned recipe is needed before binding. Keep 522 MB source volumes local;
  bounded whole-grid previews should connect to exact selected native views, not
  enter the general catalogue as original arrays.
- **No missing supplied data:** all 122 input files, final method/output and three
  embedded deliveries are available. Intermediate raw script/image versions,
  calibrated contrast timing, cross-visit registration, exhaustive tumor masks,
  adjudicated clinical diameters and resolved source-diameter units are absent or
  unestablished. Original T has `tests/score.py` but no `tests/evaluate.py`; the
  reproduction package's evaluator has separate provenance.
- **Terms:** retained I-SPY2 collection snapshot and curation identify CC BY 4.0.
  Preserve I-SPY2 collection attribution/DOI `10.7937/TCIA.D8Z0-9T85`, source pin and DICOM→NIfTI/display
  transformation disclosures; keep public source identities in reader/reference
  roles. No new acquisition or publication is authorized by this mapping.
- **Acceptance open:** source recovery, exact-image packaging, native geometry,
  reference hiding, narrow layout, keyboard controls, fallbacks and independent
  visual review are still required. Clinical measurement reliability and source
  workbook units remain the idea's reopening conditions. This is an assistant
  mapping, not a user research decision or a new model result.
