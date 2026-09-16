"""Standalone scientific comparison from completed, independently replayed trials."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br031-cardiac-levels'
rows=[]
for stage,phase in [('l1','terra-high'),('l1','sol-xhigh'),('l1v','sol-xhigh')]:
    p=B/f'{stage}-{phase}-receipt.json'
    if p.exists():
        r=json.loads(p.read_text())
        if r['execution']=='completed' and 'metrics' in (r['grade'] or {}):rows.append(r)
if not rows:raise SystemExit('No completed motion trial')
names=[('4 views' if r['stage']=='l1' else '3D volume')+'\n'+r['phase'] for r in rows]
m=[r['grade']['metrics'] for r in rows];x=np.arange(len(rows));colors=['#447caa','#318b83','#c78345'][:len(rows)]
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axs=plt.subplots(2,2,figsize=(11,7.5),constrained_layout=True)
a=axs[0,0];a.bar(x-.17,[v['observed_dice_mean'] for v in m],.32,label='Original four planes',color='#447caa');a.bar(x+.17,[v['unseen_dice_mean'] for v in m],.32,label='Other four planes*',color='#c78345');a.set_ylim(0,1);a.set_title('Cross-sectional agreement');a.set_ylabel('Mean Dice');a.legend(frameon=False,fontsize=9)
a=axs[0,1];a.bar(x,[v['material_rmse_mm'] for v in m],color=colors);a.axhline(2,color='#7d4545',linestyle='--',label='2 mm target');a.set_title('Material-point recovery');a.set_ylabel('RMSE (mm)');a.legend(frameon=False)
a=axs[1,0]
for j,(name,c) in enumerate(zip(['Longitudinal','Circumferential','Radial'],['#447caa','#318b83','#c78345'])):
    a.bar(x+(j-1)*.23,[v['strain_mae_pp'][j] for v in m],.22,label=name,color=c)
a.axhline(5,color='#7d4545',linestyle='--');a.set_title('Strain from recovered material motion');a.set_ylabel('Mean absolute error (percentage points)');a.legend(frameon=False,fontsize=8)
a=axs[1,1];a.bar(x,[v['tissue_volume_error_pct'] for v in m],color=colors);a.axhline(5,color='#7d4545',linestyle='--');a.set_title('Myocardial tissue-volume curve');a.set_ylabel('Mean relative error (%)')
for a in axs.flat:a.set_xticks(x,names);a.grid(axis='y',alpha=.16);a.set_axisbelow(True)
fig.suptitle('Cardiac reconstruction: appearance, material motion and mechanics score separately',fontsize=14)
fig.supxlabel('*Other planes are withheld from 4-view trials; they are inside the added 3D volume in L1V.\nOne STRAUS simulated healthy case; one fresh attempt per condition. Targets are engineering diagnostics.',fontsize=9)
for ext in ['png','pdf']:fig.savefig(B/f'agent-comparison.{ext}',dpi=180)
print(B/'agent-comparison.png')
