# BR-037: longitudinal MRI reading

This is a source-grounded, exploratory clinical-imaging pilot. The task asks an
agent to discover and compare findings across two full examinations with minimal
background. It is not a clinically validated benchmark, a rare-disease test, or
a final TB3 submission. See [design](../../docs/research-rounds/BR-037-longitudinal-reading.md)
and [results](../../docs/research-rounds/BR-037-results.md).

## Separation of evidence

- `authoring/instruction.md`: neutral deliverables, common to all patients.
- `runs/br037-longitudinal-reading/source/`: original scans, official tables,
  dictionaries and host-only core-lab references. Ignored; never solver-mounted.
- `prepared/`: full native-grid NIfTI conversions for four examinations.
- `tasks/`: frozen runnable packets, first two visits only, without patient IDs,
  derived core-lab objects, annotations, outcomes or future images.
- `grounding.json`: source trajectories and independent core-lab regions.
- `review-rubric.json`: qualitative review criteria, frozen before reading final
  agent answers but after trial launch. The source targets and case selection
  were frozen before launch. There is no aggregate clinical reward.
- `runs/br037-*/`: real Harbor attempts, tool traces and answer artifacts.
- `results.json` and `*-visible-trace.json`: private local collection of completed
  outputs and observable operations. Hidden reasoning is not used in the review.

All paths above without an explicit prefix are inside
`runs/br037-longitudinal-reading/`. Download receipts and prepared artifacts have
SHA-256 hashes. Public data can have unknown training exposure despite withholding
identifiers and prohibiting case-outcome retrieval during these trials.

## Reproduction

The existing `.venv-br037` contains idc-index 0.12.5, idc-index-data 24.2.2,
pydicom 3.0.2, nibabel 5.4.2, NumPy, SciPy, Pillow and matplotlib. Workbook/PDF
extraction used the Codex bundled Python with openpyxl and pypdf. Downloads use
official TCIA metadata and the official IDC client. These are downloads of public
data, not authorization to access the controlled brain collection.

Authoring stages, in dependency order:

1. `fetch_metadata.py`, `read_tables.py`, `read_brain_tables.py`, `triage.py`,
   `triage_brain.py`: source receipts, dictionaries and source-ordered selection.
2. `download_cases.py`, `download_references.py`: full originals and separate
   host-only reference objects. No core-lab VOLSER or SEG enters the task.
3. `convert.py P01` (then P02/P03): native pixels and DICOM-to-RAS geometry,
   orientation/plane splitting, sampled exact pixel checks. Existing completed
   conversions are protected against overwrite.
4. `ground.py`, `review_images.py P01` (then P02/P03), `package.py`: reference
   reconciliation, curator views and frozen packets. Inspect CLI before invoking;
   package/trial functions intentionally refuse overwrite.
5. `run.py p01-neutral all` (then p02-neutral, p03-neutral, p03-cue): one contract
   fixture, one no-op, one Terra/high attempt per condition. An existing private
   Harbor runtime configuration supplies provider settings. No credentials are
   stored in this tracked directory. No retry or Sol fallback is automatic.
6. `audit_packet.py CONDITION IMAGE`: inspect an isolated built solver image;
   verify frozen data hashes and absence of verifier/solution mounts.
7. `collect.py`, `plot_references.py`: collect completed attempts, source-region
   geometry, model/effort receipts and observable tool operations; render the
   host-only trajectory chart. These do not start another model trial.
8. `audit_measurements.py`, `phase_review.py`, `receipts.py`: post-trial arithmetic
   reproduction, phase-selection review and safe compact evidence export.

The oracle control is **only a contract fixture**. Passing it demonstrates that a
well-formed answer can be collected and checked. It does not validate diagnosis,
lesion correspondence, clinical measurement or forecasting. Clinical/source
disagreements need authored review and, where unresolved, expert adjudication.

## Known measurement limits

The released longest-diameter workbook does not explicitly state units. The
initial host rubric provisionally interpreted them as cm; final analysis must
flag this assumption and use unit-invariant percentage changes for firm numeric
contrasts. No absolute millimeter clinical error threshold is justified here.
FTV is an enhancement-thresholded volume, not diameter or pathology. A source
VOI is an enclosing region, not an exact contour. Inside-VOI citation agreement
therefore supports localization but cannot certify every image interpretation.

The generic native-slice renderer requires the agent to use affine geometry for
laterality. Separate-volume dynamic acquisitions retain order but lack useful
cross-series time intervals in the whitelist. Neither issue should be mistaken
for a proven failure of diagnostic reasoning. Frozen packets are preserved.
