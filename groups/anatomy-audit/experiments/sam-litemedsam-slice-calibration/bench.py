"""One-case, reference-box calibration. Never starts a general agent."""

import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

import cv2
import nibabel as nib
import numpy as np
from scipy import ndimage
import torch
from torch import nn
from torch.nn import functional as F


ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/sam-lite-bench-20260921"
ORGANS = ["liver", "kidney_right", "gallbladder", "pancreas",
          "adrenal_gland_right", "duodenum"]


def sha(path):
    return hashlib.file_digest(Path(path).open("rb"), "sha256").hexdigest()


def prepare():
    source = ROOT / "runs/br004-v1/source/s1233"
    authority = ROOT / "groups/anatomy-audit/experiments/ct-organ-segmentation-astra-xhigh/source/selected-source-manifest.json"
    manifest = json.loads(authority.read_text())
    wanted = ["ct.nii.gz"] + [f"segmentations/{o}.nii.gz" for o in ORGANS]
    hashes = {}
    for entry in manifest["files"]:
        if entry["path"] in wanted:
            digest = sha(source / entry["path"])
            assert digest == entry["sha256"], entry["path"]
            hashes[entry["path"]] = digest
    assert len(hashes) == len(wanted)
    ct_img = nib.load(source / "ct.nii.gz")
    ct = np.asarray(ct_img.dataobj, dtype=np.float32)
    arrays, samples = {}, []
    for organ in ORGANS:
        ref_img = nib.load(source / f"segmentations/{organ}.nii.gz")
        assert np.array_equal(ct_img.affine, ref_img.affine)
        ref = np.asarray(ref_img.dataobj) > 0
        assert ref.shape == ct.shape
        slices = np.flatnonzero(ref.any(axis=(0, 1)))
        for q in (0.25, 0.5, 0.75):
            z = int(slices[int(np.rint((len(slices) - 1) * q))])
            key = f"{organ}_q{int(q * 100)}"
            gt = ref[:, :, z].T.copy()
            assert np.array_equal(gt.T, ref[:, :, z])
            rgb = np.repeat(((np.clip(ct[:, :, z].T, -160, 240) + 160)
                             / 400 * 255).astype(np.uint8)[..., None], 3, axis=-1)
            ys, xs = np.where(gt)
            boxes = {}
            for name, margin in (("tight", 2), ("loose", 10)):
                boxes[name] = [max(0, int(xs.min()) - margin),
                               max(0, int(ys.min()) - margin),
                               min(gt.shape[1], int(xs.max()) + 1 + margin),
                               min(gt.shape[0], int(ys.max()) + 1 + margin)]
            arrays[key + "_image"] = rgb
            arrays[key + "_gt"] = gt
            samples.append(dict(id=key, organ=organ, q=q, slice_k=z, boxes=boxes,
                                gt_pixels=int(gt.sum())))
    out = BASE / "samples"
    out.mkdir(exist_ok=False)
    np.savez_compressed(out / "arrays.npz", **arrays)
    record = dict(case="s1233", selection="nonempty-slice-index quantiles",
                  prompt_origin="reference masks; oracle localization calibration",
                  affine=ct_img.affine.tolist(), shape=list(ct.shape),
                  spacing_mm=list(map(float, ct_img.header.get_zooms())),
                  source_hashes=hashes, samples=samples, arrays_sha256=sha(out / "arrays.npz"))
    (out / "manifest.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"sample_count": len(samples), "source_hashes_verified": len(hashes)}))


class Lite(nn.Module):
    def __init__(self, device):
        super().__init__()
        from tiny_vit_sam import TinyViT
        from segment_anything.modeling import MaskDecoder, PromptEncoder, TwoWayTransformer
        self.image_encoder = TinyViT(img_size=256, in_chans=3,
            embed_dims=[64, 128, 160, 320], depths=[2, 2, 6, 2],
            num_heads=[2, 4, 5, 10], window_sizes=[7, 7, 14, 7],
            mlp_ratio=4., drop_rate=0., drop_path_rate=0., use_checkpoint=False,
            mbconv_expand_ratio=4., local_conv_size=3, layer_lr_decay=0.8)
        self.prompt_encoder = PromptEncoder(embed_dim=256, image_embedding_size=(64, 64),
                                             input_image_size=(256, 256), mask_in_chans=16)
        self.mask_decoder = MaskDecoder(num_multimask_outputs=3,
            transformer=TwoWayTransformer(depth=2, embedding_dim=256, mlp_dim=2048, num_heads=8),
            transformer_dim=256, iou_head_depth=3, iou_head_hidden_dim=256)
        self.load_state_dict(torch.load(BASE / "weights/lite_medsam.pth",
                                        map_location="cpu", weights_only=True), strict=True)
        self.to(device).eval()
        self.device = device

    def set_image(self, image):
        self.original = image.shape[:2]
        self.ratio = 256 / max(self.original)
        self.resized = tuple(int(n * self.ratio + 0.5) for n in self.original)
        im = cv2.resize(image, self.resized[::-1], interpolation=cv2.INTER_AREA)
        im = (im - im.min()) / max(float(im.max() - im.min()), 1e-8)
        im = np.pad(im, ((0, 256 - self.resized[0]), (0, 256 - self.resized[1]), (0, 0)))
        tensor = torch.as_tensor(im, dtype=torch.float32, device=self.device).permute(2, 0, 1)[None]
        self.embedding = self.image_encoder(tensor)

    def predict(self, box):
        box256 = (np.asarray(box) * self.ratio).astype(int)
        box_tensor = torch.as_tensor(box256, dtype=torch.float32, device=self.device)[None, None]
        sparse, dense = self.prompt_encoder(points=None, boxes=box_tensor, masks=None)
        logits, score = self.mask_decoder(image_embeddings=self.embedding,
            image_pe=self.prompt_encoder.get_dense_pe(), sparse_prompt_embeddings=sparse,
            dense_prompt_embeddings=dense, multimask_output=False)
        logits = logits[..., :self.resized[0], :self.resized[1]]
        logits = F.interpolate(logits, size=self.original, mode="bilinear", align_corners=False)
        return (logits[0, 0] > 0).cpu().numpy(), float(score[0, 0].cpu())


def metrics(pred, ref, spacing):
    assert pred.shape == ref.shape and pred.dtype == bool
    inter = int((pred & ref).sum())
    p, r = int(pred.sum()), int(ref.sum())
    a = pred ^ ndimage.binary_erosion(pred)
    b = ref ^ ndimage.binary_erosion(ref)
    distances = np.concatenate([ndimage.distance_transform_edt(~a, sampling=spacing)[b],
                                ndimage.distance_transform_edt(~b, sampling=spacing)[a]]) if p and r else None
    return dict(dice=2 * inter / (p + r), precision=inter / p if p else 0.,
                recall=inter / r, hd95_mm=float(np.percentile(distances, 95)) if distances is not None else None,
                pred_pixels=p, gt_pixels=r)


def run(model_name, device, subset):
    torch.set_num_threads(4)
    torch.manual_seed(20260921)
    if device == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("MPS unavailable; do not silently change the backend")
    def sync():
        if device == "mps":
            torch.mps.synchronize()
    manifest = json.loads((BASE / "samples/manifest.json").read_text())
    assert sha(BASE / "samples/arrays.npz") == manifest["arrays_sha256"]
    data = np.load(BASE / "samples/arrays.npz")
    samples = manifest["samples"]
    if subset:
        samples = [s for s in samples if s["q"] == 0.5 and s["organ"] in ("liver", "adrenal_gland_right")]
    tag = f"{model_name}-{device}" + ("-subset" if subset else "")
    out = BASE / "results" / tag
    out.mkdir(exist_ok=False)
    started = time.perf_counter()
    if model_name == "sam2":
        from sam2.build_sam import build_sam2
        from sam2.sam2_image_predictor import SAM2ImagePredictor
        weights = BASE / "weights/sam2.1_hiera_small.pt"
        model = build_sam2("configs/sam2.1/sam2.1_hiera_s.yaml", str(weights), device=device)
        predictor = SAM2ImagePredictor(model, max_hole_area=0, max_sprinkle_area=0)
        def predict(box):
            masks, scores, _ = predictor.predict(box=np.asarray(box), multimask_output=False)
            return masks[0].astype(bool), float(scores[0])
    else:
        weights = BASE / "weights/lite_medsam.pth"
        predictor = Lite(device)
        predict = predictor.predict
    sync()
    load_seconds = time.perf_counter() - started
    masks, rows = {}, []
    with torch.inference_mode():
        start = time.perf_counter()
        predictor.set_image(data[samples[0]["id"] + "_image"])
        predict(samples[0]["boxes"]["tight"])
        sync()
        warmup_seconds = time.perf_counter() - start
        for sample in samples:
            key = sample["id"]
            sync(); start = time.perf_counter()
            predictor.set_image(data[key + "_image"])
            sync(); encode = time.perf_counter() - start
            for condition, box in sample["boxes"].items():
                sync(); start = time.perf_counter()
                pred, score = predict(box)
                sync(); decode = time.perf_counter() - start
                masks[key + "_" + condition] = pred
                row = dict(id=key, organ=sample["organ"], slice_k=sample["slice_k"],
                    condition=condition, box=box, encode_seconds=encode, decode_seconds=decode,
                    model_score=score, **metrics(pred, data[key + "_gt"], manifest["spacing_mm"][:2][::-1]))
                if device == "mps":
                    row["mps_driver_allocated_bytes_observed"] = torch.mps.driver_allocated_memory()
                rows.append(row)
                with (out / "rows.jsonl").open("a") as stream:
                    stream.write(json.dumps(row) + "\n")
                print(f"{tag} {key} {condition}: Dice={row['dice']:.4f}, encode={encode:.3f}s decode={decode:.3f}s", flush=True)
    np.savez_compressed(out / "masks.npz", **masks)
    receipt = dict(model=model_name, device=device, dtype="float32", threads=4,
        weights_sha256=sha(weights), weights_bytes=weights.stat().st_size,
        script_sha256=sha(__file__), sample_manifest_sha256=sha(BASE / "samples/manifest.json"),
        torch_version=torch.__version__, load_seconds=load_seconds, warmup_seconds=warmup_seconds,
        process_peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        masks_sha256=sha(out / "masks.npz"), prediction_count=len(rows), rows=rows)
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare", "run"])
    parser.add_argument("--model", choices=["sam2", "lite"])
    parser.add_argument("--device", choices=["cpu", "mps"], default="mps")
    parser.add_argument("--subset", action="store_true")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    else:
        run(args.model, args.device, args.subset)
