#!/usr/bin/env python3
"""Open the report with local full-resolution scan exploration. No dependencies.

Only the bundled report and the six named scan arrays are served, on loopback.
The existing archive is read in place. No trials, downloads, or rebuilds run.
"""
import argparse
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
from urllib.parse import urlsplit
from urllib.request import urlopen
import webbrowser

import build_site

ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOT = ROOT / 'runs/br016-aneurysm/blind-review'


def scan_files(root=SCAN_ROOT):
    figures = json.loads((ROOT / 'site/aneurysm-figures.json').read_text())
    files = {}
    available = []
    for case in figures['cases'].values():
        case_id = case['source_id']
        size = 4
        for dimension in case['shape']:
            size *= dimension
        pair = {f'/local-data/{case_id}/{kind}.bin': root / case_id / f'{kind}.bin'
                for kind in ('brain', 'original')}
        if all(path.is_file() and path.stat().st_size == size for path in pair.values()):
            available.append(case_id)
            files.update(pair)
    return available, files


class ReportHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, report, files, **kwargs):
        self.report, self.files = report, files
        super().__init__(*args, **kwargs)

    def do_HEAD(self):
        self.respond(head=True)

    def do_GET(self):
        self.respond()

    def respond(self, head=False):
        route = urlsplit(self.path).path
        source = self.files.get(route)
        if route in ('/', '/index.html', '/site/index.html'):
            body = self.report() if callable(self.report) else self.report
            kind = 'text/html; charset=utf-8'
        elif route == '/health':
            body = json.dumps({'app': 'tb3-local-report', 'root': str(ROOT)}).encode()
            kind = 'application/json'
        elif source is not None and source.is_file():
            body, kind = None, 'application/octet-stream'
        else:
            self.send_error(404, 'This file is not part of the local report.')
            return
        self.send_response(200)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(body) if body is not None else source.stat().st_size))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        if head:
            return
        try:
            if body is not None:
                self.wfile.write(body)
            else:
                with source.open('rb') as stream:
                    shutil.copyfileobj(stream, self.wfile, length=1024 * 1024)
        except (BrokenPipeError, ConnectionResetError):
            pass  # Closing a page or switching cases may cancel a large fetch.


def make_server(port, scan_root=SCAN_ROOT):
    available, files = scan_files(scan_root)
    # Read authored presentation changes on refresh, without rebuilding evidence.
    report = lambda: build_site.build({'base': '/local-data/', 'cases': available}).encode()
    handler = partial(ReportHandler, report=report, files=files)
    server = ThreadingHTTPServer(('127.0.0.1', port), handler)
    server.daemon_threads = True
    return server, available


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8768)
    parser.add_argument('--open', action='store_true', help='Open the report in your default browser.')
    args = parser.parse_args()
    url = f'http://127.0.0.1:{args.port}/'
    try:
        server, available = make_server(args.port)
    except OSError as error:
        try:
            with urlopen(url + 'health', timeout=1) as response:
                existing = json.load(response)
            if existing == {'app': 'tb3-local-report', 'root': str(ROOT)}:
                print(f'Your local report is already running: {url}')
                if args.open:
                    webbrowser.open(url)
                return
        except (OSError, ValueError):
            pass
        parser.exit(1, f'Cannot use port {args.port}: {error}. Try --port 8769.\n')
    print(f'Local report: {url}', flush=True)
    print(f'Full scan explorer: {len(available)}/3 cases available. Ctrl+C stops the server.', flush=True)
    if len(available) < 3:
        print(f'Restore missing scan pairs under {SCAN_ROOT}; guided views work without them.', flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nLocal report stopped. Run make site to return.')
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
