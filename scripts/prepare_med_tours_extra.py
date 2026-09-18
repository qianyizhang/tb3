#!/usr/bin/env python3
"""Derive two further guided tours from retained reviews and frozen arrays."""
from pathlib import Path
import json,re,base64,hashlib
import numpy as np
from scipy.ndimage import map_coordinates
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'site_med/tours/data';sources={}
def src(name):
 p=ROOT/name;sources[name]=hashlib.sha256(p.read_bytes()).hexdigest();return p
def read(name):return json.loads(src(name).read_text())
def save(name,data):(OUT/name).write_text(json.dumps(data,separators=(',',':'))+'\n')
def main():
 html=src('runs/br028-registration-3d-source/review/index.html').read_text()
 d=json.JSONDecoder().raw_decode(html.split('const data=',1)[1])[0]
 names=[]
 def extract(value):
  if isinstance(value,dict):return {k:extract(v) for k,v in value.items()}
  if isinstance(value,list):return [extract(v) for v in value]
  if isinstance(value,str) and value.startswith('data:image/png;base64,'):
   name=f'registration-{len(names):03}.png';(OUT/name).write_bytes(base64.b64decode(value.split(',',1)[1]));names.append(name);return name
  return value
 d=extract(d);d['image_files']=names;d['planes']=list(d['source']);save('registration.json',d)
 results=read('docs/evidence/br040-results.json');cases={};shared_index=None
 for case in ['ct-full','ct-partial']:
  base=f'runs/br039-ct-landmarks/tasks/{case}'
  truth=read(base+'/tests/truth.json');geo=read(base+'/environment/geometry.json');vol=np.load(src(base+'/environment/volume.npy'),mmap_mode='r')
  rows={r['model_setting']:r for r in results['trials'] if r['case']==case}
  answers={m:read(r['answer_path'])['landmarks'] for m,r in rows.items()}
  visible=[v['ijk'] for v in truth['targets'].values() if v['status']=='observed'];center=np.mean(visible,axis=0)
  if shared_index is None:shared_index=int(round(center[0]))
  index=shared_index;a=vol[index,:,:].T;lo,hi=geo['display_window'];a=np.uint8(np.clip((a-lo)/(hi-lo),0,1)*255)
  name=f'landmarks-{case}.png';Image.fromarray(np.flipud(a)).save(OUT/name)
  spacing=geo['spacing_ijk_mm'];targets={}
  for key,gt in truth['targets'].items():
   targets[key]={'reference':gt,'predictions':{m:v[key] for m,v in answers.items()}}
   for v in [targets[key]['reference'],*targets[key]['predictions'].values()]:
    if v.get('ijk') is not None:v['uv']=[(v['ijk'][1]+.5)/vol.shape[1],1-(v['ijk'][2]+.5)/vol.shape[2]];v['off_plane_mm']=(v['ijk'][0]-index)*spacing[0]
  cases[case]={'image':name,'shape':list(vol.shape),'spacing':spacing,'aspect':vol.shape[1]*spacing[1]/(vol.shape[2]*spacing[2]),'plane_index':index,'axis_directions':geo['positive_array_axes_patient_directions'],'targets':targets,'scores':{m:r['score'] for m,r in rows.items()}}
 save('landmarks.json',{'cases':cases,'image_files':[c['image'] for c in cases.values()],'description':'Native i-plane CT with projected markers. Physical j/k aspect retained. Out-of-plane displacement is not a 3D error estimate.'})
 prov_path=OUT/'provenance.json';prov=json.loads(prov_path.read_text());prov['sources'].update(sources);prov['outputs']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.name!='provenance.json' and p.is_file()};prov['additional_derivation_script']='scripts/prepare_med_tours_extra.py';save('provenance.json',prov)
 print('registration:',len(names),'source crops; landmarks: two native CT planes; sources:',len(sources))
if __name__=='__main__':main()
