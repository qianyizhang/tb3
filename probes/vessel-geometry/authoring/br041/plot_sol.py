"""Local diagnostic projections of saved route versus private reference."""
from pathlib import Path
import os,json
os.environ.setdefault('MPLCONFIGDIR','/tmp/br041-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br041-image-only-centerline'
r=json.loads((B/'sol-results.json').read_text())['runs'][-1]
line=np.load(ROOT/r['answer_path']/'centerline.npy');ref=np.load(B/'tasks/named-rca/tests/reference.npy')
other=np.load(B/'private-rpla-diagnostic.npy')
fig,axes=plt.subplots(1,3,figsize=(14,5),layout='constrained')
for ax,(i,j,title) in zip(axes,[(0,1,'Axial projection'),(0,2,'Coronal projection'),(1,2,'Sagittal projection')]):
    ax.plot(other[:,i],other[:,j],color='#6579b7',lw=3,ls='--',label='Other branch: R-PLA')
    ax.plot(ref[:,i],ref[:,j],color='#167a61',lw=3,label='Requested reference: R-PDA')
    ax.plot(line[:,i],line[:,j],color='#d45536',lw=1.8,label='Sol/xhigh: image + name only')
    ax.scatter(line[0,i],line[0,j],c='#d45536',marker='o',s=45)
    ax.scatter(line[-1,i],line[-1,j],c='#d45536',marker='x',s=60)
    ax.set(title=title,xlabel='RAS '+'XYZ'[i]+' (mm)',ylabel='RAS '+'XYZ'[j]+' (mm)');ax.set_aspect('equal');ax.grid(alpha=.2)
axes[0].legend(fontsize=8)
fig.suptitle('BR-041 · RCA to R-PDA centerline · same CTA crop, no supplied mask or endpoints',fontsize=13)
fig.savefig(B/'sol-centerline-comparison.png',dpi=160)
print(B/'sol-centerline-comparison.png')
