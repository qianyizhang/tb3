#!/usr/bin/env python3
"""Prepare source-derived geometry and image sequences for three guided tours.

Uses the existing .venv-br030 environment. Writes only site_med/tours/data.
No task rebuilds, model calls, or writes to retained experiments.
"""
from pathlib import Path
import base64, hashlib, importlib.util, io, json, sys
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial import cKDTree
from skimage.measure import marching_cubes

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'site_med/tours/data'
SOURCES={}
def source(relative):
    p=ROOT/relative
    SOURCES[relative]=hashlib.sha256(p.read_bytes()).hexdigest()
    return p

def save(name,obj):
    (OUT/name).write_text(json.dumps(obj,separators=(',',':'))+'\n')

def png(name,array):
    Image.fromarray(array).save(OUT/name)
    return name

def import_module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def simplify(points,faces,target=1800):
    """Display-only decimation; map every kept vertex to an exact input vertex."""
    from vtkmodules.vtkCommonCore import vtkPoints
    from vtkmodules.vtkCommonDataModel import vtkPolyData,vtkCellArray
    from vtkmodules.vtkFiltersCore import vtkDecimatePro
    from vtkmodules.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
    points=np.asarray(points);faces=np.asarray(faces)
    vp=vtkPoints();vp.SetData(numpy_to_vtk(points,deep=True));poly=vtkPolyData();poly.SetPoints(vp)
    c=vtkCellArray();c.SetCells(len(faces),numpy_to_vtkIdTypeArray(np.c_[np.full(len(faces),3),faces].ravel().astype('int64'),deep=True));poly.SetPolys(c)
    d=vtkDecimatePro();d.SetInputData(poly);d.SetTargetReduction(max(0,1-target/len(faces)));d.PreserveTopologyOff();d.SplittingOn();d.Update()
    o=d.GetOutput();q=vtk_to_numpy(o.GetPoints().GetData());dist,ids=cKDTree(points).query(q)
    assert dist.max()<1e-5,dist.max()
    ff=vtk_to_numpy(o.GetPolys().GetData()).reshape(-1,4)[:,1:]
    ids_unique,inverse=np.unique(ids,return_inverse=True)
    return ids_unique,inverse[ff],float(dist.max())

def segment():
    sys.path.insert(0,str(ROOT/'probes/revisions/br013/authoring'))
    from inspect_scene import load_scene
    inspect=import_module('med_tour_ct','probes/revisions/br017/authoring/inspect_ct.py')
    base='runs/br017-absorption/'
    before=load_scene(ROOT/base/'build/abdomen-n01');after=load_scene(ROOT/base/'build/abdomen-m02')
    groups=[]
    for objects in [before,after]:
        selected=[o for o in objects if o['proposed_label'] in ['pancreas','duodenum']]
        for o in selected:o['color_index']=1 if o['proposed_label']=='duodenum' else 0
        groups.append(selected)
    z=np.load(source(base+'author/abdomen-m02/region-0.npz'))
    region={k:z[k] for k in ['mask','affine_lps','surface_lps']};region.update(object_id='transferred tissue',color_index=3)
    groups.append([region])
    ct=np.load(source(base+'build/abdomen-m02/ct.npz'))
    for condition in ['abdomen-n01','abdomen-m02']:
        for o in groups[0 if condition.endswith('n01') else 1]:source(base+f'build/{condition}/{o["object_id"]}.npz')
    key=json.loads(source(base+'author/abdomen-m02/expected.json').read_text())
    center=np.array(key['findings'][0]['oracle_point_lps_mm']);span=180;size=420
    zmin,zmax=region['surface_lps'][:,2].min(),region['surface_lps'][:,2].max()
    positions=sorted(set(np.round(np.r_[np.linspace(zmin,zmax,23),center[2],324.7],4)))
    frames=[]
    for j,pos in enumerate(positions):
        states={}
        for name,objects in zip(['before','after','region'],groups):
            im,_=inspect.render_slice(ct['hu'],ct['affine_lps'],objects,'axial',pos,center=center,span=span,size=size)
            rgb=np.asarray(im).copy(); axis=np.linspace(-span/2,span/2,size)
            q=np.zeros((size,size,3));q[:]=center;q[:,:,2]=pos;q[:,:,0]+=axis[None,:];q[:,:,1]+=axis[:,None]
            for o in objects:
                mask=inspect.sample(o['mask'],o['affine_lps'],q,False)
                color=np.array(tuple(bytes.fromhex(inspect.PALETTE[o['color_index']][1:])))
                alpha=.48 if name=='region' else .28
                edge=np.all(rgb==color,axis=-1)
                rgb[mask]=np.uint8(rgb[mask]*(1-alpha)+color*alpha)
                rgb[edge]=color
            states[name]=png(f'seg-{j:02}-{name}.png',rgb)
        frames.append({'z_mm':float(pos),'images':states})
    point=np.array([-22.9,-199.9,324.7]);uv=((point[:2]-center[:2])/span+.5).tolist()
    save('segmentation.json',{'frames':frames,'hero':int(np.argmin(np.abs(np.array(positions)-center[2]))),'pointFrame':int(np.argmin(np.abs(np.array(positions)-point[2]))),'pointUV':uv,'span_mm':span,'center_lps_mm':center.tolist(),'point_lps_mm':point.tolist(),'transferred_ml':21.04,'description':'Nearest-neighbor physical LPS reslices, fixed CT window level 50/width 400. Exact source masks; no artificial tissue motion.'})
    print('segmentation:',len(frames),'physical slices',flush=True)

def vessel():
    import nibabel as nib
    import trimesh
    base='runs/br030-vessel-geometry/geometry/'
    ref=np.load(source(base+'reference.npz'));aff=ref['affine'];before=ref['proposed']
    c=np.load(source(base+'terra-arc-correction/cpr.npz'))
    path=np.load(source(base+'terra-arc-correction/centerline.npy'))
    after=np.asarray(nib.load(source(base+'terra-arc-correction/corrected_mask.nii.gz')).dataobj)>0
    verts,faces,_,_=marching_cubes(before.astype('uint8'),.5)
    verts=np.einsum('nj,ij->ni',verts,aff[:3,:3])+aff[:3,3];ids,ff,_=simplify(verts,faces)
    original={'points':np.round(verts[ids],3).tolist(),'faces':ff.tolist()}
    mesh=trimesh.load(source(base+'terra-arc-correction/vessels.ply'),process=False)
    ids,ff,_=simplify(mesh.vertices,mesh.faces);fixed={'points':np.round(mesh.vertices[ids],3).tolist(),'faces':ff.tolist()}
    added=np.einsum('nj,ij->ni',np.argwhere(after&~before),aff[:3,:3])+aff[:3,3]
    assert len(added)==103
    cp=[]
    for angle in range(8):cp.append(png(f'vessel-cpr-{angle}.png',np.uint8(np.clip((c['hu'][angle].T+100)/800,0,1)*255)))
    geom=import_module('med_tour_vessel_geom','probes/vessel-geometry/authoring/geometry.py')
    tangent,normal,binormal=geom.frames(path.astype(float))
    indices=np.arange(len(path))
    offsets=np.linspace(-8,8,65);a,b=np.meshgrid(offsets,offsets,indexing='ij');coords=path[indices,None,None]+a[None,:,:,None]*normal[indices,None,None]+b[None,:,:,None]*binormal[indices,None,None]
    inv=np.linalg.inv(aff);ijk=np.einsum('...j,ij->...i',coords,inv[:3,:3])+inv[:3,3]
    hu=ndimage.map_coordinates(ref['image'],ijk.reshape(-1,3).T,order=1,mode='constant',cval=-1000).reshape(len(indices),65,65)
    cuts=[png(f'vessel-cut-{j:02}.png',np.uint8(np.clip((x+100)/800,0,1)*255)) for j,x in enumerate(hu)]
    points=np.asarray(fixed['points']);center=(points.max(0)+points.min(0))/2;radius=float(np.linalg.norm(points-center,axis=1).max())
    save('vessels.json',{'before':original,'after':fixed,'path':path.round(4).tolist(),'arc':c['arc_mm'].round(4).tolist(),'normal':normal.round(6).tolist(),'binormal':binormal.round(6).tolist(),'added':added.round(4).tolist(),'center':center.tolist(),'radius':radius,'gap_index':int(cKDTree(path).query(added.mean(0))[1]),'cpr':cp,'cuts':cuts,'cut_indices':indices.tolist(),'original_axis_length_mm':184.808529,'saved_line_length_mm':float(c['arc_mm'][-1]),'description':'Real source geometry. Display-only surface simplification. Corrected package changes only arc_mm; original trial remains a failure.'})
    print('vessels:',len(path),'route points,',len(added),'added voxels',flush=True)

def cardiac():
    base='runs/br035-segmentation-mechanics/'
    review=json.loads(source(base+'review/masks-synthetic/data.json').read_text());models=[]
    for m in review['models']:
        p=np.asarray(m['points']);f=np.asarray(m['faces'])
        models.append({'points':p.tolist(),'faces':f.tolist(),'display_vertex_map_max_mm':0,'original_vertices':p.shape[1],'original_faces':len(f)})
    raw=json.loads(source('docs/evidence/br035-segmentation-mechanics-results.json').read_text());trial=next(r for r in raw['trials'] if r['phase']=='sol-xhigh' and r['condition']=='masks')
    pred_path=str(Path(trial['result_path']).parent/'artifacts/app/answer/prediction.npz')
    pred=np.load(source(pred_path));truth=np.load(source(base+'prepared/truth.npz'))
    geom=import_module('med_tour_cardiac_geom','probes/cardiac-reconstruction/authoring/segmentation_mechanics/geometry.py')
    cells=truth['points'][0,truth['tetra']].mean(1)
    # Deterministic spread through reference cell order, not selected for large errors.
    candidates=np.linspace(0,len(cells)-1,160,dtype=int)
    ids,w=geom.locate(pred['points'][0],pred['tetra'],cells[candidates]);valid=np.flatnonzero(ids>=0)
    take=valid[np.linspace(0,len(valid)-1,24,dtype=int)];ids=ids[take];w=w[take];truth_ids=candidates[take]
    tracked_pred=np.einsum('tnvi,nv->tni',pred['points'][:,pred['tetra'][ids]],w)
    tracked_ref=truth['points'][:,truth['tetra'][truth_ids]].mean(2)
    assert np.max(np.linalg.norm(tracked_pred[0]-tracked_ref[0],axis=1))<1e-6
    masks=np.load(source(base+'prepared/synthetic_masks.npz'))['masks'];mid=masks.shape[2]//2
    mask_imgs=[png(f'cardiac-mask-{t:02}.png',(masks[t,:,mid,:].astype('uint8')*205)) for t in range(len(masks))]
    material=trial['grade']['material'];regions=material['regions'];curves={'reference':[r[0][2] for r in material['reference_regional_engineering_pct']],'prediction':[r[0][2] for r in material['predicted_regional_engineering_pct']],'region':regions[0]}
    save('cardiac.json',{'models':models,'center':review['center'],'radius':review['extent']*1.3,'frames':30,'masks':mask_imgs,'material_tracks':{'reference':tracked_ref.round(4).tolist(),'prediction':tracked_pred.round(4).tolist(),'source_cells':truth_ids.tolist(),'selection':'24 covered probes spread through 160 regularly spaced source cell IDs; not ranked by error.'},'curve':curves,'metrics':{'dice':trial['grade']['geometry']['mean_mask_dice'],'motion_rmse_mm':material['motion_rmse_mm'],'strain_mae_pp':material['strain_mae_pp']},'description':'Masks-only Sol condition versus STRAUS source. Display meshes retain all original surface vertices and triangles from the review; no rescore. Material probes share the same reference position at frame zero. All 30 acquired phases retained.'})
    print('cardiac:',[(len(m['points'][0]),len(m['faces'])) for m in models],'display meshes; 24 shared material probes',flush=True)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    segment();vessel();cardiac()
    save('provenance.json',{'sources':SOURCES,'source_path_base':'repository root','output_path_base':'site_med/tours/data','derivation_script':'scripts/prepare_med_tours.py','scope':'Derived presentation assets only. Fixed historical scores retained. No new model inference.','terms':{'segmentation':'TotalSegmentator CC BY 4.0','vessels':'Source declarations: ImageCAS Apache 2.0, ImageCAS-X CC BY 4.0. Retain original source receipt.','cardiac':'STRAUS simulation-derived previews; not real patient motion. Source terms are not broadened.','reference_records':['docs/evidence/br030-sources.json','site/cardiac-provenance.json','probes/revisions/br017/authoring/README.md']},'outputs':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.name!='provenance.json' and p.is_file()}})

if __name__=='__main__':main()
