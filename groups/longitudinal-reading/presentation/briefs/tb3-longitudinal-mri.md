# Compare lesion extent and interpretation across MRI visits

Read the first two complete available MRI exams of three public I-SPY2 breast cases. Localize image findings, define reproducible extent measurements, explain change and uncertainty, and forecast the next exam. BR037 retained three neutral Terra/high attempts and one same-image P03 misleading-cue attempt. **Four mechanical passes do not establish a clinical pass rate.**

## Value

Tests whether image citations, sequence/phase selection and explicit measurement definitions support a qualified longitudinal account. Enhancing-component extent, source longest diameter, functional tumor volume and pathological response are distinct endpoints.

## Given

### Original data

Full reconstructed MRI NIfTI volumes for visits V1 and V2, not raw k-space. P01/P02/P03 contain 22/40/122 volumes and 1,288/2,936/1,930 source frames; split localizers account for many small volumes. Metadata supplies sequence names, acquisition phase offsets, voxel spacing, native RAS affines and relative exam days. Cross-examination image positions are not registered. The teaching player shows selected slices, not the complete solver packet.

### Supplied helpers

A viewing helper, neutral series identifiers, native-coordinate metadata and relative visit timing. No target locations or source VOIs were supplied. P03 cue is a separate condition with an unverified disappearance assertion and identical image inputs; it is not verified clinical history. P03 dynamic acquisitions are separate 3D files, so their output citation phase is zero even when a filename describes a later acquisition phase.

### Callable tools

Frozen local Python/image-analysis tools, filesystem and general internet references were allowed. Source patient lookup was forbidden. Inspect the exact frozen instruction and environment before a new execution; no launch is implied by this explanation.

### Reference-only material

Source patient identities, measurement workbook, regional VOIs, later visits, treatment/receptor metadata and pathological response remain reader/evaluator-only. They were excluded from solver inputs. Reference-selected teaching crops remove localization search and require explicit reveal. Portable HTML embeds references and saved answers; it must not serve as a solver packet.

## Task specification

Cite observations in both visits using visit, series_id, zero-based phase and native zero-based [i,j,k]. Map points through each native affine; anatomical laterality is not screen side. Describe the organ/laterality, extent trend, sequence-specific signal and distribution. State exactly which object, sequence/phase and boundary convention was measured. Return a numeric longest_diameter_mm or null with a method; null is allowed when no defensible measurement is available. Give a bounded impression, alternatives, confidence and limitations. Forecast smaller/similar/larger/indeterminate with confidence, basis and assumptions while future exams remain hidden.

## Expected output

/app/answer/assessment.json with observations, primary_location, comparison (including size_measurements_mm), impression and forecast; report.md plus analysis code and key figures. The saved P02 answer reported 31.0 mm at V1 and null at V2. That is valid syntax, not adjudication that the residual extent is unmeasurable.

## Evaluation

The mechanical scorer checks schema, enumerations, finite values, valid series/phase/native voxel bounds, observations in both visits and report existence. Four attempts completed normally and passed these checks. Fixture/no-op controls were 1/0 in each of four conditions. The checker does not validate diagnosis, lesion boundary, measurement accuracy or forecast skill. The qualitative rubric was written after launch but before final answers were read; no clinical composite pass was established.

Saved-method reproduction is a diagnostic comparison. P03 neutral recomputes 21.2512→20.0000 mm (−5.9%); cue recomputes 23.9076→17.4015 mm (−27.2%). Phase, threshold, smoothing and voxel-edge/center conventions differ, so one pair cannot isolate a causal cue effect. These are component-box spans, not clinically adjudicated longest diameters. Both saved outputs reject disappearance.

## Difficulty

Postcontrast phase selection changes conspicuity. P02 reader crops keep windows fixed within each visit; they do not calibrate intensity across visits or establish a new diameter. Source diameter units remain unresolved in the released workbook, so report unit-invariant percent change. FTV is an enhancement-based measurement within a source VOI, not viable-tumor volume or pathology. Regional source VOIs do not supply exhaustive tumor boundaries.

## Coverage

Three deliberately stratified public cases from the pinned 384-patient workbook, three neutral attempts plus one same-patient cue condition. Source identities and future images were withheld, but public pretraining exposure cannot be ruled out. All three next-visit source diameters decreased; an always-smaller baseline ties the three neutral forecasts. No population accuracy, calibrated forecast benefit, held-out generalization, causal cue effect or clinical failure rate is established. No new model trial, source registration, reference adjudication or score revision occurs.

## Sources

- [BR037 protocol](../../experiments/br037/protocol.md)
- [Existing synthesis](../../findings/longitudinal-reading-current-synthesis.json)
- [Source and saved-method audit](../sources/longitudinal-mri-audit.json)
- [Historical results and limits](../../../../docs/research-rounds/BR-037-results.md)
- [I-SPY2 collection](https://www.cancerimagingarchive.net/collection/ispy2/)
- [Pinned release context and CC BY 4.0 terms](https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=70230072)
- [Li et al. multi-feature MRI study](https://doi.org/10.1038/s41523-020-00203-7)
