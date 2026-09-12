#!/usr/bin/env python3
"""Index local TB3 trials, curate ideas, and render an evidence-linked workbench."""
from __future__ import annotations

import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit

from tb3_catalog import core


ROOT = Path(__file__).resolve().parents[1]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ROOT, help="workspace root (default: this repository)")
    sub = p.add_subparsers(dest="command", required=True)
    sync = sub.add_parser("sync", help="idempotently import individual Harbor trials; never start a run")
    sync.add_argument("--runs", type=Path, default=Path("runs"), help="directory containing job/trial/result.json")
    listing = sub.add_parser("list", help="search catalog records")
    listing.add_argument("--kind", choices=("trials", "ideas"), default="trials")
    listing.add_argument("--query", default="", help="case-insensitive AND search over terms")
    listing.add_argument("--task")
    listing.add_argument("--status")
    listing.add_argument("--json", action="store_true")
    show = sub.add_parser("show", help="show one trial or idea as JSON")
    show.add_argument("id")
    add = sub.add_parser("idea-add", help="capture a candidate without claiming it is tested")
    add.add_argument("id")
    add.add_argument("--title", required=True)
    add.add_argument("--hypothesis", required=True)
    add.add_argument("--next-action", required=True)
    add.add_argument("--tag", action="append", default=[])
    add.add_argument("--source", action="append", default=[])
    curate = sub.add_parser("curate", help="update an authored idea; omitted fields are preserved")
    curate.add_argument("id")
    curate.add_argument("--status", choices=core.STATUSES)
    curate.add_argument("--next-action")
    curate.add_argument("--notes")
    curate.add_argument("--tag", action="append", help="replace tags with the provided repeated flags")
    review = sub.add_parser("review", help="append an evidence-bound analysis; does not certify qualification")
    review.add_argument("id")
    review.add_argument("--verdict", choices=core.VERDICTS, required=True)
    review.add_argument("--failure-mode", default="")
    review.add_argument("--explanation", required=True)
    review.add_argument("--next-action", required=True)
    review.add_argument("--evidence", action="append", required=True, help="existing workspace path; repeat as needed")
    for command in ("report", "serve"):
        report = sub.add_parser(command, help="render HTML" if command == "report" else "render and serve the report and linked evidence on loopback")
        report.add_argument("--output", type=Path, default=Path("runs/catalog/index.html"))
        if command == "serve":
            report.add_argument("--port", type=int, default=8766)
    return p


def allowed_paths(root: Path, data: dict, output: Path) -> set[Path]:
    paths = {output.resolve()}
    for idea in data["ideas"]:
        for path in idea.get("evidence", []):
            paths.add(core.workspace_path(root, path))
    for trial in data["trials"]:
        for item in trial["evidence"]:
            paths.add(core.workspace_path(root, item["path"]))
        for path in (trial.get("review") or {}).get("evidence", []):
            paths.add(core.workspace_path(root, path))
    return paths


class ReportHandler(SimpleHTTPRequestHandler):
    """Read-only server: no directory listing, dotfile browsing, or writes."""
    def __init__(self, *args, root: Path, output: Path, allowed: set[Path], **kwargs):
        self.root, self.output, self.allowed = root, output, allowed
        super().__init__(*args, directory=str(root), **kwargs)

    def send_head(self):
        path = unquote(urlsplit(self.path).path)
        if path == "/":
            self.send_response(302)
            self.send_header("Location", "/" + self.output.relative_to(self.root).as_posix())
            self.end_headers()
            return None
        try:
            resolved = core.workspace_path(self.root, path.lstrip("/"))
        except core.CatalogError:
            self.send_error(404)
            return None
        if resolved not in self.allowed or not resolved.is_file():
            self.send_error(404)
            return None
        return super().send_head()

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def guess_type(self, path):
        # Evidence is displayed as text, never as executable HTML/script.
        return "text/html; charset=utf-8" if Path(path).resolve() == self.output else "text/plain; charset=utf-8"

    def log_message(self, format, *args):
        pass


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "sync":
            result = core.sync(root, args.runs)
            print(json.dumps(result, indent=2))
            return 1 if result["errors"] else 0
        if args.command == "idea-add":
            result = core.add_idea(root, args.id, args.title, args.hypothesis, args.next_action, args.tag, args.source)
        elif args.command == "curate":
            result = core.curate(root, args.id, status=args.status, next_action=args.next_action, notes=args.notes, tags=args.tag)
        elif args.command == "review":
            result = core.review_trial(root, args.id, args.verdict, args.failure_mode, args.explanation, args.next_action, args.evidence)
        else:
            data = core.dataset(root)
            if args.command == "show":
                result = next((r for r in data["trials"] + data["ideas"] if r["id"] == args.id), None)
                if result is None:
                    raise core.CatalogError("unknown trial or idea ID")
            elif args.command == "list":
                result = core.search(data[args.kind], args.query, args.task, args.status)
                if not args.json:
                    for r in result:
                        print("\t".join(str(v) if v is not None else "—" for v in (r["id"], r.get("classification") or r.get("status"), r.get("model") or r.get("title"), r.get("reward"))))
                    print(f"{len(result)} {args.kind}")
                    return 0
            else:
                from tb3_catalog.view import render_report
                output = core.workspace_path(root, args.output)
                render_report(data, output, root)
                print(output, flush=True)
                if args.command == "serve":
                    handler = functools.partial(ReportHandler, root=root, output=output, allowed=allowed_paths(root, data, output))
                    with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
                        print(f"http://127.0.0.1:{server.server_port}/", flush=True)
                        server.serve_forever()
                return 0
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (core.CatalogError, OSError) as exc:
        print(f"tb3 catalog: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
