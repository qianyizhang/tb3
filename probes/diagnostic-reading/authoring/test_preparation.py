import json
from pathlib import Path
import tempfile
import unittest

import nibabel as nib
import numpy as np

from inspect_ct import bounds, render, sample, window
from prepare import prepare


class PreparationTests(unittest.TestCase):
    def test_physical_coordinate_sampling(self):
        data = np.zeros((3, 4, 5), dtype=np.float32)
        data[1, 2, 3] = 700
        # Permuted and flipped axes with unequal spacing and translation.
        affine = np.array([[0, -3, 0, 20], [2, 0, 0, -5],
                           [0, 0, 4, 8], [0, 0, 0, 1]], dtype=float)
        ras = nib.affines.apply_affine(affine, [1, 2, 3])
        self.assertEqual(float(sample(data, affine, np.array([ras]))[0]), 700)
        lo, hi = bounds(data.shape, affine)
        np.testing.assert_array_equal(lo, [11, -5, 8])
        np.testing.assert_array_equal(hi, [20, -1, 24])
        self.assertEqual(float(sample(data, affine, np.array([[999, 0, 0]]))[0]), -1024)

    def test_orientation_and_window(self):
        data = np.zeros((101, 101, 3), dtype=np.float32)
        data[65:80, 65:80, :] = 100
        image = np.asarray(render(data, np.eye(4), 'axial', 1, 50, 100, 201))
        # Positive RAS x/y must appear at upper left in radiological axial view.
        self.assertGreater(image[55, 55, 0], 240)
        self.assertEqual(image[145, 145, 0], 0)
        np.testing.assert_array_equal(window(np.array([-100, 0, 100]), 0, 200),
                                      [0, 127, 255])
        with self.assertRaises(ValueError):
            render(data, np.eye(4), 'axial', 99, 50, 100, 201)

    def test_packet_separation_and_admission(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / 'secret-subject.nii.gz'
            nib.save(nib.Nifti1Image(np.zeros((3, 4, 5)), np.eye(4)), image)
            report = root / 'report.txt'
            report.write_text('HIDDEN_REFERENCE_SENTINEL')
            case = {'case_id': 'C001', 'patient_key': 'secret-subject',
                    'source_url': 'https://example.invalid/synthetic-test',
                    'source_revision': 'synthetic-v1',
                    'reference_kind': 'clinical_radiologist_report',
                    'report_path': str(report), 'images': [{'path': str(image)}],
                    'context': {'indication': 'synthetic fixture'},
                    'technical_review_complete': True,
                    'solver_metadata_review_complete': True,
                    'rights_review_complete': True}
            manifest = root / 'manifest.json'
            manifest.write_text(json.dumps([case]))
            out = root / 'pack'
            prepare(manifest, out)
            public = out / 'solver/C001'
            self.assertTrue((public / 'image-01.nii.gz').exists())
            for path in public.iterdir():
                self.assertNotIn(b'HIDDEN_REFERENCE_SENTINEL', path.read_bytes())
                self.assertNotIn('secret-subject', path.name)
            self.assertEqual((out / 'reference/C001-report.txt').read_text(),
                             'HIDDEN_REFERENCE_SENTINEL')
            with self.assertRaises(FileExistsError):
                prepare(manifest, out)
            case2 = {**case, 'case_id': 'C002'}
            manifest.write_text(json.dumps([case, case2]))
            with self.assertRaisesRegex(ValueError, 'patient'):
                prepare(manifest, root / 'duplicate')
            case['technical_review_complete'] = False
            manifest.write_text(json.dumps([case]))
            with self.assertRaisesRegex(ValueError, 'review'):
                prepare(manifest, root / 'unreviewed')


if __name__ == '__main__':
    unittest.main()
