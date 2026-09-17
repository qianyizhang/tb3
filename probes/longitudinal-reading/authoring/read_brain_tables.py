"""Extract openly released ACRIN references without fetching controlled scans."""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
import json,csv,openpyxl
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br037-longitudinal-reading/source'
z=ZipFile(B/'brain-clinical.zip');out={};books={}
for name in z.namelist():
 if name.startswith('__MACOSX') or Path(name).name.startswith('.'):
  continue
 if name.endswith('.csv'):
  out[name]=list(csv.DictReader(z.read(name).decode('utf-8-sig').splitlines()))
 if name.endswith('.xlsx'):
  w=openpyxl.load_workbook(BytesIO(z.read(name)),read_only=True,data_only=True)
  books[name]={s.title:list(s.values) for s in w}
(B/'brain-clinical.json').write_text(json.dumps(out,indent=2)+'\n')
(B/'brain-dictionary.json').write_text(json.dumps(books,default=str,indent=2)+'\n')
book=next(iter(books.values()))
for sheet in ['S0','S1','T0','BR','PR']:
 print(sheet)
 print(book[sheet][:8])
 print([r for r in book[sheet] if any(x in str(r).lower() for x in ['progress','volume','enhanc','flair','identification','patient','visit'])])
for k,v in out.items():
 if Path(k).name in ['S0.csv','S1.csv','T0.csv','BR.csv','PR.csv']:
  print(Path(k).name,len(v),v[:2])
