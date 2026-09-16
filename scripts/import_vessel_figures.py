#!/usr/bin/env python3
"""Import retained vessel/airway review figures; never rerun or alter an experiment.

This deliberate refresh needs local evidence. The normal site build uses only
the tracked payload and Python's standard library.
"""
import base64
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRAIN = 'runs/br033-brain-routing/viewer-brain/index.html'
FIGURES = {
    'brain': 'runs/br033-brain-routing/review/brain-calibration-summary.png',
    'airway': 'runs/br033-airway-routing/viewer-review-20260916/repair-and-unrepaired-controls.png',
}
EVIDENCE = [
    'docs/evidence/br025-curation.json',
    'docs/evidence/br026-results.json',
    'docs/evidence/br026-discrepancy-review.json',
    'docs/evidence/br030-results.json',
    'docs/evidence/br030-adjudication.json',
    'docs/evidence/br033-results.json',
    'docs/evidence/br033-scope-audit.json',
    'docs/evidence/br033-source-audit.json',
    'docs/evidence/br033-brain-resumption.json',
    'runs/br033-brain-routing/gap-calibration/metrics.json',
    'runs/br033-brain-routing/gap-calibration/cpr.npz',
    'runs/br033-brain-routing/calibration-validation.json',
    'probes/brain-routing/authoring/build_calibration_viewer.py',
    'probes/brain-routing/authoring/render_calibration.py',
    'probes/airway-routing/authoring/audit_scope.py',
]


def main():
    original, _ = json.JSONDecoder().raw_decode(
        (ROOT / BRAIN).read_text().split('const DATA=', 1)[1])
    case = original['cases'][0]
    brain = json.loads((ROOT / 'docs/evidence/br033-brain-resumption.json').read_text())
    scope = json.loads((ROOT / 'docs/evidence/br033-scope-audit.json').read_text())
    keys = ['arc', 'initial', 'cpr', 'cprBefore', 'cprAfter', 'cprChanges', 'sections']
    payload = {
        'figures': {key: 'data:image/png;base64,' + base64.b64encode(
            (ROOT / path).read_bytes()).decode() for key, path in FIGURES.items()},
        'brain': {**{key: case[key] for key in keys}, 'angles_deg': list(range(0, 360, 45)),
                  'offset_mm': [-5, 5], 'tile_height': 51,
                  'metrics': brain['calibration'], 'agent_trial': False},
        'airway': scope['cases'],
    }
    target = ROOT / 'site/vessel-figures.json'
    target.write_text(json.dumps(payload, separators=(',', ':')) + '\n')
    paths = [BRAIN, *FIGURES.values(), *EVIDENCE, 'site/vessel-figures.json']
    provenance = {
        'scope': 'BR-025 vessel curation, BR-026, BR-030 and BR-033 closeout. No new trial.',
        'sources': [
            {'name': 'TopCoW / TopBrain, Yang et al. and the challenge contributors',
             'urls': ['https://zenodo.org/records/15692630', 'https://zenodo.org/records/21972006',
                      'https://zenodo.org/records/21959166'],
             'terms': 'Attribution and source noncommercial restrictions retained; this local research report does not resolve commercial benchmark redistribution.'},
            {'name': 'AeroPath, Raidionics contributors',
             'urls': ['https://huggingface.co/datasets/andreped/AeroPath',
                      'https://doi.org/10.1371/journal.pone.0311416'],
             'terms': 'Downloaded license.md says CC BY 4.0; HF card says MIT. Both retained in source audit; attribution provided here.'},
            {'name': 'ImageCAS / ImageCAS-X, Xu et al. / ImageCAS-X contributors',
             'urls': ['https://www.kaggle.com/datasets/xiaoweixumedicalai/imagecas',
                      'https://zenodo.org/records/21887809'],
             'terms': 'Source listings declare Apache 2.0 for ImageCAS and CC BY 4.0 for ImageCAS-X. This chapter uses numerical results, no coronary image payload.'},
        ],
        'figure_method': 'Exact PNG reuse from retained author review panels. Brain CPR and cross-section atlases copied byte-for-byte from the final version-3 viewer. Gray values derive from real MRA signal; mask overlays are separate. No generated anatomy, smoothing or new resampling in the import.',
        'display': 'Eight CPR angles, 51 offsets spanning -5 to +5 mm. Columns are ordered saved route samples, with arc_mm used for cursor distance. Cross-section is 51 by 51 pixels perpendicular to the route. CPR height is enlarged for readability; it is not a uniform physical-scale display.',
        'limits': 'Brain repair is an author geometry baseline, not a coding-agent result. One of two additions is reference background. Airway A02/A03 preserve detached fragments and remain disconnected from the parent. Portable figures are inspection aids, not native scan viewers or clinical validation.',
        'refresh': 'python3 scripts/import_vessel_figures.py then python3 scripts/build_site.py',
        'evidence': {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in paths},
    }
    (ROOT / 'site/vessel-provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    print(f'Imported two evidence panels, eight CPR angles and route cross-sections: {target.stat().st_size:,} bytes.')


if __name__ == '__main__':
    main()
