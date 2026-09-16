"""Independent mesh/image inspection without reference labels."""
import hashlib,json,shutil
from pathlib import Path
import numpy as np
import cv2
from PIL import Image,ImageDraw
from score import score,volumes

ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;B=ROOT/'runs/br032-real-echo'

def sections(points,faces,plane):
    o,u,v=[np.asarray(plane[k]) for k in ['origin','u','v']];n=np.cross(u,v)
    tri=points[faces];d=np.einsum('fvi,i->fv',tri-o,n);cut=(d.min(1)<0)&(d.max(1)>0)
    tri=tri[cut];d=d[cut];out=np.zeros((len(tri),2,3));counts=np.zeros(len(tri),int)
    for a,b in [(0,1),(1,2),(2,0)]:
        hit=(d[:,a]<0)!=(d[:,b]<0);ids=np.flatnonzero(hit);t=d[ids,a]/(d[ids,a]-d[ids,b])
        q=tri[ids,a]+t[:,None]*(tri[ids,b]-tri[ids,a]);out[ids,counts[ids]]=q;counts[ids]+=1
    out=out[counts==2]-o
    return np.stack([np.einsum('svi,i->sv',out,u),np.einsum('svi,i->sv',out,v)],axis=-1)/.75+127.5

def mask_from_segments(seg):
    mask=np.zeros((256,256),np.uint8)
    if not len(seg):return mask
    x0,y0=seg[:,0].T;x1,y1=seg[:,1].T
    for y in range(256):
        valid=(y0>y)!=(y1>y)
        xs=np.sort(x0[valid]+(y-y0[valid])*(x1[valid]-x0[valid])/(y1[valid]-y0[valid]))
        for a,b in zip(xs[::2],xs[1::2]):
            lo=max(0,int(np.ceil(a)));hi=min(256,int(np.ceil(b)))
            if hi>lo:mask[y,lo:hi]=1
    return mask

def image_proxies(img,mask):
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7));inner=(mask>0)&(cv2.erode(mask,kernel)==0)
    outer=(cv2.dilate(mask,kernel)>0)&(mask==0);valid=img>0;inner&=valid;outer&=valid
    if inner.sum()<20 or outer.sum()<20:return None
    return dict(outer_minus_inner=float(img[outer].mean()-img[inner].mean()),inside_mean=float(img[(mask>0)&valid].mean()),
                mask_area_px=int(mask.sum()),boundary_support_fraction=float(inner.sum()/max(1,((mask>0)&(cv2.erode(mask,kernel)==0)).sum())))

def main():
    paths=list((ROOT/'runs/br032-real-echo-sol-xhigh-v1-20260916').glob('*/result.json'));assert len(paths)==1
    folder=paths[0].parent;answer=folder/'artifacts/app/answer';graded=score(answer)
    assert graded['reward']==1,graded
    z=dict(np.load(answer/'prediction.npz'));spec=json.loads((B/'private-review.json').read_text());imgs=np.load(B/'private-review.npz')['images']
    out=B/'review';out.mkdir(exist_ok=True);(out/'images').mkdir(exist_ok=True)
    allpoints=[z['points'],*z['alternative_points']];names=['Agent reconstruction']+[f'Alternative {i+1}' for i in range(len(allpoints)-1)]
    models=[]
    for i,p in enumerate(allpoints):
        curves=[];proxies=[]
        for j,plane in enumerate(spec['planes']):
            seq=[];pr=[]
            for t,frame in enumerate(p):
                seg=sections(frame,z['faces'],plane);seq.append(np.round(seg,3).tolist())
                pr.append(image_proxies(imgs[j,t],mask_from_segments(seg)))
            curves.append(seq);proxies.append(pr)
        models.append(dict(name=names[i],points=np.round(p,4).tolist(),volumes=volumes(p,z['faces']).tolist(),sections=curves,image_proxies=proxies))
    for j,seq in enumerate(imgs):
        for t,img in enumerate(seq):Image.fromarray(img).save(out/'images'/f'p{j}_f{t}.png')
    static=[]
    for j,plane in enumerate(spec['planes']):
        m=mask_from_segments(sections(z['points'][0],z['faces'],plane));static.append([image_proxies(img,m) for img in imgs[j]])
    summary=json.loads((answer/'summary.json').read_text())
    receipt=dict(round='BR-032',source=json.loads((B/'source/source-receipt.json').read_text()),contract=graded,
                 summary=summary,observed=spec['observed'],withheld=spec['withheld'],
                 image_proxies={m['name']:m['image_proxies'] for m in models},static_initial_mesh_proxies=static,
                 image_proxy_limit='outer-minus-inner intensity is a brightness proxy, not segmentation or anatomy accuracy',
                 known_unavailable=['reference 3D geometry','material correspondence','strain truth','clinical EF','flow','diagnosis'])
    (B/'review-metrics.json').write_text(json.dumps(receipt,indent=2)+'\n')
    data=dict(models=models,faces=z['faces'].tolist(),planes=spec['planes'],observed=spec['observed'],withheld=spec['withheld'],summary=summary,contract=graded,dt=.16115)
    (out/'data.json').write_text(json.dumps(data,separators=(',',':')))
    for fn in ['solve.py','method.md','summary.json']:shutil.copy2(answer/fn,out/fn)
    shutil.copy2(HERE/'viewer.html',out/'index.html')
    # Static inspection sheet is independent of the solver's optional overlays.
    for name,times in [('agent-overlay-contact',[0,5,10,17]),('agent-extrema-contact',[1,3,9,13])]:
        sheet=Image.new('RGB',(4*256,8*282));draw=ImageDraw.Draw(sheet)
        for j,p in enumerate(spec['planes']):
            for col,t in enumerate(times):
                img=Image.fromarray(imgs[j,t]).convert('RGB');d=ImageDraw.Draw(img)
                for seg in models[0]['sections'][j][t]:d.line(tuple(map(tuple,seg)),fill=(61,233,214),width=2)
                sheet.paste(img,(col*256,j*282));draw.text((col*256+5,j*282+259),f'{"Observed" if j in spec["observed"] else "WITHHELD"} {p["name"]} / F{t+1}',fill='white')
        sheet.save(B/f'{name}.png')
    print(out)

if __name__=='__main__':main()
