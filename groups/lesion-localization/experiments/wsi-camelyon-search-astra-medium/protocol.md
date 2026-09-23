# CAMELYON whole-slide metastasis search — Astra medium

Can `openai/gpt-6-astra` at medium find metastatic tissue by navigating the full `tumor_091` lymph-node WSI? This selected positive slide has relatively large regions; a diagnostic result cannot establish sparse-lesion sensitivity or negative-answer specificity.

The solver sees a neutral TIFF, GT-free overview, physical scale and crop helper, then returns level-0 point locations with confidence. The XML is evaluator-only. The diagnostic scorer reports the fraction of six Tumor polygons containing a point, supported and outside-reference points, and points falling in the Exclusion polygon. These are polygon hits, not independent-lesion counts or clinical stage. The crop ledger describes tool use but does not enforce a read budget because direct TIFF reads remain possible.

Use `openai/gpt-6-astra` medium, one 3600-second attempt, no automatic retry, Docker 4 CPUs/12 GiB/0 GPUs, and existing restricted transport. Preview and run oracle/no-op controls before dispatch. Do not promote the task until appropriate negative and small-lesion cases, polygon merging, exclusion, and score domain rules are frozen. Stop on source mismatch, leakage, invalid controls, infrastructure failure or weekly Codex usage below a 20% reserve.

## Question and method

## Inputs and reference

## Findings and limits

### Diagnostic observation — 2026-09-23

`attempt-fc12d5620c0b4d15` completed with `gpt-6-astra` medium in Harbor, no terminal exception, and unchanged frozen task bytes. Its valid-artifact `reward=1` is separate from the private score in `observation-950002481d2bb6163a60f449`: 7 submitted points, 4 of 6 Tumor polygons with at least one point, 4 reference-supported points, 3 points outside Tumor polygons, and 0 in the Exclusion polygon. Polygons are not independent connected lesions; this is a polygon-hit fraction of 0.667, not lesion sensitivity. The crop helper logged 8 calls, without enforcing all possible reads. The inspected 11 shell commands showed no explicit access to private `tests/` or `solution/` paths. This one positive slide with relatively large regions cannot measure negative-answer specificity or sparse metastasis sensitivity. Review outside-reference points and add negative/small-lesion cases before any task promotion.
