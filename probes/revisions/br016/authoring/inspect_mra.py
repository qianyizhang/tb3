"""Native-grid MRA slice / maximum-intensity projection viewer (NumPy, Pillow)."""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

def load(root,raw=False):
    z=np.load(Path(root)/('original.npz' if raw else 'brain.npz'))
    return z['volume'],z['affine']

def panel(a,spacing,axis,index=None,bounds=None,high=None,size=640):
    # Array indices increase R,A,S. Image horizontal increases first remaining axis;
    # vertical increases towards top. Labels state these conventions explicitly.
    bounds=bounds or [0,a.shape[0],0,a.shape[1],0,a.shape[2]]
    sl=[slice(bounds[2*d],bounds[2*d+1]) for d in range(3)]
    if index is None:v=a[tuple(sl)].max(axis=axis)
    else:sl[axis]=int(index);v=a[tuple(sl)]
    rem=[d for d in range(3) if d!=axis]
    b=np.clip(v.T[::-1]/high*255,0,255).astype('uint8')
    physical=[v.shape[d]*spacing[rem[d]] for d in range(2)]
    wh=[max(1,round(size*f/max(physical))) for f in physical]
    im=Image.fromarray(b).resize(tuple(wh),Image.Resampling.NEAREST)
    out=Image.new('RGB',(size+90,size+75),'#10151e');left=65;top=35
    out.paste(im,(left,top));draw=ImageDraw.Draw(out)
    axes='ijk';directions='RAS';tag='MIP' if index is None else f'{axes[axis]}={index}'
    draw.text((10,8),f'{tag} | horizontal +{axes[rem[0]]} ({directions[rem[0]]}), vertical up +{axes[rem[1]]} ({directions[rem[1]]})',fill='white')
    for t in np.linspace(0,1,5):
        x=left+t*wh[0];y=top+(1-t)*wh[1]
        valx=bounds[2*rem[0]]+t*(v.shape[0]-1);valy=bounds[2*rem[1]]+t*(v.shape[1]-1)
        draw.text((int(x)-10,top+wh[1]+5),str(round(valx)),fill='white')
        draw.text((8,int(y)),str(round(valy)),fill='white')
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--data',default='/app/data');ap.add_argument('--raw',action='store_true');ap.add_argument('--axis',choices=['i','j','k'],default='k');ap.add_argument('--slices',type=int,nargs='+');ap.add_argument('--bounds',type=int,nargs=6,metavar=('I0','I1','J0','J1','K0','K1'));ap.add_argument('--high',type=float);ap.add_argument('--out',required=True);ap.add_argument('--size',type=int,default=640)
    args=ap.parse_args();a,aff=load(args.data,args.raw);spacing=np.linalg.norm(aff[:3,:3],axis=0);axis='ijk'.index(args.axis)
    bounds=args.bounds or [0,a.shape[0],0,a.shape[1],0,a.shape[2]]
    assert all(0<=bounds[2*d]<bounds[2*d+1]<=a.shape[d] for d in range(3))
    high=args.high or float(np.percentile(a[a>0],99.5));assert high>0
    indexes=args.slices or [None]
    assert all(x is None or 0<=x<a.shape[axis] for x in indexes)
    ims=[panel(a,spacing,axis,x,bounds,high,args.size) for x in indexes];cols=min(3,len(ims));rows=(len(ims)+cols-1)//cols
    out=Image.new('RGB',(ims[0].width*cols,ims[0].height*rows),'#10151e')
    for n,im in enumerate(ims):out.paste(im,((n%cols)*im.width,(n//cols)*im.height))
    Path(args.out).parent.mkdir(parents=True,exist_ok=True);out.save(args.out)
    print(json.dumps({'shape':list(a.shape),'axis':args.axis,'slices':indexes,'bounds_exclusive':bounds,'window':[0,high],'output':args.out}))
if __name__=='__main__':main()
