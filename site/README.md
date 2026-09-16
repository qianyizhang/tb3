# Interview report

`index.html` contains the overview and five studies in one portable page. All
figures, styling, and guided image controls are embedded. Open it directly in a
browser; it also works under a GitHub project-site prefix. Evidence links open
GitHub. The published page never requests local scans.

## Come back and explore locally

Double-click **Open local report.command** in this folder, or run from the repo:

```sh
make site
```

This opens **http://127.0.0.1:8768/** in your browser. In the aneurysm chapter,
choose **Explore full scan** on any case. You can:

- Scroll through linked side, front, and top views.
- Click an image to move the shared cursor.
- Change zoom, brightness, and the number of combined slices.
- Switch between the original scan and the brain-only image.
- Hide the guide markers or return to the reference location.

A lower **White level** makes the image brighter. **Single slice** is useful for
confirming depth; combined slices show the brightest value along several slices.
Yellow rings mark approximate reference locations, not lesion boundaries. Pink
diamonds mark Sol's answer; blue crosshairs mark your cursor.

Keep the terminal open while exploring. Stop with Ctrl+C; run `make site` or
use the launcher to return later. An existing report server is reused. To choose
another port or avoid automatically opening the browser:

```sh
python3 scripts/serve_site.py --port 8769
```

The server uses Python's standard library and listens only on this computer.
It reads the six existing arrays in `runs/br016-aneurysm/blind-review/R01` through
`R03`. It does not install packages, launch trials, download scans, or rewrite
source files. One scan is loaded at a time. On a fresh clone, the guided figures
still work; restore those folders from your local archive for full exploration.

## Edit and preview

- `content/`: authored chapter text, comparisons, and retained trace images.
- `report.css`: shared typography, spacing, colors, and controls.
- `aneurysm.js`: guided figures and optional native-array viewer.
- `aneurysm-figures.json`: small, source-derived views with crop coordinates,
  voxel spacing, reference points, and source checksums.

After editing:

```sh
python3 scripts/build_site.py
python3 scripts/build_site.py --check
make site
```

Refresh the local page to see changes. Commit changed sources and rebuilt
`index.html` together. Chapter files are build inputs; use `index.html` to read
the report. `build_site.py` requires no native scans or imaging libraries.

Re-render the guided scan figures only when deliberately changing their display:

```sh
.venv-br003/bin/python scripts/render_site_scans.py
python3 scripts/build_site.py
```

The renderer uses NumPy and Pillow from the existing imaging environment. It
reads retained arrays in place and writes only `site/aneurysm-figures.json`.
The positive cases use 48 mm fields centered on the source references; all views
combine seven native slices. Reference overlays are drawn separately, so they
can be hidden. No generated or retouched anatomy is used.

`provenance.json` retains migration history and the current figure derivation.
Update changed large-file receipts in `configs/artifact-policy.json` before
staging. Frozen tasks, source scans, and original model images stay unchanged.

## Publish with GitHub Pages

1. In **Settings → Pages → Build and deployment**, select **GitHub Actions**.
2. Push `main`, or run **Publish interview report** from the Actions tab.
3. The workflow publishes only `site/index.html` at
   `https://qianyizhang.github.io/tb3/`.

The full native scan arrays remain local. Publishing this report does not
publish them. Local edits alone do not update the hosted page.

## Registration session

The Registration chapter covers BR-019–024 and BR-028, including the later
user acceptance of q06 alongside the unchanged numerical result. It reuses
actual CT panels with query and plane controls, without loading native scans.
`registration-provenance.json` records source attribution and exact hashes.
The standard build needs only the tracked `registration-figures.json`; refreshing
that authored payload deliberately requires the retained BR-028 report:

```sh
python3 scripts/import_registration_figures.py
python3 scripts/build_site.py
```
