# Finding a hard task

An interview take-home investigation using coding agents to design compact,
independently verifiable benchmark tasks—and revise the claim when better
evidence arrives.

**[Read the complete report](site/index.html)** · **[Publish with GitHub Pages](site/README.md)**

One tracked page contains the overview and all four studies, including figures,
interactive comparisons and trace walkthroughs. Open `site/index.html` directly,
or serve the repository. No ignored runtime files are needed.

## Reading order

| Study | Main finding |
| --- | --- |
| [Earlier boundary audits](site/index.html#boundaries) | Three reviewed misses and one source hold; case 32 ruled out as too nitpicky; case 61 explained with a labeled omission plane. |
| [Anatomical identity](site/index.html#anatomy) | A compact-pancreas miss resolves when context is added. |
| [Tissue ownership](site/index.html#absorption) | Broad partial-inclusion audit misses; a focused audit of identical data passes. |
| [Aneurysm localization](site/index.html#aneurysm) | One reference-label miss, one localization, one source-assisted negative answer. |

No robust, repeatable Sol-failure task is established. The report preserves
individual outcomes, task-validity limits and later reassessments.

## Repository layout

- `site/`: the complete publication, editable chapters and source-image provenance.
- `docs/`: protocols, decisions, evidence receipts and the [archive index](docs/archive.md).
- `catalog/`: retained candidate reviews and trial summaries.
- `probes/`: task implementations, verifiers and frozen revisions.
- `scripts/`, `tests/`, `configs/`: workshop tooling and checks.
- `runs/`, `jobs/`: ignored local execution evidence and full-resolution viewers.

See [reproduction](docs/reproduce.md), [historical submission handoff](docs/submission.md),
and [the original assignment](docs/task.md).

## Preview and publish

```sh
python3 -m http.server 8767 --bind 127.0.0.1
```

Open `http://127.0.0.1:8767/site/index.html`.
For GitHub Pages, select **GitHub Actions** in repository **Settings → Pages**,
then push `main`. The included workflow publishes only the bundled report.
Expected URL after successful deployment: `https://qianyizhang.github.io/tb3/`.

## Maintenance

Edit `site/content/`, then run `python3 scripts/build_site.py`.
Check the bundle with `python3 scripts/build_site.py --check` and the repository
with `make check` using Python 3.12. See [contributing](CONTRIBUTING.md).
Research is closed; historical proposals are not an active queue.
