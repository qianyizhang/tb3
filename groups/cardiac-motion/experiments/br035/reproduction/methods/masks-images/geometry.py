"""Independent rasterization, tetrahedral point location, and finite kinematics."""
import numpy as np
from scipy.spatial import cKDTree

def boundary(tet):
    f=np.concatenate([tet[:,v] for v in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]])
    _,i,n=np.unique(np.sort(f,axis=1),axis=0,return_index=True,return_counts=True)
    return f[i[n==1]]

def voxelize(points,tet,origin,spacing,shape):
    """Exact tetrahedron membership at voxel centers, including shared faces."""
    p=(np.asarray(points)-origin)/spacing;result=np.zeros(shape,bool);xyzshape=np.array(shape[::-1])
    for start in range(0,len(tet),1024):
        x=p[tet[start:start+1024]];low=np.maximum(np.ceil(x.min(1)-1e-8).astype(int),0);high=np.minimum(np.floor(x.max(1)+1e-8).astype(int),xyzshape-1)
        sizes=np.maximum(high-low+1,0);counts=sizes.prod(1);n=int(counts.sum())
        if not n:continue
        if n>20000000:raise ValueError('Pathological tetrahedral bounding boxes exceed rasterizer memory bound')
        owner=np.repeat(np.arange(len(x)),counts);idx=np.arange(n)-np.repeat(np.cumsum(counts)-counts,counts)
        sz=sizes[owner];xyz=low[owner]+np.stack([idx%sz[:,0],idx//sz[:,0]%sz[:,1],idx//(sz[:,0]*sz[:,1])],axis=1)
        edges=x[:,1:]-x[:,:1];det=np.linalg.det(edges);valid=abs(det)>1e-12
        inv=np.zeros_like(edges);inv[valid]=np.linalg.inv(edges[valid])
        b=np.einsum('ni,nij->nj',xyz-x[owner,0],inv[owner]);ok=valid[owner]&(b.min(1)>=-1e-7)&(b.sum(1)<=1+1e-7)
        q=xyz[ok];result[q[:,2],q[:,1],q[:,0]]=True
    return result

def cavity_mask(points,faces,origin,spacing,shape):
    """Odd-even parallel z-ray intersections through a closed triangle surface."""
    p=(points-origin)/spacing;events=[]
    for face in faces:
        x=p[face];lo=np.maximum(np.ceil(x[:,:2].min(0)).astype(int),0);hi=np.minimum(np.floor(x[:,:2].max(0)).astype(int),np.array(shape[:0:-1])-1)
        if np.any(hi<lo):continue
        edges=x[1:,:2]-x[0,:2]
        if abs(np.linalg.det(edges))<1e-10:continue
        yy,xx=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1];xy=np.stack([xx.ravel(),yy.ravel()],1)
        b=(xy-x[0,:2])@np.linalg.inv(edges);ok=(b.min(1)>=-1e-8)&(b.sum(1)<=1+1e-8);xy=xy[ok];b=b[ok]
        zz=x[0,2]+b@(x[1:,2]-x[0,2]);events.extend(zip((xy[:,1]*shape[2]+xy[:,0]).tolist(),zz.tolist()))
    buckets={}
    for col,z in events:buckets.setdefault(col,[]).append(z)
    mask=np.zeros(shape,bool);grid=np.arange(shape[0])
    for col,vals in buckets.items():
        vals=np.unique(np.round(vals,7));inside=np.searchsorted(vals,grid,side='right')%2==1
        mask[:,col//shape[2],col%shape[2]]=inside
    return mask

def locate(X,tet,queries):
    """Locate arbitrary probes; exact AABB fallback avoids nearest-centroid assumptions."""
    cells=X[tet];edges=cells[:,1:]-cells[:,:1];det=np.linalg.det(edges);good=abs(det)>1e-10
    inv=np.zeros_like(edges);inv[good]=np.linalg.inv(edges[good]);center=cells.mean(1);tree=cKDTree(center)
    ids=np.full(len(queries),-1,int);weights=np.zeros((len(queries),4));k=min(64,len(tet))
    for start in range(0,len(queries),256):
        q=queries[start:start+256];cand=tree.query(q,k=k)[1];cand=np.asarray(cand).reshape(len(q),k)
        b=np.einsum('nki,nkij->nkj',q[:,None]-cells[cand,0],inv[cand]);w=np.concatenate([1-b.sum(-1,keepdims=True),b],-1)
        hit=(w.min(-1)>=-1e-7)&good[cand];has=hit.any(1);j=hit.argmax(1);ii=np.where(has)[0]
        ids[start+ii]=cand[ii,j[ii]];weights[start+ii]=w[ii,j[ii]]
    low=cells.min(1)-1e-7;high=cells.max(1)+1e-7
    for i in np.where(ids<0)[0]:
        q=queries[i];cand=np.where(good&np.all((q>=low)&(q<=high),axis=1))[0]
        if not len(cand):continue
        b=np.einsum('ni,nij->nj',q-cells[cand,0],inv[cand]);w=np.c_[1-b.sum(1),b];hit=np.where(w.min(1)>=-1e-7)[0]
        if len(hit):j=hit[0];ids[i]=cand[j];weights[i]=w[j]
    return ids,weights

def fields(X,points,tet):
    e0=X[tet[:,1:]]-X[tet[:,:1]];et=points[:,tet[:,1:]]-points[:,tet[:,:1]]
    F=np.linalg.solve(e0[None],et).swapaxes(-1,-2)
    E=(np.einsum('tmki,tmkj->tmij',F,F)-np.eye(3))/2
    J=np.linalg.det(et)/np.linalg.det(e0)[None]
    return F,E,J
