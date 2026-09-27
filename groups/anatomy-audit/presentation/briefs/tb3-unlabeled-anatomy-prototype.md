# Assign identities to anonymous anatomical objects

Assign one anatomical name to each of 17 anonymous supplied objects, using their
shapes and shared spatial arrangement. This is the retained BR-011 I2 authoring
prototype, not an admitted model experiment.

## Value

Explores anatomical identity inference when object names are withheld.

## Given

### Original data

An integer occupancy volume (`objects.npz`) derived at **3 mm** resolution from
retained case **32**, plus **17 PLY surface point clouds**. The affine maps voxel
coordinates to physical LPS millimetres: positive left, posterior and superior.
There are no CT intensities or anatomical labels in the public object metadata.

### Supplied helpers

The packet supplies anonymous object IDs and mask values, a scene index and the
full **117-name vocabulary**. All objects retain shared position, orientation and
scale; do not fit them independently. The boundaries are supplied, so this is not
segmentation from images. PLY points have no faces: occupancy and connectivity
come from the volume, not a sparse display.

### Callable tools

The local prototype supplies the NPZ/PLY representation and a brief instruction.
A ready blind viewer and tested volume loader are requirements for a future
trial package. No frozen agent environment, model configuration or trial is
established by this prototype record.

### Reference-only material

The source identity key and reviewer preview are outside the public packet.
The teaching story samples the actual 17 PLY clouds and later reveals this key
to the reader. That reveal is not solver assistance or a model answer. This
review checked each private-key identity against the separately hash-verified
original occupancy array and taxonomy; it did not adjudicate clinical truth or
whether every identity is inferable from masks alone.

## Task specification

Assign one vocabulary label to each supplied object ID. Preserve patient
orientation and global relationships. No proposed names, CT, annotation-quality
judgments or disease diagnosis are part of I2's deliverable.

## Expected output

Write `assignments.json` as `{"assignments":[{"object_id":"o123","label":"label-name"}]}`,
with each of the 17 actual IDs exactly once. The example ID and name above are
placeholders. Labels must match the source spelling; row order is irrelevant.

## Evaluation

The retained scorer checks exact source-key agreement and reports missing,
extra and wrong identities; duplicate IDs or malformed rows fail. Its eight
author controls test scorer behavior, not clinical validity or task fairness.
The protocol calls for a blind identity/ambiguity review before admitting a trial.

## Difficulty

Shape and global relationships must support names without proposed-label
anchoring. A simple author classifier labeled 16/17 objects in this selected
case correctly, using labeled examples from seven other patients that the
prototype solver does not receive. That screening result is not a general-agent
trial or evidence that the residual error defines a fair difficult task.

## Coverage

| Candidate | Input and deliverable boundary |
|---|---|
| I1: identity audit | Proposed names supplied; return corrected identities. A separate hypothesis. |
| I2: this prototype | Anonymous intact objects; assign identities from shape and arrangement. |
| I3: identity plus quality | Unusual anatomy and potential errors; identity, annotation quality and anatomical pattern are separate proposed outputs. Not implemented here. |

The display retains up to 1,600 source points per object and one shared fitting
transform; it omits occupancy detail. Case 32 is distinct from the seven-object
s1233 teaching assembly used for other entries. No model trial was run here.

## Sources

- [BR-011 — Identify anatomy, then separate unusual anatomy from errors](../../experiments/br011/protocol.md)
- [Author-screen source and public-file receipt](../../../../docs/evidence/br011-author-screen.json)
- [Scorer controls](../../../../docs/evidence/br011-grader-controls.json)
- [Point-display derivation and terms](../../../../presentation/task-explorer/prototype-identity/NOTICE.md)
