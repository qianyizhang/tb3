"""Build the source-linked MRA calibration viewer from actual saved arrays."""
from pathlib import Path
import importlib.util, json, sys
import nibabel as nib
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'runs/br033-brain-routing'
G = BASE / 'gap-calibration'
sys.path.insert(0, str(ROOT/'probes/vessel-geometry/authoring'))
from geometry import transform, frames, section_coordinates, sample, mesh_from_mask
spec=importlib.util.spec_from_file_location('atlas_helpers',ROOT/'probes/airway-routing/authoring/build_viewer.py')
helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)


def main():
    ni=nib.load(G/'image.nii.gz');im=np.asarray(ni.dataobj)
    before=np.isin(np.asarray(nib.load(G/'original_labels.nii.gz').dataobj),[1,25])
    after=np.isin(np.asarray(nib.load(G/'corrected_crop_labels.nii.gz').dataobj),[1,25])
    added=after&~before;line=np.load(G/'centerline.npy');cpr=np.load(G/'cpr.npz')
    assert cpr['intensity'].shape == (8,len(line),51)
    metrics=json.loads((G/'metrics.json').read_text())
    anchors=line[[0,-1]]
    _,normal,binormal=frames(line)
    section_xyz=section_coordinates(line,normal,binormal,cpr['offsets_mm'])
    # A square cross-section reaches sqrt(2)*5 mm from the line; sample from
    # the full native MRA so corners are never filled with CT-style padding.
    full=nib.load(BASE/'sources/TopBrain_Data_Release_Batches1n2nTA36_081726/imagesTr_topbrain/topcow_mr_004_0000.nii.gz')
    coords=transform(section_xyz,np.linalg.inv(full.affine))
    assert np.all(coords>=0) and np.all(coords<=np.array(full.shape)-1)
    section=sample(np.asarray(full.dataobj),full.affine,section_xyz,1,0)
    top=float(np.percentile(im,99.8))
    def gray(a): return np.clip(a/top*255,0,255).astype('uint8')
    overlay=helpers.overlay;atlas=helpers.atlas;png=helpers.png
    changes=overlay(before,[125,153,171]);changes[added]=[255,85,171,235]
    center=transform(np.argwhere(added).mean(0),ni.affine)
    initial=int(np.linalg.norm(line-center,axis=1).argmin())
    note='Two voxels connect the basilar parent to the distal right SCA. One addition matches the reference label; one is reference background. Route-to-reference error: 0.30 mm at the 95th percentile. This is an easy geometry calibration, not an admitted hard benchmark.'
    record={'id':'B01','title':'MRA 004 · basilar → right SCA','shape':list(im.shape),
        'spacing':ni.header.get_zooms()[:3],'path':line.tolist(),'pathIJK':transform(line,np.linalg.inv(ni.affine)).tolist(),
        'arc':cpr['arc_mm'].tolist(),'initial':initial,'added':int(added.sum()),'removed':0,
        'anchors':anchors.tolist(),'note':note,'repairCase':True,
        'connectivityBefore':helpers.connectivity(before,ni.affine,anchors),
        'connectivityAfter':helpers.connectivity(after,ni.affine,anchors),
        'source':[atlas(gray(im),k) for k in range(3)],
        'before':[atlas(overlay(before,[255,176,70]),k) for k in range(3)],
        'after':[atlas(overlay(after,[51,217,180]),k) for k in range(3)],
        'changes':[atlas(changes,k) for k in range(3)],
        'cpr':png(gray(cpr['intensity'].transpose(0,2,1)).reshape(8*51,len(line))),
        'cprBefore':png(overlay(sample(before,ni.affine,cpr['source_ras_mm'],0,0).transpose(0,2,1)>0,[255,176,70]).reshape(8*51,len(line),4)),
        'cprAfter':png(overlay(sample(after,ni.affine,cpr['source_ras_mm'],0,0).transpose(0,2,1)>0,[51,217,180]).reshape(8*51,len(line),4)),
        'cprChanges':png(np.stack([sample(changes[...,k],ni.affine,cpr['source_ras_mm'],0,0).transpose(0,2,1) for k in range(4)],-1).astype('uint8').reshape(8*51,len(line),4)),
        'sections':png(gray(section).reshape(-1,51)),
        'meshBefore':helpers.surface(mesh_from_mask(before,ni.affine),np.zeros_like(added),ni.affine),
        'meshAfter':helpers.surface(mesh_from_mask(after,ni.affine),added,ni.affine),
        'downloads':'../gap-calibration/'}
    payload=json.dumps({'label':'Geometry-only calibration · no agent trial','cases':[record]},default=lambda x:np.asarray(x).tolist(),separators=(',',':'))
    html=Path(__file__).with_name('brain_viewer.html').read_text().replace('__DATA__',payload)
    out=BASE/'viewer-brain';out.mkdir(exist_ok=True)
    (out/'index.html').write_text(html)
    Image.fromarray(gray(cpr['intensity'][0].T)).resize((1200,300)).save(out/'cpr-preview.png')
    print(json.dumps({'viewer':str(out/'index.html'),'bytes':len(html),'initial_route_mm':float(cpr['arc_mm'][initial]),'window_max_signal':top}))


if __name__=='__main__':main()
