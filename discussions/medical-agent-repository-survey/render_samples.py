"""Render local survey examples; no network, model execution, or benchmark scoring.

Run with the existing imaging environment:
  .venv-br030/bin/python discussions/medical-agent-repository-survey/render_samples.py
Inputs and their download receipts live in runs/task-brief-samples/.
"""
from pathlib import Path
import hashlib
import io
import json
import os
import zipfile

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'runs/task-brief-samples'
os.environ.setdefault('MPLCONFIGDIR', str(DATA / 'matplotlib-cache'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pydicom
from scipy.ndimage import binary_erosion
import SimpleITK as sitk

OUT = ROOT / 'presentation/tours/data/task-briefs'
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'figure.facecolor': '#101a28', 'axes.facecolor': '#101a28',
                     'text.color': '#e6edf7', 'axes.labelcolor': '#c5d4e5',
                     'xtick.color': '#c5d4e5', 'ytick.color': '#c5d4e5',
                     'font.size': 12, 'savefig.facecolor': '#101a28'})
RECEIPTS = []


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finish(fig, name, details):
    path = OUT / (name + '.png')
    fig.savefig(path, dpi=140, bbox_inches='tight', pad_inches=.18)
    plt.close(fig)
    RECEIPTS.append({'path': str(path.relative_to(ROOT)), 'sha256': digest(path), **details})


def panel(ax, array, title, *, aspect=1, low=None, high=None):
    ax.imshow(array, cmap='gray', vmin=low, vmax=high, aspect=aspect, interpolation='nearest')
    ax.set_title(title, fontsize=13, pad=12)
    ax.set_axis_off()


def border(ax, mask, color='#ffd166'):
    edge = mask.astype(bool) & ~binary_erosion(mask.astype(bool))
    rgba = np.zeros((*edge.shape, 4))
    rgba[edge] = matplotlib.colors.to_rgba(color)
    ax.imshow(rgba, interpolation='nearest', aspect=ax.get_aspect())


def imaging():
    base = DATA / 'imaging101/tasks/ct_sparse_view'
    raw = np.load(base / 'data/raw_data.npz', allow_pickle=False)
    gt = np.load(base / 'data/ground_truth.npz', allow_pickle=False)['phantom'][0]
    ref = np.load(base / 'evaluation/reference_outputs/reconstructions.npz', allow_pickle=False)
    fig, ax = plt.subplots(figsize=(6.6, 5.3))
    ax.imshow(raw['sinogram_sparse'][0], cmap='gray', aspect='auto',
              extent=[float(raw['angles_sparse'].min()), float(raw['angles_sparse'].max()), 255, 0])
    ax.set(xlabel='Projection angle (degrees)', ylabel='Detector index',
           title='Actual supplied measurements: 256 detectors × 30 angles')
    finish(fig, 'imaging101-input', {'role': 'input', 'shape': [256, 30], 'synthetic': True})
    fig, axs = plt.subplots(1, 3, figsize=(12, 4.6))
    for ax, array, title in zip(axs, [gt, ref['fbp_sparse'][0], ref['tv_recon'][0]],
                                 ['Ground-truth phantom', 'Published sparse-view FBP', 'Published TV reconstruction']):
        panel(ax, array, title, low=0, high=1)
    fig.text(.5, .025, 'Repository reference arrays · common display scale [0, 1] · not new agent results', ha='center', color='#bacade')
    finish(fig, 'imaging101-reference', {'role': 'reference and published algorithm outputs',
                                       'window': [0, 1], 'model_run': False})


def abra():
    z = zipfile.ZipFile(DATA / 'abra/seg.zip')
    seg = pydicom.dcmread(io.BytesIO(z.read('00000001.dcm')))
    masks = seg.pixel_array
    frame = int(np.argmax(masks.sum((1, 2))))
    group = seg.PerFrameFunctionalGroupsSequence[frame]
    sop = str(group.DerivationImageSequence[0].SourceImageSequence[0].ReferencedSOPInstanceUID)
    z = zipfile.ZipFile(DATA / 'abra/ct.zip')
    cts = [pydicom.dcmread(io.BytesIO(z.read(n))) for n in z.namelist() if n.endswith('.dcm')]
    cts.sort(key=lambda d: float(d.ImagePositionPatient[2]))
    index = next(i for i, d in enumerate(cts) if str(d.SOPInstanceUID) == sop)
    ct = cts[index]
    assert str(ct.SeriesInstanceUID) == str(seg.ReferencedSeriesSequence[0].SeriesInstanceUID)
    assert np.allclose(ct.ImagePositionPatient, group.PlanePositionSequence[0].ImagePositionPatient)
    assert np.allclose(ct.ImageOrientationPatient, seg.SharedFunctionalGroupsSequence[0].PlaneOrientationSequence[0].ImageOrientationPatient)
    assert np.allclose(ct.PixelSpacing, seg.SharedFunctionalGroupsSequence[0].PixelMeasuresSequence[0].PixelSpacing)
    hu = ct.pixel_array.astype(float) * float(ct.RescaleSlope) + float(ct.RescaleIntercept)
    mask = masks[frame].astype(bool)
    aspect = float(ct.PixelSpacing[0]) / float(ct.PixelSpacing[1])
    details = {'case_id': 'LIDC-IDRI-0003', 'series_uid': str(ct.SeriesInstanceUID), 'sop_instance_uid': sop,
               'slice_index_ascending_z_zero_based': index, 'position_lps_mm': list(map(float, ct.ImagePositionPatient)),
               'segment_label': str(seg.SegmentSequence[0].SegmentLabel), 'selected_frame': frame,
               'selection': 'largest area of this source annotation, post hoc reader selection',
               'window_width': 1500, 'window_center': -600, 'reference_pixels': int(mask.sum()),
               'reference_scope': 'one source DICOM SEG annotation; not a regenerated ABRA consensus task',
               'alignment_checks': ['source SOP UID', 'series UID', 'image position', 'orientation', 'pixel spacing']}
    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    panel(ax, hu, f'LIDC-IDRI-0003 · slice {index} · lung window', aspect=aspect, low=-1350, high=150)
    finish(fig, 'abra-input', {**details, 'role': 'input, no contour or target crop'})
    ys, xs = np.where(mask)
    y, x = int(np.round(ys.mean())), int(np.round(xs.mean()))
    crop = (slice(max(0, y-55), min(512, y+56)), slice(max(0, x-55), min(512, x+56)))
    fig, axs = plt.subplots(1, 2, figsize=(10.2, 5.8))
    panel(axs[0], hu, 'Reference annotation on the full CT slice', aspect=aspect, low=-1350, high=150)
    border(axs[0], mask)
    panel(axs[1], hu[crop], 'Reader-only crop around the reference', aspect=aspect, low=-1350, high=150)
    border(axs[1], mask[crop])
    fig.text(.5, .045, 'Gold outline = released annotation · no agent prediction · crop chosen using reference', ha='center', fontsize=11)
    finish(fig, 'abra-reference', {**details, 'role': 'reference', 'crop_xyxy': [crop[1].start, crop[0].start, crop[1].stop, crop[0].stop]})


def automed():
    image = nib.load(DATA / 'automed/ct.nii.gz')
    a = image.get_fdata(dtype=np.float32)
    names = ['kidney_left', 'kidney_right', 'liver', 'spleen', 'aorta']
    colors = ['#ffd166', '#f8961e', '#ed6a85', '#56cfe1', '#b494ff']
    masks = []
    for name in names:
        m = nib.load(DATA / f'automed/{name}.nii.gz')
        assert m.shape == image.shape and np.allclose(m.affine, image.affine)
        masks.append(m.get_fdata(dtype=np.float32) > 0)
    # Coronal plane through the largest combined kidney cross-section.
    y = int(np.argmax((masks[0] | masks[1]).sum((0, 2))))
    plane = np.flipud(a[:, y, :].T)
    aspect = float(image.header.get_zooms()[2] / image.header.get_zooms()[0])
    details = {'case_id': 'TSG_00000001', 'upstream_id': 's1366', 'plane': 'coronal', 'y_index': y,
               'selection': 'post hoc plane selected using the two kidney references', 'window_hu': [-160, 240],
               'orientation': 'RAS+ array; R increases rightward, S upward', 'shape': list(a.shape),
               'shown_classes': names, 'scope': 'five reference masks from the 117-class task; 78 classes present in source case'}
    for role in ['input', 'reference']:
        fig, ax = plt.subplots(figsize=(7.2, 7.2))
        panel(ax, plane, 'AutoMedBench · TSG_00000001 · coronal CT', aspect=aspect, low=-160, high=240)
        if role == 'reference':
            for m, color in zip(masks, colors):
                border(ax, np.flipud(m[:, y, :].T), color)
            from matplotlib.lines import Line2D
            ax.legend([Line2D([0], [0], color=c, lw=3) for c in colors], [n.replace('_', ' ') for n in names],
                      loc='lower center', ncol=2, facecolor='#101a28', labelcolor='white', fontsize=10)
        finish(fig, 'automed-tsg-' + role, {**details, 'role': role, 'agent_prediction': False})


def rexmle():
    base = ROOT / 'runs/br030-vessel-geometry/sources/TopCoW2024_Data_Release'
    image = nib.as_closest_canonical(nib.load(base / 'imagesTr/topcow_ct_012_0000.nii.gz'))
    mask = nib.as_closest_canonical(nib.load(base / 'cow_seg_labelsTr/topcow_ct_012.nii.gz'))
    assert image.shape == mask.shape and np.allclose(image.affine, mask.affine)
    a = image.get_fdata(dtype=np.float32); m = mask.get_fdata(dtype=np.float32)
    z = int(np.argmax((m > 0).sum((0, 1))))
    aspect = float(image.header.get_zooms()[1] / image.header.get_zooms()[0])
    details = {'case_id': 'topcow_ct_012', 'release': 'TopCoW2024_Data_Release',
               'plane': 'axial', 'z_indices': [z-10, z, z+10], 'orientation': 'canonical RAS+; R increases rightward, A upward',
               'selection': 'middle plane maximizes reference cross-section; adjacent planes at +/- 5 mm',
               'window_hu': [0, 600], 'scope': 'upstream training example; membership in the prepared ReX-MLE split not verified'}
    cmap = plt.get_cmap('tab20')
    for role in ['input', 'helpers']:
        fig, axs = plt.subplots(1, 3, figsize=(11.4, 6.2))
        for ax, zz in zip(axs, details['z_indices']):
            panel(ax, np.flipud(a[:, :, zz].T), f'Axial plane {zz}', aspect=aspect, low=0, high=600)
            if role == 'helpers':
                mm = np.flipud(m[:, :, zz].T).astype(int)
                rgba = cmap(mm / 20); rgba[..., 3] = (mm > 0) * .8
                ax.imshow(rgba, aspect=aspect, interpolation='nearest')
        fig.text(.5, .075, 'TopCoW CT 012 · input already braincase-cropped by the source release', ha='center', fontsize=11)
        if role == 'helpers':
            fig.text(.5, .03, 'Colors distinguish supplied vessel class IDs · training labels, not test answers or an agent result', ha='center', fontsize=10)
        finish(fig, 'rexmle-' + role, {**details, 'role': role})


def bcer():
    modalities = ['t2w', 'adc', 'hbv']
    images = [sitk.ReadImage(str(DATA / f'bcer/10001_1000001_{m}.mha')) for m in modalities]
    t2 = images[0]; p = t2.TransformIndexToPhysicalPoint(tuple(int(s//2) for s in t2.GetSize()))
    fig, axs = plt.subplots(1, 3, figsize=(12, 5))
    details = []
    for ax, im, mod, title in zip(axs, images, modalities, ['T2-weighted: anatomy', 'ADC: diffusion map', 'High-b DWI: diffusion contrast']):
        idx = im.TransformPhysicalPointToIndex(p); z = min(max(idx[2], 0), im.GetSize()[2]-1)
        a = sitk.GetArrayFromImage(im)[z]
        lo, hi = np.percentile(a, [1, 99.5])
        panel(ax, a, title, aspect=im.GetSpacing()[1]/im.GetSpacing()[0], low=lo, high=hi)
        ax.text(.5, -.04, f'{im.GetSize()[0]} × {im.GetSize()[1]} · {im.GetSize()[2]} slices', transform=ax.transAxes, ha='center', fontsize=10)
        # BCER accepts NIfTI; retain original MHA and convert geometry without registration.
        filename = {'t2w': 'T2w', 'adc': 'ADC', 'hbv': 'DWI_bhigh'}[mod]
        path = DATA / f'bcer/prepared/10001/{filename}.nii.gz';path.parent.mkdir(parents=True, exist_ok=True)
        sitk.WriteImage(im, str(path))
        details.append({'modality': mod, 'size_xyz': list(im.GetSize()), 'spacing_xyz_mm': list(im.GetSpacing()),
                        'origin_lps_mm': list(im.GetOrigin()), 'direction': list(im.GetDirection()), 'slice_index': z,
                        'display_percentiles': [1, 99.5], 'display_range': [float(lo), float(hi)],
                        'nifti_path': str(path.relative_to(ROOT)), 'nifti_sha256': digest(path)})
    fig.text(.5, .025, 'PI-CAI 10001 · nearest native planes to one physical point · not registered or processed by BCER', ha='center', fontsize=11)
    finish(fig, 'bcer-input', {'role': 'representative compatible input', 'case_id': '10001_1000001',
                              'selection': 'T2 volume center, corresponding physical point in other sequences', 'modalities': details})
    manifest = {'case_id': 'prostate__10001', 'domain': 'prostate',
                'case_root': str(DATA / 'bcer/prepared/10001'), 'input_format': 'nifti',
                'modalities': {'t2w': True, 'adc': True, 'dwi': True, 't1c': False},
                'supports_tasks': ['short_denoise', 'short_superres', 'medium_register_prostate', 'long_prostate_full']}
    (DATA / 'bcer/cases_manifest.jsonl').write_text(json.dumps(manifest) + '\n')


if __name__ == '__main__':
    imaging(); abra(); automed(); rexmle(); bcer()
    (DATA / 'rendered.json').write_text(json.dumps(RECEIPTS, indent=2) + '\n')
    print(json.dumps({'figures': len(RECEIPTS), 'output': str(OUT)}, indent=2))
