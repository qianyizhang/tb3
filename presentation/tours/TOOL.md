# Reusable medical media tool

Run `npm run media -- --help` from the repository. The tool renders frames from retained data; it does not screen-record a live browser or require hand-timed clicks. One renderer produces the interactive view and video.

## Edit copy, translate, change pacing

- **English:** edit `presentation/tours/storyboards.json` for titles, subtitles and scene captions. `locales/en.json` holds editable English in-frame labels; a config can also override `labels`.
- **Chinese:** edit `presentation/tours/locales/zh-CN.json`. It contains all six stories plus fixed and dynamic in-frame labels. English dataset names and attribution may remain in footers. The surrounding prototype controls are primarily English.
- **Other languages:** copy the locale JSON, keep the same tour/scene identities, and use `--locale=YOUR-FILE-STEM`. The renderer wraps Chinese text by character and English by word. Review the generated stills after translating; longer text can require shortening or layout changes.
- **Timing:** set scene lengths in a config’s `durations` array, or use `--duration-scale`. Visual events stay mapped to their authored scenes; changing a caption’s reading time does not move the label-reveal or final result into the wrong scene.
- **One-off edits:** put `title`, `subtitle` or scene `title` / `caption` in `overrides`, without rewriting the English master. Do not reorder/delete scenes without updating their renderer.

```sh
# Refresh every English tour with compact settings.
npm run media --

# Preview new copy in still frames first.
npm run media -- --stills-only --only=registration

# Chinese, custom copy and 9/11/10/12-second scenes (42 seconds total).
npm run media -- --config=presentation/tours/presets/example-edit.json

# Independently export the Chinese edition of any other tour.
npm run media -- --locale=zh-CN --only=cardiac --output=presentation/tours/exports/chinese-cardiac

# Slow all scenes by 25% in a separate variant.
npm run media -- --only=vessels --duration-scale=1.25 --output=presentation/tours/exports/slower-vessels
```

`resolved-storyboards.json` records the actual copy and timing used for an export. WebVTT/SRT captions use those same timestamps, including millisecond precision. A locale can be switched in the interactive player without regenerating data.

## Add background music

Choose a local audio file you want to use. No music is downloaded or selected automatically.

```sh
npm run media -- --only=segmentation \
  --music=/absolute/path/to/music.wav --music-volume=0.12 \
  --output=presentation/tours/exports/music-version
```

The track loops to cover the movie, is trimmed at the movie end, and fades in/out. `musicVolume` is a linear multiplier, not loudness normalization. Set `fadeSeconds` in the config. The source track’s filename and SHA-256 are recorded. Music is encoded as AAC for MP4 and Opus for the optional WebM preset. Silent export remains the default. The audio test used a generated tone stored only in `runs/med-media-qa/`; it is not a soundtrack choice for the demos.

## Compression presets

| Preset | Video | Stills | Intended use |
| --- | --- | --- | --- |
| `compact` (default) | H.264, slow preset, CRF 26, 24 fps, 720p | JPEG quality 90 | Smaller shareable MP4s with captions |
| `master` | H.264, slow preset, CRF 18, 24 fps, 720p | PNG | Higher-quality revision/export source |
| `web-av1` | SVT-AV1, preset 6, CRF 32, 24 fps, WebM | WebP quality 88 | Optional web variant; test the destination’s accepted formats |

```sh
npm run media -- --preset=master --only=landmarks --output=runs/med-media-master
npm run media -- --preset=web-av1 --only=segmentation
```

No preset reduces spatial resolution or removes source cardiac surface triangles. Video and shareable JPEG stills are lossy presentation derivatives. The interactive player instead uses **lossless WebP** scan frames and gzip-compressed JSON; decoded pixels/JSON are checked against the authoring data. Original PNGs and JSON remain under `data/` for reproduction.

The compact experiment re-encoded the original 32-second segmentation landscape movie from 2.407 MB to 1.460 MB (39.3% smaller), with full-frame SSIM 0.9964 relative to that already compressed movie. This is a codec comparison, not a clinical image-quality validation. Final regenerated files may differ slightly. Compression controls follow the [FFmpeg codec documentation](https://ffmpeg.org/ffmpeg-codecs.html); the lossless image path follows [WebP’s documented lossless mode](https://developers.google.com/speed/webp/docs/compression).

Refresh web derivatives after changing source presentation data:

```sh
.venv/bin/med media optimize
```

The six-tour data bundle falls from 38.81 MB to 15.54 MB, a 60.0% reduction, without changing decoded data. The player fetches only the selected tour’s JSON and images. Most bytes are the full cardiac geometry; this is still a local prototype, and an Astro component should defer that fetch until requested.

## Extend and reproduce

- `tb3_medical.media`: restore the retained derived snapshot, check scientific display invariants, optimize lossless web assets.
- `presentation/tours/inputs.json`: exact canonical inputs, restored under `.local/inputs/tours/`.
- `scripts/export_med_tours.cjs`: browser rendering, captions, encoding, music and manifests, using declared Playwright dependencies.
- `docs/migration/retired-interfaces.json`: recovery locators for historical raw derivation programs. They are not runtime dependencies.

Setup: `uv sync --locked --inexact --group dev --extra imaging`, `npm ci`, and
`npx playwright install chromium`. Install FFmpeg separately when producing video.
Use `med media prepare` after restoring the listed input files, then `med media check`.
`TOUR_BROWSER` is an optional explicit browser executable; otherwise Playwright's
installed Chromium is used. No personal Codex cache is consulted.

The older social ZIP and raw-data preprocessing commands are retired. Existing
outputs remain local; selected video/still outputs can be shared with these source
notices and their renderer manifest. Nothing is published automatically.

## Browser verification

After the declared Node/Playwright setup, check navigation, source panels,
keyboard/mobile behavior and deferred tours with:

```sh
make presentation-check
# Use the Playwright-managed browser instead of installed Chrome.
PLAYWRIGHT_CHANNEL=chromium make presentation-check
```

The harness uses disposable profiles. On macOS, run browser-launching checks
outside the restricted command sandbox with approval for that specific command.
If startup reports a permission denial or immediate LaunchServices/WindowServer
abort, stop unchanged retries and report verification as blocked. Headless mode
and Chrome's `--no-sandbox` flag do not bypass that outer execution boundary.
Do not use personal browser profiles or stop unrelated browsers.

Reports and screenshots go to `.local/presentation-qa/`, separate from the site.
Override `PRESENTATION_OUTPUT` and `PRESENTATION_REPORTS` when needed. Ordinary
`make check` does not launch a browser.
