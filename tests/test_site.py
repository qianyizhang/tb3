"""Publication regressions: portable assets, valid routes and a reproducible bundle."""
import importlib.util
from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('build_site',ROOT/'scripts/build_site.py')
site=importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


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
        cls.documents={key:Document((ROOT/'site/content'/f'{key}.html').read_text()) for key in site.CHAPTERS}

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


if __name__=='__main__':
    unittest.main()
