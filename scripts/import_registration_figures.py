#!/usr/bin/env python3
"""Reuse exact BR-028 review images in the portable session chapter.

Run only when intentionally refreshing authored figures. The normal site build
reads the tracked payload and needs no ignored evidence, image library or CT.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'runs/br028-registration-3d-source/review/index.html'


def main():
    raw = (ROOT / SOURCE).read_text()
    data, _ = json.JSONDecoder().raw_decode(raw.split('const data=', 1)[1])
    payload = {key: data[key] for key in ['ids', 'source', 'manual']}
    payload['methods'] = {key: value for key, value in data['methods'].items() if key.startswith('Sol /')}
    target = ROOT / 'site/registration-figures.json'
    target.write_text(json.dumps(payload, separators=(',', ':')) + '\n')
    evidence = [SOURCE, 'site/registration-figures.json',
                'docs/evidence/br028-results.json', 'docs/evidence/br028-adjudication.json',
                'docs/evidence/br028-formulation-analysis.json',
                'probes/registration-deformation/authoring/br028_present.py',
                'probes/registration-deformation/authoring/present.py']
    provenance = {
        'scope': 'BR-019–024 and BR-028 session synthesis; no new model trial.',
        'source': 'Learn2Reg LungCT 1.11, Hering, Murphy and van Ginneken (2020), Radboud University Medical Center',
        'license': 'CC BY 4.0', 'source_url': 'https://doi.org/10.5281/zenodo.3835682',
        'figure_method': 'Reuse exact base64 PNGs from the completed BR-028 review. 97x97 trilinear samples, 0.65 mm step, 62.4 mm center-to-center field, original window and center cross. Three orthogonal source planes use full source CT; oblique source uses the original 2D view. Target panels are separately centered at manual/old/new coordinates in the same plane. Dataset axes are not asserted scanner LPS/RAS.',
        'changes': 'Select the two model methods; no change to image bytes or coordinates. Add authored narrative and separate post-trial user adjudication.',
        'limits': 'Centered panels can look similar despite coordinate offsets. Derived report planes are not necessarily agent-used patches. No dense-field or clinical validation.',
        'refresh': 'python3 scripts/import_registration_figures.py then python3 scripts/build_site.py',
        'evidence': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in evidence}
    }
    (ROOT / 'site/registration-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    print(f'Reused {len(payload["ids"])} queries, four planes, two model attempts; {target.stat().st_size:,} bytes.')


if __name__ == '__main__':
    main()
