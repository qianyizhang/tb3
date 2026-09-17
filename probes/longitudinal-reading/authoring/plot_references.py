"""Host-only source trajectories; withheld values never enter solver packets."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br037-longitudinal-reading'
g=json.loads((B/'grounding.json').read_text());fig,axes=plt.subplots(1,3,figsize=(14,4.8))
for ax,c in zip(axes,g):
    x=np.arange(1,5);lab=c['labels']
    ftv=np.array([lab[f'VOLUME_TUM_BLU_V{i}0'] for i in x]);ld=np.array([lab[f'LD_T{i-1}'] for i in x])
    ax.axvspan(.8,2.1,color='#e9f0f9',zorder=0);ax.axvline(2.5,color='#999',ls='--',lw=1)
    ax.plot(x,100*ftv/ftv[0],'o-',label='Enhancement-defined volume',color='#3269a8')
    ax.plot(x,100*ld/ld[0],'s-',label='Longest diameter',color='#bd6039')
    ax.set(title=f"{c['case']} · source pCR = {lab['pCR']}",xticks=x,xticklabels=['V1','V2','V3','V4'],ylim=(-5,195),xlim=(.8,4.2),ylabel='% of baseline source measurement')
    ax.grid(axis='y',alpha=.2);ax.text(1.5,180,'Supplied',ha='center',color='#36587f');ax.text(3.5,180,'Withheld',ha='center',color='#777')
    ax.spines[['top','right']].set_visible(False)
axes[0].legend(loc='upper left',bbox_to_anchor=(0,-.12),frameon=False,ncol=2)
fig.suptitle('Longitudinal targets: enhancement burden and diameter can diverge',fontsize=15)
fig.text(.5,.01,'Source measurements, not model predictions. pCR is a surgical outcome label; none of these fields were supplied to Terra.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.06,1,.94));fig.savefig(B/'review/source-trajectories.png',dpi=160)
