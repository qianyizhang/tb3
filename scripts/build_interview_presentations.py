#!/usr/bin/env python3
"""Reuse completed local reports with interview navigation and a shared theme.

Only writes runs/interview-presentations/. No trials, imports, or evidence edits.
The original reports and volume assets must already exist locally.
"""
from pathlib import Path
import argparse
import hashlib
import html
import json
import os
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'runs/interview-presentations'
REPORTS = {
    'boundaries': ('Earlier boundary audits', 'docs/boundary-audits.html', 'catalog/analyses/br004-sol-followup.md'),
    'anatomy': ('Anatomical identity', 'runs/anatomy-history-presentation/index.html', 'docs/anatomy-experiments.md'),
    'absorption': ('Tissue ownership', 'runs/br017-absorption/review/index.html', 'docs/research-rounds/BR-017-results.md'),
    'aneurysm': ('Aneurysm localization', 'runs/br016-aneurysm/blind-review/index.html', 'docs/research-rounds/BR-016-results.md'),
}


def relative(path):
    return Path(os.path.relpath(path, OUT)).as_posix()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify outputs without writing')
    args = parser.parse_args()
    theme_path = ROOT / 'docs/presentation-theme.css'
    theme = theme_path.read_text()
    source_to_output = {(ROOT / value[1]).resolve(): OUT / (key + '.html') for key, value in REPORTS.items()}
    products = {}
    receipts = []
    for key, (title, name, written) in REPORTS.items():
        source = ROOT / name
        if not source.is_file():
            raise SystemExit(f'Missing local report: {name}. See docs/reproduce.md; no evidence was regenerated.')
        original = source.read_text()
        output = OUT / (key + '.html')

        def link(match):
            attr, quote, value = match.groups()
            if not value or value.startswith(('#', '/', 'data:')) or re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', value):
                return match.group(0)
            path, sep, fragment = value.partition('#')
            target = (source.parent / html.unescape(path)).resolve()
            target = source_to_output.get(target, target)
            return attr + '=' + quote + html.escape(relative(target), quote=True) + (sep + fragment if sep else '') + quote

        page = re.sub(r'\b(href|src)=([\"\'])(.*?)\2', link, original)
        # BR-016 streams native arrays. Reuse the existing files in place, on
        # the same repository-root HTTP server as the main report.
        if key == 'aneurysm':
            prefix = relative(source.parent) + '/'
            for filename in ('manifest.json', 'references.json', 'case-stories.json'):
                old = "fetch('" + filename + "')"
                assert page.count(old) == 1, f'Unexpected {filename} loader'
                page = page.replace(old, "fetch('" + prefix + filename + "')")
            old = 'fetch(`${entry.id}/'
            assert page.count(old) == 1, 'Unexpected volume loader'
            page = page.replace(old, 'fetch(`' + prefix + '${entry.id}/')
            page = page.replace('Can a general agent read an angiogram?', 'Localizing an aneurysm')
            page = page.replace('BR-016 / A SMALL IMAGING EXPERIMENT', 'BR-016 / ANEURYSM LOCALIZATION')
            page = page.replace('<html lang="en">', '<html lang="en" class="aneurysm-report">', 1)
        nav = '<div class="interview-nav" role="navigation" aria-label="Interview report series">'
        nav += '<a href="../../docs/report.html">← Research overview</a><span>Explore the experiments</span>'
        for other, (label, _, _) in REPORTS.items():
            nav += f'<a href="{other}.html"' + (' aria-current="page"' if other == key else '') + f'>{html.escape(label)}</a>'
        nav += f'<a href="{relative(ROOT / written)}">Written evidence ↗</a></div>'
        nav += '<p class="interview-scope">Completed experiment · Original figures and trace analysis reused · One attempt per condition; no failure-rate estimate</p>'
        # Both source page structures occur in the existing reports.
        if '<body>' in page:
            page = page.replace('<body>', '<body>' + nav, 1)
        else:
            page = page.replace('<main>', nav + '<main>', 1)
        page = page.replace('</style>', '</style><style data-interview-theme>' + theme + '</style>', 1)
        products[output] = page
        receipts.append({'report': key, 'source': name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                         'output': relative(output), 'output_sha256': hashlib.sha256(page.encode()).hexdigest(),
                         'changes': 'Shared presentation theme/navigation; relative evidence links; same-origin BR-016 asset URLs; BR-016 title.'})
    manifest = {'theme_sha256': hashlib.sha256(theme.encode()).hexdigest(), 'reports': receipts,
                'scope': 'Presentation-only reuse. Original reports, trials, figures and source arrays are unchanged.'}
    products[OUT / 'manifest.json'] = json.dumps(manifest, indent=2) + '\n'
    if args.check:
        mismatches = [str(p.relative_to(ROOT)) for p, text in products.items() if not p.is_file() or p.read_text() != text]
        if mismatches:
            raise SystemExit('Missing/stale presentation outputs: ' + ', '.join(mismatches))
        print(f'All {len(REPORTS)} presentations and provenance manifest match their sources.')
    else:
        OUT.mkdir(parents=True, exist_ok=True)
        for path, text in products.items():
            path.write_text(text)
        print(f'Built {len(REPORTS)} presentations under runs/interview-presentations/.')


if __name__ == '__main__':
    main()
