"""Original BR-004 local-defect cohort. Truth is constructed before DICOM encoding."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import nibabel as nib
from PIL import Image,ImageDraw
from imaging import write_ct,write_seg,archive

CASES=[
 ('case-74','s0965','clean','limited coverage'),
 ('case-19','s1127','clean','marked thoracic abnormality'),
 ('case-83','s0629','kidney_cap','marked thoracic abnormality'),
 ('case-46','s0885','clean','source pathology'),
 ('case-28','s1233','rib_patch','ordinary anatomy'),
 ('case-61','s0915','heart_cap','ordinary anatomy'),
 ('case-95','s0344','clean','source pathology'),
 ('case-32','s1336','kidney_spill','ordinary anatomy'),
]
FOCUS=['kidney_left','kidney_right','liver','spleen','heart','rib_right_7','rib_right_8','rib_left_7','rib_left_8','vertebrae_L1','vertebrae_L2']


def shifted(mask,axis,offset):
    out=np.zeros_like(mask)
    a=[slice(None)]*3;b=a.copy()
    if offset>0:a[axis]=slice(offset,None);b[axis]=slice(None,-offset)
    else:a[axis]=slice(None,offset);b[axis]=slice(-offset,None)
    out[tuple(a)]=mask[tuple(b)]
    return out

def dilate(mask):
    out=mask.copy()
    for axis in range(3):
        for direction in [-1,1]:out|=shifted(mask,axis,direction)
    return out

def pole_cap(mask,fraction,direction=1):
    coords=np.argwhere(mask)
    # Tilted curved cap avoids an all-slice dropout or rectangular editing scar.
    scale=np.ptp(coords,axis=0).astype(float)
    center=coords.mean(axis=0)
    xyz=(coords-center)/np.maximum(scale,1)
    rank=direction*xyz[:,2] + .19*xyz[:,0] - .11*xyz[:,1] - .18*(xyz[:,0]**2+xyz[:,1]**2)
    chosen=coords[np.argsort(rank)[-max(1,round(len(coords)*fraction)):]]
    out=np.zeros_like(mask);out[tuple(chosen.T)]=True
    return out

def edit(labels,names,kind):
    changed=labels.copy();info={}
    if kind=='kidney_cap' or kind=='heart_cap':
        target='kidney_left' if kind=='kidney_cap' else 'heart'
        region=pole_cap(labels==names[target],.04,1 if kind=='kidney_cap' else -1)
        changed[region]=0
        info={'family':'focal_omission','target':target,'fraction':.04}
    elif kind=='rib_patch':
        a,b=names['rib_right_7'],names['rib_right_8']
        union=(labels==a)|(labels==b);coords=np.argwhere(union)
        ylo,yhi=np.quantile(coords[:,1],[.43,.57])
        y=np.indices(labels.shape,sparse=True)[1]
        region=union&(y>=ylo)&(y<=yhi)
        changed[region&(labels==a)]=b;changed[region&(labels==b)]=a
        info={'family':'local_identity_exchange','labels':['rib_right_7','rib_right_8'],'source_y_quantiles':[.43,.57]}
    elif kind=='kidney_spill':
        kidney=labels==names['kidney_left'];muscle=labels==names['iliopsoas_left']
        expanded=kidney.copy();distance=0
        while not np.any(expanded&muscle):
            expanded=dilate(expanded);distance+=1
            if distance>15:raise ValueError('kidney/psoas too far apart for this contrast')
        contact=np.argwhere(expanded&muscle)
        kidney_center=np.argwhere(kidney).mean(axis=0)
        center=contact[np.argmin(np.sum((contact-kidney_center)**2,axis=1))]
        grid=np.indices(labels.shape,sparse=True)
        sphere=sum((grid[i]-center[i])**2 for i in range(3))<=3.0**2
        region=sphere&((labels==0)|muscle)&dilate(expanded)
        changed[region]=names['kidney_left']
        info={'family':'connected_local_leakage','labels':['kidney_left','iliopsoas_left'],'radius_mm':9.,'contact_index':center.tolist(),'contact_dilation_steps':distance}
    return changed,info


def review_tile(ct,base,changed,label_id,point):
    # CT plus original and edited masks at the SAME world location in all planes.
    canvas=Image.new('RGB',(1080,800),'#111');d=ImageDraw.Draw(canvas)
    x,y,z=[int(v) for v in point]
    for row,axis in enumerate([2,1,0]):
        sl=[slice(None)]*3;sl[axis]=[x,y,z][axis];sl=tuple(sl)
        gray=np.clip((ct[sl].astype(float)+180)/600*255,0,255).astype('uint8')
        for col,arr in enumerate([None,base,changed]):
            rgb=np.repeat(gray[...,None],3,axis=2)
            if arr is not None:
                mask=arr[sl]==label_id
                rgb[mask]=(rgb[mask]*.45+np.array([20,230,190])*.55).astype('uint8')
            im=Image.fromarray(np.flipud(rgb.transpose(1,0,2)))
            im.thumbnail((350,235));im=im.resize((int(im.width*min(350/im.width,235/im.height)),int(im.height*min(350/im.width,235/im.height))),Image.Resampling.NEAREST);canvas.paste(im,(col*360,row*260+25))
            d.text((col*360+8,row*260+5),f'{["CT","source mask","submitted mask"][col]} axis={axis} slice={[x,y,z][axis]}',fill='white')
    return canvas


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--scratch',type=Path,required=True);p.add_argument('--taxonomy',type=Path,required=True);p.add_argument('--cases',nargs='*');a=p.parse_args()
    probe=Path(__file__).resolve().parents[1]
    a.scratch.mkdir(parents=True,exist_ok=True);data=a.scratch/'data';data.mkdir(exist_ok=True)
    taxonomy=json.loads(a.taxonomy.read_text());names={v:int(k) for k,v in taxonomy.items()}
    manifest=[];truth=[];receipts=[];regions={};answers=[]
    for case_id,subject,kind,stratum in CASES:
        if a.cases and case_id not in a.cases:continue
        path=a.source/subject
        img=nib.load(path/'ct.nii.gz')
        ct=np.asarray(img.dataobj)[::2,::2,::2].astype(np.int16)
        affine=img.affine@np.diag([2,2,2,1]);affine=np.diag([-1,-1,1,1])@affine
        labels=np.zeros(ct.shape,dtype=np.uint8)
        for label,number in names.items():
            source=nib.load(path/'segmentations'/f'{label}.nii.gz')
            if source.shape!=img.shape or not np.allclose(source.affine,img.affine):raise ValueError('source alignment mismatch')
            mask=np.asarray(source.dataobj)[::2,::2,::2]>0
            labels[mask]=number
        changed,mutation=edit(labels,names,kind)
        focus=[n for n in FOCUS if not (n=='spleen' and subject in ['s0629','s0885'])]
        out=data/case_id;out.mkdir(exist_ok=True)
        src=write_ct(out/'ct',ct,affine,'br004/'+case_id)
        encoded=write_seg(out/'seg.dcm',src,changed,names,'br004/'+case_id)
        findings=[];answer=[];change_stats={}
        for label in focus:
            original=labels==names[label];current=changed==names[label];difference=original^current
            if not difference.any():continue
            coords=np.argwhere(difference)
            xyz=sum(coords[:,i,None]*affine[:3,i] for i in range(3))+affine[:3,3]
            key=case_id+'__'+label;regions[key]=xyz.astype(np.float32)
            # An actual discrepancy voxel nearest its average, not an arbitrary centroid in empty space.
            witness=coords[np.argmin(np.sum((coords-coords.mean(axis=0))**2,axis=1))]
            point=sum(witness[i]*affine[:3,i] for i in range(3))+affine[:3,3]
            findings.append({'label':label,'region_key':key})
            answer.append({'label':label,'point_lps_mm':[round(float(v),4) for v in point]})
            change_stats[label]={'original_voxels':int(original.sum()),'submitted_voxels':int(current.sum()),'changed_voxels':len(coords),'dice':float(2*np.count_nonzero(original&current)/(original.sum()+current.sum())),'witness_index':witness.tolist()}
            (a.scratch/'review').mkdir(exist_ok=True)
            review_tile(ct,labels,changed,names[label],witness).save(a.scratch/'review'/f'{case_id}-{label}.png')
        manifest.append({'case_id':case_id,'directory':case_id,'focus_labels':focus})
        truth.append({'case_id':case_id,'focus_labels':focus,'stratum':stratum,'findings':findings})
        answers.append({'case_id':case_id,'findings':answer})
        receipts.append({'case_id':case_id,'subject':subject,'stratum':stratum,'mutation':mutation,'source_receipt':str(path/'source-receipt.json'),'derived_shape':ct.shape,'affine_lps':affine.tolist(),'focus_labels':focus,'changes':change_stats,'encoding':encoded})
        np.savez_compressed(a.scratch/(case_id+'-private.npz'),ct=ct,original=labels,submitted=changed,affine=affine)
        print(case_id,subject,kind,change_stats,flush=True)
    if a.cases:
        (a.scratch/'partial-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n');return
    (data/'cases.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (data/'label-list.json').write_text(json.dumps(taxonomy,indent=2)+'\n')
    (probe/'tests/expected.json').write_text(json.dumps({'cases':truth},indent=2)+'\n')
    np.savez_compressed(probe/'tests/regions.npz',**regions)
    (probe/'solution/findings.json').write_text(json.dumps({'cases':answers},indent=2)+'\n')
    (probe/'environment/findings.json').write_text(json.dumps({'cases':[{'case_id':x['case_id'],'findings':[]} for x in manifest]},indent=2)+'\n')
    (a.scratch/'build-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
    archive(data,probe/'environment/data.tar.gz')

if __name__=='__main__':main()
