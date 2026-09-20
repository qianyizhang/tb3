# Guided medical-image tours

Six local, source-derived prototypes share one storyboard and renderer. Each has a short interactive tour, two captioned videos and a set of still frames. [Reusable tool guide: copy, Chinese translation, pacing, music and encoding](TOOL.md). No model trial was rerun. The main site’s index synthesis remains separate.

| Tour | Story | Landscape / portrait | Still frames |
| --- | --- | --- | --- |
| Tissue ownership | Original organ labels → controlled reassignment → transferred region → broad/focused audit outcome | [32 s landscape](exports/segmentation-landscape.mp4) · [32 s portrait](exports/segmentation-portrait.mp4) | `exports/segmentation-*-step1.jpg` through `step4.jpg` |
| Vessel to CPR | Real gap → local repair → linked section/CPR → distance-axis error | [36 s landscape](exports/vessels-landscape.mp4) · [36 s portrait](exports/vessels-portrait.mp4) | `exports/vessels-*-step1.jpg` through `step4.jpg` |
| Shape and motion | Supplied masks → reconstructed geometry → matched material probes → strain → conceptual ambiguity | [40 s landscape](exports/cardiac-landscape.mp4) · [40 s portrait](exports/cardiac-portrait.mp4) | `exports/cardiac-*-step1.jpg` through `step5.jpg` |
| Match after a breath | Actual CT neighborhoods → earlier/final errors → frozen threshold | [32 s landscape](exports/registration-landscape.mp4) · [32 s portrait](exports/registration-portrait.mp4) | `exports/registration-*-step1.jpg` through `step4.jpg` |
| Outside or missed? | Full spine → actual crop boundary → T4 abstention → visible T5 miss | [32 s landscape](exports/landmarks-landscape.mp4) · [32 s portrait](exports/landmarks-portrait.mp4) | `exports/landmarks-*-step1.jpg` through `step4.jpg` |
| Find the bulge | Full scan → three native planes → accepted point and weak label → missed finding → source-assisted contrast | [40 s landscape](exports/aneurysm-landscape.mp4) · [40 s portrait](exports/aneurysm-portrait.mp4) | `exports/aneurysm-*-step1.jpg` through `step5.jpg` |

Videos are H.264 / yuv420p at 24 fps, 1280×720 or 720×1280, with fast-start metadata. They have no audio; captions are burned into the frames. Matching `.vtt` and `.srt` files support a native player or a separate caption track. Portrait layouts are composed independently, not cropped from landscape. The JPEG step frames can also become a carousel. The [social media pack](exports/social-pack.zip) collects the twelve English videos, 52 JPEG stills, caption tracks and source notes without HTML. Outputs stay local; nothing has been published or migrated.

## Open and explore

From the repository root:

```sh
python3 -m http.server 8796 --bind 127.0.0.1 --directory presentation/tours
```

Open `http://127.0.0.1:8796/`. Add `?tour=segmentation`, `?tour=vessels`, `?tour=cardiac`, `?tour=registration`, `?tour=landmarks` or `?tour=aneurysm` for a direct link. The player does not autoplay. The language selector covers all six stories; download links explicitly identify the English edition. A [42-second Chinese example](exports/chinese-example/segmentation-portrait.mp4) demonstrates independent translation and scene timing. Use Play, time scrubbing or chapter buttons; pause to explore physical slices, route position, CPR rotation, cardiac phase or a shared 3D camera. **Return to guided view** restores the authored view. Files must be served over HTTP, since a `file:` URL cannot fetch the local JSON reliably.

## What is measured, derived or conceptual?

- **Segmentation (BR-017):** TotalSegmentator case s1233. Original N01 and edited M02 organ masks are sampled on the same CT planes in LPS millimetres. The 180 mm square crop and window level 50 / width 400 are fixed. Salmon is pancreas, blue duodenum, yellow the exact transferred region. A translucent fill makes the source contours legible at phone size. The guided sweep uses interior slices; the slider includes all 24 exported planes. The focused audit point is displayed only on its own z = 324.7 mm plane. It is an accepted point near included tissue, not a centroid. Broad and focused outcomes are one Sol run each, not a causal estimate or clinical accuracy study.
- **Vessels (BR-030):** ImageCAS case 1, with ImageCAS-X source material and a real CAS-Net segmentation gap. The view uses the saved Terra repair, its 103 added voxels and all 371 centerline positions. Display surfaces are simplified; source geometry and grading artifacts remain unchanged. Every route position has its own CT cross-section; the cursor, square and ribbon use the same saved path index. The eight CPR ribbons contain saved HU values, windowed to −100…700 HU. The transverse image is resampled from the original CT in the same local frame. CPR image aspect is chosen for explanation, not quantitative caliper use. The author-corrected `arc_mm` is used; the original 184.81 mm axis and resulting model failure remain explicit. The corrected saved route measures 175.92 mm. This case came from the source training split.
- **Cardiac (BR-035):** The masks-only Sol run on a STRAUS **simulation**, not a patient. All 30 phases and all retained surface triangles are shown. The two models share physical scale, camera and phase. Surface shading is geometric lighting, not strain. The 24 material probes come from a deterministic spread of covered source cells and start at matched reference positions; they were not selected by error. Dots are visible through the surfaces for inspection. The regional engineering-strain curve is region 1’s average; it is distinct from the 7.37 percentage-point local radial-strain MAE. The 5-point cutoff is a research target. Playback repeats a cycle in four seconds for readability and does not represent physiological timing. The final twisting cylinder is an analytical illustration of ambiguity, not an observed explanation of this run’s error.


- **Registration (BR-028):** Exact retained 62.4 mm review crops in four planes, with all eight query points and saved scoring rows. Each source/reference/prediction crop is independently centered, so their apparent alignment is not a displacement measurement. Earlier/final comparison changes both input information and strategy. The gray bars show the earlier 2D-source attempt; final errors are color-coded and the 5 mm maximum is marked. The q06 frozen failure remains separate from later visual acceptance. Source: Learn2Reg LungCT 1.11, Hering, Murphy and van Ginneken, [CC BY 4.0 record](https://doi.org/10.5281/zenodo.3835682); [retained results](../../docs/evidence/br028-results.json).
- **Landmarks (BR-040):** The full and cropped VerSe CT arrays share native sagittal index 263. The actual crop retains k indices 0–919 from the full scan. Gold marks the reference center and true crop boundary; gray shading reveals which full-scan anatomy was outside the cropped task. Point markers are projected, not guaranteed to lie in the selected plane. The reference T4 center lies outside, T5 inside. Terra/high and Sol/xhigh differ in both model and reasoning setting. Derived VerSe illustrations retain CC BY-SA 4.0; [source notice](../../runs/br039-ct-landmarks/tasks/ct-full/environment/SOURCE_NOTICE.md), [results](../../docs/evidence/br040-results.json).


- **Aneurysm (BR-016):** N02 is the anchor, with N01 and N03 as contrasts. The opening image is a whole-volume maximum projection of the skull-stripped TOF-MRA. Subsequent views are native slices in approximately 32 mm crops, with 25 neighboring indices per axis and physical aspect preserved. The tour uses stored RAS orientation: i increases toward right, j anterior, k superior; screen horizontal increases rightward and screen vertical upward. These are dataset-oriented views, not a radiological display convention. Gold is the actual weak source mask, excluding the scoring tolerance dilation. Teal is the submitted point, displayed only on its own plane. Neither is a precise clinical lesion boundary. The guided crop and reference reveal were authored afterward, not given as trial inputs. Pause to change the primary plane, sweep neighboring slices, or hide the weak label. The older full-volume native explorer remains available through the [chapter reproduction links](../../groups/lesion-localization/presentation/story.md#inspect-or-reproduce).

The cardiac renderer caches unchanged phase/camera views to keep playback responsive. It retains the full source surface because an aggressively simplified moving mesh produced distracting display artifacts in the first draft. The cardiac geometry is about 32.5 MB before compression; the complete six-tour player bundle is about 15.54 MB after lossless compression. Load it on demand during Astro integration.

## Sources and attribution

Exact local inputs and SHA-256 digests are in [data/provenance.json](data/provenance.json). Export dimensions, durations, frame counts, file hashes and renderer/storyboard hashes are in [exports/manifest.json](exports/manifest.json). These are presentation derivatives; source licenses and attribution remain applicable.

- **OpenNeuro ds003949:** Lausanne TOF-MRA cohort, Di Noto et al., CC0; [retained source notice](../../runs/br016-aneurysm/tasks/aneurysm-n02-v2/environment/SOURCE_NOTICE.md), [trial ledger](../../docs/evidence/br016-results.json). The three selected scans do not establish diagnostic accuracy; N03 follows allowed source lookup.
- **TotalSegmentator:** [dataset record](https://zenodo.org/records/6802614), [source project](https://github.com/wasserth/TotalSegmentator), CC BY 4.0. Local task provenance: [BR-017 authoring](../../probes/revisions/br017/authoring/README.md). The tour changes the label presentation and shows the workshop’s controlled label edit.
- **ImageCAS / ImageCAS-X:** [ImageCAS listing](https://www.kaggle.com/datasets/xiaoweixumedicalai/imagecas), [ImageCAS-X record](https://zenodo.org/records/21887809), [source project](https://github.com/kitbransby/ImageCAS-X). The retained receipt records Apache 2.0 on the ImageCAS listing and CC BY 4.0 on the ImageCAS-X record. See the [exact source receipt](../../docs/evidence/br030-sources.json), including scan, masks and source revisions. Tour geometry, camera, highlights and CPR display are derived presentation material.
- **STRAUS:** [source dataset](https://humanheart-project.creatis.insa-lyon.fr/multimodalityStraus.html), [local cardiac provenance](../../groups/cardiac-motion/presentation/sources/cardiac-provenance.json) and [BR-035 result receipt](../../docs/evidence/br035-segmentation-mechanics-results.json). These local tour previews include simulation-derived meshes and mask images; they extend the earlier plot-only publication bundle. The earlier report’s “no full meshes” scope does not describe this local folder. Source terms are not broadened by generating previews.

For a social post, retain the source attribution and the experiment qualification in the post description. [social-copy.md](social-copy.md) contains compact copy to accompany each video.

## Reproduce the presentation

The preprocessing environment already present in this workspace has NumPy, SciPy, Pillow, nibabel, scikit-image, trimesh and VTK:

```sh
.venv-br030/bin/python scripts/prepare_med_tours.py
.venv-br030/bin/python scripts/prepare_med_tours_extra.py
.venv-br030/bin/python scripts/prepare_med_tours_aneurysm.py
.venv-br030/bin/python scripts/optimize_med_tours.py
```

This reads retained local arrays under `runs/`; a clean checkout alone does not include them. It writes only the presentation data folder. It does not regenerate benchmark tasks or model predictions.

The export script needs Node.js, Playwright, a local Chromium/Chrome executable and FFmpeg. This workspace can use the bundled Playwright package:

```sh
NODE_PATH=/Users/zhangqy/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules \
  node scripts/export_med_tours.cjs
```

Use `scripts/med-media` as the normal entry point; the Node script remains available. The script starts its own temporary localhost server. It defaults to the installed macOS Google Chrome and `ffmpeg` on PATH; override with `TOUR_BROWSER` and `FFMPEG` on another machine. `--stills-only` renders storyboards, `--only=cardiac` rerenders one tour, and `--fps=24` sets the frame rate. A normal export renders all six, records the hashes and closes the temporary server. It never downloads dependencies or contacts a model provider.

```sh
python3.12 scripts/check_med_tours.py --exports
python3.12 scripts/check_medical.py
```

## Astro handoff

Keep `storyboards.json`, the renderer, source data and export manifest together. Move the player into an isolated component and load the selected tour on interaction; avoid pulling cardiac geometry into every chapter. Reuse the same deterministic frame rendering for subsequent video exports. Use the MP4 poster/video as a static fallback and retain the prose caption outside the canvas for accessibility. The current shell is a prototype, not a redesign of the site’s HTML/CSS.
