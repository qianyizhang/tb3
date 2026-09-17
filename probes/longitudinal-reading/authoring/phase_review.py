"""Post-trial P02 review of the phase-selection limitation, using host reference regions."""
from pathlib import Path
import json
import numpy as np
import nibabel as nib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br037-longitudinal-reading'
c=next(c for c in json.loads((B/'grounding.json').read_text()) if c['case']=='P02')
m=json.loads((B/'prepared/P02/manifest.json').read_text());fig,ax=plt.subplots(2,4,figsize=(14,8.4));rows=[]
for r,ref in enumerate(c['references']):
    s=next(s for s in m['series'] if s['visit']==ref['visit'] and len(s['shape'])==4)
    ni=nib.load(B/'prepared/P02'/s['file']);center=np.rint(nib.affines.apply_affine(np.linalg.inv(ni.affine),ref['voi_center_ras_mm'])).astype(int)
    i,j,k=center;rad=55;a=np.asarray(ni.dataobj[i-rad:i+rad,j-rad:j+rad,k,:],dtype=np.float32)
    lo,hi=np.percentile(a,[1,99.5])
    for col,t in enumerate([0,1,2,6]):
        ax[r,col].imshow(a[:,:,t].T,origin='lower',cmap='gray',vmin=lo,vmax=hi)
        ax[r,col].set_title(f"{ref['visit']} · phase {t}",fontsize=12,pad=10)
        ax[r,col].set_xticks([]);ax[r,col].set_yticks([])
    rows.append({'visit':ref['visit'],'series_id':s['id'],'native_reference_center':center.tolist(),'display_range':[float(lo),float(hi)]})
fig.suptitle('P02: persistent source-region mass is more conspicuous after the first postcontrast phase',fontsize=13)
fig.text(.5,.025,'Host-only source-region crops. Agent spatial review used phases 0 and 1. Window fixed within each visit; no cross-visit intensity calibration.',ha='center',fontsize=9)
fig.subplots_adjust(left=.02,right=.98,bottom=.08,top=.9,hspace=.23,wspace=.1);fig.savefig(B/'review/P02-phase-selection.png',dpi=150)
(B/'phase-review.json').write_text(json.dumps({'posthoc':True,'rows':rows,'meaning':'Visual evidence of phase-dependent conspicuity, not a validated clinical diameter measurement.'},indent=2)+'\n')
