---
schema: 2
id: automedbench-full-synthrad2025-mrct-task
title: Explain MR to CT synthesis without invented synthetic CT
locale: en
purpose: "Teach input/helper/output domains, geometry and source evaluator boundaries."
scope: "Matching Full MR/mask/private CT absent; symbolic roles and no result."
recipe: automedbench-full-synthrad2025-mrct-task-v1
asset_pack: retained-automedbench-full-synthrad2025-mrct-task-source-v1
source_class: source-derived-teaching
reference_policy: reader-reference-reveal
fps: 24
source_locators:
- presentation/external-tasks/briefs/automedbench-full-synthrad2025-mrct-task.md
- presentation/external-tasks/sources/automedbench-full-synthrad2025-mrct-task-resolution.json
- scripts/build_automed_synthrad_mrct_assets.py
---

# full-pair-gap

```beat
id: full-pair-gap
scene: input
frames: 168
caption: "Full pair absent · zenodo.org/records/15373853"
narration: "Matching public MR/mask and private CT, Full NIfTI geometry and selected IDs are unstaged."
visual: "Symbolic Full MR/mask/sCT/private CT sockets; no matching Full pixels."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# mr-mask-contract

```beat
id: mr-mask-contract
scene: operation
frames: 168
caption: "MR and mask are given; CT is private"
narration: "MR arbitrary intensity and outline mask do not reveal paired CT HU."
visual: "Symbolic Full MR/mask/sCT/private CT sockets; no matching Full pixels."
channels:
  progress: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# same-grid-domain

```beat
id: same-grid-domain
scene: operation
frames: 168
caption: "Same grid, different intensity domain"
narration: "No super-resolution factor; shape equality does not establish affines, spacing, registration or inverse normalization."
visual: "Symbolic Full MR/mask/sCT/private CT sockets; no matching Full pixels."
channels:
  progress: [0.3333333333333333, 0.3333333333333333]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# tier-format-boundary

```beat
id: tier-format-boundary
scene: operation
frames: 168
caption: "Inspect inference-only tiers and format"
narration: "Prescribed or compared model guidance does not establish checkpoint availability or successful execution."
visual: "Symbolic Full MR/mask/sCT/private CT sockets; no matching Full pixels."
channels:
  progress: [0.6666666666666666, 0.6666666666666666]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# metric-denominators

```beat
id: metric-denominators
scene: operation
frames: 168
caption: "Keep metric denominators distinct"
narration: "HU voxel error, finite PSNR and optional full-slice SSIM use different denominators; no quality measured."
visual: "Symbolic Full MR/mask/sCT/private CT sockets; no matching Full pixels."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# absent-synthetic-ct

```beat
id: absent-synthetic-ct
scene: output
frames: 168
caption: "Synthetic CT output remains empty"
narration: "The expected plural agents_outputs case path is a contract, not a generated or acquired CT."
visual: "Symbolic Full MR/mask/sCT/private CT sockets; no matching Full pixels."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# upstream-mr-and-rules

```beat
id: upstream-mr-and-rules
scene: reference
frames: 168
caption: "Reveal source rules, never private CT"
narration: "Explicit later reader control displays upstream training MR 1HNC117 and source threshold/validity rules; no paired CT, Full membership or measured metric."
visual: "Symbolic Full MR/mask/sCT/private CT sockets; no matching Full pixels."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [1, 1]
cut: intentional-cut
```

# pairing-geometry-gap

```beat
id: pairing-geometry-gap
scene: limits
frames: 168
caption: "Recover Full pairing and geometry"
narration: "Upstream MHA and metadata do not establish HN20 NIfTI membership, private CT, normalization or model runtime."
visual: "Symbolic Full MR/mask/sCT/private CT sockets; no matching Full pixels."
channels:
  progress: [1, 1]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
