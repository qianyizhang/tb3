"""Public-input multiresolution Demons baseline; does not read annotations."""
import argparse
import json
import time
from pathlib import Path
import numpy as np
import SimpleITK as sitk


def load(path):
    with np.load(path) as z:
        hu=np.clip(z['hu'],-1000,200).astype(np.float32);a=z['voxel_to_world']
    image=sitk.GetImageFromArray(hu.transpose(2,1,0))
    spacing=np.linalg.norm(a[:3,:3],axis=0)
    image.SetSpacing(spacing.tolist());image.SetOrigin(a[:3,3].tolist())
    image.SetDirection((a[:3,:3]/spacing).ravel().tolist())
    return image


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--iterations',default='150,150,100,60')
    args=ap.parse_args();t=time.time();sitk.ProcessObject.SetGlobalDefaultNumberOfThreads(4)
    fixed=load(args.data/'reference_volume.npz');moving=load(args.data/'volume.npz')
    # Global histogram matching compensates phase-dependent lung density.
    matcher=sitk.HistogramMatchingImageFilter();matcher.SetNumberOfHistogramLevels(1024)
    matcher.SetNumberOfMatchPoints(7);matcher.ThresholdAtMeanIntensityOn()
    moving=matcher.Execute(moving,fixed)
    field=None;levels=[]
    for shrink,iterations in zip([8,4,2,1],map(int,args.iterations.split(','))):
        f=sitk.Shrink(sitk.SmoothingRecursiveGaussian(fixed,max(.5,shrink/2)),[shrink]*3)
        m=sitk.Shrink(sitk.SmoothingRecursiveGaussian(moving,max(.5,shrink/2)),[shrink]*3)
        if field is None:
            field=sitk.Image(f.GetSize(),sitk.sitkVectorFloat64);field.CopyInformation(f)
        else:field=sitk.Resample(field,f,sitk.Transform(),sitk.sitkLinear,0.,sitk.sitkVectorFloat64)
        demons=sitk.FastSymmetricForcesDemonsRegistrationFilter()
        demons.SetNumberOfIterations(iterations);demons.SetStandardDeviations(1.)
        field=demons.Execute(f,m,field)
        entry={'shrink':shrink,'iterations':iterations,'metric':demons.GetMetric(),'elapsed_s':time.time()-t}
        levels.append(entry);print(json.dumps(entry),flush=True)
    transform=sitk.DisplacementFieldTransform(field)
    queries=json.loads((args.data/'queries.json').read_text())
    answer={'query_ids':queries['query_ids'],'points_world_mm':[list(transform.TransformPoint(p)) for p in queries['reference_world_mm']]}
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(answer,indent=2)+'\n')
    args.out.with_suffix('.log.json').write_text(json.dumps({'method':'SimpleITK FastSymmetricForcesDemons + histogram matching','levels':levels,'elapsed_s':time.time()-t},indent=2)+'\n')


if __name__=='__main__':main()
