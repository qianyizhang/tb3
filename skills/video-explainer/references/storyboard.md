# Small storyboard contract

`STORYBOARD.md` is a working plan, not a new scientific record or a renderer
schema. Keep it readable in plain Markdown and traceable to TB3 sources.

```markdown
# <Title>

- Source: <task brief or finding and explanation path/ID>
- Viewer: <audience and language>
- Point: <one supported sentence the viewer should remember>
- Target length: <rough duration>

## 1. <Scene name>

- Time: ~<seconds>
- Point: <one sentence>
- Visual: <asset path or diagram description>; role: <input | result | reference | diagnostic | conceptual>
- Source: <claim locator and asset provenance, or "conceptual">
- Words: <caption or narration>
- Reveal/limit: <reference visibility, selection caveat or uncertainty if relevant>
```

Repeat the scene block only as needed. A scene may have several visual roles;
label each one. `Source` should locate the supporting finding/brief passage,
measure, trace step or figure, not merely name a broad folder. If a metric is
shown, carry its denominator and original endpoint. If a comparison is shown,
carry its comparability status. If GT/reference appears, say whether it was
solver-visible. State `unavailable` when a needed source or visual is missing.

The storyboard is inspired by HyperFrames' ordered frame plan and reviewable
intermediate artifact, but this format is independent of HyperFrames and copies
no upstream code or prose. See the
[upstream storyboard format](https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes/references/storyboard-format.md)
only if that renderer is actually selected.
