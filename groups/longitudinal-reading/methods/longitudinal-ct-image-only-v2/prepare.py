"""Materialize a fresh instruction-only revision from the verified frozen v1 task."""

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
METHOD = Path(__file__).resolve().parent
SOURCE = ROOT / ".local/longitudinal-ct-image-only-v1"
DESTINATION = ROOT / ".local/longitudinal-ct-image-only-v2/whole-volume"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    expected = json.loads((SOURCE / "task-files.json").read_text())
    for name, checksum in expected.items():
        assert digest(SOURCE / "task" / name) == checksum, name
    destination = DESTINATION / "task"
    if destination.exists():
        raise SystemExit("Refusing to overwrite an existing task")
    shutil.copytree(SOURCE / "task", destination)
    shutil.copyfile(METHOD / "instruction.md", destination / "instruction.md")
    current = {
        str(p.relative_to(destination)): digest(p)
        for p in sorted(destination.rglob("*"))
        if p.is_file()
    }
    changes = [key for key in current if current[key] != expected[key]]
    assert changes == ["instruction.md"]
    (DESTINATION / "task-files.json").write_text(json.dumps(current, indent=2) + "\n")
    shutil.copyfile(SOURCE / "image-identities.json", DESTINATION / "image-identities.json")
    (DESTINATION / "preparation.json").write_text(
        json.dumps(
            {
                "source": str(SOURCE.relative_to(ROOT)),
                "changed_files": changes,
                "unchanged_images_references_scorer_runtime": True,
                "original_task_digest": "f2aa2fb2f71acd930e927d581a2513c31dd6c5a03f1f0387ff64e00f098eea24",
                "instruction_sha256": current["instruction.md"],
            },
            indent=2,
        )
        + "\n"
    )
    print(json.dumps({"task": str(destination), "changed_files": changes}))


if __name__ == "__main__":
    main()
