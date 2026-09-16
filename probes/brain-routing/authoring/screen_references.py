"""Reference-only inventory; does not admit a prediction error."""
from pathlib import Path
import json,nibabel as nib,numpy as np
from scipy import ndimage as ndi
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br033-brain-routing'
D=B/'sources/TopBrain_Data_Release_Batches1n2nTA36_081726'

if __name__=='__main__':
    rows=[]
    for p in sorted(D.glob('labelsTr_topbrain_v1_*/*.nii.gz')):
        ni=nib.load(p);a=np.asarray(ni.dataobj);vol=np.bincount(a.ravel(),minlength=43)
        names=json.loads((D/'labelmap_jsons'/f'labels_topbrain_v1_{p.stem.split("_")[1]}.json').read_text())['labels']
        row={'case':p.name.split('.')[0],'shape':ni.shape,'spacing_mm':list(map(float,ni.header.get_zooms()[:3])),
             'labels':{name:int(vol[v]) for name,v in names.items() if v and vol[v]},
             'affine':ni.affine.tolist()};rows.append(row)
        print(row['case'],{k:v for k,v in row['labels'].items() if k in ['3rd-A2','3rd-A3','R-AICA','L-AICA','R-PICA','L-PICA','R-AChA','L-AChA']},flush=True)
    (B/'reference-inventory.json').write_text(json.dumps(rows,indent=2)+'\n')
