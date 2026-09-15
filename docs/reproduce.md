# Inspect and reproduce

[Final report](../site/index.html) · [Research archive](archive.md) · [Submission](submission.md)

## Read or publish

The overview and four studies are bundled in `site/index.html`. Open it directly
for offline reading, guided scan figures, and interactive comparisons.

For the full local scan explorer, double-click `site/Open local report.command`
or run:

```sh
make site
```

The report opens at **http://127.0.0.1:8768/**. Choose **Explore full scan** in the
aneurysm chapter to use linked slice sliders, zoom, contrast, original/brain-only
images, and reference markers. Keep the terminal open; Ctrl+C stops it. Reopen
with the same command whenever you want to return.

The guided figures work without `runs/`. Full exploration reads the six retained
arrays under `runs/br016-aneurysm/blind-review/R01` through `R03`; restore those
folders when moving to another machine. No trials, downloads, or package
installation run when opening the report. Written evidence links open GitHub.

## Edit and validate the presentation

```sh
python3 scripts/build_site.py
python3 scripts/build_site.py --check
```

The builder reads tracked chapters, shared styling, viewer code, and guided-figure data under `site/`. It neither launches
trials nor changes frozen evidence. [Publishing instructions](../site/README.md)
cover the included GitHub Pages workflow and the one-time repository setting.
[Presentation provenance](../site/provenance.json) identifies the reused sources.

## Original local viewers

Original generated reports and full-resolution viewers remain unchanged under
`runs/`. Their authoring records explain reconstruction:
[anatomy](../probes/revisions/anatomy-history/authoring/README.md),
[absorption](../probes/revisions/br017/authoring/README.md),
[aneurysm](../probes/revisions/br016/README.md).
These are optional research-archive tools, independent of the published page.

## Repository checks

Python 3.12, Git and Make are sufficient; Docker and model credentials are not
needed. From the repository root:

```sh
make check PYTHON=python3.12
```

The artifact gate reads the **Git index**. In a clone it checks committed inputs;
for a change, stage only the intended paths first. Tests exercise workshop
classification, provenance and tooling. They do not run model trials or certify
TB3 difficulty. See [contributing](../CONTRIBUTING.md).

## Inspect the trial catalog

```sh
python3 scripts/tb3_catalog.py list --task dicom-audit-32
python3 scripts/tb3_catalog.py report
python3 scripts/tb3_catalog.py serve
```

The last command serves the generated catalog locally. Its detailed behavior is
in the [catalog reference](catalog.md). Do not run `sync` merely to view the
archive: it imports raw results and writes catalog records.

A fresh clone contains summaries, authored reviews and task inputs, but no raw
`runs/` directory. The catalog will explicitly mark missing local evidence;
that is an availability limitation, not a newly observed model outcome.

## Re-execute an experiment

This is optional future work, outside research closeout. Use the exact owning
round protocol, freeze, dependency locks and command receipts from the
[archive](archive.md). [Historical setup](setup.md) documents the machine used,
including local network settings; those are not portable defaults. Do not
substitute present task bytes or harness defaults for a recorded snapshot.

For the final task, follow the clean submission's own commands and evaluation
status described in [the handoff](submission.md).

## Restore local evidence

Keep a copy of the whole workspace, including ignored `runs/`, when moving to
another machine. Restore raw files under their original repository-relative
paths before inspecting hash-bound reviews. The local closeout snapshot under
`runs/archive-closeout/` preserves pre-cleanup authored files and a SHA-256
inventory; it is a same-disk recovery copy, not an off-machine backup.

Raw runs, environments and caches were retained during cleanup because the
submission work was active. No remote backup, data deletion or GitHub archive
operation is implied by this research closeout.
