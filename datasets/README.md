# Datasets and selected samples

Datasets are a first-class source register. Each source owns its explanation,
release, reference limits, selected sample identities, file receipts and links to
the tasks that use it. Experiment manifests still own exact task transformations,
solver visibility, freezes and scoring. A supplied mask, a hidden reference and
a reader-only overlay can come from the same dataset under different conditions.

The [2026-09-22 audit](audits/2026-09-22.md) records the initial gaps, repairs and
verification scope. It covers registered medical experiments, retained source
screens and the acquired external Task Explorer examples. It does **not** claim
that every case in a surveyed external benchmark has been acquired or verified.
The `anatomy.json` and `cardiac.json` records remain historical overview indexes.

## Browse and learn

Build the Task Explorer and open **Datasets** in its header, or follow **Learn
about the data** from a task. Every source has a stable `#datasets/dataset-ID`
page with original-data/reference explanations, selected samples, task links,
release/access notes and explicit gaps. Each page leads with a [frozen sample snapshot](previews/README.md), an explicit
ground-truth/source-reference reveal, and an enlarge/zoom control. The visual
register pins every PNG and records its source selection, crop, coordinate frame
and reference limits. Sources missing images or paired GT show the retained
material and the specific gap. Conceptual diagrams are secondary explanations.

```sh
uv run med brief build --output .local/dataset-explorer/index.html
uv run med brief check
# Metadata and receipt checks only; ordinary builds never hash scans.
uv run python -m tb3_medical.datasets
# Explicit read-only byte audit; no acquisition or inference.
uv run python -m tb3_medical.datasets --verify-local \
  --output .local/dataset-audit.json
```

Missing local files are reported separately from mismatching files. Neither
changes the historical outcome. File sets use exact workspace-relative recovery
locators; there is no basename search, implicit download or authoring import.

## Sources

| Data | Registered sources |
| --- | --- |
| CT anatomy | [TotalSegmentator](totalsegmentator.json), [NLST](nlst.json), [PDDCA](pddca.json), [VerSe](verse.json), [MedPelvis3D screen](medpelvis3d.json) |
| Dental CBCT | [ToothFairy3](toothfairy3.json), [STS-3D-Tooth audit](sts3d.json) |
| Brain and vessels | [AFIDs](afids.json), [generic MNI atlas assistance](afids-atlas.json), [OpenNeuro ds003949](openneuro.json), [TopCoW](topcow.json), [TopBrain](topbrain.json), [AeroPath](aeropath.json), [ImageCAS / ImageCAS-X](imagecas.json) |
| Correspondence | [Learn2Reg](learn2reg.json), [RESECT](resect.json), [Longitudinal-CT](longitudinal-ct.json), [I-SPY2](ispy2.json) |
| Cardiac sequences | [FeEcho4D](feecho4d.json), [STRAUS simulation](straus.json), [EchoSlicer](echoslicer.json), [EchoXFlow](echoxflow.json) |
| External examples | [LIDC-IDRI](lidc-idri.json), [PI-CAI](picai.json), [Imaging-101 phantom](imaging101.json); AutoMedBench and ReX-MLE examples link to TotalSegmentator and TopCoW |
| Metadata and fixtures | [CT-RATE access screen](ct-rate.json), [ACRIN brain metadata](acrin-brain.json), [synthetic MR fixtures](synthetic-mr.json) |

## Add or revise documentation

Use one `datasets/<source>.json` record with a stable `dataset-*` ID. Explain
`summary`, `modality`, `sample_unit`, `image_description`,
`annotation_description`, `reference_note`, `version_note` and `terms_note`.
Do not label source masks as clinical certainty or treat a training sample as
held-out data. Source access and redistribution terms are historical observations
unless explicitly refreshed.

- `sample_sets` names exact IDs, selection role and scope. Roles distinguish
  `used`, `curated`, `screened`, `metadata-only`, `illustration`, `helper`,
  `synthetic` and `not-acquired`. They are not mutually exclusive patient counts.
- Each selection cites a receipt by repository path, SHA-256 and optional JSON
  Pointer. Retain original receipts; append a correction when interpretation
  changes. `receipts/` stores compact source metadata, never scans or model output.
- `file_sets` selects lists in those receipts, an exact `path_field` and optional
  `local_root`/`indices`. Every entry requires a recorded SHA-256. A normalized
  receipt preserves the original receipt digest and explains its derivation.
  Source data and derived task inputs retain separate identities.
- `experiment_ids` and `brief_ids` are explicit relationships. Multiple tasks,
  conditions or views may reuse one patient. `example_brief` must actually depict
  this source, with a caption identifying representative versus exact task input.
- Document `documentation_gaps`. Set `native_payload_expected: false` only for
  an explicit metadata-only or unacquired source; it does not excuse missing
  acquired images. Use an empty-file audit result to report absent payloads.
- `unverified_payloads` retains a known used sample, original runtime locator,
  explanation and pinned receipt when no recoverable native SHA-256 inventory
  exists. These gaps appear separately in the audit and must not be counted as
  verified because a parent archive or pointer file matched.

The composed explorer requires dataset coverage for every experiment and exactly
one dataset owner for every acquired/reused external example file. It rejects
missing fields, broken receipt pointers, changed receipt digests, unknown links,
and unsafe paths. This checks the declared inventory, not the truth of every
clinical annotation or arbitrary unregistered content in ignored folders. A new
source selection in an existing experiment also needs a new or updated sample
selection and receipt; an experiment link alone does not establish sample coverage.

Native payloads remain local. Keep recovery location, original source/version,
attribution, selection reason and original hashes even when a source is rejected.
