---
schema: 2
id: supplied-object-identity
title: Name the supplied objects
locale: en
purpose: Explain assigning anatomical identities to anonymous supplied masks, with
  assistance conditions and an explicit source-name reveal.
scope: 'Source-derived teaching subset: seven objects from s1233, also the source
  of BR-013 A01 (13 objects). Teaching IDs and surfaces are not the frozen task. Source
  names are a reader reveal, not a solver result.'
recipe: anatomy-identity-v1
asset_pack: retained-anatomy-v1
source_class: source-derived-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- groups/anatomy-audit/presentation/briefs/tb3-supplied-object-identity.md
- docs/research-rounds/BR-013-abdominal-direction.md
- docs/research-rounds/BR-014-inventory-components.md
- docs/research-rounds/BR-015-clinical-evidence.md
- docs/evidence/br013-freeze.json
- presentation/task-explorer/anatomy/manifest.json
---

# Name the supplied objects

## input

```beat
id: input
frames: 144
caption: The masks are already supplied. Assign identities, not new contours.
narration: The original A01 and A02 conditions supply anonymous masks, object IDs,
  an overview and a vocabulary. Their affine maps voxels to physical LPS millimetres;
  no CT is supplied. Here seven retained source objects use teaching IDs T01 to T07.
visual: Show the shared assembly, anonymous teaching IDs and empty assignments.
channels:
  focus:
  - 0.0
  - 0.0
  inventory:
  - 0.0
  - 0.0
  reveal:
  - 0.0
  - 0.0
```

## inspect

```beat
id: inspect
frames: 240
caption: Inspect each object in its shared anatomical context.
narration: Follow shape and neighbouring structures while retaining scale and patient
  orientation. The original masks are authoritative; these smoothed display surfaces
  are only a teaching view. The highlight does not predict a label.
visual: Move the highlight through the seven objects while every assignment stays
  unfilled.
channels:
  focus:
  - 0.0
  - 1.0
  inventory:
  - 0.0
  - 0.0
  reveal:
  - 0.0
  - 0.0
```

## assistance

```beat
id: assistance
frames: 192
caption: Inventory, fragments and CT define different conditions.
narration: A01 and A02 allow unused vocabulary labels, with each name used at most
  once. I01 supplies the exact inventory. F01 allows repeated names for fragments.
  C01 adds CT, while V01 supplies a venous branch inventory. These changes remove
  different uncertainty.
visual: Keep names hidden and show the inventory and repeated-label distinction.
channels:
  focus:
  - 1.0
  - 1.0
  inventory:
  - 0.0
  - 1.0
  reveal:
  - 0.0
  - 0.0
```

## source-reveal

```beat
id: source-reveal
frames: 240
caption: Reveal retained source names to illustrate an assignment table.
narration: This is a reader-facing reveal from source metadata, not an agent answer
  or a recognition algorithm. Return one object ID and label for every supplied object.
  The separate proposed-label audit returns only corrections.
visual: Fill the seven teaching rows from retained source names, leaving geometry
  unchanged.
channels:
  focus:
  - 1.0
  - 1.0
  inventory:
  - 1.0
  - 1.0
  reveal:
  - 0.0
  - 1.0
```

## scope

```beat
id: scope
frames: 192
caption: Seven teaching objects do not reproduce the full frozen task.
narration: The scene shares source patient s1233 with A01, but omits six objects and
  replaces the original IDs. It does not demonstrate fragment recognition, CT reasoning
  or eight-branch venous identity. Exact task conditions and evaluator references
  remain separate.
visual: Hold the source-name table with the explicit subset, source and evaluation
  limits.
channels:
  focus:
  - 1.0
  - 1.0
  inventory:
  - 1.0
  - 1.0
  reveal:
  - 1.0
  - 1.0
```
