"""Retain a concise, reproducible audit of the local FeEcho4D source sample."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'runs/br025-cardiac/source'
NATIVE = SOURCE / 'native/Patient001'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_mesh(path):
    lines = path.read_text().splitlines()
    v = np.array([[float(x) for x in l.split()[1:4]] for l in lines if l.startswith('v ')])
    f = np.array([[int(x.split('/')[0]) - 1 for x in l.split()[1:4]] for l in lines if l.startswith('f ')])
    return v, f


def main():
    manifest = json.loads((SOURCE / 'native/extraction-manifest.json').read_text())
    for entry in manifest['members']:
        relative = Path(entry['name']).relative_to('FeEcho4D/FeEcho4D_Annotated/Patient001')
        assert sha(NATIVE / relative) == entry['sha256']
    v, faces = read_mesh(NATIVE / 'mesh/Patient001_time001.obj')
    all_faces = [read_mesh(p)[1] for p in sorted((NATIVE / 'mesh').glob('*.obj'))]
    edges = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    mirror_dice = []
    for t in range(1, 31):
        a = np.asarray(Image.open(NATIVE / f'mask/Patient001_slice001time{t:03d}.png'))[:, ::-1] == 127
        b = np.asarray(Image.open(NATIVE / f'mask/Patient001_slice037time{t:03d}.png')) == 127
        mirror_dice.append(float(2 * np.sum(a & b) / (np.sum(a) + np.sum(b))))
    straus = {}
    for kind in ['image', 'mesh']:
        p = SOURCE / f'straus-p1-{kind}-items.json'
        items = json.loads(p.read_text())
        straus[kind] = {'item_count': len(items), 'first_items':
                       [{k: x[k] for k in ['_id', 'name', 'size']} for x in items[:3]],
                       'metadata_sha256': sha(p), 'data_downloaded': False}
    audit = {
        'round': 'BR-025', 'checked_on': '2026-09-16',
        'source_url': 'https://zenodo.org/records/21322299',
        'source_archive_size_bytes': manifest['archive_size'],
        'full_archive_md5_verified': False,
        'prefix_sha256': manifest['prefix_sha256'], 'partial_index_sha256': manifest['index_sha256'],
        'extracted_members': len(manifest['members']), 'member_crcs_checked_on_extraction': True,
        'member_sha256_rechecked': True,
        'native_counts': {'image_png': 1110, 'mask_png': 1110, 'mesh_obj': 30, 'config': 1},
        'source_config': (NATIVE / 'Patient001_info.cfg').read_text(),
        'phase_indexing': 'Pilot treats ED_time=2 and ES_time=17 as one-based filename frames. Config does not explicitly declare index base; this is unresolved and must not be used as an exact expert frame-selection gate.',
        'image_shape_hw': [464, 485], 'labels': {'background': 0, 'lv_cavity': 127, 'myocardium': 255},
        'radial_angles_status': 'Assumed 0..180 degrees inclusive at 5 degree increments from source convention; no per-plane transform file audited',
        'duplicate_direction_mirror_dice': {'mean': float(np.mean(mirror_dice)), 'min': float(min(mirror_dice)), 'max': float(max(mirror_dice))},
        'native_mesh': {'vertices': len(v), 'faces': len(faces),
                        'fixed_face_connectivity': all(np.array_equal(f, faces) for f in all_faces),
                        'boundary_edges': int(sum(counts == 1)), 'nonmanifold_edges': int(sum(counts > 2)),
                        'coordinate_min': v.min(0).tolist(), 'coordinate_max': v.max(0).tolist(),
                        'physical_transform_audited': False,
                        'cavity_surface_partition_audited': False,
                        'whole_mesh_volume_is_ef_oracle': False,
                        'cross_section_inspection': 'At x=-0.5,-0.2,0.0,0.2, two closed section loops were observed, consistent with a myocardial shell; not a single capped blood-pool surface'},
        'github_example_rejected_for_voxel_volume': {'case': 'FeEcho4D_017', 'shape': [256,256,256],
            'labels': [0,100,200], 'affine': 'identity', 'reason': 'Sparse radial slice embedding; unobserved zeros are not background annotations'},
        'straus_patient01_us_inventory': straus,
        'access_and_reuse': {'public_native_sample_downloaded': True,
            'publication_or_redistribution_performed': False,
            'feecho_project_terms': 'Non-commercial research stated; exact redistribution license unresolved',
            'gated_mitea_mvseg_echonet_mimic_access_requested': False},
        'pilot_results_sha256': sha(ROOT / 'runs/br025-cardiac/pilot-v1/results.json'),
        'raw_manifest': 'runs/br025-cardiac/source/native/extraction-manifest.json',
    }
    output = ROOT / 'docs/evidence/br025-source-audit.json'
    output.write_text(json.dumps(audit, indent=2) + '\n')
    print(json.dumps({'verified_members': len(manifest['members']), 'audit': str(output),
                      'straus_inventory': straus}))


if __name__ == '__main__':
    main()
