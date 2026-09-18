# Medical imaging with coding agents

Six source-backed articles explain what the tasks require, what agents did, and
where their outputs held up or failed. The main stories are written for readers
with either a technical or clinical background, with deeper evidence linked.

The cross-task synthesis, current-state assessment and future outlook remain for
a separate editorial pass. This page is navigation, not that synthesis.

| Article | Anchor experiment | Guided tour |
| --- | --- | --- |
| [Tissue ownership](01-segmentation.md) | BR-017 organ-label audit | [Segmentation](tours/index.html?tour=segmentation) |
| [Aneurysm localization](02-aneurysms.md) | BR-016 three-case pilot | Native viewer linked in the article |
| [Matching after a breath](03-registration.md) | BR-028 sparse CT correspondence | [Registration](tours/index.html?tour=registration) |
| [Vessel repair and curved views](04-vessels-cpr.md) | BR-030 coronary geometry; BR-033 contrast | [Vessels](tours/index.html?tour=vessels) |
| [Cardiac shape and motion](05-cardiac-mechanics.md) | BR-035 segmentation-to-mechanics | [Cardiac](tours/index.html?tour=cardiac) |
| [Named landmarks and scan coverage](06-landmarks.md) | BR-040 CT/MRI localization | [Landmarks](tours/index.html?tour=landmarks) |

## Where things live

| Path | Purpose | Git treatment |
| --- | --- | --- |
| `01-*.md` … `06-*.md`, [references.md](references.md) | Current article copy and reproduction links | Tracked |
| `task_cards/` | Source-linked measurements, JSON pointers and source hashes | Tracked |
| `assets/` | Eleven attributed scientific PNGs, six editable Mermaid diagrams and their manifest | Tracked; binary figures individually allowlisted |
| [editorial/](editorial/README.md) | Brief, decisions, source audit and migration notes | Tracked |
| [tours/](tours/README.md) | Player, storyboards, translations and encoding presets | Authored files tracked |
| `tours/data/`, `tours/web/`, `tours/exports/` | Derived geometry, compressed web assets, videos, subtitles and social packs | Local, ignored, reproducible |
| `tours/validation.json`, `tours/compression-report.json` | Latest local media verification receipts | Local, ignored |
| `css/`, `js/`, `data/` | Earlier HTML presentation; `data/segmentation_assets.js` also supplies retained figure bytes | Existing files retained |

The articles, task cards and six guided tours are the current editorial version.
The older `scripts/build_site_med.py` HTML builder has not been brought into line
with it. Its generated prose is not a source of current claims. The obsolete
Markdown and task-card generators have been removed so they cannot overwrite the
source-backed version.

## Read, edit or rebuild

- [Source guide](references.md): evidence, task definitions and reproduction limits.
- [Tour guide](tours/README.md): local playback, source distinctions and attribution.
- [Reusable media tool](tours/TOOL.md): copy, Chinese translation, scene timing,
  optional music, encoding and exports. Entry point: `scripts/med-media --help`.
- [Editorial decisions](editorial/README.md): audience, narrative structure and
  qualifications to preserve during Astro migration.

From the repository root:

```sh
python3.12 scripts/check_site_med.py          # portable content and figure checks
python3.12 scripts/check_site_med.py --local  # also require local media/evidence links
python3.12 scripts/check_med_tours.py --exports  # requires retained local tour data
python3 -m http.server 8796 --bind 127.0.0.1 --directory site_med/tours
```

Open `http://127.0.0.1:8796/` for local tours. A clean checkout includes the
articles and static figures; interactive datasets and movies must be rebuilt
from retained local inputs using the tour guide. No model reruns are needed to
rebuild the presentation. Nothing here publishes or migrates to Astro.
