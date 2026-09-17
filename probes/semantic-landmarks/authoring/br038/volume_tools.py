"""Native array[i,j,k] display/conversion helper. No reference landmarks."""
import argparse,json
from pathlib import Path
import numpy as np
import nibabel as nib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
BASE=Path(__file__).resolve().parent

def plane(a,axis,index):
    # Transpose makes first remaining array axis horizontal, second vertical.
    axes=[x for x in range(3) if x!=axis]
    return np.take(a,index,axis=axis).T,axes

def main():
 ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='op',required=True)
 sub.add_parser('check')
 c=sub.add_parser('convert');c.add_argument('ijk',nargs=3,type=float)
 v=sub.add_parser('view');v.add_argument('ijk',nargs=3,type=float);v.add_argument('--out',required=True);v.add_argument('--radius-mm',type=float,default=0);v.add_argument('--window',nargs=2,type=float)
 args=ap.parse_args();a=np.load(BASE/'volume.npy',mmap_mode='r');g=json.loads((BASE/'geometry.json').read_text());aff=np.array(g['voxel_to_ras_mm']);spacing=np.linalg.norm(aff[:3,:3],axis=0)
 if args.op=='check':
  ni=nib.load(BASE/'volume.nii.gz');assert list(a.shape)==g['shape_ijk'];assert np.array_equal(a,np.asarray(ni.dataobj));assert np.allclose(aff,ni.affine)
  for item in g['nonanatomical_coordinate_examples']:
   v=np.array(item['ijk']);w=nib.affines.apply_affine(aff,v);assert np.allclose(w,item['ras_mm']);assert np.allclose(nib.affines.apply_affine(np.linalg.inv(aff),w),v)
  print(json.dumps({'coordinate_check':'PASS','output_space':'voxel_ijk_zero_based','shape':a.shape,'positive_array_axes_patient_directions':g['positive_array_axes_patient_directions'],'warning':'Scanner world origin is not an anatomical landmark. No AC-PC or MNI alignment is implied.'}));return
 if args.op=='convert':
  print(json.dumps({'ijk':args.ijk,'ras_mm':nib.affines.apply_affine(aff,args.ijk).tolist()}));return
 p=np.array(args.ijk);assert np.all(p>=0) and np.all(p<=np.array(a.shape)-1),'View centre outside array';cent=np.rint(p).astype(int)
 window=args.window or g['display_window'];fig,axs=plt.subplots(1,3,figsize=(15,5),constrained_layout=True)
 for axis,ax in enumerate(axs):
  sl,axes=plane(a,axis,cent[axis]);u,v=axes
  ax.imshow(sl,cmap='gray',vmin=window[0],vmax=window[1],origin='lower',extent=[-.5,a.shape[u]-.5,-.5,a.shape[v]-.5],aspect=spacing[v]/spacing[u],interpolation='nearest')
  ax.axvline(p[u],color='cyan',lw=.6);ax.axhline(p[v],color='cyan',lw=.6)
  ax.set_xlabel(f'{"ijk"[u]} (voxel; increasing toward {g["positive_array_axes_patient_directions"][u]})');ax.set_ylabel(f'{"ijk"[v]} (voxel; increasing toward {g["positive_array_axes_patient_directions"][v]})');ax.set_title(f'{"ijk"[axis]} = {cent[axis]}');ax.grid(alpha=.3)
  if args.radius_mm:
   ax.set_xlim(max(-.5,p[u]-args.radius_mm/spacing[u]),min(a.shape[u]-.5,p[u]+args.radius_mm/spacing[u]));ax.set_ylim(max(-.5,p[v]-args.radius_mm/spacing[v]),min(a.shape[v]-.5,p[v]+args.radius_mm/spacing[v]))
 fig.suptitle(f'Array [i,j,k] = {p.tolist()}; cyan crosshair is your requested centre, NOT a detected landmark')
 fig.savefig(args.out,dpi=130);plt.close(fig)
if __name__=='__main__':main()
