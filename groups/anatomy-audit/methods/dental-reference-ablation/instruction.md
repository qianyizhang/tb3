# Segment a dental cone-beam CT

The target CT is `/app/data/ct.nii.gz`. The complete label-ID dictionary is
`/app/data/labels.json`. Produce `/app/answer/segmentation.nii.gz` as a single
integer-label NIfTI on exactly the target voxel grid, preserving dimensions,
affine, qform and sform. Use background 0 and the supplied IDs. Also save
`/app/answer/method.md` describing your approach, uncertainties and omissions.

## Native-axis and semantic-side contract: version 2

For assigning anatomical names in this dataset, native array axes `(i,j,k)`
(the three axes of the loaded NIfTI voxel array) increase toward **Right,
Posterior, Inferior**, respectively. These are patient-side names used by the
annotation convention, not the side of a displayed picture. This explicit
mapping is authoritative for semantic labeling in this task; do not infer
semantic laterality or superior/inferior direction from the stored affine.
The legacy header orientation is not authoritative for those names. Keep it
unchanged in the submitted file solely to preserve the required voxel grid.
Do not flip, resample or relabel the target just to make its header canonical.
The same native-axis convention applies to any provided example volume.

## Annotation scope and boundaries

- Segment all represented structures you judge to be present within the scan.
  The dictionary is dataset-wide and does not imply that every label occurs in
  this target. Do not extrapolate anatomy outside the imaged field of view.
- Labels are mutually exclusive. Tooth IDs represent natural mineralized tooth
  tissue. Pulp IDs (corresponding tooth ID + 100) represent internal pulp chambers
  and root-canal spaces; these replace the tooth ID at those voxels. A complete
  tooth object is the union of its tooth-tissue and pulp labels.
- Jawbone labels include the cortical and enclosed cancellous compartments,
  excluding separately labeled teeth, restorations and canals. Do not assign
  unrelated facial/cervical bones to a jaw merely because they touch it.
- Maxillary sinus labels represent the imaged cavity inside its bony boundary,
  excluding the bony wall. Pharynx represents the imaged air lumen, excluding
  the surrounding soft-tissue wall and neighboring oral/nasal spaces.
- Canal labels represent the named intrabony canal spaces, excluding their bony
  walls and unrelated marrow spaces. Cover their supported in-field extent;
  thin or low-contrast regions can be uncertain.
- Bridge, Crown and Implant refer to prosthetic structures, not bright natural
  enamel. A crown is a prosthetic coronal unit; a bridge is a connected prosthetic
  span replacing missing teeth; an implant is an implanted supporting body.
  Preserve distinguishable underlying natural tooth tissue under its tooth ID.
  Subtype boundaries can be ambiguous in this annotation system: make your best
  supported assignment and document alternatives rather than assuming a
  particular restoration or tooth inventory. Pooled restoration geometry and
  subtype agreement will be reported separately.

## Completeness, uncertainty and evaluation

Submit your best supported segmentation, including uncertain portions where you
can make a defensible anatomical estimate. Do not invent anatomy merely to use a
label. If a structure cannot be resolved, document that explicitly. An unused
label is not a statement that the structure is anatomically absent.

Evaluation compares the submitted mask with a withheld dense reference.
Omitted reference voxels count as misses; uncertainty notes do not create an
ignored region or an abstention exemption. Reported measures separate whole-tooth
shape from tooth identity, and evaluate pulp, main canals, small canals, jaws,
air spaces and restorations separately. Per-label Dice excludes labels empty in
both prediction and reference; extra predicted labels count as errors. No target
reference mask, score, prior output or case-specific finding is available during
the task.

Choose your own method using the installed local tools. External data, websites
and pretrained model weights are unavailable. You have up to two hours; save
your output before finishing.
