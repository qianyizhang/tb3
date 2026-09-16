#!/usr/bin/env python3
"""Import completed cardiac results for presentation; never run or rescore a trial.

The PNG remains an exact copy of the retained scientific figure. Curves and
metrics retain their full JSON precision. Normal site builds use these tracked
outputs and do not need the local runs directory or scientific dependencies.
"""
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = 'docs/evidence/br035-segmentation-mechanics-results.json'
FIGURE = 'runs/br035-segmentation-mechanics/review/function-comparison.png'


def main():
    source = json.loads((ROOT / EVIDENCE).read_text())
    conditions = {}
    for trial in source['trials']:
        if trial['phase'] != 'sol-xhigh':
            continue
        key = trial['condition']
        grade = trial['grade']
        conditions[key] = {
            'geometry': grade['geometry'],
            'material': grade['material'],
            'construction_gates': grade['construction_gates'],
            'limits': grade['limits'],
            'clinical': source['replays'][key]['grade'],
            'mesh_quality': source['posthoc_mesh_quality'][key],
        }
    figure = (ROOT / FIGURE).read_bytes()
    payload = {'conditions': conditions,
               'figure': 'data:image/png;base64,' + base64.b64encode(figure).decode()}
    output = ROOT / 'site/cardiac-figures.json'
    output.write_text(json.dumps(payload, separators=(',', ':')) + '\n')
    records = [EVIDENCE, FIGURE, 'site/cardiac-figures.json',
               'docs/research-rounds/BR-035-results.md',
               'docs/research-rounds/BR-035-segmentation-mechanics.md',
               'docs/research-rounds/BR-031-cardiac-agent-results.md',
               'docs/research-rounds/BR-032-real-echo-results.md',
               'docs/research-rounds/BR-034-results.md']
    provenance = {
        'scope': 'Completed BR-025/027/029/031/032/034/035 cardiac series. Presentation closeout, no new experiments.',
        'sources': [
            {'name': 'Multimodality STRAUS',
             'url': 'https://humanheart-project.creatis.insa-lyon.fr/multimodalityStraus.html',
             'role': 'Synthetic ultrasound and known electromechanical reference motion. Not measured human strain.'},
            {'name': 'EchoXFlow', 'url': 'https://huggingface.co/datasets/Ahus-AIM/EchoXFlow',
             'role': 'Clinical LV cavity surfaces and ultrasound. Source surfaces have annotation/model uncertainty; no material-strain truth.'},
        ],
        'figure_method': 'Exact retained author-generated BR-035 scientific PNG; no image editing or anatomical image synthesis. Interactive regional curves are copied exactly from the independently scored material records.',
        'curve_definition': 'Volume-weighted regional engineering strain on source anatomical axes, over covered reference tissue. These are distinct from minimum principal Green-Lagrange E colors in the local 3D viewer and are not clinical GLS.',
        'limits': 'Aggregate measurements and an authored scientific plot only. No source ultrasound, native arrays, patient identifiers, model weights, raw sessions or full meshes are embedded. Dataset redistribution terms are not broadened by this report. Public training exposure remains unknown.',
        'refresh': 'python3 scripts/import_cardiac_figures.py; python3 scripts/build_site.py',
        'evidence': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in records},
    }
    (ROOT / 'site/cardiac-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    print(f'Imported completed results and exact figure: {output.stat().st_size:,} bytes.')


if __name__ == '__main__':
    main()
