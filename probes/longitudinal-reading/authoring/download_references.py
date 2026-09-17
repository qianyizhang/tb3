"""Host-only core-lab references; never copied into a solver packet."""
from pathlib import Path
import json
import pandas as pd
from idc_index import IDCClient
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br037-longitudinal-reading'
idx=pd.read_parquet(B/'source/ispy2-index.parquet');selected=json.loads((B/'selected.json').read_text());client=IDCClient()
out=[]
for c in selected:
 d=idx[idx.PatientID.eq(c['source_id'])&idx.Modality.eq('MR')&idx.StudyDescription.isin(['ISPY2_MRI_T0','ISPY2_MRI_T1'])&idx.SeriesDescription.str.contains('VOLSER.*: SER$',regex=True,na=False)]
 assert len(d)==2,(c['case'],len(d))
 target=B/'source/private-reference'/c['case'];target.mkdir(parents=True,exist_ok=True)
 print(c['case'],round(d.series_size_MB.sum()),'MB',flush=True)
 client.download_from_selection(downloadDir=str(target),seriesInstanceUID=list(d.SeriesInstanceUID),quiet=True,show_progress_bar=False)
 out.extend(d.to_dict('records'))
(B/'reference-series.json').write_text(json.dumps(out,indent=2)+'\n')
