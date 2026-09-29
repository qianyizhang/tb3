"""Build four source-pinned TopCoW box/edge teaching packs without running ReX code."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import struct
import zlib
from pathlib import Path

import numpy as np

ENTRIES = {
    'rexmle-topcow-track1-task2': ('rex-topcow-ct-box','retained-rex-topcow-ct-box-v1','ct','box'),
    'rexmle-topcow-track2-task2': ('rex-topcow-mr-box','retained-rex-topcow-mr-box-v1','mr','box'),
    'rexmle-topcow-track1-task3': ('rex-topcow-ct-edges','retained-rex-topcow-ct-edges-v1','ct','edges'),
    'rexmle-topcow-track2-task3': ('rex-topcow-mr-edges','retained-rex-topcow-mr-edges-v1','mr','edges'),
}
FRAME='TopCoW2024-native-NIfTI-RAS'
LICENSE='LicenseRef-TopCoW-OpenDataSwiss'
ANTERIOR=('L-A1','Acom','3rd-A2','R-A1')
POSTERIOR=('L-Pcom','L-P1','R-P1','R-Pcom')


def root_default() -> Path:
    for p in Path(__file__).resolve().parents:
        if (p/'pyproject.toml').is_file() and (p/'src/tb3_medical').is_dir(): return p
    raise RuntimeError('Pass --repo-root while running the staged script')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n')


def png(path: Path, array: np.ndarray) -> None:
    h,w=array.shape[:2];channels=1 if array.ndim==2 else 4
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
    pixels=array.astype(np.uint8,copy=False).tobytes()
    rows=b''.join(b'\0'+pixels[y*w*channels:(y+1)*w*channels] for y in range(h))
    raw=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,0 if channels==1 else 6,0,0,0))
    raw+=chunk(b'IDAT',zlib.compress(rows,9))+chunk(b'IEND',b'')
    path.write_bytes(raw)


def read_nifti(path: Path) -> tuple[np.ndarray,dict]:
    raw=gzip.decompress(path.read_bytes())
    if struct.unpack_from('<i',raw)[0]!=348 or raw[344:348]!=b'n+1\0': raise ValueError('Wrong NIfTI header')
    dims=struct.unpack_from('<8h',raw,40)
    datatype=struct.unpack_from('<h',raw,70)[0]
    dtype={4:'<i2',16:'<f4'}.get(datatype)
    if dims[0]!=3 or dtype is None or struct.unpack_from('<h',raw,254)[0]<=0:
        raise ValueError('Expected 3D signed image NIfTI with sform')
    shape=tuple(dims[1:4]);offset=int(struct.unpack_from('<f',raw,108)[0]);slope,intercept=struct.unpack_from('<ff',raw,112)
    image=np.frombuffer(raw,dtype=dtype,count=int(np.prod(shape)),offset=offset).reshape(shape,order='F')
    affine=[list(struct.unpack_from('<4f',raw,280+16*i)) for i in range(3)]+[[0.,0.,0.,1.]]
    return image,{'shape_ijk':list(shape),'spacing_ijk_mm':list(struct.unpack_from('<3f',raw,80)),
                  'affine_ijk_to_ras_mm':affine,'sform_code':struct.unpack_from('<h',raw,254)[0],
                  'scaling':[slope,intercept],'native_axis_basis':'NIfTI RAS world mm'}


def plane(array: np.ndarray,k: int,size: int=384) -> np.ndarray:
    nx,ny,_=array.shape;scale=min(1.,size/max(nx,ny))
    i=np.rint(np.linspace(0,nx-1,max(1,round(nx*scale)))).astype(int)
    j=np.rint(np.linspace(ny-1,0,max(1,round(ny*scale)))).astype(int)
    return array[np.ix_(i,j,[k])][:,:,0].T


def parse_box(path: Path) -> tuple[list[int],list[int]]:
    lines=path.read_text().splitlines()
    size=next([int(v) for v in re.findall(r'\d+',line)] for line in lines if line.startswith('Size (Voxels):'))
    location=next([int(v) for v in re.findall(r'\d+',line)] for line in lines if line.startswith('Location (Voxels):'))
    if len(size)!=3 or len(location)!=3: raise ValueError('Expected three box values')
    return size,location


def parse_edges(path: Path) -> dict[str,dict[str,int]]:
    graph={'anterior':{},'posterior':{}};section=None
    for line in path.read_text().splitlines():
        value=line.strip()
        if value in ('anterior:','posterior:'):
            section=value[:-1]
        elif ':' in value and section:
            key,bit=value.split(':',1);graph[section][key.strip()]=int(bit.strip())
    if tuple(graph['anterior'])!=ANTERIOR or tuple(graph['posterior'])!=POSTERIOR:
        raise ValueError('Changed named edge order or keys')
    if any(bit not in (0,1) for side in graph.values() for bit in side.values()): raise ValueError('Nonbinary edge')
    return graph


def overlay_box(shape: tuple[int,int],native_shape: tuple[int,int,int],k: int,size: list[int],location: list[int]) -> np.ndarray:
    h,w=shape;nx,ny,_=native_shape
    rgba=np.zeros((h,w,4),dtype=np.uint8)
    if not location[2]<=k<=location[2]+size[2]-1: return rgba
    x0=round(location[0]*(w-1)/(nx-1));x1=round((location[0]+size[0]-1)*(w-1)/(nx-1))
    y0=round((ny-1-(location[1]+size[1]-1))*(h-1)/(ny-1));y1=round((ny-1-location[1])*(h-1)/(ny-1))
    if not (0<=x0<=x1<w and 0<=y0<=y1<h): raise ValueError('Source ROI extends outside native display')
    rgba[y0:y1+1,x0:x1+1]=[255,189,70,30]
    width=3
    rgba[y0:y0+width,x0:x1+1]=[255,189,70,240]
    rgba[y1-width+1:y1+1,x0:x1+1]=[255,189,70,240]
    rgba[y0:y1+1,x0:x0+width]=[255,189,70,240]
    rgba[y0:y1+1,x1-width+1:x1+1]=[255,189,70,240]
    return rgba


def build(root: Path,entry: str,receipt_path: Path,output: Path) -> None:
    if output.exists(): raise FileExistsError(f'Refusing to overwrite existing output: {output}')
    directory,pack_id,modality,kind=ENTRIES[entry]
    if output.name!=directory: raise ValueError(f'Expected destination basename {directory}')
    receipt=json.loads(receipt_path.read_text())
    if receipt['entry_id']!=entry or receipt['illustration_basis']!='mixed': raise ValueError('Wrong resolution receipt')
    for pin in receipt['adapter_files']:
        if sha(root/pin['local_path'])!=pin['sha256']: raise ValueError(f'Changed pinned adapter {pin["local_path"]}')
    for asset in receipt['assets']:
        if sha(root/asset['path'])!=asset['sha256']: raise ValueError(f'Changed native source {asset["path"]}')
    image_path,target_path=[root/a['path'] for a in receipt['assets']]
    image,geometry=read_nifti(image_path)
    if list(image.shape)!=receipt['native_geometry']['shape_ijk'] or not np.allclose(
            geometry['affine_ijk_to_ras_mm'][:3],receipt['native_geometry']['affine_rows'],atol=1e-5):
        raise ValueError('Changed native physical geometry')
    source_target=(parse_box(target_path) if kind=='box' else parse_edges(target_path))
    if kind=='box':
        size,location=source_target
        if size!=receipt['source_annotation']['size_voxels'] or location!=receipt['source_annotation']['location_voxels']:
            raise ValueError('Changed source ROI values')
    elif source_target!=receipt['source_annotation']:
        raise ValueError('Changed source graph bits')
    scalar=image.astype(np.float32);slope,intercept=geometry['scaling'];scalar=scalar*(slope if slope else 1)+intercept
    finite=scalar[np.isfinite(scalar)];lo,hi=[float(v) for v in np.quantile(finite,[.01,.995])]
    if hi<=lo: raise ValueError('Invalid fixed display window')
    indices=np.rint(np.linspace(image.shape[2]*.20,image.shape[2]*.80,9)).astype(int).tolist()
    output.mkdir(parents=True);(output/'images').mkdir()
    samples=[];reference_samples=[];created=[]
    for n,k in enumerate(indices):
        raw=plane(scalar,k);gray=np.rint(255*np.clip((raw-lo)/(hi-lo),0,1)).astype(np.uint8)
        name=f'images/input-{n:02d}.png';png(output/name,gray);created.append(name)
        affine=np.asarray(geometry['affine_ijk_to_ras_mm']);world=affine@np.asarray([(image.shape[0]-1)/2,(image.shape[1]-1)/2,k,1.])
        samples.append({'file':name,'native_k_zero_based':k,'center_ras_mm':[round(float(v),3) for v in world[:3]],
                        'display_shape_xy':[gray.shape[1],gray.shape[0]]})
        if kind=='box':
            size,location=source_target
            overlay=overlay_box(gray.shape,image.shape,k,size,location)
            ref_name=f'images/reference-roi-{n:02d}.png';png(output/ref_name,overlay);created.append(ref_name)
            reference_samples.append({'file':ref_name,'native_k_zero_based':k,'intersects_scorer_box':bool(np.any(overlay[:,:,3]))})
    source={'entry_id':entry,'case_id':'012','modality':'CTA' if modality=='ct' else 'MRA',
            'source_role':'held-out test input under static pinned ReX split','native_input_sha256':receipt['assets'][0]['sha256'],
            'geometry':geometry,'fixed_window_scaled_native_values':[round(lo,6),round(hi,6)],
            'sample_rule':'9 fixed 20%-to-80% native k indices; no target-guided input selection',
            'display_mapping':'PNG x=i, y=ny-1-j; nearest-neighbor downsample to longest axis <=384 pixels',
            'samples':samples,'source_split':receipt['static_split']}
    answer={'status':'not-retained','participant_prediction':None,'submission':None,'score':None,
            'csv':'submission.csv','columns':receipt['output_contract']['columns'],
            'relative_prediction_pattern':receipt['output_contract']['path_template'],
            'required_json_schema':receipt['output_contract']['json_schema'],
            'coordinate_units':'voxel indices' if kind=='box' else 'binary edge presence bits',
            'illustrative_path_not_a_file':True}
    if kind=='box':
        size,location=source_target
        reference={'role':'reader-only private ReX test ROI','source_sha256':receipt['assets'][1]['sha256'],
                   'size_voxels':size,'location_voxels':location,
                   'scorer_interpreted_min_corner_voxels':location,
                   'scorer_interpreted_max_corner_inclusive_voxels':[location[i]+size[i]-1 for i in range(3)],
                   'description_calls_location_center':True,
                   'samples':reference_samples,'prediction_or_score':None}
        diagram={'type':'symbolic voxel grid only','sample_size_voxels':[3,2],
                 'sample_location_voxels':[4,3],
                 'scorer_rule':'min=location; max=location+size-1; margin=ceil(ratio*size)',
                 'ratios':{'boundary_iou':.2,'metric_named_iou':.5},
                 'description_conflict':'Task prose says center; scorer uses minimum corner. This toy uses neither patient annotation.'}
    else:
        reference={'role':'reader-only private ReX test graph annotation','source_sha256':receipt['assets'][1]['sha256'],
                   'anterior':source_target['anterior'],'posterior':source_target['posterior'],
                   'prediction_or_score':None}
        diagram={'type':'symbolic candidate-edge graph, not traced from this patient scan',
                 'anterior_keys':list(ANTERIOR),'posterior_keys':list(POSTERIOR),
                 'scorer_rule':'four-bit anterior and posterior variant strings; balanced accuracy across cases, separately',
                 'candidate_presence':'unknown until reader-only source reveal'}
    dump(output/'source.json',source);dump(output/'output.json',answer)
    dump(output/'reference.json',reference);dump(output/'diagram.json',diagram)
    license_path=root/'presentation/task-explorer/rex-topcow/DATA-LICENSE.txt'
    license_sha='6b527078226cc70d90f6938b55002961e8b311aa57fb720e0d4cc8f180919690'
    if sha(license_path)!=license_sha: raise ValueError('Changed source license')
    (output/'DATA-LICENSE.txt').write_bytes(license_path.read_bytes())
    (output/'NOTICE.md').write_text(
        f'# {entry} local teaching pack\n\nExact TopCoW2024 source case012, {receipt["source_url"]}. '
        'Noncommercial use with attribution; commercial use requires owner permission. The image is a static '
        'test-partition input. Its ROI or edge annotation exists in the full source archive but is private '
        'in ReX test staging and may mount only after reader reveal. Nine deterministic native-index source '
        'slices are display derivatives. Diagrams are explicitly symbolic; participant JSON, grader run and '
        'score are absent. Native source SHA-256 and physical geometry are pinned in source.json/manifest.json.\n')
    created+=['source.json','output.json','reference.json','diagram.json','DATA-LICENSE.txt','NOTICE.md']
    sources={f'presentation/external-tasks/sources/{entry}-resolution.json':sha(receipt_path),
             str(license_path.relative_to(root)):license_sha}
    sources.update({a['path']:a['sha256'] for a in receipt['assets']})
    sources.update({p['local_path']:p['sha256'] for p in receipt['adapter_files']})
    manifest={'schema':1,'id':pack_id,'frame':FRAME,'units':'mm','license':LICENSE,'label_license':LICENSE,
              'reference_policy':'reader-reference-reveal','runtime_geometry':'source-slices',
              'source_class':'source-derived-teaching','illustration_basis':'mixed','sources':sources,
              'checks':{'native_input_verified':True,'native_target_verified':True,
                        'case_012_partition':'static-test','participant_output_retained':False,
                        'scorer_or_preparer_run':False,'sampled_native_slices':9},
              'assets':[{'file':name,'bytes':(output/name).stat().st_size,'sha256':sha(output/name),
                         'provenance':'source-derived-teaching',
                         'role':'reader-reference-reveal' if name=='reference.json' or name.startswith('images/reference-roi-') else 'illustration'} for name in created]}
    dump(output/'manifest.json',manifest)


def main() -> None:
    p=argparse.ArgumentParser();p.add_argument('--repo-root',type=Path)
    p.add_argument('--entry',choices=ENTRIES,required=True);p.add_argument('--receipt',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=(a.repo_root or root_default()).resolve()
    receipt=(a.receipt or root/'presentation/external-tasks/sources'/f'{a.entry}-resolution.json').resolve()
    build(root,a.entry,receipt,a.output.resolve())


if __name__=='__main__':main()
