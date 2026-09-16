"""Unedited single-checkpoint CLAIM predictions on supplied native CoW crops.

This uses an author-provided ROI, one fold, final checkpoint and no mirroring;
it is not the original YOLO + ten-checkpoint challenge ensemble.
"""
import hashlib,json,os,time
from pathlib import Path
import nibabel as nib
import numpy as np
import torch
from nnunetv2.inference.predict_from_raw_data import nnUNetPredictor

ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'runs/br030-vessel-geometry'
SRC=ROOT/'runs/br025-vessel-curation/TopCoW2024_Data_Release'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    import re,subprocess
    torch.set_num_threads(4)
    model=BASE/'sources/topcow_claim_models/topcow-claim-models'
    checkpoint=model/'fold_0/checkpoint_final.pth'
    manifest=json.loads((BASE/'source-manifest.json').read_text())
    expected=next(x for x in manifest if x['path']==str(checkpoint.relative_to(ROOT)))
    assert sha(checkpoint)==expected['sha256']
    predictor=nnUNetPredictor(tile_step_size=.5,use_gaussian=True,use_mirroring=False,
        perform_everything_on_device=False,device=torch.device('mps' if torch.backends.mps.is_available() else 'cpu'),
        verbose=False,verbose_preprocessing=False,allow_tqdm=True)
    # This 2024 checkpoint contains NumPy scalar metadata. Keep PyTorch's
    # restricted weights loader and admit only those concrete numerical types.
    with torch.serialization.safe_globals([np.dtype,np._core.multiarray.scalar,np.dtypes.Float64DType,np.dtypes.Float32DType]):
        predictor.initialize_from_trained_model_folder(str(model),use_folds=(0,),checkpoint_name='checkpoint_final.pth')
    rows=[];out=BASE/'predictions';out.mkdir(exist_ok=True)
    for pid in ['004','007','009','012']:
        dst=out/f'mra-{pid}-labels.nii.gz';assert not dst.exists(),'Never overwrite a prediction'
        path=SRC/'imagesTr'/f'topcow_mr_{pid}_0000.nii.gz';ni=nib.load(path)
        nums=list(map(int,re.findall(r'\d+',(SRC/'roi_loc_labelsTr'/f'topcow_mr_{pid}.txt').read_text())))
        size,origin=np.array(nums[:3]),np.array(nums[3:]);lo=np.maximum(0,origin-10);hi=np.minimum(ni.shape,origin+size+10)
        sl=tuple(slice(int(a),int(b)) for a,b in zip(lo,hi));image=np.asarray(ni.dataobj)[sl].astype(np.float32)
        affine=ni.affine.copy();affine[:3,3]=(ni.affine@np.r_[lo,1])[:3]
        spacing=ni.header.get_zooms()[:3];start=time.perf_counter()
        print('START',pid,image.shape,flush=True)
        result=predictor.predict_single_npy_array(image.transpose(2,1,0)[None],{'spacing':list(spacing[::-1])})
        pred=np.asarray(result).transpose(2,1,0).astype('uint8');pred[pred==13]=15
        assert pred.shape==image.shape
        nib.save(nib.Nifti1Image(pred,affine),dst)
        row={'source':pid,'input_sha256':sha(path),'roi_origin_ijk':lo.tolist(),'roi_shape':list(pred.shape),
             'seconds':time.perf_counter()-start,'output':str(dst.relative_to(ROOT)),'output_sha256':sha(dst),
             'unique_labels':list(map(int,np.unique(pred)))};rows.append(row)
        receipt={'method':'CLAIM 2024 ResEncM, fold_0 checkpoint_final, public ROI plus 10-voxel halo',
            'full_challenge_pipeline':False,'mirroring':False,'synthetic_mask_edits':False,
            'checkpoint_sha256':sha(checkpoint),'torch':torch.__version__,'device':str(predictor.device),
            'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE/'claim-source',text=True).strip(),
            'training_overlap':'Source TopCoW cases participated in the released training collection; per-fold membership not established. No unseen-test claim.',
            'rows':rows}
        (BASE/'prediction-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('DONE',row,flush=True)

if __name__=='__main__':main()
