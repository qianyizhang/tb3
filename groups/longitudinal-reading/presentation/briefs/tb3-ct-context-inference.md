# Infer only clinical context supported by CT

**A CT-only context assessment should connect each claim to evidence and retain justified unknowns.** In the one retained Astra-medium attempt, two of nine fields were inferred and seven marked unknown. Those counts are not an accuracy score.

## Given

### Original data

deidentified baseline and follow-up full CT volumes, 512 × 512 × 615 and 512 × 512 × 743 voxels, with cleaned NIfTI headers. Native i/j/k axes increase L/P/S; affines map to RAS millimeters.

### Supplied helpers

earlier/later ordering only; explicit permission to answer unknown. No clinical record, dates, demographics, diagnosis, locations, reference masks or earlier model output.

### Callable tools

installed NiBabel, NumPy and Pillow were used for header inspection, sampled axial/coronal surveys and focused views. This was not exhaustive lesion review.

### Reference-only material

independently retained patient CSV age/sex/interval and cohort diagnosis/treatment/purpose were withheld. Individual operative records, treatment dates and regimen are unavailable. The independent context-supplied lesion session did not receive this inference output.

## Task specification

Inspect available images and headers. Separate visible observations from hypotheses and unavailable history. Return `context.json` with all nine requested fields: broad diagnosis, specific primary, age, recorded sex, interval, baseline/follow-up purposes, systemic treatment and surgical context. Each has status, value, confidence, basis and alternatives; unknown uses a null value. The companion report states method, limits and zero-based native evidence coordinates.

## Expected output

`context.json` with all nine field records and a companion `report.md` with method, native coordinates and limits.

The retained answer infers suspected metastatic liver disease and probable prior right inguinal/local intervention. It leaves the other seven fields unknown; melanoma is an alternative, not exact identification. Numeric confidences describe the submitted assessments and have no measured calibration. The surgical suggestion lacks an individual reference for adjudication.

## Evaluation

**Mechanical validity only:** the frozen validator checks field structure and a nonempty report; it returns no scientific score. Its saved result replays exactly. Author-created all-unknown and unsupported-assertion outputs both pass; inconsistent unknown/value and missing-report variants fail. These four diagnostics are saved-output checks, not new model trials or corrections to original rewards.

The model and oracle originally received reward 1; no-op received 0. One model session took 207.37 seconds and retained 14 image observation blocks, including montages. Blocks do not count distinct native slices. Coincidental agreement with hidden metadata does not establish CT-only identifiability; one patient cannot establish diagnostic performance.

## Difficulty

Plausible image hypotheses are weaker than a clinical record. Missing history may justify abstention; a schema pass cannot adjudicate diagnostic support.

## Visual explanation

The [canonical story](../stories/ct-context.story.md) uses four native axial crops at the agent's cited liver and groin planes. The input view precedes amber point/region overlays. Those overlays are submitted evidence citations, not supplied hints, segmentation or GT. Grayscale uses HU −40 to 140; i increases right and j down, patient right on image left. No resampling or registration is performed. Metadata appears only through the reader reference reveal, with patient, cohort and unavailable facts separated.

### Workflow

- Inspect native images and headers without private context.
- Connect qualified claims and unknowns to evidence.
- Reveal source levels and explain the mechanical validator boundary.

## Sources

- [Frozen experiment condition](../../experiments/longitudinal-ct-context-inference-astra-medium/protocol.md)
- [Exact instruction](../../methods/longitudinal-ct-context-v1/inference-instruction.md)
- [Predeclared two-condition design](../../methods/longitudinal-ct-context-v1/protocol.md)
- [Existing finding and field-by-field interpretation](../../findings/longitudinal-ct-context-hypothesis.md)
- [Retained source audit and saved-output diagnostics](../sources/ct-context-audit.json)
- [Source derivation and license](../../../../presentation/task-explorer/ct-context/NOTICE.md)
