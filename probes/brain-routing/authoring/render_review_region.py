"""Native-plane evidence for an explicitly selected anatomical review location."""
import argparse, json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import nibabel as nib
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'runs/br033-brain-routing'
DATA = BASE / 'sources/TopBrain_Data_Release_Batches1n2nTA36_081726'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--case', required=True)
    ap.add_argument('--center', nargs=3, type=int, required=True)
    ap.add_argument('--labels', nargs='+', type=int, required=True)
    ap.add_argument('--radius-mm', type=float, default=12)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    ni = nib.load(DATA / 'imagesTr_topbrain' / f'topcow_mr_{args.case}_0000.nii.gz')
    a = np.asarray(ni.dataobj)
    pred = np.asarray(nib.load(BASE / 'predictions-resencm-v1' / f'topcow_mr_{args.case}.nii.gz').dataobj)
    ref = np.asarray(nib.load(DATA / 'labelsTr_topbrain_v2_topaneu36class' / f'topcow_mr_{args.case}.nii.gz').dataobj)
    names = json.loads((DATA / 'labelmap_jsons/labels_topbrain_v2_topaneu36class.json').read_text())['labels']
    names = {v:k for k,v in names.items()}
    colors = ['#ffb347', '#23d8c4', '#e272dc', '#91b8ff']
    spacing = np.asarray(ni.header.get_zooms()[:3])
    center = np.asarray(args.center)
    half = np.ceil(args.radius_mm / spacing).astype(int)
    lo, hi = np.maximum(center - half, 0), np.minimum(center + half + 1, a.shape)
    crop = tuple(slice(x,y) for x,y in zip(lo,hi))
    vmax = np.percentile(a[crop], 99.8)
    fig, axes = plt.subplots(3,3,figsize=(12,11), facecolor='#101820')
    for axis in range(3):
        remaining = [d for d in range(3) if d != axis]
        sl = list(crop); sl[axis] = center[axis]
        gray = a[tuple(sl)].T
        extent = [lo[remaining[0]]*spacing[remaining[0]],hi[remaining[0]]*spacing[remaining[0]],
                  lo[remaining[1]]*spacing[remaining[1]],hi[remaining[1]]*spacing[remaining[1]]]
        for j, labels in enumerate([None,pred,ref]):
            ax = axes[axis,j]
            ax.imshow(gray,cmap='gray',origin='lower',vmin=0,vmax=vmax,extent=extent,interpolation='nearest')
            if labels is not None:
                plane = labels[tuple(sl)].T
                rgba = np.zeros((*plane.shape,4))
                for label,color in zip(args.labels,colors):
                    rgba[plane==label] = matplotlib.colors.to_rgba(color,.6)
                ax.imshow(rgba,origin='lower',extent=extent,interpolation='nearest')
            ax.scatter(center[remaining[0]]*spacing[remaining[0]],center[remaining[1]]*spacing[remaining[1]],marker='+',s=50,c='white',linewidths=.7)
            ax.set_xticks([]); ax.set_yticks([])
            ax.set_title(f'{["MRA", "Unedited prediction", "Reference annotation"][j]} · {"ijk"[axis]}={center[axis]}',color='white',fontsize=10)
    fig.suptitle(f'TopBrain MRA {args.case} — candidate review, not an admitted error',color='white',fontsize=17)
    legend = fig.legend(handles=[Patch(color=c,label=names[k]) for k,c in zip(args.labels,colors)],loc='lower center',ncol=len(args.labels),facecolor='#17232c',edgecolor='#17232c')
    for text in legend.get_texts(): text.set_color('white')
    fig.subplots_adjust(top=.94,bottom=.06,wspace=.03,hspace=.13)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(args.output,dpi=150,facecolor=fig.get_facecolor())
    print(args.output)


if __name__ == '__main__':
    main()
