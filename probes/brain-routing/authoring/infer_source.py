"""Untouched native-grid predictions from one verified released TA36 checkpoint.

Uses the released preprocessing/predictor and exact network plan on Apple MPS.
This is a single ensemble component, not the official three-model Docker result.
No reference masks or annotation-derived crops enter inference.
"""
from pathlib import Path
import argparse, hashlib, importlib.metadata, json, os, sys, time

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'runs/br033-brain-routing'
SOURCE = BASE / 'ta36-source'
sys.path.insert(0, str(SOURCE))
os.environ['nnUNet_compile'] = 'false'
os.environ['nnUNet_def_n_proc'] = '4'
import nibabel as nib
import numpy as np
import torch
from nnunetv2.inference.predict_from_raw_data import nnUNetPredictor
from nnunetv2.utilities.get_network_from_plans import get_network_from_plans
from nnunetv2.utilities.plans_handling.plans_handler import PlansManager


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', nargs='+', default=['004', '007', '012'])
    ap.add_argument('--model', choices=['resEncM', 'plain_conv'], default='resEncM')
    args = ap.parse_args()
    receipt = json.loads((BASE / 'ta36-source-manifest.json').read_text())
    assert receipt['layer_sha256_verified']
    files = {x['path']: x['sha256'] for x in receipt['files']}
    # Verify executable model source and checkpoint bytes before loading.
    for rel, expected in files.items():
        assert sha(SOURCE / rel) == expected, rel
    model = next((SOURCE / 'data/results/Dataset572_TopAneu_Vessel_36fgCls_wLRSwap').glob(args.model + '*'))
    ckpt = model / 'fold_4/checkpoint_final.pth'
    # Official hash-verified checkpoint includes optimizer defaultdict metadata
    # that PyTorch's restricted loader cannot reconstruct.
    ck = torch.load(ckpt, map_location='cpu', weights_only=False)
    pm = PlansManager(json.loads((model / 'plans.json').read_text()))
    cm = pm.get_configuration(ck['init_args']['configuration'])
    dataset = json.loads((model / 'dataset.json').read_text())
    assert ck['trainer_name'] == 'Tr_rot30_Mirror01_DiffClusterSM_TopK_ceW_EnvCfg'
    # This released trainer inherits the standard static architecture builder;
    # its training-only feature decoder has identical inference tensors.
    network = get_network_from_plans(cm.network_arch_class_name, cm.network_arch_init_kwargs,
        cm.network_arch_init_kwargs_req_import, 1, pm.get_label_manager(dataset).num_segmentation_heads,
        allow_init=False, deep_supervision=False)
    network.load_state_dict(ck['network_weights'], strict=True)
    torch.set_num_threads(4)
    assert torch.backends.mps.is_available(), 'Run with local GPU access'
    predictor = nnUNetPredictor(tile_step_size=.5, use_gaussian=True, use_mirroring=True,
        perform_everything_on_device=False, device=torch.device('mps'), allow_tqdm=True,
        verbose=True, verbose_preprocessing=True)
    predictor.manual_initialization(network, pm, cm, [ck['network_weights']], dataset,
        ck['trainer_name'], ck['inference_allowed_mirroring_axes'])
    out = BASE / f'predictions-{args.model.lower()}-v1'
    out.mkdir(exist_ok=True)
    data = BASE / 'sources/TopBrain_Data_Release_Batches1n2nTA36_081726/imagesTr_topbrain'
    prior_path = out / 'prediction-receipt.json'
    prior = json.loads(prior_path.read_text()) if prior_path.exists() else None
    if prior:
        assert prior['checkpoint_sha256'] == sha(ckpt)
        for r in prior['rows']:
            assert sha(out / f'topcow_mr_{r["case"]}.nii.gz') == r['output_sha256']
    rows = prior['rows'] if prior else []
    for case in args.cases:
        p = data / f'topcow_mr_{case}_0000.nii.gz'
        dst = out / f'topcow_mr_{case}.nii.gz'
        assert not dst.exists(), 'Never overwrite a prediction'
        ni = nib.load(p)
        assert nib.aff2axcodes(ni.affine) == ('L', 'P', 'S')
        image = np.asarray(ni.dataobj, dtype=np.float32)
        start = time.monotonic()
        print('START', case, image.shape, flush=True)
        with torch.inference_mode():
            result = predictor.predict_single_npy_array(image.transpose(2, 1, 0)[None],
                {'spacing': list(map(float, ni.header.get_zooms()[:3][::-1]))})
        pred = np.asarray(result).transpose(2, 1, 0).astype(np.uint8)
        assert pred.shape == ni.shape and pred.max() <= 36
        nib.save(nib.Nifti1Image(pred, ni.affine, ni.header), dst)
        rows.append({'case': case, 'input_sha256': sha(p), 'output_sha256': sha(dst),
            'shape': list(ni.shape), 'seconds': round(time.monotonic() - start, 2),
            'labels': np.unique(pred).tolist()})
        evidence = {'method': 'Official TA36 ResEncM/plain-conv single released component, fold 4',
            'model_directory': model.name, 'checkpoint_sha256': sha(ckpt),
            'official_three_model_ensemble': False, 'official_postprocessing': False,
            'reference_used_for_inference': False, 'synthetic_errors': False,
            'source_manifest_sha256': sha(BASE / 'ta36-source-manifest.json'),
            'device': 'mps', 'precision': 'float32 network; released predictor accumulation',
            'tile_step_size': .5, 'gaussian_blending': True,
            'checkpoint_mirroring_axes': ck['inference_allowed_mirroring_axes'],
            'environment': {n: importlib.metadata.version(n) for n in ['torch', 'numpy', 'scipy', 'dynamic-network-architectures']},
            'training_overlap': 'Public development scans; no unseen-patient generalization claim.', 'rows': rows}
        (out / 'prediction-receipt.json').write_text(json.dumps(evidence, indent=2) + '\n')
        print('DONE', rows[-1], flush=True)


if __name__ == '__main__':
    main()
