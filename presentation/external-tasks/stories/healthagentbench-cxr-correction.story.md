---
schema: 2
id: healthagentbench-cxr-correction
title: Correct an existing CXR findings section
locale: en
purpose: "Explain the constrained edit of an existing CXR draft using an inspectable symbolic clause gate."
scope: "Symbolic edit rules only. No patient image, report, correction or judge result."
recipe: healthagentbench-cxr-correction-v1
asset_pack: retained-healthagentbench-cxr-correction-interpretation-v1
source_class: symbolic-protocol
reference_policy: no-reference-assets
fps: 24
source_locators:
- presentation/external-tasks/briefs/healthagentbench-cxr-correction.md
- presentation/external-tasks/sources/healthagentbench-cxr-correction-resolution.json
- scripts/build_cxr_correction_refined_assets.py
---

# Begin with absent patient material

```beat
id: input
scene: input
frames: 264
caption: "Start with the supplied input"
narration: "The source task supplies current and prior chest radiographs and reports, but this explanation has none of those credentialed patient files. The target report would include a draft FINDINGS section. No patient text or private answer appears here."
visual: "Empty patient-image and report sockets."
channels:
  cursor: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
```

# Locate the target within the chronology

```beat
id: inspect
scene: inspect
frames: 288
caption: "Find the current study"
narration: "The pinned manifest lists twelve chronologically sorted folders: eleven prior studies and a highest-numbered target. Prior full reports would be helpers; the current target's draft is the text to edit. This diagram shows roles only, not the patient's studies or findings."
visual: "Prior-study placeholders leading to the target draft socket."
channels:
  cursor: [0, 1]
  detail: [0, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Apply a clause-preserving edit gate

```beat
id: operation
scene: operation
frames: 336
caption: "Check each existing clause"
narration: "For each existing draft clause, inspect current images and relevant prior evidence, then keep supported wording, correct the existing claim or remove it. Adding a new finding is outside this task. The interactive clause slots are authored placeholders and cannot produce a patient claim."
visual: "Interactive abstract clause-to-evidence-to-keep/correct/remove gate; no clinical sentence."
channels:
  cursor: [0, 1]
  detail: [1, 1]
  reference: [0, 0]
cut: intentional-cut
```

# Keep output limited to FINDINGS

```beat
id: schema
scene: schema
frames: 288
caption: "Write only corrected FINDINGS"
narration: "The one-row submission uses task_id case_01 and a final_answer that begins with a literal FINDINGS header on its own line. It contains corrected existing claims only, with no IMPRESSION. The output remains empty here."
visual: "Empty FINDINGS-only JSON schema; no generated report text."
channels:
  cursor: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# Explain the private judge boundary

```beat
id: reference
scene: reference
frames: 264
caption: "Keep the gold report outside"
narration: "The original target FINDINGS are verifier-only. The pinned wrapper defaults to five CheXprompt calls and requires at least three zero-significant-error votes, with environment overrides possible. Missing gold or judge errors are infrastructure states. No judge call or score occurred in this explanation."
visual: "Reference and judge unavailable; rule only, no vote outcome."
channels:
  cursor: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```

# State acquisition and reproducibility limits

```beat
id: limits
scene: limits
frames: 252
caption: "Read the source boundary"
narration: "MIMIC-CXR reports and MIMIC-CXR-JPG views require credentialed access. CheXprompt is installed from an unpinned main branch in the source task, so a future judge run needs its own source revision and approved data-handling route. This story claims no patient correction or clinical result."
visual: "Official acquisition routes and symbolic scope."
channels:
  cursor: [0, 0]
  detail: [0, 0]
  reference: [0, 0]
cut: intentional-cut
```
