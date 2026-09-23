# CAMELYON whole-slide metastasis search — Sol 6 xhigh

Can `openai/gpt-6-sol` at xhigh find metastatic tissue by navigating the full `tumor_091` lymph-node WSI? This selected positive slide has relatively large regions; a diagnostic result cannot establish sparse-lesion sensitivity or negative-answer specificity.

The solver sees a neutral TIFF, GT-free overview, physical scale and crop helper, then returns level-0 point locations with confidence. The XML is evaluator-only. The diagnostic scorer reports the fraction of six Tumor polygons containing a point, supported and outside-reference points, and points falling in the Exclusion polygon. These are polygon hits, not independent-lesion counts or clinical stage. The crop ledger describes tool use but does not enforce a read budget because direct TIFF reads remain possible.

Use `openai/gpt-6-sol` xhigh, one 3600-second attempt, no automatic retry, Docker 4 CPUs/12 GiB/0 GPUs, and existing restricted transport. Preview and run oracle/no-op controls before dispatch. Do not promote the task until appropriate negative and small-lesion cases, polygon merging, exclusion, and score domain rules are frozen. Stop on source mismatch, leakage, invalid controls or infrastructure failure. Apply the one-time quota preflight in `docs/workflow.md`; a lower-cost condition or shorter timeout requires user acceptance before launch.

## Question and method

## Inputs and reference

## Findings and limits
