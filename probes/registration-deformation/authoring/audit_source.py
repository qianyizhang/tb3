"""Verify actual phase data, annotation provenance and irreducible global fit."""
import hashlib
import json
from pathlib import Path
import numpy as np
import nibabel as nib
from scipy.ndimage import map_coordinates
from geometry import errors,rigid_fit,affine_fit

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br021-deformable'

def main():
    source=OUT/'source';receipt=json.loads((source/'source-receipt.json').read_text())
    for item in receipt['files']:
        assert hashlib.sha256((source/item['member']).read_bytes()).hexdigest()==item['sha256']
    rows=[]
    for case in [1,2,3]:
        images=[nib.load(source/f'LungCT/imagesTr/LungCT_{case:04d}_{phase:04d}.nii.gz') for phase in [0,1]]
        assert images[0].shape==images[1].shape==(192,192,208)
        assert np.array_equal(images[0].affine,images[1].affine)
        a=images[0].affine;arrays=[np.asarray(x.dataobj) for x in images]
        assert not np.array_equal(*arrays)
        ijk=[np.loadtxt(source/f'LungCT/landmarksTr/LungCT_{case:04d}_{phase:04d}.csv',delimiter=',') for phase in [0,1]]
        for phase,q in enumerate(ijk):
            assert np.all(q>=0) and np.all(q<=np.array(images[phase].shape)-1)
            # Archive and repository reference annotations must be byte-identical.
            name=f'LungCT_{case:04d}_{phase:04d}.csv'
            assert (source/'LungCT/landmarksTr'/name).read_bytes()==(source/'l2r-reference/evaluation/L2RTest/ground-truth/landmarksTr'/name).read_bytes()
        world=[np.einsum('ij,nj->ni',a[:3,:3],q)+a[:3,3] for q in ijk]
        records={'case':case,'landmarks':len(ijk[0]),'shape':list(images[0].shape),
                 'voxel_to_world':a.tolist(),'identity':errors(*world),
                 'best_rigid':errors(rigid_fit(*world),world[1]),
                 'best_affine':errors(affine_fit(*world),world[1]),
                 'landmark_intensities':[map_coordinates(img,q.T,order=1).tolist() for img,q in zip(arrays,ijk)],
                 'source_origin':'Manual validation landmarks in the actual LungCT release, identical to official evaluation repository.',
                 'preprocessing':'Provider affine prealignment/crop/resampling; not raw DICOM.'}
        rows.append(records)
    # First qualifying pair, before any public-input registration trial.
    selected=next(r['case'] for r in rows if r['best_rigid']['rms_mm']>3 and r['best_affine']['rms_mm']>3)
    (OUT/'author').mkdir(exist_ok=True)
    (OUT/'author/source-audit.json').write_text(json.dumps({'selected_case':selected,'cases':rows},indent=2)+'\n')
    print(json.dumps({'selected_case':selected,'cases':[{k:r[k] for k in ['case','landmarks']}|{k:r[k]['rms_mm'] for k in ['identity','best_rigid','best_affine']} for r in rows]},indent=2))

if __name__=='__main__':main()
