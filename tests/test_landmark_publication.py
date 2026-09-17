"""Publication integrity checks using retained receipts, without native scans."""
import base64
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LandmarkPublicationTests(unittest.TestCase):
    def test_exact_panels_complete_tables_and_evidence_hashes(self):
        figures = json.loads((ROOT / 'site/landmark-figures.json').read_text())
        provenance = json.loads((ROOT / 'site/landmark-provenance.json').read_text())
        self.assertEqual([c['case'] for c in figures], ['ct-full', 'ct-partial', 'mri32-full'])
        self.assertEqual([c['html'].count('<tr>') - 1 for c in figures], [26, 26, 32])
        self.assertEqual(sum(len(c['images']) for c in figures), 7)
        for case in figures:
            options = re.findall(r'<option value="([^"]+)"', case['html'])
            self.assertEqual(set(options), set(case['images']))
            for name, uri in case['images'].items():
                data = base64.b64decode(uri.split(',', 1)[1], validate=True)
                self.assertTrue(data.startswith(b'\x89PNG\r\n\x1a\n'))
                source = 'runs/br040-sol-landmarks/review/' + name
                self.assertEqual(hashlib.sha256(data).hexdigest(), provenance['evidence'][source])
        for path, digest in provenance['evidence'].items():
            if not path.startswith('runs/'):
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)

    def test_summary_endpoints_match_retained_scores(self):
        trials = json.loads((ROOT / 'docs/evidence/br040-results.json').read_text())['trials']
        expected = {
            ('ct-full', 'terra-high'): [2, 7, 9],
            ('ct-full', 'sol-xhigh'): [1, 13, 23],
            ('ct-partial', 'terra-high'): [1, 2, 5],
            ('ct-partial', 'sol-xhigh'): [4, 8, 12],
            ('mri32-full', 'terra-high'): [3, 8, 20],
            ('mri32-full', 'sol-xhigh'): [14, 23, 32],
        }
        chapter = (ROOT / 'site/content/landmarks.html').read_text()
        for trial in trials:
            thresholds = [3, 5, 10] if trial['case'].startswith('mri') else [5, 10, 20]
            counts = [trial['success_counts_mm'][str(t)] for t in thresholds]
            self.assertEqual(counts, expected[trial['case'], trial['model_setting']])
            self.assertIn(' / '.join(map(str, counts)) + ' at ' + ' / '.join(map(str, thresholds)), chapter)
            self.assertIsNone(trial['exception'])
            self.assertTrue(trial['host_replay_exact'])
