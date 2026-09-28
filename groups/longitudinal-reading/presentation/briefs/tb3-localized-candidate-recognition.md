# Judge supplied CT candidates before linking them

Inspect two supplied native CT locations, record explicit judgments, and segment/link only accepted tumor candidates. The retained result is a disagreement with the selected source reference after location assistance; clinical correctness remains unresolved.

## Value

Separates an unexplained whole-volume omission from explicit rejection of an indicated structure. This is an adaptive diagnostic condition, not an independent detection benchmark.

## Given

### Original data

The same full Longitudinal-CT v3 case 0a09c8844b baseline/follow-up CT pair used in the earlier revised whole-volume task. Native grids are 512×512×261 and 512×512×274, with 0.822265625/0.84765625 mm in-plane spacing and 3 mm through-plane spacing. Visits are not registered.

### Supplied helpers

R01 baseline [304,263,213] and R02 follow-up [302,221,216], zero-based native voxel indices. These are exact localization assistance, selected as the reference voxel nearest each voxel-index centroid after a predeclared omission trigger. No diagnosis, anatomical label, source identity, prior result, mask or guaranteed-positive statement was supplied. Other findings are outside scope.

### Callable tools

Installed Python/imaging tools and local image rendering under the frozen protocol. The full CTs were available. Target-source lookup, external retrieval and additional model downloads were blocked; the model transport route remained allowed. One fresh Astra/medium attempt, two-hour cap, no retry/resume.

### Reference-only material

The new private reference retained source label 3 at both visits and its persistent event; all other labels were zeroed only in this separate freeze. Two visit instances represent one focus. The original source labels, whole-volume references and scores remain unchanged. Reader reference overlays are never solver assistance.

## Task specification

First judge each candidate as `tumor`, `normal_or_benign` or `indeterminate`, with a nonempty image-based reason. Segment only `tumor` candidates; rejected/indeterminate candidates get no tumor mask. Include full visible extent on the exact native grid/affine. IDs are local to each visit; identity requires explicit events. `persistent` means identity, not unchanged size.

## Expected output

Five files: baseline/follow-up integer instance NIfTIs, `events.json`, `report.md`, and `candidate_judgments.json`. Every positive ID appears once in the appropriate event list. Zero masks with empty events and supported negative/indeterminate judgments are permitted; they do not declare disappearance or absence of other disease.

## Evaluation

The saved model answer rejected 2/2 indicated candidates and produced exact-grid uint16 zero masks and empty events. Replay retains 0/2 source-positive acceptance, 0/2 localization and 0/1 end-to-end links/events. No conditional link/group is eligible; conditional scores and specificity are undefined. No negative reference controls exist.

Mechanical reward is output validity, not scientific success. Fresh offline controls additionally reproduce an enforcement gap: rejected judgments paired with oracle masks still validate and detect 2/2, while tumor judgments paired with empty masks report 2/2 acceptance and 0/2 detection. Judgment/mask consistency is not checked by the frozen wrapper. The actual saved answer is internally consistent, so this finding does not replace its original scores.

## Difficulty

The supplied centers remove discovery for this selected focus, while image interpretation and inclusion remain. Saved step-11 orthogonal views and step-14 center montages display the target locations; step 16 explicitly rejects them. The model's normal-soft-tissue explanation is an attributed interpretation, not a clinical verdict.

## Coverage

One selected focus in one patient, two visits, one normally completed attempt (200.206477 seconds of recorded agent time). Selection depended on an earlier result: the persistent group had zero foreground coverage at both visits under the <10% omission trigger. This supports recognition/inclusion disagreement after assistance, not isolated search causality, population sensitivity, specificity or conditional segmentation/linking ability.

The source annotation protocol used CT and clinical examination reports. The solver had CT and points only. Case-specific reports and clinical/reference adjudication remain unavailable; exact geometry and score replay do not resolve image-only target suitability.

## Sources

- [Localized protocol](../../experiments/longitudinal-ct-localized-astra-medium/protocol.md)
- [Exact solver instruction](../../experiments/longitudinal-ct-localized-astra-medium/instruction.md)
- [Existing result and appended reader audit](../../findings/longitudinal-ct-v2-and-localized.md)
- [Source, freeze and replay audit](../sources/localized-ct-audit.json)
- [Native view derivation and terms](../../../../presentation/task-explorer/localized-ct/NOTICE.md)
- [Longitudinal-CT v3: annotation protocol and source terms](https://fdat.uni-tuebingen.de/records/qe950-g4h94)
