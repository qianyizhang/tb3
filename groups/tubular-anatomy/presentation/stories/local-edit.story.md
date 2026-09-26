---
schema: 2
id: local-edit
title: Repair only the supported region; preserve intact controls
locale: en
purpose: Explain a specific operation with an inspectable synthetic witness.
scope: Binary grid fixture only. No CT/MRA support or clinical defect is inferred.
recipe: local-edit-v1
asset_pack: local-edit-v1
source_class: procedural-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- groups/tubular-anatomy/presentation/briefs/tb3-vessel-connection-repair.md
---

# Repair only the supported region; preserve intact controls

Authored explanation only. Scientific task records remain authoritative. Integrated operation sub-explanation; source task inputs and references remain separate.

## 1. given

```beat
id: given
frames: 120
caption: A supplied mask has a bounded editable region.
narration: The boundary constrains what may be changed; it does not prove that a change is needed.
visual: Show supplied mask and outline the editable domain.
channels:
  domain:
  - 0.0
  - 1.0
  correction:
  - 0.0
  - 0.0
  control:
  - 0.0
  - 0.0
```

## 2. repair

```beat
id: repair
frames: 168
caption: First require source support; then check the bounded edit.
narration: No source image is supplied in this fixture, so support is not established. The constructed change only demonstrates the editing invariant.
visual: Overlay changed cells, driven by the actual XOR of the masks.
channels:
  domain:
  - 1.0
  - 1.0
  correction:
  - 0.0
  - 1.0
  control:
  - 0.0
  - 0.0
```

## 3. preserve

```beat
id: preserve
frames: 120
caption: The exterior remains identical.
narration: The fixture has zero changed cells outside the editable region.
visual: Highlight exterior and show a computed changed-cell count, labelled fixture.
channels:
  domain:
  - 1.0
  - 1.0
  correction:
  - 1.0
  - 1.0
  control:
  - 0.0
  - 0.0
```

## 4. control

```beat
id: control
frames: 168
caption: An intact control returns unchanged.
narration: Do not make every scene end in a repair. No edit is a valid output when the evidence supports it.
visual: Switch to the separate intact-control panels, showing zero changed cells.
channels:
  domain:
  - 1.0
  - 1.0
  correction:
  - 1.0
  - 1.0
  control:
  - 0.0
  - 1.0
```
