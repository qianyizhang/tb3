"""Prospective source-label stratification; no solver outputs consulted."""
from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br037-longitudinal-reading';S=B/'source'
def table(name):
 rows=next(iter(json.loads((S/f'{name}.json').read_text()).values()))
 return pd.DataFrame(rows[1:],columns=rows[0])
def main():
 clinical=table('clinical');m=table('measurements');idx=pd.read_parquet(S/'ispy2-index.parquet')
 d=m.merge(clinical,left_on='CLINICAL-TRIAL-SUBJECT-ID',right_on='Patient_ID',validate='one_to_one')
 d['source_id']='ISPY2-'+d.Patient_ID.astype(str)
 d=d[d.source_id.isin(idx.PatientID)].sort_values('Patient_ID')
 # All four measured visits; two early visits supplied, remaining visits withheld.
 # Include a concordant good outcome, residual disease despite reduction, and
 # weak early imaging response. The thresholds define strata, not clinical truth.
 specs=[('strong_response_pcr',(d.pCR==1)&(d.FTV_pch_T0_T1<=-50)),
        ('strong_response_residual',(d.pCR==0)&(d.FTV_pch_T0_T1<=-50)),
        ('weak_response_residual',(d.pCR==0)&(d.FTV_pch_T0_T1>=-20))]
 out=[]
 for name,mask in specs:
  candidates=d[mask].copy()
  print(name,len(candidates),flush=True)
  for _,r in candidates.head(4).iterrows():
   rows=idx[idx.PatientID.eq(r.source_id)]
   originals=rows[rows.Modality.eq('MR')&~rows.SeriesDescription.str.contains('VOLSER|DynaVIEWS|MASK|SEG|SER MAP|SUBTR|MIP',case=False,na=False)]
   v={'stratum':name,'source_id':r.source_id,'labels':r.to_dict(),'candidate_original_series':originals.to_dict('records'),'all_series':rows.to_dict('records')}
   out.append(v)
   print(r.source_id,'pCR',r.pCR,'FTV', [round(r[f'VOLUME_TUM_BLU_V{x}0'],2) for x in range(1,5)],'LD',[r[f'LD_T{x}'] for x in range(4)],'MB',round(originals.series_size_MB.sum()),flush=True)
 (B/'triage-candidates.json').write_text(json.dumps(out,indent=2,default=str)+'\n')
if __name__=='__main__':main()
