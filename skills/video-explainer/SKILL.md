---
name: video-explainer
description: Plan and make a short, source-backed TB3 explainer video from an existing task brief, finding, or evidence explanation. Use for video requests, not for deciding medical claims or running experiments.
metadata:
  version: "0.1.0"
---

# Video Explainer

Turn an established TB3 explanation into a watchable local video. The useful
middle ground is a small, reviewable storyboard between the source and the
renderer. Read [the storyboard contract](references/storyboard.md) when starting
a video; it is renderer-independent.

## Ground the story

- Read repository and owning-group guidance. Identify the authoritative task
  brief or finding, its explanation, evidence receipt, and available visuals.
  If the task or result still needs interpretation, use `author-task-brief` or
  `explain-medical-evidence` first. Do not decide a clinical, scientific, or
  failure-attribution claim while editing a video.
- Agree with the source on the one point the viewer should remember. Keep the
  requested audience, language and length; infer modest defaults if absent.
- Use actual source/result figures where available. Mark conceptual drawings,
  selected crops, post-hoc diagnostics and GT/reference visibly. Never imply a
  private reference or teaching aid was solver-visible. Preserve exact frozen
  scores, denominators, attribution strength and comparison limits.

## Storyboard before rendering

Write `STORYBOARD.md` in an owned local work directory, normally
`.local/presentation/<source-id>/`. For each scene, capture its single teaching
point, approximate duration, planned visual, the exact source locator for any
substantive claim or source-derived asset, and the words the viewer will read or
hear. Use the [small scene format](references/storyboard.md). Add only fields
needed by this video. A scene can say `unavailable` and narrow its claim rather
than inventing a missing visual.

Read the sequence once without the source open. Check that it explains the input
and output, gives the decisive evidence, reveals reference material with its
proper role, and ends at the source's actual conclusion and limit. Shorten before
adding visual effects. If the user asks only for a plan, stop with the storyboard.

## Make and inspect the video

- Inspect existing local media tools before choosing a renderer. Use the smallest
  path that fits the scenes; HyperFrames is optional. If using an external CLI,
  verify its current commands and dependencies. Keep source imagery local unless
  the user explicitly authorizes another data path. No synthetic medical image
  should stand in for a source image.
- Build a readable rough cut with simple cuts, fades, highlights or sequential
  reveals. Motion should clarify the scene's point. Narration is optional; when
  absent, captions must carry the explanation. Keep a script only if it helps
  synchronize narration or captions.
- Inspect representative frames at the final viewing size, including the first
  source view, any result/reference reveal, and the ending. Watch the rendered
  video for timing, legibility, audio/caption sync and misleading transitions.
  Check the output can be decoded and seeked. Fix material issues and recheck
  the affected scenes.

Keep generated media and working assets local. Do not rewrite scientific records
or commit an MP4 by default. At delivery, link the storyboard, video and a few
representative frames; name any scene that could not be supported faithfully.

## Close out

Read only **Active lessons** in
[the feedback ledger](references/feedback-ledger.md). Add a History entry only
for material reusable feedback, recording the invoked version. Routine success
needs no entry.

## Canonical task stories

For explicitly bound task explainers, resolve the group-owned canonical script
and follow [the shared explainer contract](../../presentation/EXPLAINERS.md).
Do not author another copy of its words or timing in a local storyboard. Local
exports and acceptance receipts remain derived products of that source.
