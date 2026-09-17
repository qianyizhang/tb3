"""Fetch public source documents only; retain exact bytes and hashes."""
from pathlib import Path
import hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[3]
B=ROOT/'runs/br037-longitudinal-reading/source'
URLS={
 'ispy2.html':'https://www.cancerimagingarchive.net/collection/ispy2/',
 'acrin-brain.html':'https://www.cancerimagingarchive.net/collection/acrin-dsc-mr-brain/',
 'clinical.xlsx':'https://www.cancerimagingarchive.net/wp-content/uploads/ISPY2-Imaging-Cohort-1-Clinical-Data.xlsx',
 'measurements.xlsx':'https://www.cancerimagingarchive.net/wp-content/uploads/Multi-feature-MRI-NACT-Data.xlsx',
 'private-tags.xlsx':'https://www.cancerimagingarchive.net/wp-content/uploads/ACRIN-6698-ISPY2-Shared-Private-Tag-Data-Dictionary_20210520.xlsx',
 'data-description.pdf':'https://www.cancerimagingarchive.net/wp-content/uploads/ACRIN-6698-ISPY2-DWI-and-DCE-MRI-Data-Descriptions_20210520.pdf',
}
def main():
 B.mkdir(parents=True,exist_ok=True);rows=[]
 for name,url in URLS.items():
  p=B/name
  if not p.exists():
   tmp=p.with_suffix(p.suffix+'.partial')
   subprocess.run(['curl','-L','--fail','--max-time','90','--retry','2',url,'-o',str(tmp)],check=True)
   tmp.rename(p)
  rows.append(dict(file=name,url=url,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 (B/'metadata-receipts.json').write_text(json.dumps(rows,indent=2)+'\n')
 print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
