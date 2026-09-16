"""Fit a non-affine material body with image, smoothness and volume constraints.

This is a kinematic inverse problem, not an active-stress or circulation solver.
Only public videos, initial geometry and the frozen public affine fit are read.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
from scipy.sparse import coo_matrix, vstack, eye, diags
from scipy.sparse.linalg import cg

from mechanics import edge_matrices


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--affine',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--max-cg',type=int,default=300)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    start=time.perf_counter();cv2.setNumThreads(1)
    manifest=json.loads((a.input/'manifest.json').read_text())
    for fn,h in manifest.items(): assert hashlib.sha256((a.input/fn).read_bytes()).hexdigest()==h
    geo=json.loads((a.input/'geometry.json').read_text())
    init=dict(np.load(a.input/'initial_mesh.npz'));X=init['points'];cells=init['tetra'];N=len(X)
    rows=[];cols=[];values=[];obs=[];row=0
    for i,plane in enumerate(geo['planes']):
        u,v,origin=[np.array(plane[k]) for k in ['u','v','origin']]
        ids=np.where(abs(np.einsum('nj,j->n',X-origin,np.cross(u,v)))<1.5)[0]
        px0=np.stack([np.einsum('nj,j->n',X[ids]-origin,ax)/geo['spacing_mm']+geo['pixel_center'] for ax in [u,v]],axis=1)
        good=np.all((px0>5)&(px0<geo['image_size']-6),axis=1);ids,px0=ids[good],px0[good];px=px0.copy()
        old=np.asarray(Image.open(a.input/f'view_{i}/frame_01.png'));trajectory=[px.copy()]
        dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
        for t in range(1,30):
            new=np.asarray(Image.open(a.input/f'view_{i}/frame_{t+1:02d}.png'))
            flow=dis.calc(old,new,None)
            delta=np.stack([map_coordinates(flow[...,j],px[:,::-1].T,order=1,mode='nearest') for j in range(2)],axis=1)
            px+=delta;trajectory.append(px.copy());old=new
        trajectory=(np.array(trajectory)-px0)*geo['spacing_mm']
        for j,axis in enumerate([u,v]):
            for k in range(3):
                rows.extend(np.arange(row,row+len(ids)));cols.extend(3*ids+k);values.extend(np.repeat(axis[k],len(ids)))
            obs.append(trajectory[:,:,j]);row+=len(ids)
    O=coo_matrix((values,(rows,cols)),shape=(row,3*N)).tocsr()/0.75
    Y=np.concatenate(obs,axis=1)/0.75
    edges=np.unique(np.sort(np.concatenate([cells[:,ij] for ij in [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]]),axis=1),axis=0)
    lengths=np.linalg.norm(X[edges[:,1]]-X[edges[:,0]],axis=1)
    edgeweight=np.sqrt(row/(3*len(edges)))/(.30*lengths)
    er=np.repeat(np.arange(3*len(edges)),2)
    ec=np.stack([3*edges[:,0,None]+np.arange(3),3*edges[:,1,None]+np.arange(3)],axis=-1).ravel()
    ev=(np.repeat(edgeweight,3)[:,None]*np.array([-1,1])).ravel()
    S=coo_matrix((ev,(er,ec)),shape=(3*len(edges),3*N)).tocsr()
    D0=edge_matrices(X,cells);invD=np.linalg.inv(D0)
    gradients=np.concatenate([-invD.sum(axis=1)[:,None,:],invD],axis=1)
    # Rows of inv(D0) are gradients of the three non-origin shape functions.
    tetcolumns=(3*cells[:,:,None]+np.arange(3)).reshape(-1)
    tetrows=np.repeat(np.arange(len(cells)),12)
    volumeweight=np.sqrt(row/len(cells))/.15
    baseH=(O.T@O+S.T@S+eye(3*N,format='csr')*1e-7).tocsr()
    rhsdata=np.asarray(O.T@Y.T).T
    affine=np.load(a.affine)['points']
    predictions=[X.copy()];logs=[]
    for t in range(1,30):
        disp=(affine[t]-X).reshape(-1)
        frame=[]
        for iteration in range(3):
            F=np.einsum('nij,njk->nik',edge_matrices(X+disp.reshape(N,3),cells),invD)
            J=np.linalg.det(F)
            assert J.min()>.05
            cofactor=J[:,None,None]*np.swapaxes(np.linalg.inv(F),1,2)
            derivative=np.einsum('nij,nvj->nvi',cofactor,gradients)
            V=coo_matrix((derivative.ravel()*volumeweight,(tetrows,tetcolumns)),shape=(len(cells),3*N)).tocsr()
            target=V@disp+(1-J)*volumeweight
            H=(baseH+V.T@V).tocsr();rhs=rhsdata[t]+V.T@target
            M=diags(1/np.maximum(H.diagonal(),1e-12))
            candidate,info=cg(H,rhs,x0=disp,M=M,rtol=1e-5,atol=0,maxiter=a.max_cg)
            step=1.
            while step>1/128:
                trial=disp+step*(candidate-disp)
                FF=np.einsum('nij,njk->nik',edge_matrices(X+trial.reshape(N,3),cells),invD)
                if np.linalg.det(FF).min()>.05:break
                step/=2
            assert step>1/128,'Could not maintain a positive material map'
            disp=trial
            frame.append(dict(cg_info=int(info),normal_equation_relative_residual=float(np.linalg.norm(H@candidate-rhs)/max(np.linalg.norm(rhs),1e-12)),step=step,J_min=float(np.linalg.det(FF).min())))
        predictions.append(X+disp.reshape(N,3));logs.append(frame)
        print('frame',t+1,'Jmin',round(frame[-1]['J_min'],3),'CG', [s['cg_info'] for s in frame],flush=True)
    np.savez_compressed(a.output/'prediction.npz',points=np.array(predictions))
    receipt=dict(kind='development_informed_public_input_kinematic_tissue_fit',
                 public_manifest_sha256=hashlib.sha256((a.input/'manifest.json').read_bytes()).hexdigest(),
                 affine_prediction_sha256=hashlib.sha256(a.affine.read_bytes()).hexdigest(),
                 prediction_sha256=hashlib.sha256((a.output/'prediction.npz').read_bytes()).hexdigest(),
                 script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 scales=dict(image_mm=.75,edge_gradient=.30,jacobian=.15),nonlinear_steps=3,max_cg_iterations=a.max_cg,
                 all_cg_converged=all(s['cg_info']==0 for f in logs for s in f),iterations=logs,
                 elapsed_seconds=time.perf_counter()-start)
    (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('complete',receipt['elapsed_seconds'],'seconds, converged',receipt['all_cg_converged'])


if __name__=='__main__':main()
