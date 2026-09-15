# Inspect and reproduce

[Final report](report.html) · [Research archive](archive.md) · [Submission](submission.md)

## Read without setup

Open `docs/report.html` in a browser. It is a standalone, offline report with
no package installation or external script dependency. Evidence links resolve
against the repository; links explicitly marked local-only need retained `runs/`.

For a local HTTP preview, from the repository root:

```sh
python3 -m http.server 8766 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8766/docs/report.html`. Stop the server when finished.

## Experiment presentations

The updated overview links three reused presentations. With the existing raw
reports/assets restored, run from the repository root:

```sh
python3 scripts/build_interview_presentations.py
python3 scripts/build_interview_presentations.py --check
python3 -m http.server 8767 --bind 127.0.0.1
```

Open `http://127.0.0.1:8767/docs/report.html`. All three presentations use that
same origin and provide navigation back to the overview. No other report server
or fixed localhost port is required.

The builder reads the existing anatomy-history, BR-017 and BR-016 reports,
retains their analysis and interactions, and adds `docs/presentation-theme.css`
plus shared navigation. It writes only `runs/interview-presentations/`.
Its manifest records the source/output hashes. Original reports stay unchanged.

| Presentation | Required original output |
| --- | --- |
| Anatomy history | `runs/anatomy-history-presentation/index.html` |
| Absorption | `runs/br017-absorption/review/index.html` |
| Aneurysm | `runs/br016-aneurysm/blind-review/`, including JSON and native `.bin` arrays |

The first two pages embed their images and can open offline. The aneurysm page
fetches local arrays, so use HTTP rather than a file URL. A fresh Git clone lacks
these ignored outputs; read the linked written reports or restore the local
archive. The original authoring READMEs describe source-report reconstruction:
[anatomy](../probes/revisions/anatomy-history/authoring/README.md),
[absorption](../probes/revisions/br017/authoring/README.md),
[aneurysm](../probes/revisions/br016/README.md). Those source builders may also
write derived trace indexes; they are not automatically run by this wrapper.

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
