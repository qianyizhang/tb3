# BR-004 — DICOM annotation difficulty revisit

**Completed follow-up:** one fresh Terra/max attempt per patient task, under the
[frozen single-patient protocol](BR-004-single-patient-benchmark.md). All eight
finished normally: five raw passes and three raw misses. Review retains two
controlled-defect failures and two source holds. [Results and resource comparison](../../catalog/analyses/br004-single-patient.md)
identify case-32 as the lead: 10.21 minutes, 23,713 output tokens, estimated $0.857.
The prior eight-patient timeout below remains a separate, excluded condition.

## Execution update — 2026-09-15

The user approved building the difficult test set and explicitly requested a
fresh **Terra/max** attempt. The implemented successor is
[`dicom-anatomy-audit`](../../probes/dicom-anatomy-audit/instruction.md), with a
fixed JSON audit report as the deliverable. Its
[authoring record](../../probes/dicom-anatomy-audit/authoring/notes.md) and
[v1 freeze](../evidence/br004-anatomy-audit-v1-freeze.json) own the executed scope.
The design below remains the earlier proposal, not a claim that all proposed
features were implemented.

The admitted cohort has eight independent source patients, 86 focus-label
decisions, four clean cases and five altered labels across four cases. It uses
two local omissions, a local adjacent-rib identity exchange, and a small kidney
mask extension. Exact labels and one 3-mm-tolerant spatial witness per altered
label make grading deterministic. Actual postoperative history was unavailable;
coverage/pathology controls were admitted, while ambiguous absence and narrow
muscle-boundary judgments were excluded. Postoperative discrimination remains
untested.

All eight CT/SEG source-to-loader checks and private evidence-coordinate checks
passed. The old saved checker missed all five altered labels on this cohort;
that remains a saved-program check, not a model result. The
[author controls](../evidence/br004-anatomy-author-controls.json) and
[source provenance](../evidence/br004-anatomy-source-provenance.json) retain the
evidence and limitations. Matching Harbor oracle/nop controls precede the one
authorized model attempt. Terra/max is an explicit change from the earlier
Terra/high default; the 1800-second budget is retained.

### Completed pilot outcome

**Terra/max timed out at 1,800 seconds without a final report.** Its extracted
JSON is the unchanged empty starter. The raw reward 0 and 4/8 passing cases
therefore describe the starter artifact, not model anatomical accuracy.
The [trial receipt](../evidence/br004-anatomy-round-summary.json) confirms
matching normal oracle 1 / nop 0 controls, an independent re-score, and intact
frozen bytes. The [authored analysis](../../catalog/analyses/br004-anatomy-audit.md)
and [trace receipt](../evidence/br004-anatomy-terra-trace-summary.json) explain
the exclusion and remaining source-admission questions.

Disposition: **complete, inconclusive; v1 parked**. One fresh Terra/max attempt,
zero completed model accuracy results, zero genuine failures. The proposed
next design is a two-patient, one-family batch with a matched clean control,
the same normal time budget, and complete review of its graded source regions.
This reduces review volume rather than manufacturing time pressure. No rerun
or post-result task changes were made. The local
[visual evidence report](../../runs/br004-v1/report.html) retains the CT/mask
comparisons and clearly separates unfinished-artifact grades from model results.

## Earlier design review — before implementation

The sections below preserve the initial intake, proposal and source screen.
Statements about work not yet curated or run describe that earlier stage;
the execution update above and completed-trial evidence own the current state.

### Intake and initial disposition

- Captured **2026-09-15**; state **captured**. The design review and saved-program
  diagnostic are complete; the proposed new patient cohort is not curated or run.
- Source: current [Codex conversation](codex://threads/01a0a248-241a-76b0-8ecf-15e259df9734).
  The initiating user message asks to revisit the previous anatomical checker,
  augment real labels with deliberately subtle errors, and curate unusual but
  possible anatomy, including surgery. Message UUID and conversation title are
  unavailable in the supplied context; this is a direct current-turn capture.
- Predecessor: [BR-003/H03](BR-003-work-history.md), catalog
  [`dicom-label-audit`](../../catalog/ideas/dicom-label-audit.json).
- Scope: user-directed revisit, source screen, and bounded author checks. No new
  model trial or submission qualification. The
  [benchmark-backed shortlist](../research-benchmark-backed.md) retains priority;
  this candidate has no demonstrated new Terra failure.

**Recommendation:** test whether annotations agree with the anatomy of this
particular patient. Combine believable annotation defects with correctly labeled
unusual anatomy. Keep the small checker deliverable and ordinary tool access.

## What the previous pass established

The original five packets share TotalSegmentator small v2.0.1 subject s1245 and
four focus labels. They contain two clean/coverage controls, a missing whole
heart, an opposite-side upper-lobe swap, and a contralateral rib replacement.
There was no graded `misplaced` finding despite that category being public.
Minor boundary errors were explicitly outside the contract.

The [saved Terra submission](../../runs/br003-audit-terra-high-v1-20260915/dicom-label-audit__PRbFdXR/artifacts/app/answer/auditor.py)
uses label presence, centroid laterality relative to the spine, and broad CT
tissue-intensity thresholds. It has no same-side rib-number or lobe-identity
check and no local contour-completeness check. Therefore its healthy pass was
evidence for this bounded fixture, not general anatomical QA.

### Completed author diagnostic

Re-executed the saved program, preserving its bytes, CT, focus labels and old
packets. Two additional SEG variants exchange complete voxel class assignments:

| Condition | Correct focus-label finding | Saved program output |
| --- | --- | --- |
| Original five packets | Original expected sets | **5/5 correct** |
| Right ribs 7 and 8 exchanged | `rib_right_7: misplaced` | `[]` — missed |
| Right upper and middle lung lobes exchanged | `lung_upper_lobe_right: misplaced` | `[]` — missed |

The exchanges preserve the combined foreground, patient side, and all unrelated
label voxels. highdicom source-reference reconstruction matches the authored
arrays exactly. These remain obvious identity changes on inspection; they are
an inexpensive baseline screen, not the proposed subtle-error cohort.

Receipt: [saved-program checks](../evidence/br004-saved-auditor-check.json).
Raw script and SEG variants remain in `runs/br004-revisit/`. Local reproduction:

```bash
.venv-br003/bin/python runs/br004-revisit/check_saved.py
```

The local script requires the retained BR-003 raw artifacts. macOS NumPy emitted
matrix-multiplication warnings during CT sampling. An observation wrapper returned
the original samples and compared all 22 calls with an elementwise coordinate
calculation: every sample array was finite and exactly equal. The receipt retains
the warnings. This cross-check addresses numeric execution, not clinical truth.

**Denominators:** one source patient, two new correlated perturbations, zero new
model attempts. These are failures of the saved program under author checks,
not fresh Terra failures. The retired BR-003 snapshot and its evidence remain intact.

## Proposed candidate — BR-004/A01, `dicom-label-audit`

### Task and hypothesis

- **Task:** implement an offline `audit(ct_dir, segmentation_path, focus_labels)`
  checker. Return label-level annotation findings. Supply the full vocabulary
  and CT/SEG inspection tools, without a public organ-relation rule list.
- **Crux:** distinguish a real annotation defect from legitimate patient-specific
  absence, shape, position or scan coverage.
- **Hypothesis:** coarse global plausibility checks miss localized, plausible
  errors; stronger atlas/count rules increase false alarms on unusual anatomy.
- **Evidence against it:** a fresh model builds a compact checker that handles
  both the defect cases and the clean unusual cases under the frozen contract.

### Error families, in priority order

| Family | Deliberate change to a reviewed real mask | Why existing checks can miss it | Necessary matched control |
| --- | --- | --- | --- |
| Same-side identity | Adjacent rib relabeling; same-side lobe relabeling | Side and tissue class remain plausible | Correctly labeled neighboring structures, with enough landmarks to resolve identity |
| Focal omission | Remove an interior slab or a visible terminal portion, leaving most of the organ labeled | Presence, centroid and median intensity barely change | Natural taper, scan-edge truncation, and an actual reviewed surgical remnant |
| Focal misassignment | Transfer a small, contiguous region to an adjacent label with similar tissue intensity | Whole-organ averages hide a local disagreement | Valid close contact between structures and an accepted boundary-tolerance control |

Start from reviewed masks and change annotations only. Prefer coherent editing
mistakes to random voxel noise. A proposed initial size band is 1–5% of the target
volume, but it is not a grading threshold: admission depends on a clearly visible
wrong region at the native scan resolution. Preserve the native resolution where
3-mm sampling would erase the feature. Do not tune severity after seeing model
results, or call an ambiguous one-voxel boundary difference an error.

Minor/local errors require an explicit new public contract. The old gross-error
contract cannot fairly be used to grade them retroactively. Proposed categories
are `missing`, `wrong_side`, `misplaced`, `partial_omission`, and `leakage`;
define precedence and exact semantics before freezing. Keep borderline contours
outside the primary binary evaluation.

### Patient curation priorities

| Priority | Real anatomy to seek | Correct behavior and paired error contrast |
| --- | --- | --- |
| 1 | Confirmed nephrectomy or splenectomy, with adequate regional CT coverage | Accept the truly absent structure; flag a deleted annotation of a structure actually visible in another case. On the postoperative case, inject an independent defect in remaining visible anatomy. |
| 1 | Confirmed lung resection with remaining anatomy visibly displaced | Accept correctly labeled absent/repositioned structures; flag a local omission or identity error in a remaining structure. |
| 2 | Congenital position/count variants with explicit label semantics | Use as clean false-alarm controls only after identity and annotation convention are unambiguous. |
| Defer | Transplants, fused kidneys, transitional vertebral numbering | Potentially useful, but donor identity versus location and numbering conventions can make a fixed label ontology ambiguous. Resolve the contract before admitting them. |

A removed organ is not created by deleting its annotation. Do not call an empty
mask proof of surgery, use a mirrored ordinary CT as a real congenital case, or
invent operative history. Acquire a real deidentified source with usable rights;
retain case-level provenance, scan coverage, label convention and adjudication.
If images alone cannot establish the needed distinction, add genuine available
context and declare that information condition, or exclude the case. Do not
silently grade against clinical facts withheld from the participant.

For each admitted source, retain privately: source/version/license and hashes;
the original and reviewed masks; the reviewer and actual review status; the
region supporting absence or unusual anatomy; mutation and seed; discrepancy
voxels in patient coordinates; and an orthogonal CT/overlay review. Surgical
claims need source evidence or qualified review. None is claimed completed here.

### Small cohort and verification

Proposed first cohort: **eight independent patients, one visible packet each**.
Balance four clean and four corrupted packets, with two ordinary and two altered
anatomy patients in each annotation condition. Use one error family first;
reserve other families for separately frozen contrasts. If sufficient reviewed
postoperative cases cannot be sourced, report the smaller feasible design rather
than fabricate replacements. Each private source may have clean/mutated versions
for author controls, but do not expose both versions of the same patient in the
agent's batch: direct comparison could reveal the injected edit.

- Keep the focus-label list balanced: requested does not imply defective. Mix
  untouched labels and clean packets; keep defect counts private.
- Use a few separate development examples. If held-out patients are introduced,
  state that change from the fixed BR-003 packet contract explicitly. Keep all
  versions/crops of a patient in one split. Do not claim unseen-patient generality
  from the original inspectable one-patient fixture.
- Private truth comes from reviewed source anatomy plus the authored mutation
  map. The grader compares submitted findings to that truth; it does not reuse
  the submitted algorithm or the old centroid-based reference as its oracle.
- Add one patient-coordinate witness point per finding only if needed to reject
  guesses. Accept a point in a predeclared discrepancy region/tolerance; do not
  require prose to match an LLM judge. Freeze witness semantics before trials.
- Report defect recall and false-positive rates on clean ordinary and clean
  altered anatomy separately, with raw label and patient denominators. Require
  exact finding sets for the small deterministic diagnostic and publish any
  localization tolerance in its contract. Whole-mask Dice is supplementary:
  deleting 2% of a mask leaves Dice about 0.990, which can conceal a clear local
  omission. Do not use average Dice to grade an audit-finding list.
- Author controls: validated reference, no-findings baseline, flag-everything
  baseline, saved BR-003 checker, and a strong permitted image-aware baseline.
  Confirm clean cases reject over-flagging and each admitted defect is decidable.
  DICOM round-trip checks establish encoding only.
- Keep ordinary libraries, image rendering and model/runtime access available
  under the owning protocol. Supply a tested geometry reader if decoding has
  become incidental to the anatomy question. Verify enough time and memory;
  neither shorter reasoning budgets nor extra setup supplies the difficulty.

### Proposed execution and stop rule

First curate the smallest decidable real cases, establish the independent
reference and controls, and freeze task bytes, patient assignment and error
severity. Then use the existing Terra/high diagnostic protocol with its normal
time budget and capture tool/image access and all run settings. No model run is
launched by this document. Final submission gates remain in
[requirements.md](../requirements.md).

A healthy pass retires the tested snapshot. For a miss, inspect whether the
submitted checker missed visible tissue, over-applied ordinary anatomy, or
failed in implementation. Unclear anatomy, source-label errors, encoding faults,
crashes, and timeouts do not support the conceptual hypothesis. A frozen CT-only
versus genuinely available clinical-context contrast can isolate reliance on
history later; it is not a reason to withhold necessary evidence in the main task.

## Source screen and retrieval limits

1. [TotalSegmentator small v2.0.1](https://zenodo.org/records/10047263) provides
   102 subjects and is the licensed source of the existing fixture. Its locally
   retained metadata has pathology/coverage fields but no operation-history
   field. **No confirmed postoperative subject was identified in this revisit.**
2. [Touchstone, NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/1b8726b572e0dfa72793f9f6590664fd-Paper-Datasets_and_Benchmarks_Track.pdf),
   section 4, reports annotation errors and inconsistent labeling standards in
   multi-organ datasets. This supports reviewing source truth rather than treating
   released masks as flawless. It is segmentation benchmark evidence, not a
   task-level Terra failure for an annotation checker.
3. [MRSegmentator study](https://pubs.rsna.org/doi/10.1148/ryai.240777) illustrates
   correct nonsegmentation after nephrectomy. This is a primary research example
   of the proposed negative control, not a verified downloadable postoperative
   CT/SEG case; do not transfer its MRI example into the CT cohort by assertion.
4. [Kimpton et al., postoperative case report](https://pubmed.ncbi.nlm.nih.gov/26101303/)
   documents mediastinal repositioning following pneumonectomy. It is a clinical
   plausibility lead, not a reusable volumetric segmentation fixture.

These sources motivate curation. They provide no new coding-agent difficulty
result. Surgical sourcing and clinical adjudication are the main unresolved
work; simply adding more ordinary scans would not test the intended distinction.

## Outcomes and dated decisions

| Condition | Validity / result | Hypothesis support | Disposition |
| --- | --- | --- | --- |
| Saved checker, original packets | 5/5 reproduced locally | Reconfirms bounded earlier pass | Preserve retired BR-003 snapshot |
| Saved checker, two same-side exchanges | Exact encoding checks; 0/2 detected | Concrete gap in this saved program only | Use as baseline controls |
| Subtle local defects and real postoperative controls | Not curated; no model run | Unknown | Proposed next bounded experiment |

- **2026-09-15:** capture user-requested revisit as BR-004; complete the two
  saved-program contrasts; retain all earlier outcomes. Keep catalog status
  `calibration` until new evidence supports a different disposition.
