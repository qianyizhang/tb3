"""One entry point; inspection never starts a trial."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from . import core as c, workflow as w, packaging


def main(argv=None):
    parser = argparse.ArgumentParser(prog="med", description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("list"); p.add_argument("query", nargs="?", default=""); p.add_argument("--kind", choices=sorted(c.KINDS)); p.add_argument("--group"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("show"); p.add_argument("id")
    p = sub.add_parser("validate"); p.add_argument("id", nargs="?")
    p = sub.add_parser("new"); p.add_argument("group"); p.add_argument("id"); p.add_argument("--title", required=True)
    p = sub.add_parser("idea"); p.add_argument("group"); p.add_argument("id"); p.add_argument("--title", required=True); p.add_argument("--question", required=True); p.add_argument("--source", required=True)
    p = sub.add_parser("decide"); p.add_argument("id"); p.add_argument("disposition"); p.add_argument("--reason", required=True); p.add_argument("--actor", choices=["user", "assistant"], required=True); p.add_argument("--source", required=True)
    p = sub.add_parser("issue"); p.add_argument("targets", nargs="+"); p.add_argument("--impact", choices=["suspected", "confirmed"], required=True); p.add_argument("--reason", required=True); p.add_argument("--evidence", action="append", required=True); p.add_argument("--actor", required=True)
    p = sub.add_parser("review"); p.add_argument("id"); p.add_argument("validity", choices=sorted(c.VALIDITY)); p.add_argument("--reason", required=True); p.add_argument("--evidence", action="append", required=True); p.add_argument("--actor", required=True); p.add_argument("--resolves", action="append", default=[])
    p = sub.add_parser("prepare"); p.add_argument("id"); p.add_argument("--execute", action="store_true")
    p = sub.add_parser("freeze"); p.add_argument("id")
    p = sub.add_parser("plan"); p.add_argument("freeze"); p.add_argument("--agent", choices=["oracle", "nop", "codex"], required=True); p.add_argument("--model"); p.add_argument("--effort")
    p = sub.add_parser("run"); p.add_argument("id"); p.add_argument("--harbor", required=True, help="Explicit executable; this command launches the planned trial")
    p = sub.add_parser("collect"); p.add_argument("id"); p.add_argument("sources", nargs="+")
    p = sub.add_parser("present"); p.add_argument("--output", type=Path, default=Path(".cache/medical/site")); p.add_argument("--serve", action="store_true"); p.add_argument("--port", type=int, default=8765); p.add_argument("--local-media", action="store_true")
    p = sub.add_parser("export"); p.add_argument("recipe"); p.add_argument("destination", type=Path)
    p = sub.add_parser("verify-package"); p.add_argument("destination", type=Path)
    p = sub.add_parser("assets"); p.add_argument("--write", action="store_true")
    args = parser.parse_args(argv); root = args.root.resolve(); cmd = args.command
    try:
        if cmd == "list":
            rows = [r for r in c.projection(root).values() if (not args.kind or r["kind"] == args.kind) and (not args.group or r.get("group_id", r["id"]) == args.group) and all(word in json.dumps(r).lower() for word in args.query.lower().split())]
            if not args.json:
                for r in rows:
                    state = r["current"].get("disposition", r.get("disposition", r["current"]["validity"]))
                    print(f'{r["kind"]:11} {r["id"]:55} {state:13} {r.get("title", r.get("classification", ""))}')
                return 0
            result = rows
        elif cmd == "show": result = c.projection(root)[c.lookup(root, args.id)["id"]]
        elif cmd == "validate":
            if args.id:
                _, _, files = w.task_validate(root, args.id); result = {"files": len(files), "task_digest": w.tree_digest(files), "checks": "Static required-file and TOML checks; no Docker or inference."}
            else: result = c.validate(root)
        elif cmd == "new": result = w.new(root, args.group, args.id, args.title)
        elif cmd == "idea": result = c.add_idea(root, args.group, args.id, args.title, args.question, args.source)
        elif cmd == "decide": result = c.decide(root, args.id, args.disposition, args.reason, args.actor, args.source)
        elif cmd == "issue": result = c.issue(root, args.targets, args.impact, args.reason, args.evidence, args.actor)
        elif cmd == "review": result = c.review(root, args.id, args.validity, args.reason, args.evidence, args.actor, args.resolves)
        elif cmd == "prepare": result = w.prepare(root, args.id, args.execute)
        elif cmd == "freeze": result = w.freeze(root, args.id)
        elif cmd == "plan": result = w.plan(root, args.freeze, args.agent, args.model, args.effort)
        elif cmd == "run": result = w.run(root, args.id, args.harbor)
        elif cmd == "collect": result = w.collect(root, args.id, args.sources)
        elif cmd == "export": result = packaging.export(root, args.recipe, args.destination)
        elif cmd == "verify-package": result = packaging.verify(args.destination)
        elif cmd == "assets":
            from .presentation import assets
            result = assets(root, args.write)
        elif cmd == "present":
            from .presentation import present, serve
            out = args.output if args.output.is_absolute() else root / args.output
            result = present(root, out, args.local_media)
            if args.serve:
                print(f'Open http://127.0.0.1:{args.port}/ — Ctrl-C stops the read-only server.', flush=True)
                serve(out, args.port)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (c.MedicalError, w.harbor.CatalogError, OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"med: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
