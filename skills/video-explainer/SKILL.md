---
name: video-explainer
description: Make a short, source-backed TB3 video from an established task brief, finding or explanation. Use for video requests, not medical interpretation or experiments.
metadata:
  version: "0.2.1"
---

# Video Explainer

Turn an established explanation into a watchable local video. Keep its source
words, evidence and timing authoritative.

## Select the source

Locate contracts from the active `workbench.toml`, not this installed directory.

- **Canonical story:** resolve the entry's `illustration.story_id` and read
  workspace `presentation/EXPLAINERS.md`. Export its `.story.md` with the shared
  exporter into a fresh local destination; use `med story batch` for multiple
  stories. Edit words/timing in the canonical source, never a second storyboard
  or export override. Author missing or unsuitable stories within the requested
  scope; `author-task-story` supports integrated explanations.
- **Standalone video:** use the
  [storyboard contract](references/storyboard.md) to write local `STORYBOARD.md`,
  normally in `.local/presentation/<source-id>/`. Each scene needs its teaching
  point, duration, visual, claim/asset locators and exact visible/spoken words.
  Mark missing visuals unavailable and narrow the claim. For plan-only requests,
  deliver the storyboard without rendering.

## Ground the explanation

Read repository/group guidance, the authoritative brief or finding, explanation,
evidence receipt and available visuals. Use `author-task-brief` or
`explain-medical-evidence` for unresolved interpretation before video editing.
Preserve the requested audience, language and length; infer modest defaults.

Keep one main point. Preserve frozen scores, denominators, attribution strength
and comparison limits. Label conceptual drawings, crops, diagnostics and reference
reveals; never imply a private reference or teaching aid was solver-visible.
Use actual source/result figures when available. Read the sequence without its
source: input, output, decisive evidence, reference role, conclusion and limit
should remain clear.

## Render and inspect

Use existing local media tools and the simplest renderer fitting the scenes;
HyperFrames is optional. Verify commands/dependencies before using an external
CLI. Keep source imagery local unless another data path is authorized; synthetic
medical images cannot substitute for source images.

Use cuts, fades and highlights that clarify the point. Narration is optional;
without it, captions must carry the explanation. Keep a separate script only when
it helps synchronize narration or captions.

Inspect representative frames at final size: first source view, result/reference
reveal and ending. Watch the rendered video for timing, legibility, audio/caption
sync and misleading transitions. Verify decoding and seeking; fix material issues
and recheck affected scenes. Export verification alone is not visual acceptance.

Deliver the canonical story or standalone storyboard, video and representative
frames, naming unsupported scenes. Keep generated media/working assets local;
scientific-record changes and committed MP4s need their own requested scope.

At closeout, read **Active lessons** in the
[feedback ledger](references/feedback-ledger.md). Record material reusable feedback
with the invoked version and source; routine success needs no entry. For skill
maintenance, use the [behavioral cases](references/behavioral-cases.md) to review
both source modes and the export/acceptance boundary.
