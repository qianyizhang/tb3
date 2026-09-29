# Segment brain tumor subregions from four MRI contrasts

Resolve four MRI modality paths, call the supplied specialist tools, and retain the tumor label map and whole-tumor mask. This is a symbolic task explanation with no patient or run result.

> **Symbolic illustration — no matching four-sequence BraTS case is available here; request the actual data through the [official BraTS access page](https://www.med.upenn.edu/cbica/brats2021/).**

## Given

### Original data

The pinned `short_segment_brain` task requires T1, post-contrast T1c, T2 and FLAIR NIfTI volumes. No complete matching local case is available. The tool expects aligned inputs; the symbolic diagrams assert no patient voxels, dimensions, physical affine, intensity or lesion shape.

### Supplied helpers

The case manifest, runtime state and typed artifact references help resolve actual files. Input aliases are `t1_nifti`, `t1c_nifti`, `t2_nifti`, `flair_nifti`. They are not a supplied tumor mask.

### Callable tools

`identify_sequences` precedes `brats_mri_segmentation`. The segmentation arguments are `t1_path`, `t1c_path`, `t2_path`, `flair_path`. The normal code path uses a MONAI BraTS bundle with T1c,T1,T2,FLAIR ordering. A MONAI-dependency import failure can instead produce a heuristic T1c+FLAIR fallback. Neither path has been executed here.

### Reference-only material

A case-matched BraTS annotation could support a later independent comparison; none is retained. It is not a solver input. Label meanings are public contract information, not a private patient mask.

## Task specification

Identify each modality, map its actual path into the correct argument, call the segmentation tool and preserve both required artifact paths. The source fault profile includes a T1c/FLAIR swap: file existence alone cannot establish modality identity.

## Expected output

The registry requires `seg_path` and `wt_mask_path`. The source label map uses **0 background, 1 necrotic core, 2 edema/invaded tissue and 4 enhancing tumor**; binary WT is the union of **1, 2 and 4**. TC (1 or 4) and ET masks are optional tool products, not the two registry-required artifacts. Every rendered output socket is empty; there is no saved patient prediction.

## Evaluation

BCER checks successful identification and segmentation stages, path existence and nonempty NIfTI content for both required outputs. On a NIfTI read error, its nonempty check can fall back to positive file size. These structural workflow checks do not calculate anatomical overlap or boundary accuracy. No pass score, clinical outcome or learned-model performance is claimed.

## Gaps

No matching four-sequence case, BCER segmentation output or case-matched annotation is available. The official BraTS page routes acquisition through Synapse registration and a data-request form; no anonymous case file was exposed by the inspected route. Real-case use requires authorized acquisition, exact case/modalities and geometry review, and separately retained reference. A single unrelated T1c archive cannot stand in for the quartet.

## Visual explanation

### Workflow

- Identify the four symbolic modality inputs and map their typed paths.
- Trace the segmentation tool and distinguish its documented normal/fallback paths.
- Read the empty label/WT output contract and the limits of structural checks.

## Sources


- [Pinned BCER task registry](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/configs/tasks_registry.json)
- [Pinned BCER segmentation tool](https://github.com/Albertlongzi/BCER/blob/d10816712793a9e27f2e70640f9afc06f08a0c5c/tools/brain_tumor_segmentation.py)
- [Official BraTS 2021 data and annotation description](https://www.med.upenn.edu/cbica/brats2021/)
- Source hashes, access attempt and scope are pinned in `presentation/external-tasks/sources/bcer-brain-resolution.json`.
