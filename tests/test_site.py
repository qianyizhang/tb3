"""Publication regressions: portable assets, valid routes and a reproducible bundle."""
import importlib.util
import io
import json
from html.parser import HTMLParser
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('build_site',ROOT/'scripts/build_site.py')
site=importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)
server_spec=importlib.util.spec_from_file_location('serve_site',ROOT/'scripts/serve_site.py')
server=importlib.util.module_from_spec(server_spec)
with patch.dict(sys.modules,{'build_site':site}):
    server_spec.loader.exec_module(server)


class Document(HTMLParser):
    def __init__(self,text):
        super().__init__()
        self.refs=[]
        self.ids=set()
        self.feed(text)

    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.add(attrs['id'])
        for attr in ('href','src'):
            if attr in attrs:self.refs.append((tag,attr,attrs[attr]))


class PublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents={key:Document(html) for key,html in site.load_chapters().items()}

    def test_committed_page_matches_tracked_sources(self):
        self.assertEqual((ROOT/'site/index.html').read_text(),site.build())

    def test_chapters_need_no_network_or_runtime_assets(self):
        for key,doc in self.documents.items():
            for tag,attr,value in doc.refs:
                with self.subTest(chapter=key,tag=tag,attribute=attr):
                    if attr=='src':
                        self.assertTrue(value.startswith('data:image/'),value[:120])
                    else:
                        self.assertTrue(value.startswith(('#','https:','data:image/')),value[:120])

    def test_internal_routes_and_repository_evidence_exist(self):
        for key,doc in self.documents.items():
            for _,attr,value in doc.refs:
                if attr!='href':continue
                with self.subTest(chapter=key,link=value[:150]):
                    if value.startswith('#study='):
                        chapter,_,anchor=value[7:].partition('/')
                        self.assertIn(chapter,self.documents)
                        if anchor:self.assertIn(anchor,self.documents[chapter].ids)
                    elif value.startswith('#') and value!='#':
                        self.assertIn(value[1:],doc.ids)
                    elif value.startswith('https://github.com/qianyizhang/tb3/blob/main/'):
                        path=unquote(urlsplit(value).path.split('/blob/main/',1)[1])
                        self.assertTrue((ROOT/path).is_file(),path)

    def test_publication_keeps_native_scan_loading_opt_in(self):
        chapter=site.load_chapters()['aneurysm']
        self.assertIn('<script id="local-scans" type="application/json">null</script>',chapter)
        self.assertNotIn('__SCAN_FIGURES__',chapter)
        local=site.load_chapters({'base':'/local-data/','cases':['R02']})['aneurysm']
        self.assertIn('"cases": ["R02"]',local)
        self.assertIn('data-explore class="primary" hidden',chapter)

    def test_guided_views_keep_native_geometry_and_reference_mapping(self):
        figures=json.loads((ROOT/'site/aneurysm-figures.json').read_text())['cases']
        self.assertEqual({key:value['source_id'] for key,value in figures.items()},
                         {'n01':'R02','n02':'R03','n03':'R01'})
        self.assertEqual(figures['n01']['reference']['center'],[166,273,84])
        self.assertEqual(figures['n02']['answer'],[312,213,94])
        self.assertIsNone(figures['n03']['reference'])
        for case in figures.values():
            for plane in case['planes']:
                axis=plane['axis'];rem=[d for d in range(3) if d!=axis]
                self.assertEqual(plane['range'],[case['center'][axis]-3,case['center'][axis]+3])
                self.assertAlmostEqual(plane['aspect'],plane['width']*case['spacing'][rem[0]]/(plane['height']*case['spacing'][rem[1]]))
                for d,offset,width in zip(rem,plane['offset'],[plane['width'],plane['height']]):
                    self.assertLessEqual(offset,case['center'][d])
                    self.assertLess(case['center'][d],offset+width)
                    self.assertLessEqual(offset+width,case['shape'][d])


class LocalReportTests(unittest.TestCase):
    def test_missing_or_incomplete_arrays_leave_portable_report_available(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            self.assertEqual(server.scan_files(root),([],{}))
            case=root/'R02';case.mkdir()
            size=350*448*144*4
            for name in ('brain','original'):
                with (case/f'{name}.bin').open('wb') as stream:
                    stream.truncate(size)
            available,files=server.scan_files(root)
            self.assertEqual(available,['R02'])
            self.assertEqual(set(files),{'/local-data/R02/brain.bin','/local-data/R02/original.bin'})
            (case/'original.bin').write_bytes(b'incomplete')
            self.assertEqual(server.scan_files(root),([],{}))

    def test_server_serves_only_report_and_explicit_scan_files(self):
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'scan.bin';source.write_bytes(b'native scan bytes')
            handler=object.__new__(server.ReportHandler)
            handler.report=b'complete offline report';handler.files={'/local-data/R02/brain.bin':source}
            handler.send_header=lambda *args:None
            handler.end_headers=lambda:None
            codes=[]
            handler.send_response=lambda status:codes.append(status)
            handler.send_error=lambda status,message:codes.append(status)
            for path,expected in [('/',handler.report),('/site/index.html',handler.report),
                                  ('/local-data/R02/brain.bin',b'native scan bytes'),
                                  ('/local-data/R02/../references.json',b''),('/runs/',b'')]:
                handler.path=path;handler.wfile=io.BytesIO();handler.respond()
                self.assertEqual(handler.wfile.getvalue(),expected)
                self.assertEqual(codes[-1],200 if expected else 404)
            handler.path='/local-data/R02/brain.bin';handler.wfile=io.BytesIO();handler.respond(head=True)
            self.assertEqual(handler.wfile.getvalue(),b'')


if __name__=='__main__':
    unittest.main()
