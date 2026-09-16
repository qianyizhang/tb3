"""Static evidence of the geometric repair, source CPR, and full parent route."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'runs/br033-brain-routing'
G=BASE/'gap-calibration'


def main():
    ni=nib.load(G/'image.nii.gz');im=np.asarray(ni.dataobj)
    original=np.asarray(nib.load(G/'original_labels.nii.gz').dataobj)
    fixed=np.asarray(nib.load(G/'corrected_crop_labels.nii.gz').dataobj)
    changed=fixed!=original;pts=np.argwhere(changed);center=np.rint(pts.mean(0)).astype(int)
    sp=nib.affines.voxel_sizes(ni.affine)
    half=np.ceil(4/sp).astype(int);lo=np.maximum(center-half,0);hi=np.minimum(center+half+1,im.shape)
    z=int(center[2]);sl=(slice(lo[0],hi[0]),slice(lo[1],hi[1]),z)
    fig=plt.figure(figsize=(14,8),facecolor='#101820')
    ax1=fig.add_subplot(221);ax2=fig.add_subplot(222);ax3=fig.add_subplot(223);ax4=fig.add_subplot(224,projection='3d')
    for ax,mask,title in [(ax1,original,'Input · distal branch disconnected'),(ax2,fixed,'Geometry baseline · two voxels added')]:
        ax.imshow(im[sl].T,cmap='gray',origin='lower',vmin=0,vmax=np.percentile(im,99.8),interpolation='nearest')
        rgba=np.zeros((*im[sl].T.shape,4));rgba[np.isin(mask[sl].T,[1,25])]=matplotlib.colors.to_rgba('#79b9c4',.55)
        if ax==ax2:rgba[changed[sl].T]=matplotlib.colors.to_rgba('#ff55ab',.95)
        ax.imshow(rgba,origin='lower',interpolation='nearest');ax.set_xticks([]);ax.set_yticks([])
        ax.set_title(title,color='white',fontsize=13)
    cpr=np.load(G/'cpr.npz');metrics=json.loads((G/'metrics.json').read_text())
    ax3.imshow(cpr['intensity'][0].T,cmap='gray',origin='lower',aspect='auto',vmin=0,vmax=np.percentile(im,99.8),extent=[0,cpr['arc_mm'][-1],-5,5])
    ax3.set_title('Source-sampled CPR · 0°',color='white',fontsize=13);ax3.set_xlabel('Distance from basilar anchor (mm)',color='white');ax3.set_ylabel('Offset (mm)',color='white');ax3.tick_params(colors='white')
    mesh=trimesh.load(G/'basilar-right-sca.ply',process=False)
    surf=Poly3DCollection(mesh.triangles,alpha=.38,facecolor='#71bcb5',edgecolor='none');ax4.add_collection3d(surf)
    line=np.load(G/'centerline.npy');ax4.plot(*line.T,color='#ffda88',linewidth=2)
    ax4.scatter(*line[[0,-1]].T,c='white',s=24)
    ax4.text(*line[0], '  BA parent',color='white',fontsize=10);ax4.text(*line[-1],'  R-SCA target',color='white',fontsize=10)
    low,high=mesh.bounds;mid=(low+high)/2;r=(high-low).max()/2
    ax4.set(xlim=(mid[0]-r,mid[0]+r),ylim=(mid[1]-r,mid[1]+r),zlim=(mid[2]-r,mid[2]+r))
    ax4.set_box_aspect((1,1,1));ax4.set_axis_off();ax4.set_facecolor('#101820');ax4.view_init(elev=18,azim=-70)
    ax4.set_title(f'Connected parent-to-target surface · {metrics["route_length_mm"]:.1f} mm route',color='white',fontsize=13)
    fig.suptitle('TopBrain MRA 004 · real gap, easy geometric calibration',color='white',fontsize=19,y=.98)
    fig.text(.5,.018,'One addition matches the reference vessel; one is reference background. Route error p95: 0.30 mm. No agent trial or clinical validation.',ha='center',color='#b9c8d2',fontsize=11)
    fig.subplots_adjust(top=.91,bottom=.09,hspace=.30,wspace=.18)
    out=BASE/'review/brain-calibration-summary.png';fig.savefig(out,dpi=150,facecolor=fig.get_facecolor());print(out)


if __name__=='__main__':main()
