"""Small compiled-asset fixture for Python assembly tests; browser tests use Vite."""

import hashlib
import json
import shutil
from pathlib import Path

from tb3_medical import frontend


def install_explorer(root: Path) -> None:
    """Copy only assembly templates; unit tests do not need anatomy or teaching media."""
    source = Path(__file__).resolve().parents[1] / "presentation"
    for name in (
        "ui.css",
        "task-explorer/index.html",
        "task-explorer/style.css",
        "task-explorer/datasets.css",
        "task-explorer/brief-template.md",
    ):
        target = root / "presentation" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, target)
    install_frontend(root)


def install_frontend(root: Path) -> None:
    for name in frontend.BUILD_INPUTS:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("{}\n" if target.suffix == ".json" else "// fixture\n")
    output = root / frontend.BUILD_DIR
    output.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for entry in ("explorer", "overview"):
        code = "/* browser behavior is tested against the real Vite build */\n"
        name = entry + ".js"
        (output / name).write_text(code)
        outputs[name] = hashlib.sha256(code.encode()).hexdigest()
    (output / "manifest.json").write_text(
        json.dumps({"schema_version": 1, "inputs": frontend.input_hashes(root), "outputs": outputs})
    )
