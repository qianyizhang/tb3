"""Lossless spatial/temporal packing of original DICOM pixels into NIfTI.

Keep native FOV, every frame, rescale parameters, and physical geometry. Split
scout orientations. Output metadata is a whitelist; source IDs/private tags and
later examinations are not exposed to the solver.
"""
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import argparse,hashlib,json,re
import numpy as np
import nibabel as nib
import pydicom

ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br037-longitudinal-reading'
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def sec(v):
 s=str(v or '').split('.')[0].ljust(6,'0')
 try:return int(s[:2])*3600+int(s[2:4])*60+int(s[4:6])
 except ValueError:return None
def convert(case):
 assert (B/f'{case}-download.json').exists(),'Require complete source download'
 out=B/'prepared'/case;out.mkdir(parents=True,exist_ok=True)
 assert not (out/'manifest.json').exists(),'Never overwrite prepared case'
 groups=defaultdict(list);audit=[]
 for p in sorted((B/'source/dicom'/case).rglob('*.dcm')):
  d=pydicom.dcmread(p,stop_before_pixels=True)
  assert 'VOLSER' not in str(d.SeriesDescription)
  key=(str(d.StudyDescription),str(d.SeriesInstanceUID),tuple(np.round(d.ImageOrientationPatient,5)),int(d.Rows),int(d.Columns),str(getattr(d,'EchoTime','')))
  # Scout acquisitions can contain irregularly spaced, overlapping plane sets.
  # Preserve each distinct plane instead of inventing a regular volume geometry.
  if re.search('SCOUT|SURVEY|LOCALIZER',str(d.SeriesDescription),re.I):
   key=(*key,tuple(np.round(d.ImagePositionPatient,4)))
  groups[key].append((p,d))
 dates={k[0]:str(v[0][1].StudyDate) for k,v in groups.items()}
 base=datetime.strptime(dates['ISPY2_MRI_T0'],'%Y%m%d');manifest=[]
 for n,(key,items) in enumerate(sorted(groups.items(),key=lambda v:(v[0][0],int(v[1][0][1].SeriesNumber),v[0][2])),1):
  visit='V'+str(int(key[0][-1])+1);sid=f'S{n:02d}';first=items[0][1]
  iop=np.array(first.ImageOrientationPatient,float);normal=np.cross(iop[:3],iop[3:]);normal/=np.linalg.norm(normal)
  positions=defaultdict(list)
  for p,d in items:positions[round(float(np.dot(d.ImagePositionPatient,normal)),3)].append((p,d))
  levels=sorted(positions);counts={len(x) for x in positions.values()};assert len(counts)==1,(key,counts)
  phases=counts.pop();ordered=[]
  for loc in levels:
   records=sorted(positions[loc],key=lambda x:(int(getattr(x[1],'TemporalPositionIdentifier',0)),sec(getattr(x[1],'AcquisitionTime','')) or 0,int(x[1].InstanceNumber)))
   ordered.append(records)
  if len(levels)>1:
   delta=np.diff(levels);spacing=float(np.median(delta));assert np.max(np.abs(delta-spacing))<.03,(key,delta)
   origins=np.array([x[0][1].ImagePositionPatient for x in ordered],float)
   step=np.median(np.diff(origins,axis=0),axis=0)
   assert np.max(np.abs(origins-(origins[0]+np.arange(len(levels))[:,None]*step)))<.05
  else:step=normal*float(getattr(first,'SpacingBetweenSlices',getattr(first,'SliceThickness',1)))
  aff=np.eye(4);aff[:3,0]=iop[:3]*float(first.PixelSpacing[1]);aff[:3,1]=iop[3:]*float(first.PixelSpacing[0]);aff[:3,2]=step;aff[:3,3]=ordered[0][0][1].ImagePositionPatient
  aff=np.diag([-1,-1,1,1])@aff
  volume=np.empty((int(first.Columns),int(first.Rows),len(levels),phases),np.float32)
  samples=[]
  for k,records in enumerate(ordered):
   for t,(p,h) in enumerate(records):
    d=pydicom.dcmread(p);pix=d.pixel_array.astype(np.float32)*float(getattr(d,'RescaleSlope',1))+float(getattr(d,'RescaleIntercept',0))
    assert pix.shape==volume.shape[:2][::-1]
    volume[:,:,k,t]=pix.T
    assert np.linalg.norm(nib.affines.apply_affine(aff,[0,0,k])-np.array(d.ImagePositionPatient)*[-1,-1,1])<.06
    if k in [0,len(levels)//2,len(levels)-1] and t in [0,phases-1]:samples.append(dict(source=str(p.relative_to(B)),k=k,phase=t,sha256=sha(p)))
  times=[sec(getattr(ordered[len(levels)//2][t][1],'AcquisitionTime','')) for t in range(phases)]
  name=f'{visit}_{sid}.nii.gz';ni=nib.Nifti1Image(volume[:,:,:,0] if phases==1 else volume,aff);ni.header.set_xyzt_units('mm');nib.save(ni,out/name)
  check=nib.load(out/name)
  for sample in samples:
   d=pydicom.dcmread(B/sample['source']);expected=d.pixel_array.astype(np.float32)*float(getattr(d,'RescaleSlope',1))+float(getattr(d,'RescaleIntercept',0))
   got=np.asarray(check.dataobj[:,:,sample['k'],sample['phase']] if phases>1 else check.dataobj[:,:,sample['k']]);assert np.array_equal(got,expected.T)
  desc=re.sub(r'^ISPY2:\s*','',str(first.SeriesDescription))
  row=dict(id=sid,visit=visit,day=(datetime.strptime(dates[key[0]],'%Y%m%d')-base).days,file=name,sequence=desc,shape=list(ni.shape),voxel_sizes_mm=nib.affines.voxel_sizes(aff).tolist(),axes=list(nib.aff2axcodes(aff)),affine_ras_mm=aff.tolist(),phase_acquisition_offsets_seconds=[v-times[0] if v is not None and times[0] is not None else None for v in times],echo_time_ms=float(getattr(first,'EchoTime',0)),repetition_time_ms=float(getattr(first,'RepetitionTime',0)),flip_angle_deg=float(getattr(first,'FlipAngle',0)),source_frame_count=len(items))
  manifest.append(row);audit.append(dict(series=sid,source_uid=key[1],sample_checks=samples,output_sha256=sha(out/name)))
  print(case,name,ni.shape,desc,flush=True)
 (out/'manifest.json').write_text(json.dumps(dict(case=case,series=manifest),indent=2)+'\n')
 (B/f'{case}-conversion-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
 return manifest
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('case');a=p.parse_args();convert(a.case)
