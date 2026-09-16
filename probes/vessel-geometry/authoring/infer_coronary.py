"""Published ImageCAS-X CAS-Net inference, unchanged weights and full CTA input."""
from pathlib import Path
import hashlib,json,sys,time,subprocess
import numpy as np
import torch
import SimpleITK as sitk

ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'runs/br030-vessel-geometry'
SOURCE=BASE/'imagecas-x-source';sys.path.insert(0,str(SOURCE))
from utils.config import BenchmarkConfig
from models.registry import build_model
from preprocessing.pipeline import build_preprocessing
from postprocessing.pipeline import build_postprocessing
from inference import run_inference,_resample_probs_to_original_space
from utils.io import save_mask

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    torch.set_num_threads(4);torch.manual_seed(0)
    cfg=BenchmarkConfig.from_json(str(SOURCE/'configs/cas_net.json'))
    cfg.data.params['inference_batch_size']=1
    weights=BASE/'sources/coronary/cas_net.pt'
    assert sha(weights)==json.loads((BASE/'coronary-weight-manifest.json').read_text())['sha256']
    cfg.model.checkpoint=str(weights)
    device=torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    model=build_model(cfg).to(device).eval()
    source=BASE/'sources/coronary/original/1.img.nii.gz'
    out=BASE/'predictions/coronary-1-casnet.nii.gz';assert not out.exists(),'Never overwrite predictions'
    start=time.perf_counter();ni=sitk.ReadImage(str(source))
    sample=build_preprocessing(cfg)({'sitk_img':ni,'volume':sitk.GetArrayFromImage(ni).transpose(2,1,0)})
    volume=torch.from_numpy(sample['volume']).float()[None,None]
    print('INPUT',tuple(volume.shape),'device',device,'TTA',cfg.data.params['inference_mirror_tta'],flush=True)
    with torch.inference_mode():logits=run_inference(model,volume,cfg,device)['logits'][0]
    prob=torch.sigmoid(logits).numpy()
    prob=_resample_probs_to_original_space(prob,sample['spacing'],ni)
    raw_mask=np.argmax(prob,axis=0).astype('uint8')
    mask=build_postprocessing(cfg)({'pred':prob})['mask']
    save_mask(raw_mask,ni,str(out.with_name('coronary-1-casnet-before-component-filter.nii.gz')))
    save_mask(mask,ni,str(out))
    r={'source':'ImageCAS case 1','input_sha256':sha(source),'output':str(out.relative_to(ROOT)),
       'output_sha256':sha(out),'checkpoint_sha256':sha(weights),'seconds':time.perf_counter()-start,
       'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=SOURCE,text=True).strip(),
       'device':str(device),'torch':torch.__version__,'full_volume_input':True,
       'preprocessing':{'spacing_mm':.5,'HU_clip':[-200,1000],'normalised_range':[0,1]},
       'patch_size':[128,160,160],'overlap':.5,'weighting':'gaussian','mirror_TTA_axes':['X','Y'],
       'inference_batch_size':1,'postprocessing':'published argmax then >=100-voxel connected components',
       'synthetic_mask_edits':False,'training_overlap':'Case 1 is in the released train split; this is a development source, not a held-out accuracy estimate.'}
    (BASE/'coronary-prediction-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2),flush=True)

if __name__=='__main__':main()
