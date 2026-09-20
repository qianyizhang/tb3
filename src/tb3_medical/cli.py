"""Author, run, inspect and package medical research."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from . import core as c, workflow as w, packaging


def main(argv=None):
    parser = argparse.ArgumentParser(prog="med", description=__doc__)
    parser.add_argument("--root", type=Path, help="Workspace containing workbench.toml")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("brief", help="Author or render task explanations; never launches a trial")
    brief_sub = p.add_subparsers(dest="brief_command", required=True)
    for action in ("new", "build", "check"):
        b = brief_sub.add_parser(action)
        b.add_argument(
            "--catalog", default="discussions/medical-agent-repository-survey/catalog.json"
        )
        if action == "new":
            b.add_argument("id")
            b.add_argument("--title", required=True)
            b.add_argument("--repository", required=True)
            b.add_argument("--family", required=True)
            b.add_argument("--repository-id", help="Optional source-inventory repository ID")
            b.add_argument("--destination", required=True)
        elif action == "build":
            b.add_argument("--output", type=Path, default=Path("runs/task-explorer/index.html"))
    p = sub.add_parser("list")
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--kind", choices=sorted(c.KINDS))
    p.add_argument("--group")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("show")
    p.add_argument("id")
    p = sub.add_parser("check")
    p.add_argument(
        "--assets", action="store_true", help="Also verify retained presentation source assets"
    )
    p = sub.add_parser("new")
    p.add_argument("group")
    p.add_argument("id")
    p.add_argument("--title", required=True)
    p = sub.add_parser("idea")
    p.add_argument("group")
    p.add_argument("id")
    p.add_argument("--title", required=True)
    p.add_argument("--question", required=True)
    p.add_argument("--source", required=True)
    p = sub.add_parser("decide")
    p.add_argument("id")
    p.add_argument("state", choices=c.VOCABULARY["axes"]["idea_state"]["values"])
    p.add_argument("--reason", required=True)
    p.add_argument("--actor", choices=["user", "assistant"], required=True)
    p.add_argument("--source", required=True)
    p.add_argument(
        "--accepted",
        action="store_true",
        help="Record an already accepted decision with its user source",
    )
    p = sub.add_parser("issue")
    p.add_argument("targets", nargs="+")
    p.add_argument("--reason", required=True)
    p.add_argument("--evidence", action="append", default=[])
    p.add_argument("--actor", default="assistant")
    p = sub.add_parser("review")
    p.add_argument("experiment")
    p.add_argument("assessment", choices=c.VOCABULARY["axes"]["assessment"]["values"])
    p.add_argument("--reason", required=True)
    p.add_argument("--scope", required=True)
    p.add_argument("--evidence", action="append", default=[])
    p.add_argument("--actor", default="assistant")
    p.add_argument("--resolves", action="append", default=[])
    p.add_argument("--qualify-attempt", action="append", default=[])
    p = sub.add_parser("prepare")
    p.add_argument("experiment")
    p.add_argument("--case")
    p.add_argument("--execute", action="store_true")
    p = sub.add_parser("run")
    p.add_argument("experiment")
    p.add_argument("--case")
    p.add_argument("--agent", choices=["oracle", "nop", "codex"], default="codex")
    p.add_argument("--model")
    p.add_argument("--effort")
    p.add_argument("--harbor", default="harbor")
    p.add_argument("--diagnostic", action="store_true")
    p.add_argument("--preview", action="store_true")
    p = sub.add_parser("collect")
    p.add_argument("experiment")
    p.add_argument("sources", nargs="+")
    p = sub.add_parser("replay")
    p.add_argument("experiment")
    p.add_argument("--case")
    p = sub.add_parser("view")
    p.add_argument("experiment")
    p.add_argument("--case", required=True)
    p.add_argument("--output", type=Path)
    p = sub.add_parser("present")
    p.add_argument("--output", type=Path, default=Path(".local/site"))
    p.add_argument("--serve", action="store_true")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--local-media", action="store_true")
    p = sub.add_parser("media")
    p.add_argument("operation", choices=["prepare", "check", "optimize"])
    p = sub.add_parser("export")
    p.add_argument("recipe")
    p.add_argument("destination", type=Path)
    p.add_argument("--include-flagged", action="store_true")
    p = sub.add_parser("verify-package")
    p.add_argument("destination", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "verify-package":
            print(json.dumps(packaging.verify(args.destination), indent=2))
            return 0
        root = c.workspace(args.root)
        command = args.command
        if command == "list":
            rows = [
                r
                for r in c.projection(root).values()
                if (not args.kind or r["kind"] == args.kind)
                and (not args.group or r.get("group_id", r["id"]) == args.group)
                and all(word in json.dumps(r).lower() for word in args.query.lower().split())
            ]
            if not args.json:
                for row in rows:
                    axes = c.VOCABULARY["display_rules"].get(row["kind"] + "_primary", [])
                    labels = [
                        c.VOCABULARY["axes"][a]["values"][row["current"][a]]["label"]
                        for a in axes
                        if a in row["current"]
                    ]
                    print(
                        f"{row['kind']:11} {row['id']:55} {' / '.join(labels):30} {row.get('title', '')}"
                    )
                return 0
            result = rows
        elif command == "show":
            result = c.projection(root)[args.id]
        elif command == "check":
            from .presentation import check, assets

            result = check(root)
            from . import task_briefs

            if (root / task_briefs.DEFAULT_CATALOG).is_file():
                result["task_briefs"] = task_briefs.check(root)
            if args.assets:
                result.update(assets(root))
        elif command == "brief":
            from . import task_briefs

            if args.brief_command == "new":
                result = task_briefs.new(
                    root,
                    args.id,
                    args.title,
                    args.repository,
                    args.family,
                    args.destination,
                    args.catalog,
                    args.repository_id,
                )
            elif args.brief_command == "build":
                output = args.output if args.output.is_absolute() else root / args.output
                result = task_briefs.build(root, output, args.catalog)
            else:
                result = task_briefs.check(root, args.catalog)
        elif command == "new":
            result = w.new(root, args.group, args.id, args.title)
        elif command == "idea":
            result = c.add_idea(root, args.group, args.id, args.title, args.question, args.source)
        elif command == "decide":
            result = c.decide(
                root, args.id, args.state, args.reason, args.actor, args.source, args.accepted
            )
        elif command == "issue":
            result = c.issue(root, args.targets, args.reason, args.evidence, args.actor)
        elif command == "review":
            eligible = [
                w.qualify_attempt(root, args.experiment, key) for key in args.qualify_attempt
            ]
            result = c.review(
                root,
                args.experiment,
                args.assessment,
                args.reason,
                args.scope,
                args.evidence,
                args.actor,
                args.resolves,
                eligible,
            )
        elif command == "prepare":
            result = w.prepare(root, args.experiment, args.case, args.execute)
        elif command == "run":
            result = w.run(
                root,
                args.experiment,
                args.agent,
                args.harbor,
                case=args.case,
                model=args.model,
                effort=args.effort,
                diagnostic=args.diagnostic,
                preview=args.preview,
            )
        elif command == "collect":
            result = w.collect(root, args.experiment, args.sources)
        elif command in {"replay", "view"}:
            from . import landmarks

            experiment = c.lookup(root, args.experiment)
            if experiment.get("method") != "landmarks":
                raise c.MedicalError(
                    "No maintained replay/view method is declared for this experiment"
                )
            result = (
                landmarks.replay(root, experiment, args.case)
                if command == "replay"
                else landmarks.view(root, experiment, args.case, args.output)
            )
        elif command == "media":
            from . import media

            result = getattr(media, args.operation)(root)
        elif command == "export":
            result = packaging.export(
                root, args.recipe, args.destination, include_flagged=args.include_flagged
            )
        elif command == "verify-package":
            result = packaging.verify(args.destination)
        elif command == "present":
            from .presentation import present, serve

            output = args.output if args.output.is_absolute() else root / args.output
            result = present(root, output, args.local_media)
            if args.serve:
                print(f"Open http://127.0.0.1:{args.port}/", flush=True)
                serve(output, args.port)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except (
        c.MedicalError,
        w.harbor.HarborError,
        OSError,
        ValueError,
        KeyError,
        subprocess.CalledProcessError,
    ) as exc:
        print(f"med: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
