"""Build the local SQLite amalgamation without a Make dependency."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).parent


def main() -> None:
    subprocess.run(
        [
            "cc", "-O2", "-g", "-DSQLITE_THREADSAFE=0", "-DSQLITE_OMIT_READLINE",
            "-o", str(ROOT / "sqlite3"), str(ROOT / "sqlite" / "shell.c"),
            str(ROOT / "sqlite" / "sqlite3.c"), "-lm",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
