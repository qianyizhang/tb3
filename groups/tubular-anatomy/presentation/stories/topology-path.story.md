---
schema: 2
id: topology-path
title: One requested path is not a branch inventory
locale: en
purpose: Explain a specific operation with an inspectable synthetic witness.
scope: Synthetic graph teaching example. No CTA search, coronary identity, image evidence or clinical result is
  shown.
recipe: topology-v1
asset_pack: topology-v1
source_class: procedural-teaching
reference_policy: no-reference-assets
fps: 24
source_locators:
- groups/tubular-anatomy/presentation/briefs/tb3-named-coronary.md
---

# One requested path is not a branch inventory

Authored explanation only. Scientific task records remain authoritative. Integrated operation sub-explanation; source task inputs and references remain separate.

## 1. question

```beat
id: question
frames: 120
caption: The requested output is one connected path.
narration: This fixture supplies a graph to explain the output. A real CTA task still needs image-based discovery.
visual: Show complete tree; only inlet and requested endpoint are identified.
channels:
  focus:
  - 0.0
  - 1.0
  trace:
  - 0.0
  - 0.0
  inventory:
  - 0.0
  - 0.0
```

## 2. follow

```beat
id: follow
frames: 168
caption: Follow connected edges, not a straight shortcut.
narration: Keep edge membership visible as the route passes each junction.
visual: Reveal e0, e1 and e2 sequentially by arc length; do not sweep a cursor through empty space.
channels:
  focus:
  - 1.0
  - 1.0
  trace:
  - 0.0
  - 1.0
  inventory:
  - 0.0
  - 0.0
```

## 3. contract

```beat
id: contract
frames: 144
caption: Return an ordered centerline, not every branch.
narration: Show the selected path and its ordered vertices as two views of the same data.
visual: A compact ordered edge/point list is generated from selected_edges.
channels:
  focus:
  - 1.0
  - 1.0
  trace:
  - 1.0
  - 1.0
  inventory:
  - 0.0
  - 0.0
```

## 4. limit

```beat
id: limit
frames: 120
caption: Teaching the path is not solving artery recognition.
narration: This tree has no coronary labels. Naming anatomy requires the actual task evidence.
visual: Keep the route held; retain scope next to the visual.
channels:
  focus:
  - 1.0
  - 1.0
  trace:
  - 1.0
  - 1.0
  inventory:
  - 0.0
  - 0.0
```
