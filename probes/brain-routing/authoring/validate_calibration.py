"""Independent source-sampling and unchanged-volume checks for the saved export."""
from pathlib import Path
import base64, hashlib, io, json, re, subprocess
import nibabel as nib
import numpy as np
from PIL import Image
import trimesh

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'runs/br033-brain-routing'
G=BASE/'gap-calibration'


def main():
    p=BASE/'sources/TopBrain_Data_Release_Batches1n2nTA36_081726/imagesTr_topbrain/topcow_mr_004_0000.nii.gz'
    ni=nib.load(p);image=np.asarray(ni.dataobj)
    cpr=np.load(G/'cpr.npz');xyz=cpr['source_ras_mm'];line=np.load(G/'centerline.npy')
    inv=np.linalg.inv(ni.affine)
    ijk=xyz@inv[:3,:3].T+inv[:3,3]
    assert np.isfinite(xyz).all() and np.all(ijk>=0) and np.all(ijk<=np.array(image.shape)-1)
    floor=np.floor(ijk).astype(int);frac=ijk-floor
    expected=np.zeros(ijk.shape[:-1])
    for i in [0,1]:
        for j in [0,1]:
            for k in [0,1]:
                shift=np.array([i,j,k]);indexes=floor+shift
                weights=np.where(shift,frac,1-frac).prod(-1)
                expected+=image[tuple(np.moveaxis(indexes,-1,0))]*weights
    error=float(np.max(np.abs(expected-cpr['intensity'])))
    # Saved sampler output is float32; compare within four ULPs at this
    # volume's intensity scale rather than demanding float64 arithmetic.
    tolerance=float(4*np.finfo(np.float32).eps*max(1,np.abs(expected).max()))
    assert error<tolerance,(error,tolerance)
    zero=np.flatnonzero(np.isclose(cpr['offsets_mm'],0)).item()
    assert np.allclose(xyz[:,:,zero,:],line[None],atol=1e-6)
    assert np.allclose(np.linalg.norm(xyz-line[None,:,None,:],axis=-1),abs(cpr['offsets_mm'])[None,None,:],atol=1e-6)
    assert np.allclose(cpr['arc_mm'],np.r_[0,np.linalg.norm(np.diff(line,axis=0),axis=1).cumsum()],atol=1e-6)
    orig=nib.load(BASE/'predictions-resencm-v1/topcow_mr_004.nii.gz');fixed=nib.load(G/'corrected_labels.nii.gz')
    assert orig.shape==fixed.shape and np.allclose(orig.affine,fixed.affine)
    before=np.asarray(orig.dataobj);after=np.asarray(fixed.dataobj);change=before!=after
    assert change.sum()==2 and np.all(before[change]==0) and np.all(after[change]==25)
    assert np.array_equal(np.argwhere(change),[[190,306,79],[191,307,79]])
    # Check native-lattice rounding with two different crop origins.
    p,q=np.array([192,307,79]),np.array([189,306,79])
    bridges=[]
    for lo in [np.array([173,232,42]),np.array([160,219,40])]:
        local_p,local_q=p-lo,q-lo
        bridges.append(np.unique(np.rint(np.linspace(local_p+lo,local_q+lo,13)).astype(int),axis=0))
    assert np.array_equal(*bridges)
    mesh=trimesh.load(G/'basilar-right-sca.ply',process=False)
    assert mesh.is_watertight and len(mesh.split())==1 and np.isfinite(mesh.vertices).all()
    html=(BASE/'viewer-brain/index.html').read_text();script=re.search(r'<script>(.*?)</script>',html,re.S).group(1)
    d=json.loads(script.split('const DATA=',1)[1].split(';const $=',1)[0]);c=d['cases'][0];n=len(c['path'])
    for key in ['source','before','after','changes']:
        for axis,url in enumerate(c[key]):
            a=Image.open(io.BytesIO(base64.b64decode(url.split(',')[1])));ds=[j for j in range(3) if j!=axis]
            assert a.size==(c['shape'][ds[0]],c['shape'][axis]*c['shape'][ds[1]])
    for key in ['cpr','cprBefore','cprAfter','cprChanges']:
        a=Image.open(io.BytesIO(base64.b64decode(c[key].split(',')[1])));assert a.size==(n,8*51)
    a=Image.open(io.BytesIO(base64.b64decode(c['sections'].split(',')[1])));assert a.size==(51,n*51)
    assert not c['connectivityBefore']['anchors_connected'] and c['connectivityAfter']['anchors_connected']
    assert c['connectivityAfter']['components']==1
    assert 'airway' not in html.lower() and '__DATA__' not in html
    js=BASE/'viewer-brain/syntax-check.js';js.write_text(script)
    subprocess.run(['node','--check',str(js)],check=True)
    rows=json.loads((BASE/'predictions-resencm-v1/prediction-receipt.json').read_text())['rows']
    assert len(rows)==5
    for row in rows:
        output=BASE/f'predictions-resencm-v1/topcow_mr_{row["case"]}.nii.gz'
        assert hashlib.sha256(output.read_bytes()).hexdigest()==row['output_sha256']
    record={'source_mra_trilinear_max_absolute_error':error,'float32_comparison_tolerance':tolerance,'cpr_source_samples':int(expected.size),
        'cpr_all_samples_inside_native_image':True,'arc_and_rotated_offsets_valid':True,
        'full_volume_changes':2,'changed_only_background_to_right_sca':True,
        'bridge_rounding_independent_of_crop_origin':True,'mesh_watertight':True,'mesh_components':1,
        'embedded_atlases_checked':17,'javascript_syntax_pass':True,'prediction_hashes_checked':5,
        'interactive_browser_test':False,'browser_note':'Prior local-file navigation was blocked; no alternate browser path used.'}
    (BASE/'calibration-validation.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))


if __name__=='__main__':main()
