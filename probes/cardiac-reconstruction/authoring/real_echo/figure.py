"""Standalone figure of case-specific shape uncertainty and input response."""
from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from score import volumes
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br032-real-echo'
r=json.loads((B/'sol-xhigh-receipt.json').read_text());a=np.load((ROOT/r['result_path']).parent/'artifacts/app/answer/prediction.npz');s=np.load(B/'replays/static-v2/output/prediction.npz');t=np.arange(1,19)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(1,2,figsize=(11,4.2),constrained_layout=True)
for i,p in enumerate(a['alternative_points']):ax[0].plot(t,volumes(p,a['faces']),color='#899aa7',alpha=.8,label='Alternative assumptions' if i==0 else None)
ax[0].plot(t,volumes(a['points'],a['faces']),color='#228e87',lw=2.5,label='Primary estimate');ax[0].set(title='Model-dependent cavity volume',xlabel='Original frame',ylabel='Volume (mL)');ax[0].legend(frameon=False)
for p,label,c,style in [(a['points'],'Original videos','#228e87','-'),(s['points'],'Repeated first images','#c67733','--')]:
 y=np.sqrt(np.mean(np.sum((p-p[0])**2,axis=-1),axis=1));ax[1].plot(t,y,label=label,color=c,ls=style,lw=2.5)
ax[1].set(title='Identical mesh motion after removing input motion',xlabel='Original frame',ylabel='Geometric vertex displacement RMS (mm)');ax[1].legend(frameon=False)
for x in ax:x.grid(alpha=.2);x.set_xticks([1,4,7,10,13,16,18])
fig.suptitle('Real-scan case: visual measurements encoded in fixed tables',fontsize=14)
fig.supxlabel('One public scan, no reference reconstruction. Alternatives are scenarios, not confidence bounds.\nThe executable reuses its measurements when pixels change; this does not establish training contamination.',fontsize=9)
for ext in ['png','pdf']:fig.savefig(B/f'real-case-comparison.{ext}',dpi=180)
print(B/'real-case-comparison.png')
