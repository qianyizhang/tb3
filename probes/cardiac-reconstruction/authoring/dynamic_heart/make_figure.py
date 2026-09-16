"""Standalone scientific summary of the corrected author screen."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);a=p.parse_args()
    root=a.run;g=dict(np.load(root/'analysis-v2/geometry.npz'))
    r=json.loads((root/'analysis-v2/results.json').read_text())['models']
    tr=json.loads((root/'tissue-analysis-v3/results.json').read_text())['model']
    fig=plt.figure(figsize=(13,9),facecolor='white');spec=fig.add_gridspec(2,2,height_ratios=[1.45,1],hspace=.32,wspace=.26)
    norm=Normalize(-10,60);cmap=plt.get_cmap('RdYlBu_r');frame=10
    for i,(fn,title) in enumerate([(root/'analysis-v2/healthy_reference.npz','Known simulator motion'),(root/'tissue-analysis-v3/tissue_fit.npz','Reconstructed from four video planes')]):
        m=dict(np.load(fn));x=m['points'][frame];f=g['boundary'];values=100*m['nodal_fields'][frame,:,2]
        colors=cmap(norm(values[f].mean(1)));colors[(g['point_labels'][f]>0).sum(1)<2]=[.62,.66,.69,1]
        ax=fig.add_subplot(spec[0,i],projection='3d');poly=Poly3DCollection(x[f],facecolors=colors,edgecolors='none',zsort='average');ax.add_collection3d(poly);ax.auto_scale_xyz(*x.T);ax.set_box_aspect(np.ptp(g['points'],axis=0));ax.view_init(16,222);ax.set_axis_off();ax.set_title(title,fontsize=13,pad=-4)
    cax=fig.add_axes([.39,.51,.22,.012]);cb=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cmap),cax=cax,orientation='horizontal');cb.set_label('Radial engineering strain (%) · frame 11',fontsize=9);cb.ax.tick_params(labelsize=8)
    ax=fig.add_subplot(spec[1,0]);names=['Global affine\n(video)','Coupled tissue\n(video)'];x=np.arange(2);values=np.array([r['video_affine']['comparison']['directional_engineering_mae_pp'],tr['comparison']['directional_engineering_mae_pp']]);colors=['#5584bd','#3c9e9c','#df945d']
    for j,label in enumerate(['Longitudinal','Circumferential','Radial']):ax.bar(x+(j-1)*.23,values[:,j],width=.21,label=label,color=colors[j])
    ax.axhline(5,color='#b94e43',linestyle='--',linewidth=1,label='Provisional 5-point target');ax.set_xticks(x,names);ax.set_ylabel('Strain error (percentage points)');ax.set_title('Better wall thickening, incomplete motion recovery',fontsize=12);ax.spines[['top','right']].set_visible(False);ax.legend(fontsize=8,frameon=False)
    ax=fig.add_subplot(spec[1,1]);phase=np.arange(30)/29*100
    for data,label,color,ls in [(r['healthy_reference'],'Simulation reference','#222d37','-'),(r['video_affine'],'Global affine fit','#7597b7','--'),(tr,'Coupled tissue fit','#dc9963','-')]:ax.plot(phase,data['tissue_volume_ml'],label=label,color=color,linestyle=ls,linewidth=2)
    ax.set_xlabel('Cycle phase (%)');ax.set_ylabel('Myocardial tissue volume (mL)');ax.set_title('Tissue volume is not cavity volume or EF',fontsize=12);ax.spines[['top','right']].set_visible(False);ax.legend(fontsize=8,frameon=False)
    fig.suptitle('Dynamic heart modeling: recover the tissue mechanics',fontsize=18,y=.98)
    fig.text(.5,.944,'STRAUS healthy simulation · 11,370 material vertices · 47,186 tetrahedra · 30 frames',ha='center',fontsize=10,color='#576570')
    fig.text(.08,.025,'Author development screen. The tissue fit has 4.03 mm material RMSE and 6.79-point radial strain error; it does not pass all targets.\nDirectional statistics exclude missing source axes. No clinical strain, chamber EF, pressure or flow is claimed.',fontsize=9,color='#576570')
    fig.savefig(root/'dynamic-heart-summary.png',dpi=160,bbox_inches='tight')
    fig.savefig(root/'dynamic-heart-summary.pdf',bbox_inches='tight')
    print(root/'dynamic-heart-summary.png')


if __name__=='__main__':main()
