"""Portable local viewer; previews are derived from numeric source-mapped outputs."""
from pathlib import Path
import base64,io,json,sys
import numpy as np
import nibabel as nib
from PIL import Image
from geometry import *

ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br030-vessel-geometry';G=B/'geometry'
def png(a):
    f=io.BytesIO();Image.fromarray(a.astype('uint8')).save(f,format='PNG');return 'data:image/png;base64,'+base64.b64encode(f.getvalue()).decode()
def atlas(a):return a.reshape(-1,a.shape[-1])
def simplify(vertices,faces):
    from vtkmodules.vtkCommonCore import vtkPoints
    from vtkmodules.vtkCommonDataModel import vtkPolyData,vtkCellArray
    from vtkmodules.vtkFiltersCore import vtkQuadricDecimation
    from vtkmodules.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
    p=vtkPoints();p.SetData(numpy_to_vtk(vertices.astype('float64'),deep=True));poly=vtkPolyData();poly.SetPoints(p)
    c=vtkCellArray();packed=np.column_stack([np.full(len(faces),3),faces]).ravel().astype('int64');c.SetCells(len(faces),numpy_to_vtkIdTypeArray(packed,deep=True));poly.SetPolys(c)
    dec=vtkQuadricDecimation();dec.SetInputData(poly);dec.SetTargetReduction(.88);dec.Update();out=dec.GetOutput()
    return vtk_to_numpy(out.GetPoints().GetData()),vtk_to_numpy(out.GetPolys().GetData()).reshape(-1,4)[:,1:]
def main():
    solution=sys.argv[1] if len(sys.argv)>1 else 'oracle';assert solution in ['oracle','image-baseline','terra-arc-correction']
    folder=G/solution;c=np.load(folder/'cpr.npz');path=np.load(folder/'centerline.npy');z=np.load(G/'reference.npz')
    fixed=np.asarray(nib.load(folder/'corrected_mask.nii.gz').dataobj)>0;aff=z['affine'];t,n,b=frames(path.astype(float))
    section_xyz=section_coordinates(path,n,b,c['offsets_mm']);atlases={}
    if (folder/'sections.npz').exists():sec=np.load(folder/'sections.npz')
    else:
        from scipy import ndimage as ndi
        sections=sample(z['image'],aff,section_xyz);seg=sample(fixed,aff,section_xyz,0,0)>0;area=[]
        for cut in seg:
            cc,_=ndi.label(cut);k=cc[32,32];area.append(float((cc==k).sum()*.25**2) if k else 0.)
        sec={'hu':sections,'area_mm2':np.array(area),'offsets_mm':c['offsets_mm']}
        np.savez_compressed(folder/'sections.npz',**sec)
    for key,hu,xyz in [('cpr',c['hu'].transpose(0,2,1),c['source_ras_mm']),('section',sec['hu'],section_xyz)]:
        # For CPR display, rows are offset and columns arc; sections retain u/v axes.
        before=sample(z['proposed'],aff,xyz,0,0)>0;after=sample(fixed,aff,xyz,0,0)>0
        if key=='cpr':before=before.transpose(0,2,1);after=after.transpose(0,2,1)
        atlases[key]=png(atlas(np.clip((hu+100)/800*255,0,255)))
        atlases[key+'Before']=png(atlas(before*255));atlases[key+'After']=png(atlas(after*255))
    import trimesh
    mesh=trimesh.load(folder/'vessels.ply',process=False);vertices,faces=simplify(mesh.vertices,mesh.faces)
    r=json.loads((G/'build-receipt.json').read_text());request=json.loads((G/'input/request.json').read_text())
    from scipy.spatial import cKDTree
    ref=z['reference_path'];ref_arc=np.r_[0.,np.cumsum(np.linalg.norm(np.diff(ref,axis=0),axis=1))]
    ends=ref[np.searchsorted(ref_arc,[r['natural_gap_start_mm'],r['natural_gap_end_mm']])]
    gap_ids=cKDTree(path).query(ends)[1];gap_index=int(cKDTree(path).query(request['review_center_ras_mm'])[1])
    data={'path':path.round(4).tolist(),'arc':c['arc_mm'].round(4).tolist(),'area':sec['area_mm2'].tolist(),
          'gap':c['arc_mm'][gap_ids].tolist(),'gapIndices':gap_ids.tolist(),'gapIndex':gap_index,
          'review':request['review_center_ras_mm'],'vertices':vertices.round(3).tolist(),'faces':faces.tolist(),
          'center':((vertices.max(0)+vertices.min(0))/2).tolist(),'atlases':atlases}
    out=B/('viewer' if solution=='oracle' else 'viewer-'+solution);out.mkdir(exist_ok=True);template=(Path(__file__).with_name('viewer.html')).read_text()
    links='<p class="downloads"><a href="../viewer/">Reference-assisted</a><a href="../viewer-image-baseline/">Image-guided baseline</a><a href="../viewer-terra-arc-correction/">Terra + distance-axis correction</a></p>'
    template=template.replace('<div class="stats">',links+'<div class="stats">')
    if solution!='oracle':
        label='Image-guided baseline' if solution=='image-baseline' else 'Terra + axis correction'
        addition=125 if solution=='image-baseline' else 103
        summary=(f'The displayed {label.lower()} adds {addition} voxels and removes none, with no changes outside the review sphere. '+
                 ('The fixed algorithm reads only the public inputs during execution; it was designed after author source review.' if solution=='image-baseline' else
                  'Terra passed repair, tracing and mesh checks. Its original CPR distance axis overstated saved-line length by 8.89 mm. Only arc_mm was corrected by the author; the mask, path, image pixels, source locations and mesh are unchanged. This corrected package passes every gate; the frozen model result remains a failure.'))
        old='The displayed repair is reference-assisted: 205 voxels added, 17 removed, no changes outside the 8 mm review sphere. The model prediction is untouched in the input. Segmentation components change from three to two after repair.'
        template=template.replace(old,summary).replace('Reference-assisted repair',label).replace('Reference-assisted mask',label+' mask').replace('../geometry/oracle/','../geometry/'+solution+'/')
        template=template.replace('reference-assisted author artifact, separate from the blind model trial.',label+' artifact; original frozen trial remains separately recorded.')
        template=template.replace('PUBLIC DATA · LOCAL DEVELOPMENT EXPERIMENT','PUBLIC DATA · '+label.upper())
    template=template.replace("$('position').max=N-1;render()","$('position').max=N-1;$('position').value=DATA.gapIndex;render()")
    template=template.replace('DATA.gap[0]/DATA.arc.at(-1)*c.width','DATA.gapIndices[0]/(N-1)*c.width').replace('(DATA.gap[1]-DATA.gap[0])/DATA.arc.at(-1)*c.width','(DATA.gapIndices[1]-DATA.gapIndices[0])/(N-1)*c.width')
    (out/'index.html').write_text(template.replace('__DATA__',json.dumps(data,separators=(',',':'))))
    Image.fromarray(np.clip((c['hu'][0].T+100)/800*255,0,255).astype('uint8')).resize((1300,260)).save(out/'cpr-preview.png')
    print(json.dumps({'viewer':str(out/'index.html'),'html_bytes':(out/'index.html').stat().st_size,'preview_faces':len(faces)}))
if __name__=='__main__':main()
