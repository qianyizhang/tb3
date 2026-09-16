"""Fetch pinned AeroPath author-mirror files and verify their LFS SHA-256."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import time
import requests

BASE = Path("runs/br033-brain-routing/airway-access")
REV = "6d0f831ca22bf57918aba3980ae475c94d45b997"


def fetch(row):
    dst = BASE / row["path"]
    dst.parent.mkdir(parents=True, exist_ok=True)
    url = f"https://huggingface.co/datasets/andreped/AeroPath/resolve/{REV}/{row['path']}"
    start = time.monotonic()
    if not dst.exists():
        r = requests.get(url, stream=True, timeout=(30, 90))
        r.raise_for_status()
        tmp = dst.with_suffix(dst.suffix + ".part")
        with tmp.open("wb") as f:
            for b in r.iter_content(1024 * 1024):
                f.write(b)
        assert tmp.stat().st_size == row["size"]
        assert hashlib.sha256(tmp.read_bytes()).hexdigest() == row["lfs"]["oid"]
        tmp.rename(dst)
    digest = hashlib.sha256(dst.read_bytes()).hexdigest()
    assert digest == row["lfs"]["oid"]
    return {"path": row["path"], "sha256": digest, "bytes": dst.stat().st_size,
            "revision": REV, "url": url, "seconds": time.monotonic() - start}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("cases", nargs="+")
    a = p.parse_args()
    inventory = json.loads((BASE / "hf-data.json").read_text())
    rows = [x for x in inventory if x["type"] == "file" and x["path"].split("/")[1] in a.cases]
    with ThreadPoolExecutor(max_workers=3) as ex:
        result = list(ex.map(fetch, rows))
    (BASE / ("manifest-" + "-".join(a.cases) + ".json")).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
