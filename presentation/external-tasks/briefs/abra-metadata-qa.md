> **Mixed teaching illustration — the generated ABRA task and live metadata response are absent here; obtain the configured study and generate the task through official ABRA setup.** [Official acquisition/setup route](https://github.com/Luab/ABRA/tree/688814615dc368a66276798cb864fe9a587d7e6c).

# Answer questions about ABRA study metadata

Find the requested field at the study, series or instance level, then submit one formatted answer. The pinned LIDC-IDRI-0003 manifest is a real source-metadata teaching example; it is **not** an observed generated task, viewer response or participant result.

## Given

### Original data

A generated ABRA task gives a StudyInstanceUID and a metadata question. The configured OHIF/Orthanc study is meant to be queried through `get_study_metadata` or `get_study_series`. A retained source manifest has **1 study, 27 series and 166 instances**: 1 CT series with 140 instances, 13 SEG series with 1 instance each, and 13 SR series with 1 instance each. These are manifest counts; only 140 CT DICOMs are locally recovered. A local CT ZIP corroborates its study/CT-series UIDs and 140 DICOM members, but its pixels and raw patient metadata are not in this teaching pack. Neither a generated task instance nor a viewer tool response was run or retained.

### Supplied helpers

The task specifies the requested answer format. `get_study_metadata(study_uid)` exposes StudyDate, seriesCount and a series summary; `get_study_series(study_uid)` exposes each series' Modality, SeriesInstanceUID and instanceCount (with only the first three instance examples). These are legitimate solver-visible fields, even when one contains the requested answer. The manifest example is reader context, not a saved tool response.

### Callable tools

`get_study_metadata`, `get_study_series` and terminal `submit_answer`; the generator sets an eight-turn limit. No task, tool, participant or scorer run is represented here.

### Reference-only material

The generator constructs `expected_outcome.answer` from its `StudyInfo` record. That evaluator field and any participant submission are not bundled. Deriving an answer from permitted metadata is the work, not a reference leak.

## Task specification

The five generator families ask for: first CT series instance count; all-series count; sorted distinct modalities; StudyDate as `YYYYMMDD`; or first CT SeriesInstanceUID. Count all modalities for the series question, but instances only within the selected CT series for the slice-count question.

## Expected output

Output is a single `submit_answer.arguments.answer` string: an integer, date, comma-separated modality list or exact UID as requested. This pack leaves the participant answer slot empty. The modality operation deduplicates series Modality values and sorts lexicographically before joining with comma + space; it does not sort patient slices or series UIDs. The source-derived teaching list is `CT, SEG, SR`.

## Evaluation

The pinned exact-match scorer searches the trajectory backwards for the last `submit_answer` call, normalizes lowercase and whitespace, removes common numeric unit suffixes, and also accepts numeric difference strictly below 0.01. It scores that submitted string against generator state. It does not establish image interpretation quality, and no score is retained here.

## Visual explanation

A three-level study → series → instance hierarchy follows the five question families. The actual manifest rows are source evidence, not task-run output; the terminal answer field stays blank, and the evaluator's `expected_outcome` is described only after reference reveal. No patient image or fabricated response appears. A separate toy formatting fixture uses authored records, clearly marked illustrative; comparison stays covered until explicit reader reveal and returns covered on reset. It is not a patient answer, participant result or evaluator reference.

## Limits and source route

The local 140-DICOM ZIP matches the manifest study and CT-series UIDs, but its file order is not viewer slice order. It does not prove an OHIF tool response or a generated task instance. The ZIP embeds LIDC-IDRI CC BY 3.0 and TCIA usage/attribution terms; raw DICOM stays local. Reopen an observed case explanation only with a pinned generated task JSON, tool response, participant trajectory and independent result review.

## Sources

- [Pinned generator](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/scripts/task_generators/tier2.py)
- [Pinned scorer](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/src/scoring/outcome/exact_match_scorer.py)
- [Pinned tool registry](https://github.com/Luab/ABRA/blob/688814615dc368a66276798cb864fe9a587d7e6c/src/tasks/tool_registry.py)
- [Source receipt](../sources/abra-metadata-qa-resolution.json)

## Conditions

| Condition | Supplied help | Work remaining |
|---|---|---|
| Metadata QA | Study UID, precise query, answer format and two metadata tools. | Select the right hierarchy level, read the right field and submit only its requested string. |

## Coverage

This defines one metadata-QA task family. The source example is not evidence that every generated case or its viewer state was recovered.
