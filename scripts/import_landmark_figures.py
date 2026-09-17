#!/usr/bin/env python3
"""Import selected exact BR-040 panels and complete point tables; no inference."""
import base64
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'runs/br040-sol-landmarks/review/index.html'
SELECTED = {
    'ct-full': ['C3', 'L3'],
    'ct-partial': ['T4', 'T5'],
    'mri32-full': ['1', '20', '28'],
}


def main():
    receipts = {}
    def read(path):
        data = (ROOT / path).read_bytes()
        receipts[path] = hashlib.sha256(data).hexdigest()
        return data
    raw = read(SOURCE).decode()
    sections = re.findall(r'<section>.*?</section>', raw, re.S)
    assert len(sections) == 3
    output = []
    for section, (case, keys) in zip(sections, SELECTED.items()):
        assert f'<h2>{case}</h2>' in section
        images = {}
        for key in keys:
            filename = f'{case}-{key}.png'
            images[filename] = 'data:image/png;base64,' + base64.b64encode(read(str(Path(SOURCE).parent / filename))).decode()
        options = ''.join(f'<option value="{name}">{name.removesuffix(".png")}</option>' for name in images)
        section = re.sub(r'<select.*?</select>', '<select aria-label="Review landmark">' + options + '</select>', section)
        section = re.sub(r'<img src="[^"]+">', f'<img alt="Three native planes with reference and model projections" src="{next(iter(images.values()))}">', section)
        section = section.replace('<section>', f'<section data-landmark-case="{case}">')
        output.append({'case': case, 'html': section, 'images': images})
    evidence = ['docs/evidence/br040-results.json', 'docs/evidence/br040-source-audit.json', 'docs/evidence/br038-validation.json', 'docs/evidence/br039-validation.json']
    for path in evidence:
        read(path)
    (ROOT / 'site/landmark-figures.json').write_text(json.dumps(output, separators=(',', ':')) + '\n')
    provenance = {
        'source': SOURCE, 'evidence': receipts,
        'derivation': 'Seven exact retained PNGs; all 84 requested-point rows retained. Panels selected to show wrong-level errors, unavailable T4, missed visible T5, and both MRI improvement and regression. No image modification or new inference.',
        'geometry': 'Reference-centred native slices; markers projected into each plane; printed off-plane offsets. Scores use full 3D physical distances.',
        'attribution': [
            {'source': 'https://github.com/anjany/verse', 'subject': 'VerSe sub-verse823', 'license': 'CC BY-SA 4.0', 'changes': 'Native CT slices cropped and annotated for comparison; derived CT illustrations retain CC BY-SA 4.0.'},
            {'source': 'https://openneuro.org/datasets/ds004470', 'subject': 'AFIDs SNSX sub-C001', 'license': 'CC BY 4.0', 'changes': 'Native T1 MRI slices cropped and annotated; consensus AFIDs references.'},
        ],
    }
    (ROOT / 'site/landmark-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')


if __name__ == '__main__':
    main()
