"""Download full original series of three prospectively selected patients."""
from pathlib import Path
import json,hashlib
import pandas as pd
from idc_index import IDCClient
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br037-longitudinal-reading'
SELECTED={'P01':'ISPY2-102011','P02':'ISPY2-111344','P03':'ISPY2-100899'}
def main():
 candidates=json.loads((B/'triage-candidates.json').read_text());idx=pd.read_parquet(B/'source/ispy2-index.parquet')
 rows=[]
 for alias,pid in SELECTED.items():
  c=next(x for x in candidates if x['source_id']==pid)
  allrows=idx[idx.PatientID.eq(pid)].copy()
  # Source dictionary identifies VOLSER as cropped/core-lab analysis objects.
  # Retain every other MR series, including native scouts and T2 images.
  d=allrows[allrows.Modality.eq('MR')&~allrows.SeriesDescription.str.contains('VOLSER',case=False,na=False)]
  rows.append(dict(case=alias,source_id=pid,stratum=c['stratum'],labels=c['labels'],
    series=d.to_dict('records'),excluded=allrows[~allrows.index.isin(d.index)].to_dict('records')))
  print(alias,pid,len(d),'series',round(d.series_size_MB.sum()),'MB',flush=True)
 manifest=B/'selected.json'
 if manifest.exists():assert json.loads(manifest.read_text())==rows
 else:manifest.write_text(json.dumps(rows,indent=2)+'\n')
 client=IDCClient()
 for c in rows:
  target=B/'source/dicom'/c['case'];target.mkdir(parents=True,exist_ok=True)
  print('Downloading',c['case'],flush=True)
  client.download_from_selection(downloadDir=str(target),seriesInstanceUID=[s['SeriesInstanceUID'] for s in c['series']],show_progress_bar=False,quiet=True)
  files=sorted(target.rglob('*.dcm'))
  assert len(files)==sum(s['instanceCount'] for s in c['series']),(len(files),c['case'])
  receipt={str(p.relative_to(target)):dict(bytes=p.stat().st_size,sha256=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()) for p in files}
  (B/f"{c['case']}-download.json").write_text(json.dumps(receipt,indent=2)+'\n')
  print('Complete',c['case'],len(files),flush=True)
if __name__=='__main__':main()
