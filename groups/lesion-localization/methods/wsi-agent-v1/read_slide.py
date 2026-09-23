"""Read a bounded level-0 WSI tile without loading the full slide."""

import argparse
import json
import math
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image


def read_region(path: Path, x: int, y: int, width: int, height: int) -> Image.Image:
    if width <= 0 or height <= 0 or width * height > 4096 * 4096:
        raise ValueError("Tile must have positive size and at most 16,777,216 pixels")
    with tifffile.TiffFile(path) as tiff:
        page = tiff.pages[0]
        if x < 0 or y < 0 or x + width > page.imagewidth or y + height > page.imagelength:
            raise ValueError("Tile is outside the level-0 image")
        output = np.full((height, width, 3), 255, np.uint8)
        tile_width, tile_height = page.tilewidth, page.tilelength
        columns = math.ceil(page.imagewidth / tile_width)
        for row in range(y // tile_height, math.ceil((y + height) / tile_height)):
            for col in range(x // tile_width, math.ceil((x + width) / tile_width)):
                index = row * columns + col
                tiff.filehandle.seek(page.dataoffsets[index])
                raw = tiff.filehandle.read(page.databytecounts[index])
                decoded, _, _ = page.decode(raw, index, jpegtables=page.jpegtables)
                tile = decoded[0, :, :, :3]
                tx, ty = col * tile_width, row * tile_height
                xa, ya = max(x, tx), max(y, ty)
                xb, yb = min(x + width, tx + tile_width), min(y + height, ty + tile_height)
                output[ya - y : yb - y, xa - x : xb - x] = tile[
                    ya - ty : yb - ty, xa - tx : xb - tx
                ]
    return Image.fromarray(output)


def main() -> None:
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("x", type=int)
    parser.add_argument("y", type=int)
    parser.add_argument("width", type=int)
    parser.add_argument("height", type=int)
    parser.add_argument("output", type=Path)
    parser.add_argument("--slide", type=Path, default=Path("/app/data/slide.tif"))
    args = parser.parse_args()
    image = read_region(args.slide, args.x, args.y, args.width, args.height)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    ledger = Path("/app/work/read-ledger.jsonl")
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a") as stream:
        stream.write(
            json.dumps({"x": args.x, "y": args.y, "width": args.width, "height": args.height})
            + "\n"
        )
    print(args.output)


if __name__ == "__main__":
    main()
