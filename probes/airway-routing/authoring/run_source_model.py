"""Run released Raidionics ONNX models with the official segmentation backend.

Reference masks are never passed to inference. The released model bytes and
preprocessing configuration are copied unchanged into the backend's fold layout.
"""
import argparse
import configparser
import hashlib
import importlib.metadata
import json
import logging
import os
from pathlib import Path
import shutil
import time

import raidionicsseg.fit as backend


def run_predictions_compatible(**kwargs):
    """1.5.2 retains the batch axis for non-deep-supervised TensorFlow FV models."""
    result = original_predictions(**kwargs)
    if result.ndim == 5:
        assert result.shape[0] == 1, result.shape
        logging.warning("Removing singleton ONNX batch dimension: %s", result.shape)
        result = result[0]
    assert result.ndim == 4, result.shape
    return result


original_predictions = backend.run_predictions
backend.run_predictions = run_predictions_compatible


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--image", type=Path, required=True)
    p.add_argument("--models", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--stage", choices=["Lungs", "Airways"], required=True)
    p.add_argument("--lung-mask", type=Path)
    a = p.parse_args()
    a.output = a.output.resolve()
    a.output.mkdir(parents=True, exist_ok=True)
    inputs = a.output / "inputs"
    inputs.mkdir(exist_ok=True)
    image = inputs / "input0.nii.gz"
    if not image.exists():
        os.link(a.image.resolve(), image)
    assert digest(image) == digest(a.image)
    source = a.models / ("CT_" + a.stage)
    model = a.output / "model"
    (model / "fold_0").mkdir(parents=True, exist_ok=True)
    for src, dst in [(source / "model.onnx", model / "fold_0/model.onnx"),
                     (source / "pre_processing.ini", model / "pre_processing.ini")]:
        if not dst.exists():
            shutil.copy2(src, dst)
        assert digest(src) == digest(dst)
    prediction = a.output / "prediction"
    prediction.mkdir(exist_ok=True)
    cfg = configparser.ConfigParser()
    cfg["System"] = {"gpu_id": "-1", "acceleration": "cpu",
                     "inputs_folder": str(inputs), "output_folder": str(prediction),
                     "model_folder": str(model)}
    cfg["Runtime"] = {"batch_size": "1", "folds_ensembling": "False",
                      "ensembling_strategy": "average", "reconstruction_method": "thresholding",
                      "reconstruction_order": "resample_first", "use_preprocessed_data": "False",
                      "test_time_augmentation_iteration": "0"}
    if a.stage == "Airways":
        if a.lung_mask is None:
            p.error("Airway inference requires a predicted lung mask")
        cfg["Mediastinum"] = {"lungs_segmentation_filename": str(a.lung_mask.resolve())}
    config_path = a.output / "config.ini"
    with config_path.open("w") as f:
        cfg.write(f)
    manifest = {"image_sha256": digest(a.image), "model_sha256": digest(source / "model.onnx"),
                "preprocessing_sha256": digest(source / "pre_processing.ini"),
                "stage": a.stage, "reference_masks_used": False,
                "compatibility": "Remove singleton batch axis if official backend returns 5D probabilities; no probability values changed",
                "versions": {k: importlib.metadata.version(k) for k in
                             ["raidionicsseg", "onnxruntime", "numpy", "scipy", "nibabel", "SimpleITK"]}}
    if a.lung_mask:
        manifest["predicted_lung_sha256"] = digest(a.lung_mask)
    (a.output / "source.json").write_text(json.dumps(manifest, indent=2) + "\n")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    start = time.monotonic()
    backend.run_model(str(config_path), str(a.output / "inference.log"))
    expected = prediction / ("labels_" + a.stage + ".nii.gz")
    manifest.update({"elapsed_seconds": time.monotonic() - start,
                     "prediction_sha256": digest(expected), "status": "completed"})
    (a.output / "result.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest), flush=True)


if __name__ == "__main__":
    main()
