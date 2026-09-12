"""Native smoke check for a binary built from the supplied SQLite source."""

from __future__ import annotations

import subprocess
import sys


def run(binary: str, sql: str) -> list[str]:
    result = subprocess.run(
        [binary, ":memory:"], input=sql, text=True, capture_output=True, check=True
    )
    return [line for line in result.stdout.splitlines() if not line.startswith("+")]


def main() -> None:
    binary = sys.argv[1]
    sql = """
        CREATE TABLE orders(id INT, threshold INT);
        CREATE TABLE limits(value INT);
        INSERT INTO orders VALUES (11,0),(12,0);
        INSERT INTO limits VALUES (1),(1);
        SELECT count(*) FROM (
          SELECT id FROM orders
          WHERE EXISTS (SELECT 1 FROM limits WHERE value > threshold)
          LIMIT 2 OFFSET 3
        );
    """
    actual = run(binary, sql)
    if actual != ["0"]:
        raise SystemExit(f"expected 0 rows after LIMIT/OFFSET, got {actual!r}")


if __name__ == "__main__":
    main()
