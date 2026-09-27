---
schema: 2
id: unlabeled-anatomy-prototype
title: Name 17 anonymous objects
locale: en
purpose: Explain BR-011 I2 identity assignment from supplied anonymous surface points,
  with a separate private source-key reveal.
scope: 'Retained case 32 prototype: 17 objects, 117-name vocabulary, shared LPS millimetres
  and no CT. Sampled points have no mesh faces. Reader-only key reveal; no model trial
  or clinical identifiability adjudication.'
recipe: prototype-identity-v1
asset_pack: retained-prototype-identity-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- groups/anatomy-audit/presentation/briefs/tb3-unlabeled-anatomy-prototype.md
- docs/research-rounds/BR-011-unlabeled-anatomy.md
- docs/evidence/br011-author-screen.json
- docs/evidence/br011-grader-controls.json
- presentation/task-explorer/prototype-identity/manifest.json
- scripts/build_prototype_identity_assets.py
- probes/revisions/br011/authoring/grade_identity.py
---

# Anonymous object identity

## input

```beat
id: input
frames: 120
caption: The objects are supplied; their anatomical names are withheld.
narration: BR-011 I2 is an authoring prototype containing seventeen anonymous objects
  from case 32. Its public packet supplies a three-millimetre occupancy volume, surface-point
  PLY files, IDs and a vocabulary. There is no CT, proposed identity map or model
  trial.
visual: Show the actual point assembly and seventeen unassigned IDs.
channels:
  focus:
  - 0
  - 0
  inventory:
  - 0
  - 0
  reveal:
  - 0
  - 0
```

## inspect

```beat
id: inspect
frames: 624
caption: Inspect each shape while preserving the shared arrangement.
narration: Highlight every object in turn. All share the same patient orientation,
  position and scale; fitting objects separately would remove useful relationships.
  These sparse display samples contain no faces and cannot establish connectivity.
  The public occupancy volume remains authoritative.
visual: Traverse all seventeen actual source clouds with neutral context and no identity
  reveal.
channels:
  focus:
  - 0
  - 1
  inventory:
  - 0
  - 0
  reveal:
  - 0
  - 0
```

## vocabulary

```beat
id: vocabulary
frames: 144
caption: Choose among 117 allowed names, once for each supplied ID.
narration: The vocabulary is larger than the scene inventory and supplies no proposed
  object labels. Write an assignments list with one object ID and one label per row.
  Row order does not matter; duplicate, missing or extra IDs fail the retained scorer.
  Source spellings must match.
visual: Keep every assignment unfilled and show the vocabulary and output contract.
channels:
  focus:
  - 1
  - 1
  inventory:
  - 0
  - 1
  reveal:
  - 0
  - 0
```

## source-reveal

```beat
id: source-reveal
frames: 288
caption: 'Reader reveal: map the anonymous IDs to the private source key.'
narration: The highlighted rows now follow the retained source key, not a recognition
  algorithm or an agent answer. The key was checked against the retained original
  occupancy and taxonomy. This establishes source agreement only; it does not prove
  that every label is identifiable from the solver inputs.
visual: Reveal the seventeen source mappings in packet order, highlighting the last
  revealed source object.
channels:
  focus:
  - 1
  - 1
  inventory:
  - 1
  - 1
  reveal:
  - 0
  - 1
```

## scope

```beat
id: scope
frames: 192
caption: I2 asks for identity; quality and unusual anatomy remain separate.
narration: I1 would supply proposed labels for correction. I3 would ask about identity
  and annotation quality in typical or verified unusual anatomy. Those are separate
  hypotheses. This I2 example still needs blind identity and ambiguity review before
  a model trial; a source-key pass alone cannot establish fairness.
visual: Hold the completed reader-key table with prototype, provenance and scientific
  limits.
channels:
  focus:
  - 1
  - 1
  inventory:
  - 1
  - 1
  reveal:
  - 1
  - 1
```
