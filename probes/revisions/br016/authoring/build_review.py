"""Answer-free review page with full-resolution MPR and locally saved answers."""
import json,shutil
from pathlib import Path
import numpy as np
from common import OUT,write,sha
P=OUT/'blind-review';P.mkdir(exist_ok=True);cases=[];mapping={}
for public,private in [('R01','aneurysm-n03'),('R02','aneurysm-n01'),('R03','aneurysm-n02')]:
 src=OUT/'build'/private;dst=P/public;dst.mkdir(exist_ok=True);m=json.loads((src/'volume.json').read_text());cases.append({'id':public,**{k:m[k] for k in ['shape','spacing_mm','display_high']}});mapping[public]=private
 for field in ['brain','original']:
  a=np.load(src/(field+'.npz'))['volume'];a.astype('<f4').tofile(dst/(field+'.bin'))
 shutil.copy2(src/'overview.png',dst/'overview.png')
write(P/'manifest.json',{'packet':'BR-016-blind-v1','cases':cases});shutil.copy2(Path(__file__).with_name('review.html'),P/'index.html')
write(OUT/'author/review-map.json',mapping)

# Optional reference reveal was explicitly requested after the initial blind pilot.
import subprocess,sys
subprocess.run([sys.executable,str(Path(__file__).with_name("enable_guided_review.py"))],check=True)

write(OUT/'author/review-receipt.json',{'packet':'BR-016-blind-v1','files':{str(p.relative_to(P)):sha(p) for p in sorted(P.rglob('*')) if p.is_file()},'reference_reveal_available':True,'no_model_outputs_in_packet':True})
print(P)
