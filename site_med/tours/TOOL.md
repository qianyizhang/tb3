# Reusable medical media tool

Run `scripts/med-media --help` from the repository. The tool renders frames from retained data; it does not screen-record a live browser or require hand-timed clicks. One renderer produces the interactive view and video.

## Edit copy, translate, change pacing

- **English:** edit `site_med/tours/storyboards.json` for titles, subtitles and scene captions. `locales/en.json` holds editable English in-frame labels; a config can also override `labels`.
- **Chinese:** edit `site_med/tours/locales/zh-CN.json`. It contains all five stories plus fixed and dynamic in-frame labels. English dataset names and attribution may remain in footers. The surrounding prototype controls are primarily English.
- **Other languages:** copy the locale JSON, keep the same tour/scene identities, and use `--locale=YOUR-FILE-STEM`. The renderer wraps Chinese text by character and English by word. Review the generated stills after translating; longer text can require shortening or layout changes.
- **Timing:** set scene lengths in a config’s `durations` array, or use `--duration-scale`. Visual events stay mapped to their authored scenes; changing a caption’s reading time does not move the label-reveal or final result into the wrong scene.
- **One-off edits:** put `title`, `subtitle` or scene `title` / `caption` in `overrides`, without rewriting the English master. Do not reorder/delete scenes without updating their renderer.

```sh
# Refresh every English tour with compact settings.
scripts/med-media

# Preview new copy in still frames first.
scripts/med-media --stills-only --only=registration

# Chinese, custom copy and 9/11/10/12-second scenes (42 seconds total).
scripts/med-media --config=site_med/tours/presets/example-edit.json

# Independently export the Chinese edition of any other tour.
scripts/med-media --locale=zh-CN --only=cardiac --output=site_med/tours/exports/chinese-cardiac

# Slow all scenes by 25% in a separate variant.
scripts/med-media --only=vessels --duration-scale=1.25 --output=site_med/tours/exports/slower-vessels
```

`resolved-storyboards.json` records the actual copy and timing used for an export. WebVTT/SRT captions use those same timestamps, including millisecond precision. A locale can be switched in the interactive player without regenerating data.

## Add background music

Choose a local audio file you want to use. No music is downloaded or selected automatically.

```sh
scripts/med-media --only=segmentation \
  --music=/absolute/path/to/music.wav --music-volume=0.12 \
  --output=site_med/tours/exports/music-version
```

The track loops to cover the movie, is trimmed at the movie end, and fades in/out. `musicVolume` is a linear multiplier, not loudness normalization. Set `fadeSeconds` in the config. The source track’s filename and SHA-256 are recorded. Music is encoded as AAC for MP4 and Opus for the optional WebM preset. Silent export remains the default. The audio test used a generated tone stored only in `runs/med-media-qa/`; it is not a soundtrack choice for the demos.

## Compression presets

| Preset | Video | Stills | Intended use |
| --- | --- | --- | --- |
| `compact` (default) | H.264, slow preset, CRF 26, 24 fps, 720p | JPEG quality 90 | Smaller shareable MP4s with captions |
| `master` | H.264, slow preset, CRF 18, 24 fps, 720p | PNG | Higher-quality revision/export source |
| `web-av1` | SVT-AV1, preset 6, CRF 32, 24 fps, WebM | WebP quality 88 | Optional web variant; test the destination’s accepted formats |

```sh
scripts/med-media --preset=master --only=landmarks --output=runs/med-media-master
scripts/med-media --preset=web-av1 --only=segmentation
```

No preset reduces spatial resolution or removes source cardiac surface triangles. Video and shareable JPEG stills are lossy presentation derivatives. The interactive player instead uses **lossless WebP** scan frames and gzip-compressed JSON; decoded pixels/JSON are checked against the authoring data. Original PNGs and JSON remain under `data/` for reproduction.

The compact experiment re-encoded the original 32-second segmentation landscape movie from 2.407 MB to 1.460 MB (39.3% smaller), with full-frame SSIM 0.9964 relative to that already compressed movie. This is a codec comparison, not a clinical image-quality validation. Final regenerated files may differ slightly. Compression controls follow the [FFmpeg codec documentation](https://ffmpeg.org/ffmpeg-codecs.html); the lossless image path follows [WebP’s documented lossless mode](https://developers.google.com/speed/webp/docs/compression).

Refresh web derivatives after changing source presentation data:

```sh
.venv-br030/bin/python scripts/optimize_med_tours.py
```

The five-tour data bundle fell from 38.06 MB to 14.87 MB in this build, a 60.9% reduction, without changing decoded data. The player fetches only the selected tour’s JSON and images. Most bytes are the full cardiac geometry; this is still a local prototype, and an Astro component should defer that fetch until requested.

## Extend and reproduce

- `scripts/prepare_med_tours.py`: original segmentation, vessel and cardiac derivatives.
- `scripts/prepare_med_tours_extra.py`: retained registration crops and frozen full/cropped spine inputs.
- `scripts/optimize_med_tours.py`: verified lossless web derivatives.
- `site_med/tours/tour.js`: deterministic geometry and image rendering, interaction and scene mapping.
- `scripts/export_med_tours.cjs`: configuration, isolated browser, captions, encoding, music and manifests.
- `scripts/pack_med_tours.py`: compact media-only ZIP with current attribution and documentation.

Add a storyboard, a source-derived data JSON and its renderer; register it in the player. Keep novel scientific claims linked to retained receipts, and keep conceptual images labeled. Native arrays, task snapshots and model outputs stay untouched.

The CLI discovers the already-installed bundled Playwright package through `NODE_PATH`; it defaults to macOS Chrome and the `ffmpeg` command on PATH. Override `TOUR_BROWSER`, `FFMPEG` or `NODE_PATH` for another machine. It does not install dependencies. Serve the interactive folder with the command in [README.md](README.md).
