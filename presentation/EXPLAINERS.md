# Canonical task explainers

The first pilot binds only the tubular-anatomy catalogue entry `ours` to
[route-unfold-teaching-v1](../groups/tubular-anatomy/presentation/stories/route-unfold-teaching-v1.story.md).
It explains one synthetic route-conditioned sampling ribbon. It does not replace
BR030's source input, supplied helpers, repair, eight planes, mesh or scorer.
Other entries keep their typed legacy recipes and three-stage player.

See the [full candidate map](EXPLAINER-CANDIDATES.md) for all 205 catalogue entries,
operation coverage and proposed migration batches. It is planning scope, not a
request to migrate every entry.

## Owners

- Group `*.story.md`: sole maintained explanation copy, beat IDs, frame-aligned
  durations and bounded route-operation channels. Six beats, 24 fps, 792 frames.
- `explanation_stories.py`: closed Pydantic parsing, explicit asset resolution,
  hash checks and deterministic browser/caption/transcript projection. Duplicate
  keys, IDs, unknown fields, coercions, references and unresolved bindings fail.
- Python presentation contracts: optional `Illustration.story_id` and resolved
  `ExplorerData.explanation_stories`. Catalogue and brief composition preserve
  the association; it is never inferred from illustration kind.
- [Prefab index](assets/teaching-prefabs.json): discovery over retained asset
  owners. [Route fixture](assets/teaching-fixtures/route-unfold-v1/README.md)
  retains the original manifest and a deliberate subset of its assets.
- Existing `use-scene-player.ts`: one on-demand clock; legacy stages or pure
  absolute story frames. Paused load, orbit/reset, visibility and reduced motion
  remain here. Capture forces a paused canonical-camera seek.
- Existing `stage.ts`: camera, lighting, renderer, annotation projection and
  disposal. Its narrow native-content seam hosts the typed route prefab. Every
  related point shares one metre-to-display transform; source values stay in m.
- `TaskVisual.tsx`: shared interactive/export composition, chapters, caption,
  scalar profile, output column and transcript. Chinese controls retain an
  explicit English-source note. GPU fallback uses the retained fixture-derived
  poster and canonical transcript; it is not a fresh integrated GPU render.

## Build and export

Use the existing environments; no model, dataset acquisition or publication is
part of this workflow. A frontend build validates story/asset dependencies and
fingerprints the compiler, scripts and retained assets. Editing any of them
invalidates the bundle before portable HTML assembly.

```sh
npm run frontend:build
npm run media -- --story=route-unfold-teaching-v1 --output=.local/explainers/NEW-BUILD
# Review a fresh stills-only destination first if editing the visual.
npm run media -- --story=route-unfold-teaching-v1 --output=.local/explainers/NEW-STILLS --stills-only
```

The existing exporter dispatches the story source to its existing browser harness
and pipe encoder. Legacy `--only=TOUR` behavior stays intact. Story exports require
a fresh destination; copy/timing, music and preset overrides are rejected for this
bounded pilot. Edit the canonical source and regenerate every projection.

`index.html` is a single-file interactive view. `?capture=1` uses the fixed
1280×720 composed root. Only that dedicated entry exposes the capture bridge;
the Explorer exposes none. Capture waits for native readiness, the requested
React commit, fonts and image decoding, then screenshots the full root, including
DOM labels, SVG leaders, image and caption. Output is H.264 at 24 fps, 33 seconds,
792 frames, without audio. The receipt records dirty-source hashes, plan/assets,
frontend/lock identity, OS/browser/GPU, settings and output hashes. Hashes describe
that local export, not clinical validity or cross-GPU pixel equality.

## Acceptance and review boundary

```sh
.venv/bin/python -m unittest discover -s tests -p test_explanation_stories.py -v
node tests/explanation_story.cjs
# Requires an existing NumPy/Pillow environment; no installation is implied.
.venv-medical/bin/python tests/route_fixture_numerics.py
node tests/explanation_story_browser.cjs EXPORT-DIR EXPLORER-HTML
node tests/task_scene_models.cjs
make presentation-check
make check PYTHON=python3.12
```

Browser-launching commands need approved execution outside the macOS restricted
sandbox, using disposable profiles. Browser acceptance distinguishes production
`file://` checks from simulated no-WebGL/context-loss tests. The original volume
and seven-decimal mesh/frame rounding allow scalar error below `3e-5` and vertex
error below `2e-7 m`. The 192×97 scalar grid is shown through the supplied bilinear
768×184 physical-aspect raster; this display derivative reproduces within one
8-bit level. It is not a CT image and its values are not HU.

Review the integrated output and local acceptance report before reusing this
prefab for a distinct route/graph explanation. Catalogue migration remains out
of scope. Retain original frozen task outcomes and all medical evidence.
