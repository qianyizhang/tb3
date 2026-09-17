"""Read source workbooks with the bundled document Python; no workbook edits."""
from pathlib import Path
import json,openpyxl
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br037-longitudinal-reading/source'
for name in ['clinical','measurements','private-tags']:
 wb=openpyxl.load_workbook(B/f'{name}.xlsx',read_only=True,data_only=True)
 data={s.title:[list(row) for row in s.values] for s in wb}
 (B/f'{name}.json').write_text(json.dumps(data,indent=2,default=str)+'\n')
 print(name,[(k,len(v)) for k,v in data.items()])
from pypdf import PdfReader
(B/'data-description.txt').write_text('\n'.join(p.extract_text() for p in PdfReader(B/'data-description.pdf').pages))
