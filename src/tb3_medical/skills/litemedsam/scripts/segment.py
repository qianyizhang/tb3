"""Portable image+box LiteMedSAM adapter; no evaluator or benchmark inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import time
from pathlib import Path

WEIGHTS_SHA256 = "79d8c9dca6db4d69d3f905579e5250af05e859fff9c1f543e89a513c3028ce76"


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def validate_boxes(boxes, width, height):
    if not isinstance(boxes, list) or not boxes:
        raise ValueError("Provide a nonempty JSON list of [x0,y0,x1,y1] boxes")
    for box in boxes:
        if (
            not isinstance(box, list)
            or len(box) != 4
            or any(type(x) not in (int, float) or not math.isfinite(x) for x in box)
        ):
            raise ValueError("Every box must contain four finite pixel coordinates")
        x0, y0, x1, y1 = box
        if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
            raise ValueError(f"Box outside {width}x{height} image or empty: {box}")
    return boxes


def infer(args):
    import cv2
    import numpy as np
    import torch
    from PIL import Image
    from segment_anything.modeling import MaskDecoder, PromptEncoder, TwoWayTransformer
    from tiny_vit_sam import TinyViT
    from torch import nn
    from torch.nn import functional as F

    weights = args.runtime / "weights/lite_medsam.pth"
    if sha(weights) != WEIGHTS_SHA256:
        raise ValueError("Checkpoint hash mismatch; expected the pinned LiteMedSAM checkpoint")
    with Image.open(args.image) as source:
        if source.format != "PNG" or source.mode not in ("L", "RGB"):
            raise ValueError("Input must be an 8-bit grayscale or RGB PNG")
        image = np.asarray(source.convert("RGB"))
    height, width = image.shape[:2]
    boxes = validate_boxes(json.loads(args.boxes.read_text()), width, height)
    if args.device == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("MPS unavailable; use an explicit CPU run or approved Metal access")
    if args.output.exists():
        raise FileExistsError(f"Output must be new: {args.output}")
    torch.set_num_threads(4)
    torch.manual_seed(20260921)

    def sync():
        if args.device == "mps":
            torch.mps.synchronize()

    started = time.perf_counter()
    model = nn.Module()
    model.image_encoder = TinyViT(
        img_size=256,
        in_chans=3,
        embed_dims=[64, 128, 160, 320],
        depths=[2, 2, 6, 2],
        num_heads=[2, 4, 5, 10],
        window_sizes=[7, 7, 14, 7],
        mlp_ratio=4.0,
        drop_rate=0.0,
        drop_path_rate=0.0,
        use_checkpoint=False,
        mbconv_expand_ratio=4.0,
        local_conv_size=3,
        layer_lr_decay=0.8,
    )
    model.prompt_encoder = PromptEncoder(
        embed_dim=256,
        image_embedding_size=(64, 64),
        input_image_size=(256, 256),
        mask_in_chans=16,
    )
    model.mask_decoder = MaskDecoder(
        num_multimask_outputs=3,
        transformer=TwoWayTransformer(depth=2, embedding_dim=256, mlp_dim=2048, num_heads=8),
        transformer_dim=256,
        iou_head_depth=3,
        iou_head_hidden_dim=256,
    )
    model.load_state_dict(torch.load(weights, map_location="cpu", weights_only=True), strict=True)
    model.to(args.device).eval()
    sync()
    load_seconds = time.perf_counter() - started
    ratio = 256 / max(height, width)
    resized = (int(height * ratio + 0.5), int(width * ratio + 0.5))
    if min(resized) < 1:
        raise ValueError("Image aspect ratio is too extreme for a 256-pixel encoder")
    mapped_boxes = [(np.asarray(box) * ratio).astype(int) for box in boxes]
    if any(box[2] <= box[0] or box[3] <= box[1] for box in mapped_boxes):
        raise ValueError("A box collapses at encoder resolution; use a documented crop")
    masks, scores, decode_seconds = [], [], []
    with torch.inference_mode():
        sync()
        started = time.perf_counter()
        im = cv2.resize(image, resized[::-1], interpolation=cv2.INTER_AREA)
        im = (im - im.min()) / max(float(im.max() - im.min()), 1e-8)
        im = np.pad(im, ((0, 256 - resized[0]), (0, 256 - resized[1]), (0, 0)))
        tensor = torch.as_tensor(im, dtype=torch.float32, device=args.device)
        embedding = model.image_encoder(tensor.permute(2, 0, 1)[None])
        sync()
        encode_seconds = time.perf_counter() - started
        for box in mapped_boxes:
            started = time.perf_counter()
            sparse, dense = model.prompt_encoder(
                points=None,
                boxes=torch.as_tensor(box, dtype=torch.float32, device=args.device)[None, None],
                masks=None,
            )
            logits, score = model.mask_decoder(
                image_embeddings=embedding,
                image_pe=model.prompt_encoder.get_dense_pe(),
                sparse_prompt_embeddings=sparse,
                dense_prompt_embeddings=dense,
                multimask_output=False,
            )
            logits = F.interpolate(
                logits[..., : resized[0], : resized[1]],
                size=(height, width),
                mode="bilinear",
                align_corners=False,
            )
            masks.append((logits[0, 0] > 0).cpu().numpy())
            scores.append(float(score[0, 0].cpu()))
            sync()
            decode_seconds.append(time.perf_counter() - started)
    args.output.mkdir(parents=True, exist_ok=False)
    np.save(args.output / "masks.npy", np.stack(masks), allow_pickle=False)
    for i, mask in enumerate(masks):
        Image.fromarray(mask.astype(np.uint8) * 255).save(args.output / f"mask-{i:03d}.png")
    receipt = dict(
        model="LiteMedSAM",
        device=args.device,
        dtype="float32",
        threads=4,
        image_sha256=sha(args.image),
        boxes_sha256=sha(args.boxes),
        weights_sha256=WEIGHTS_SHA256,
        adapter_sha256=sha(__file__),
        image_shape=[height, width],
        boxes=boxes,
        encoder_boxes=[b.tolist() for b in mapped_boxes],
        torch_version=torch.__version__,
        model_scores=scores,
        load_seconds=load_seconds,
        encode_seconds=encode_seconds,
        decode_seconds=decode_seconds,
        timing_note="Single process, no warmup; not comparable to warm benchmark latency",
        masks_sha256=sha(args.output / "masks.npy"),
    )
    (args.output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "masks": len(masks), "device": args.device}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runtime", type=Path, default=os.environ.get("LITEMEDSAM_ROOT", "/opt/litemedsam")
    )
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--boxes", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", choices=("cpu", "mps"), default="cpu")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    for key in ("runtime", "image", "boxes", "output"):
        setattr(args, key, getattr(args, key).expanduser().resolve())
    if args.worker:
        infer(args)
        return
    python = args.runtime / ".venv/bin/python"
    vendor = args.runtime / "vendor/LiteMedSAM"
    for path in (python, vendor / "tiny_vit_sam.py", args.runtime / "weights/lite_medsam.pth"):
        if not path.is_file():
            parser.error(f"Missing provisioned runtime file: {path}")
    # Upstream's editable install omits top-level tiny_vit_sam.py. Run from its
    # directory so ordinary imports work, without altering sys.path or upstream.
    command = [
        str(python),
        "-B",
        "-c",
        "import runpy,sys; runpy.run_path(sys.argv.pop(1), run_name='__main__')",
        str(Path(__file__).resolve()),
        "--worker",
    ]
    for key in ("runtime", "image", "boxes", "output", "device"):
        command.extend(["--" + key, str(getattr(args, key))])
    raise SystemExit(subprocess.call(command, cwd=vendor))


if __name__ == "__main__":
    main()
