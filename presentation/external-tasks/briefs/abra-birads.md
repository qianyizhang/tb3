# Produce a structured breast MRI assessment

**Mixed illustration — series metadata only; matching MRI pixels, generated report and submitted answer are absent.** [Obtain matching images and clinical data from the official TCIA collection](https://www.cancerimagingarchive.net/collection/duke-breast-cancer-mri/).

The visual condition asks an agent to inspect breast MRI and submit structured fields. The separate oracle condition supplies answer-bearing constructed findings. This explanation shows pinned source metadata and code contracts; it establishes no diagnostic result.

## Value

A structured report makes field submission and reference agreement inspectable. Agreement with ABRA's constructed fields does not independently validate breast MRI interpretation.

## Given

### Original data

Tier-4 generation requires a StudyInstanceUID-matched report in locally generated `duke_breast_reports.json` and at least one MR series. It chooses the report's DCE series UID, or the first MR series as fallback. The retained public manifest contains Breast_MRI_008 series records, including six MR series and one SEG series. This pack includes metadata only. Manifest order is not DCE acquisition order; series descriptions alone do not establish lesion laterality, enhancement or category. The official collection cautions that replaced dummy FrameOfReferenceUID values may be unreliable for alignment.

### Supplied helpers

Visual assessment receives MR series metadata, OHIF/Orthanc navigation and the `breast_mri` image preprocessor. It uses conditional rescale and per-image 1st/99th percentile display windowing; MRI display values are not HU or quantitative enhancement measurements. The oracle condition instead exposes exact report-derived fields through `query_birads_model` for the matching series UID. This removes visual discovery and is a different assistance condition.

### Callable tools

The visual task uses `get_study_series`, `select_series`, `set_viewport_slice`, `get_dicom_image` and terminal `submit_birads_report`. The oracle task adds `query_birads_model(series_uid=...)`. The pinned worker dispatches that query to in-task `oracle_data`, validates the UID and returns its overview; no learned CAD inference occurs in that path. None of these tools was called here.

### Reference-only material

The loaded task YAML has scorer `expected_outcome`; the oracle YAML also embeds `oracle_data`. Source code builds the agent's system prompt from task description and initial viewer context, while the oracle tool explicitly returns answer fields. Runtime filesystem isolation remains unaudited. No generated task/report or private patient-reference asset is included. The reader's explicit derivation reveal explains general source-code policy, not a patient answer.

## Task specification

The visual condition declares vision enabled, `breast_mri` preprocessing and 20 turns. Its reference trajectory queries series, selects up to four MR series, requests three slice/image pairs per selected series, and submits a report. This prescribed trajectory is not an observed agent trace. The oracle condition disables vision, allows 10 turns and requires correct-UID query followed by field relay.

## Expected output

A terminal `submit_birads_report` call must supply `laterality` (`left|right|bilateral`), integer `lesion_count`, integer `birads_category` (`0..6`) and boolean `enhancement_present`. Optional quadrant is read by the scorer from `findings[0].location_quadrant`, not a top-level submission field. All patient output values, oracle responses, submitted reports and scores remain unset here.

## Evaluation

The scorer selects the latest successful report submission from the trajectory. It weights laterality **0.25**, category **0.30**, count **0.20** and enhancement **0.15**. Optional quadrant contributes **0.10** only when an expected quadrant exists, changing the denominator from **0.90 to 1.00**. It rounds normalized weighted agreement to four decimals. Morphology, size and recommendation are captured but unscored. No scorer was executed.

## Reference construction and limits

The clinical derivation merges spreadsheet fields with downloaded DICOM UIDs. It assigns category **5** by code from cohort membership and sets enhancement to **true** by rule. These are not independent MRI assessments. It maps multifocality to count **2 or 1**, rather than independently enumerating lesions, and normalizes laterality with position fallback and bilateral override. Its custom quadrant mapping is another constructed field. DCE selection uses description keyword priority, then any-MR fallback.

For expected category 5/6, submitted 5/6 receive full category credit, 4 receives 0.5 and 3 receives 0.2. Count ±1 receives half credit; missing expected laterality receives full laterality credit. These scoring rules measure agreement with constructed targets. They do not demonstrate diagnostic quality, sensitivity, calibration or clinical adequacy.

## Visual explanation

Start with the real unordered series list and empty image sockets. Compare visual and oracle assistance paths without generating a patient enhancement image. Inspect the required report schema with blank values. Reveal general target-construction rules explicitly, then inspect scorer weights and optional-quadrant denominator. The settled output remains an unsubmitted report schema with no score.

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Visual assessment | Series list and rendered breast MRI. | Find enhancing lesions and assign report fields. |
| Oracle findings | Prepared findings returned by query_birads_model. | Query the correct series and submit the returned fields correctly. |

## Difficulty

The visual condition requires reviewing actual images across sequences; source-manifest descriptions cannot replace that work. The oracle condition largely removes perception and tests correct query/submission. The illustration executes neither condition.

## Sources

- [Pinned tier-4 generator](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/scripts/task_generators/tier4_birads.py) and [tier-3 oracle generator](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/scripts/task_generators/tier3_oracle_birads.py).
- [Clinical target derivation](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/data/annotations/duke_breast_clinical.py), [scorer](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/src/scoring/outcome/birads_report_scorer.py) and [worker routing](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/src/controller/task_worker.py).
- [Official Duke dataset and acquisition](https://www.cancerimagingarchive.net/collection/duke-breast-cancer-mri/) and [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/); data DOI `10.7937/TCIA.e3sv-re93`.
- [Source resolution receipt](../sources/abra-birads-resolution.json).

## Coverage

A shared definition brief for the linked catalogue entries. Case identities and source conditions remain in the catalogue; this is not a claim to enumerate all generated or external cases.

## Gaps

Fresh pinned report retrieval returned 404; matching-series HEAD timed out. Neither proves a dataset restriction. Matching MRI pixels, exact generated task/report, submitted report and score remain absent. Reopen clinical-image claims only with matched data, separated grader staging and independent reference adjudication.
