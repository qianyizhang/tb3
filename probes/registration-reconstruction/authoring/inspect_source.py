"""Author-only DICOM geometry audit and native HU conversion."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pydicom
from scipy.ndimage import gaussian_filter
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'runs/br020-registration'


def main():
    receipt = json.loads((OUT/'source/source-receipt.json').read_text())
    volumes = {}; datasets = {}; records = {}
    common = ['PatientID', 'StudyInstanceUID', 'FrameOfReferenceUID', 'AcquisitionNumber',
              'KVP', 'ExposureTime', 'XRayTubeCurrent', 'Exposure', 'GantryDetectorTilt',
              'SliceThickness', 'ReconstructionDiameter']
    for series in receipt['series']:
        kernel = series['kernel']
        for item in series['files']:
            assert hashlib.sha256((OUT/'source'/item['path']).read_bytes()).hexdigest() == item['sha256']
        ds = [pydicom.dcmread(p) for p in (OUT/'source'/kernel).glob('*.dcm')]
        assert len(ds) == 139
        orientation = np.array(ds[0].ImageOrientationPatient, dtype=float)
        normal = np.cross(orientation[:3], orientation[3:])
        ds.sort(key=lambda d: float(np.dot(d.ImagePositionPatient, normal)))
        positions = np.array([d.ImagePositionPatient for d in ds], dtype=float)
        step = np.diff(positions, axis=0)
        assert np.allclose(step, step[0], atol=1e-6)
        for d in ds:
            assert d.ConvolutionKernel == kernel
            assert np.allclose(d.ImageOrientationPatient, orientation)
            assert np.allclose(d.PixelSpacing, ds[0].PixelSpacing)
            for key in common:
                assert str(d.get(key, '')) == str(ds[0].get(key, ''))
        a = np.eye(4)
        a[:3,0] = orientation[:3] * float(ds[0].PixelSpacing[1])
        a[:3,1] = orientation[3:] * float(ds[0].PixelSpacing[0])
        a[:3,2] = step[0]; a[:3,3] = positions[0]
        hu = np.stack([(d.pixel_array.astype(np.int32)*float(d.RescaleSlope)+float(d.RescaleIntercept)).T for d in ds], axis=2)
        assert hu.min() >= -32768 and hu.max() <= 32767
        hu = hu.astype(np.int16)
        volumes[kernel] = hu; datasets[kernel] = ds
        records[kernel] = {'series_uid': series['series_uid'], 'shape': list(hu.shape),
                           'voxel_to_lps': a.tolist(), 'kernel': kernel,
                           'fields': {key: str(ds[0].get(key, '')) for key in common},
                           'missing_time_fields': [key for key in ['AcquisitionDate','AcquisitionTime','SeriesTime'] if not ds[0].get(key)]}
        np.savez_compressed(OUT/'source'/f'{kernel}.npz', hu=hu, voxel_to_lps=a)
    assert records['B30f']['fields'] == records['B50f']['fields']
    assert records['B30f']['voxel_to_lps'] == records['B50f']['voxel_to_lps']
    for d,e in zip(datasets['B30f'],datasets['B50f']):
        assert np.array_equal(d.ImagePositionPatient, e.ImagePositionPatient)
    a = volumes['B30f']; b = volumes['B50f']
    # Identical coordinates, with differences dominated by spatial frequency.
    raw_a = a[::2,::2,:].astype(float); raw_b = b[::2,::2,:].astype(float)
    smooth_a = gaussian_filter(raw_a, 1.5); smooth_b = gaussian_filter(raw_b, 1.5)
    audit = {'series': records, 'slice_positions_equal': 139,
             'unblurred_hu_rmse': float(np.sqrt(np.mean((raw_a-raw_b)**2))),
             'blurred_hu_rmse': float(np.sqrt(np.mean((smooth_a-smooth_b)**2))),
             'blurred_hu_correlation': float(np.corrcoef(smooth_a.ravel(),smooth_b.ravel())[0,1]),
             'acquisition_evidence': 'Same patient, study, frame, acquisition number, exposure fields and every slice coordinate; different B30f/B50f kernels.',
             'limitation': 'Acquisition date/time are removed. Common projection acquisition is strongly supported, not independently proven from raw projection identifiers.'}
    (OUT/'author').mkdir(exist_ok=True)
    (OUT/'author/source-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    sheet = Image.new('RGB',(5*320,2*345),(18,22,28)); draw = ImageDraw.Draw(sheet)
    for i,k in enumerate([15,30,45,60,75,90,105,120]):
        tile=Image.fromarray(np.rint(np.clip((a[:,:,k].T+150)/500,0,1)*255).astype(np.uint8)).resize((320,320))
        x=(i%5)*320; y=(i//5)*345;sheet.paste(tile,(x,y));draw.text((x+8,y+322),f'B30f axial k={k}, z={records["B30f"]["voxel_to_lps"][2][3]+2*k:.1f} mm',fill='white')
    for n,(label,data) in enumerate([('coronal j=235',a[:,235,::-1].T),('sagittal i=285',a[285,:,::-1].T)],8):
        img=Image.fromarray(np.rint(np.clip((data+150)/500,0,1)*255).astype(np.uint8)).resize((320,250))
        x=(n%5)*320;y=(n//5)*345;sheet.paste(img,(x,y));draw.text((x+8,y+322),label,fill='white')
    sheet.save(OUT/'author/source-montage.png')
    print(json.dumps({key:audit[key] for key in audit if key!='series'},indent=2))


if __name__=='__main__':main()
