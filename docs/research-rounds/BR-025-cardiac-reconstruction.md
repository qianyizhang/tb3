# BR-025 — Cardiac video to dynamic geometry

Status: source curation and bounded author pilot complete, 2026-09-16. Plausible LV reconstruction; no demonstrated LLM difficulty or submission qualification.

## Authorization and provenance

The user explicitly resumed research in task `01a0a967-f33c-70a0-b661-d8919246b13b`, asking to recover a plausible 4D heart mesh from single/multiple ultrasound videos, vary supplied contours and anatomy detail, and investigate EF, flow and cardiac problems. They requested ground-truth curation first and authorized an author test to assess feasibility and calibrate acceptance. The quoted starting proposal concerns full-cycle CAMUS/TED measurement and temporal contour correction. The earlier brainstorm conversation was not independently retrieved; the supplied quotation is the available provenance.

This round owns only this note, `docs/evidence/br025-*`, `probes/cardiac-reconstruction/authoring/`, and ignored `runs/br025-cardiac/`. It preserves other active rounds, frozen evidence, the final interview report and the sibling submission. This is not a model qualification trial.

## Pilot plan, recorded before reconstruction results

- First inspect actual file geometry, label provenance, units, time references and reuse terms. Published dataset claims alone do not establish a usable fixture.
- Use the publicly supplied FeEcho4D_017 example, selected because it is the complete fetal example in the authors' code repository, not because of its reconstruction score. Inspect a second source only if needed for a material ground-truth gap.
- Compare one, two and several calibrated radial views of the same case, with supplied contours, before attempting video-only segmentation. Keep observed-view agreement, held-out-view agreement, temporal geometry and scalar measurement separate.
- Use a simple CPU reconstruction baseline and explicit static/no-motion and missing-depth controls. Record assumptions and any source-derived preprocessing; no unseen annotations may be used to tune a blind solver.
- Where the source is sparse, do not treat unannotated voxels as true background or a completed interpolated mesh as independent 3D truth. Reference-derived reconstruction only calibrates consistency with those annotations.
- Preserve source receipts/hashes, reproducible code and detailed local outputs. No cohort-level thresholds, disease accuracy, clinical validity, or Terra/Sol difficulty claims from a single author pilot.
- Propose thresholds only after checking reference uncertainty and simple baselines. Distinguish a suggested development target from a frozen acceptance rule validated on held-out patients.

## Findings and disposition

### Source inspection amendment, before reconstruction results

FeEcho4D's GitHub `FeEcho4D_017` example is a 256-cubed sparse embedding of radial slices, with unit affine and label values 100/200. Its zero voxels cannot be treated as annotated background. Therefore the pilot switches to the first annotated patient (`Patient001`) in the native Zenodo release, selected by archive order before outcomes: 30 time points, 37 radial planes, native masks, mesh sequence and calibration file. The archive is 11,423,073,355 bytes; HTTP range requests allow a bounded single-patient retrieval. This is an explicit source-quality change, not a difficulty-selected case substitution.

### Curated sources

| Source | Reference actually available | Appropriate use and limitation | Access checked |
| --- | --- | --- | --- |
| [Multimodality STRAUS](https://humanheart-project.creatis.insa-lyon.fr/multimodalityStraus.html) | Simulated 3D ultrasound sequences and corresponding moving reference meshes; 18 virtual patients | Best initial candidate for testing recovery against known 3D geometry and motion. Derive calibrated videos from the same volume/time grid, retaining the simulator reference. Synthetic realism and anatomy coverage need auditing; no clinical-diagnosis validation. Do not confuse this 18-patient release with other STRAUS versions. | Public Girder collection, patient image/mesh folders and file inventories inspected. Not run locally in this round. Public download alone does not settle redistribution terms. |
| [FeEcho4D](https://feecho4d.github.io/Website/) / [native release](https://zenodo.org/records/21322299) | Real fetal STIC, 52 annotated subjects; LV cavity/myocardium masks and fitted dynamic meshes | Best accessible real-image pilot. Intermediate annotations use motion propagation and review; meshes depend on those annotations. This is an LV reference, not a four-chamber/valve reference or independent surface scan. | Native Patient001 downloaded and verified. Non-commercial research stated on project site; precise downstream redistribution permission remains unresolved. |
| [TED / CAMUS Full Cycle](https://humanheart-project.creatis.insa-lyon.fr/ted.html), [annotation protocol](https://www.creatis.insa-lyon.fr/~bernard/publis/tmi_2022_nathan.pdf) | 98 A4C cycles with LV/myocardium masks | Strong temporal contour/area-change benchmark. Eight frames per cycle were manually traced; remaining contours were spline-interpolated, checked and corrected. Thus interpolation smoothness is partly built into the reference. A4C is a view name, not annotation of four chambers. No 3D mesh truth. | Public collection and 98 patient folders verified, first case's image/mask/config entries inspected. No full case downloaded. |
| [CAMUS](https://www.creatis.insa-lyon.fr/Challenge/camus/databases.html) / [EchoNet-Dynamic](https://echonet.github.io/dynamic/) | CAMUS: 500 patients, A2C/A4C with ED/ES labels. EchoNet: 10,030 A4C videos with EF, EDV/ESV and LV tracings | Real-video EF/frame/contour calibration. Neither is a paired 4D whole-heart mesh reference. CAMUS's separate acquisitions require phase alignment; do not assume common physical pose or identical frame numbers. | Official descriptions checked. EchoNet requires a research-use agreement; no account or agreement submitted. |
| [MITEA](https://www.cardiacatlas.org/mitea/), [methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC9871929/) | 134 subjects, scan/rescan 3D echo at ED/ES, CMR-derived LV cavity/myocardium labels | Useful adult endpoint geometry and volume cross-check. Released annotations cover two phases, not dense motion. Registered CMR labels carry registration/observer uncertainty and may extend outside the acquired echo field. | Institutional access request required; no request submitted. Its source forbids onward disclosure without consent. Third-party sample copies were not used to bypass access. |
| [MVSeg2023](https://huggingface.co/datasets/pcarnahan/MVSeg2023) | Anterior/posterior mitral leaflets in single-frame 3D TEE | Separate valve geometry task. It cannot validate a valve's entire motion or provide matched whole-heart chamber data. The card's total and split counts disagree, so no case count is treated as verified. | Gated; CC BY-NC-ND 4.0 stated. Not downloaded. |
| [DUPLEX](https://humanheart-project.creatis.insa-lyon.fr/duplex.html) | Synthetic B-mode/color Doppler with CFD blood velocity references; 20 sequences of 16 frames | Appropriate separate flow-estimation benchmark, with aliasing/clutter conditions. It supplies velocity evidence that grayscale wall motion does not. | Official source/methods checked; no files downloaded. |
| [MIMIC-IV-ECHO](https://www.physionet.org/content/mimic-iv-echo/1.0/) | Echo DICOM and structured clinical measurements, including Doppler/valvular measurements | Reserve for a clinically contextualized measurement or finding task. It does not supply paired dense mesh truth. Version 1.0.1 is listed as a later release; inspect that release before acquiring a fixture. | Credentialing, training and DUA required; not accessed. |

No verified source in this screen supplies **matched real video + dense four-chamber surfaces + moving valve leaflets + blood-flow truth**. Do not combine unrelated patients/modalities and call the result a ground-truth heart.

### Published calibration evidence

[Echo4DIR](https://arxiv.org/html/2605.22066v1) establishes a closely related research direction: sparse mask-conditioned dynamic LV reconstruction. Its clinical overlap score compares reprojected 2D masks with clinical masks; its 3D geometry results use synthetic shape-model data. Neither its headline clinical Dice nor the older [4DHeartModel implementation](https://github.com/laumerf/4DHeartModel) establishes accurate unseen patient anatomy. TED's published baseline temporal inconsistencies motivate a temporal task, but those are segmentation-model results, not failures by Terra/Sol. This proposed direction has no local benchmark-backed LLM failure yet.

### Author pilot and findings

The [reproducible implementation](../../probes/cardiac-reconstruction/authoring/README.md) used native Patient001 (healthy source label), 30 frames, 36 unique directions, and label 127 for the LV cavity. Plane 37 represents the repeated 180-degree direction and is excluded. Sampling uses the source 5-degree radial convention, image midpoint as the rotation axis, and documented 0.089950 mm in-plane spacing. The origin along that axis is computed from plane 1 only. Physical pose conventions remain a fixture assumption to audit before qualification.

The CPU baseline samples cavity radius from each supplied contour, interpolates across azimuth and exports closed meshes with shared connectivity. It requires no training and fits each frame separately. The same eight withheld planes are evaluated in every sparse condition: 3, 8, 12, 17, 21, 26, 30, 35 (1-based), totaling 240 frame/plane pairs. These are correlated observations from **one patient**, not 240 independent cases. Source ED/ES indices are used only for evaluation, not fitting.

| Supplied contour views | Mean withheld Dice | Mean per-frame/plane HD95 | Volume-curve error vs dense comparator | EF error vs dense comparator |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.874 | 1.405 mm | 31.10% | 2.68 percentage points |
| 2 | 0.929 | 0.728 mm | 7.85% | 5.97 points |
| 4 | 0.937 | 0.626 mm | 2.38% | 0.59 points |
| 8 | 0.950 | 0.509 mm | 1.43% | 0.20 points |
| Static copy of four-view frame 1 | 0.825 | 1.662 mm | 76.57% | 63.79 points |

The dense comparator reconstructs from all 36 contours. Its source-fit Dice is 0.995; this is **not withheld accuracy**. Volume errors are mean absolute relative errors over all 30 frames. All EF differences evaluate filename frames 2 and 17, treating the config's ED_time=2 and ES_time=17 as one-based. **The config does not declare its index base; that interpretation remains unverified.** Derived EF under this interpretation is 63.79%, not independently measured clinical EF. The dense maximum-volume frame is 3, one frame away from the interpreted ED. Four-view minimum volume occurs at 19, versus interpreted ES=17. Audit indexing and annotation conventions before interpreting these differences as phase-selection errors or requiring exact frame IDs.

The successful execution took 21.1 seconds for reconstruction and evaluation on the local CPU, excluding downloads and viewer generation. All generated conditions had zero boundary edges, zero nonmanifold edges, zero degenerate triangles and positive signed volume. A closed-form sphere checks volume integration independently. Fixed radial vertex IDs are geometric correspondence, not verified tissue trajectories or strain.

The native source OBJ sequence has fixed connectivity and a closed two-surface cross-section consistent with a myocardial shell. Its physical coordinate transform and cavity surface partition were not established here. Its total enclosed volume must **not** be silently substituted for LV blood-pool volume or EF. The pilot therefore grades original held-out 2D masks and reports only derived 3D/EF comparisons.

A negative identifiability control scales the unobserved depth of the one-view mesh by a smooth factor ranging from 0.75 to 1.25. The observed plane is unchanged, but derived EF changes from 66.47% to 79.88%: **13.41 points**. These are two geometrically admissible completions of that plane, not two independently validated physiological hearts. Even two or several planes leave unobserved regions; extra views reduce ambiguity without proving unique recovery.

### Recommended task and calibration

**Bounded task:** given a calibrated one-cycle video set and optional preliminary LV contours, return `vertices[T,N,3]`, shared `faces[F,3]`, source frame IDs, ED/ES selections, a cavity volume curve, EF, and explicit units/assumptions. Use a supplied template/pretrained segmenter if appropriate so setup/training cost does not become the difficulty. Define the basal closure and papillary-muscle convention. An outer heart outline alone does not specify ventricular cavity volume.

Keep the difficulty axes separate:

1. **Geometry:** calibrated 8/4/2/1 views with the same contour quality. The first three are reconstruction tasks; the one-view condition must permit uncertainty/multiple compatible completions.
2. **Image interpretation:** clean contours → realistic preliminary contours → video only, keeping cases and views fixed. The local test covered clean contours only. Do not manufacture a hard case by hiding calibration needed for grading or imposing arbitrary runtime limits.
3. **Temporal reasoning:** correct phases and maintain cross-view timing; compare with framewise fitting, static, phase-shuffled and simple temporal smoothing controls. Independently acquired clinical views need a declared synchronization procedure and cycle-quality exclusions. Temporal smoothing must not erase genuine abnormal motion.
4. **Anatomy:** LV cavity first; add myocardium, then four chambers only after obtaining matched references. Valve leaflets require their own reference and finer spatial tolerance. These additions change the task, rather than merely increasing a scalar difficulty setting.
5. **Function:** EF/volume from the cavity mesh. Flow requires measured Doppler or a specified simulated flow model. `dV/dt` constrains net cavity volume change, not a spatial blood-velocity field or separate inflow/outflow. Under regurgitation, cavity stroke volume cannot simply be equated with forward flow. Diagnosis requires independently adjudicated labels and appropriate source views; do not label low EF as a disease diagnosis or transfer adult cutoffs to fetal cases.

For **development screening only**, the pilot suggests mean withheld Dice ≥0.90, mean pairwise HD95 ≤1.0 mm, volume-curve relative error ≤10%, EF error ≤5 percentage points, and valid closed positive-volume meshes. Four/eight views pass these derived-reference targets; two views fails EF and one fails geometry/volume. These are proposed composite gates chosen after the pilot, **not predeclared or validated final acceptance criteria**. Their ease for this simple baseline is evidence against claiming a hard clean-contour task.

Before freezing a benchmark, use distinct development and hidden patients; keep all phases/views of a patient in one split. Estimate inter/intra-observer uncertainty, inspect native-versus-interpolated frames, and lock thresholds against expert repeatability and simulator truth. Withhold entire viewing directions for real data; also score unseen 3D surface and temporal displacement on STRAUS after its units, transforms and cavity/wall labels are audited. No per-frame best-fit alignment should erase pose/scale errors. Evaluate ED/ES with timing error and an adjudicated near-extremum frame set, not just one exact index. Include per-case tail errors, not only cohort means. Freeze valid oracle/nop and strong baseline controls before any normal model trial.

**Disposition:** retain video/contour-conditioned dynamic LV reconstruction as plausible and visually useful. The clean-contour version is an author calibration, not an admitted hard task. Exact 4D recovery is best developed on audited simulation references, then checked against real held-out views. Four chambers, valve motion, flow and disease remain distinct untested extensions with the source gaps above. No Harbor/provider trials, external publication, access applications or messages were launched.

### Evidence

- [Pilot metrics](../evidence/br025-pilot-results.json) and [source audit](../evidence/br025-source-audit.json).
- Raw source bytes and 2,251-member extraction manifest: ignored `runs/br025-cardiac/source/native/`.
- Mesh arrays, raw metrics and standalone interactive viewer: ignored `runs/br025-cardiac/pilot-v1/`.
- The viewer supports view count, phase, playback and mesh rotation. It includes original ultrasound at a withheld direction and source/predicted contour overlays. It is local and is not part of the published interview site.
