# Three STS dental CBCT cases: downloaded GT audit

2026-09-21 · [User request](codex://threads/01a0c25e-4b08-7552-8379-90a2b50ad40f)
· [Machine receipt](evidence/dental-sts-gt-audit.json)
· [Owning idea](../ideas/dental-cbct-agent-pilot.md)

**Result: all three scan/mask pairs load and align, but their masks are not usable
as-is for anatomical scoring, and do not provide per-tooth FDI identities.**
These conclusions concern the six downloaded mirror files, not every STS case or
the uninspected original Zenodo archive. No clinical annotation certification or
model performance claim is made.

## Recovery and technical checks

Downloaded ROI_L_001, ROI_L_002 and ROI_L_003 (one image and one mask each) plus
the [mirror card](https://huggingface.co/datasets/MedOtter/STS-3D-Tooth), pinned at
revision `2d1fdf36e225261de5d60830579c0ca16fd499f5`. Total including the card:
128,748,511 bytes, approximately 128.75 MB. Each NIfTI SHA-256 matches its upstream
LFS object; the card matches its Git blob. All seven files were rehashed after
inspection and are unchanged. This establishes mirror download integrity, not
byte equivalence to the original publisher archive.

The three pairs all pass these bounded technical checks:

- Shape: 512 × 512 × 400; image/mask shapes, affines and spacings agree.
- Header spacing: approximately 0.155859 × 0.155859 × 0.150000 mm, slightly
  anisotropic. These are stored header values, not independently verified original
  acquisition geometry. All three cases share the same affine.
- Header axes: LAS in nibabel's convention; both qform and sform codes are 1 and
  their matrices agree. Affines are invertible.
- All image and mask values are finite; masks are nonnegative integers and nonempty.
- Independent nibabel and SimpleITK readers return exactly equal decoded image
  and mask arrays after accounting for array-axis ordering.

There are 199 exactly equal adjacent image-slice pairs in each volume. The final
image slice has the constant value 2 in every case. Thus 400 stored planes are
not evidence of 400 independent native acquisitions. Resampling/padding or encoded
metadata is plausible, but its upstream cause has not been established.

## Reproduced GT-content problems

Indices below are zero-based along native array axis 2.

| Case | Actual stored labels | Full-image foreground planes | Assessment |
| --- | --- | --- | --- |
| ROI_L_001 | 0, 1, 4 | k=217 and 218 entirely label 1; k=399 entirely label 4 | Reject unmodified scoring; internal tooth-foreground defect plus non-anatomical terminal plane. |
| ROI_L_002 | 0, 1, 2 | k=399 entirely label 2 | Raw nonzero-as-tooth interpretation invalid. Label 1 is a possible binary reference, subject to review and explicit preprocessing. |
| ROI_L_003 | 0, 1, 2 | k=399 entirely label 2 | Same terminal-plane problem; label 1 is a possible binary reference, subject to review. |

Each uniform plane contains 262,144 labeled voxels. In ROI_L_001's two internal
planes, the scan shows teeth, soft tissue, bone and background, but the GT labels
every pixel as 1. About 29.1% of the image pixels in each plane are below -500 in
the stored intensity scale. The visual review also confirms coverage of background
outside the anatomy. This cannot serve as an anatomical tooth mask under the
advertised interpretation. Whether the terminal planes are deliberate metadata,
padding or an error remains unresolved; no convention explaining them was found
in the inspected card/paper.

All tooth regions in the reviewed slices share value 1. Values 2 or 4 occur only
in the terminal plane and cannot encode individual teeth. The mirror's per-tooth
FDI description does not match these three masks. Connected-component labels
would not restore independently annotated tooth identities: teeth may touch,
roots may be disconnected, and small islands occur.

![Uniform non-anatomical planes](../../../runs/dental-sts-gt-audit-20260921/review/full-plane-anomalies.png)

## Sampled visual assessment

Inspected raw/overlay pairs in three native orthogonal planes per case, nine
foreground-weighted axial views per case, ordinary peak-tooth slices and the
uniform-plane diagnostic figure. This is sampled inspection, not every-slice
clinical review. Labels broadly overlap dental structures on ordinary slices;
fine boundary accuracy and completeness remain unadjudicated.

- **001:** ordinary tooth regions are visible, but the internal slabs connect
  unrelated regions. Clearing these slices to background would remove real teeth;
  it is not a valid automatic repair. Re-annotation or an explicit ignored-slice
  evaluation domain would be needed.
- **002:** substantial streak artifacts, fragmented small mask regions and
  tooth foreground reaching k=0 (617 voxels) require attention. Cropping must not
  be scored as an anatomical endpoint failure.
- **003:** no label-1 contact with crop faces was detected. Small islands and
  boundary uncertainty remain; it is the best of these three for a provisional
  binary-mask inspection demo, not certified GT.

After excluding the uniform planes only for a diagnostic calculation, the
label-1 masks have 6, 195 and 163 components (26-neighborhood). These counts are
not tooth counts and not automatic annotation-error counts. No cleaned reference
was written and no source labels were changed.

![Actual scans and tooth-region overlays](../../../runs/dental-sts-gt-audit-20260921/review/three-case-tooth-regions.png)

Per-case views: [001](../../../runs/dental-sts-gt-audit-20260921/review/ROI_L_001-triplanar.png),
[002](../../../runs/dental-sts-gt-audit-20260921/review/ROI_L_002-triplanar.png),
[003](../../../runs/dental-sts-gt-audit-20260921/review/ROI_L_003-triplanar.png).

## Source claims and limits

The [primary paper](https://www.nature.com/articles/s41597-024-04306-9) describes
manual dental-area annotation in ITK-SNAP followed by iterative model-assisted
annotation and manual correction. The current mirror's simplified annotation
account and its FDI claim should not substitute for file inspection or an
authoritative label specification. The mirror declares CC-BY-4.0; source card and
paper locators are retained. No external redistribution occurred.

The original large multipart archive has not been downloaded for comparison.
Patient disjointness between these case IDs is also unverified. Header consistency
does not establish accurate patient laterality or physical dimensions relative to
original DICOM. No canal masks or clinician reports were obtained.

## Consequences for the agent pilot

**Assistant recommendation:** do not use these masks for tooth-numbering,
per-tooth instance scoring, canal tracing or report-fact scoring. For binary
tooth-region correction, start with case 003 only after agreeing a documented
interpretation of label 1 and the non-anatomical terminal plane, then reviewing
the remaining reference. Keep case 001 out of the initial scoring set. A mask
that copies all nonzero labels would otherwise be rewarded for reproducing
non-anatomical planes.

This task authorized download and reference validation, not a model trial. No model
was run. The previously proposed ToothFairy tooth-numbering task remains separate.

## Local reproduction and retained evidence

Raw files: `runs/dental-sts-gt-audit-20260921/source/ROI/Labeled/{Image,Mask}/`.
The [download manifest](../../../runs/dental-sts-gt-audit-20260921/download-manifest.json)
records pinned URLs, sizes and hashes. Detailed observations:
[structural audit](../../../runs/dental-sts-gt-audit-20260921/review/audit.json),
[uniform-plane audit](../../../runs/dental-sts-gt-audit-20260921/review/anomalies.json),
[duplicate-plane audit](../../../runs/dental-sts-gt-audit-20260921/review/duplicate-planes.json).

Local author scripts are retained in that run directory. Existing `.venv-br030`
was reused without installation. Versions are recorded in the structural audit.
To regenerate the primary figures from the exact retained data:

```sh
.venv-br030/bin/python runs/dental-sts-gt-audit-20260921/audit.py
.venv-br030/bin/python runs/dental-sts-gt-audit-20260921/inspect_anomalies.py
```

These are local author diagnostics, not a newly qualified portable experiment.
Do not expose the source masks, audit or reference views to a future blind solver.
