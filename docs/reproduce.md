# Reproduction and presentation

Set up the installed package through the [workflow](workflow.md). Supported
operations depend on the selected experiment. Canonical metadata does not imply
that every historical task can be rerun. The dated
[coverage inventory](migration/native-experiment-inventory.md) records migration
support; the experiment's current config and input manifest define actual inputs.

## Saved CT/MRI output replay

The maintained BR-040 landmark method supports three cases: `ct-full`, `ct-partial`
and `mri32-full`. Restore the exact local inputs named in its
[input manifest](../groups/anatomical-landmarks/experiments/br040/inputs.json).
Source locators explain provenance; the CLI does not search old directories as a
fallback or download missing data.

```sh
uv run med prepare anatomical-landmarks-br040 --case ct-partial
uv run med prepare anatomical-landmarks-br040 --case ct-partial --execute
uv run med replay anatomical-landmarks-br040 --case ct-partial
```

`prepare` previews unless `--execute` is supplied. `replay` rescores saved answers
and appends a scoring observation for the same attempt, including its comparison
criterion. It writes a receipt; it is not a new execution. The
[native implementation closeout](migration/native-closeout.md) records exact
agreement for six retained CT/MRI outputs. That proof covers saved-output scoring,
not fresh Docker execution or repeatable model behavior.

For a native-plane review image, install the optional imaging dependencies:

```sh
uv sync --locked --extra imaging
.venv/bin/med view anatomical-landmarks-br040 --case ct-partial
```

Use [exports and submission](submission.md) to build and verify the standalone
MRI replay package. Other historical methods remain source evidence under
`probes/` and their linked protocols. Their old authoring runners are not supported
daily commands; importing some of them can mutate artifacts.

## Portable stories and local tours

```sh
uv run med present
uv run med present --serve
uv run med check --assets
```

`present` writes the portable index to `.local/site/`; `--serve` starts a local
server at `http://127.0.0.1:8765`. It does not publish. Group stories and retained
figures work without raw scans. The index includes the Task Explorer, with a
return link to the workbench. `med brief build` still creates an independent
single-file Explorer. Selected small text sources can be inspected within its
Sources panel; omitted local inputs remain explicitly unavailable. Retained
preview images carry their own source notices and usage restrictions.

Index filters and the selected record are retained in the URL. Chapter navigation
opens the rendered chapters, including heading fragments. `check --assets` additionally verifies selected
figure extraction inputs when those are available.

For presentation changes, use the optional browser regression command after
setting up the declared Node/Playwright dependencies in the [media guide](../presentation/tours/TOOL.md):

```sh
make presentation-check
# With Playwright's bundled Chromium instead of installed Chrome:
PLAYWRIGHT_CHANNEL=chromium make presentation-check
```

This builds a fresh portable view under `.local/presentation-check/` and checks
chapter links, source navigation, URL history, keyboard focus, mobile layout and
tour selection ordering. It needs no scans, inference or media rendering. Missing
optional previews are tested as explicit unavailable states. The separate
presentation CI workflow provisions its declared browser and runs the same checks
for changes to presentation inputs; the ordinary `make check` remains Python-only.

For guided tours, first restore the exact derived inputs in
[presentation/tours/inputs.json](../presentation/tours/inputs.json), then run:

```sh
uv run med media prepare
uv run med media check
uv run med present --serve --local-media
```

This restores and checks the retained derived snapshot, not every original raw
scan preprocessing step. Missing inputs produce an operation-specific error.
After installing the imaging extra, `.venv/bin/med media optimize` generates
lossless player assets. Optional still/video rendering uses the separately declared
Node/Playwright setup, with FFmpeg for video, in the
[media guide](../presentation/tours/TOOL.md). No personal dependency cache is required.

## Recovery boundaries

Historical files may refer to `site/`, `site_med/`, `catalog/` or retired scripts.
Use [archive recovery](../archive/README.md) to inspect their original context;
use the commands above for the current presentation. Do not run an old generator
to repair a historical link.

Raw runs, environments and generated media remain local. Missing input files,
mutable historical Docker tags, dataset access/licensing and independent backup
are separate recovery concerns. A successful file restore or saved-output replay
does not establish clinical validity or submission readiness.
