"""Small native-trace witnesses; no retained patient arrays or model execution."""

import base64
import copy
import gzip
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

from tb3_medical.errors import MedicalError
from tb3_medical.explainers.native_trace import (
    Manifest,
    compile_components,
    compile_trace,
    compile_view,
    project_payload,
)

IDENTITY = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def compressed(value):
    return base64.b64encode(gzip.compress(bytes(value), mtime=0)).decode()


def ct_payload():
    return {
        "shape": [2, 2, 2],
        "affine": copy.deepcopy(IDENTITY),
        "attempt": "tiny-attempt",
        "preview_size": 1,
        "preview_base64_gzip": compressed([10]),
        "spacing_mm": 1.5,
        "preview_window_hu": [-1000, 500],
        "target": "target",
        "target_silhouette": "silhouette",
        "slice_previews": ["x", "y", "z"],
        "reference_pose": copy.deepcopy(IDENTITY),
        "frozen_metrics": {"rms_mm": 0},
        "elapsed_seconds": 2.0,
        "steps_in_trace": 1,
        "trace": [{"step": 1, "timestamp": "time", "calls": ["inspect"], "output": "ok"}],
        "states": [
            {
                "id": "saved",
                "trace_step": 1,
                "pose": copy.deepcopy(IDENTITY),
                "image": "image",
                "silhouette": "silhouette",
                "difference": "difference",
                "role": "saved output",
                "diagnostic": {"rms_mm": 0.25},
            }
        ],
        "private_extra": "must not leak",
    }


def mra_payload():
    return {
        "shape": [2, 2, 2],
        "affine": copy.deepcopy(IDENTITY),
        "spacing": [1, 1, 1],
        "volume": compressed(range(8)),
        "mask": compressed([1, 0, 0, 0, 0, 0, 0, 0]),
        "editable": compressed([0, 1, 1, 0, 0, 0, 0, 0]),
        "surface": compressed([0] * 12),
        "surface_vertices": 1,
        "states": [{"threshold": 165, "count": 2, "indices": [1, 2], "contacts": [[1], [2]]}],
        "added": [1, 2],
        "residual": [3],
        "seed": [0, 0, 1],
        "roi": [[0, 0, 0], [2, 2, 2]],
        "source_voxels": 1,
        "global_components": 1,
        "trace": [{"step": 1, "time": "time", "call": "union", "output": "ok"}],
        "mip": "mip",
        "frozen": {"pass": True},
        "initial": {"route": False},
    }


class NativeTraceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.story = self.root / "trace.story.md"

    def fixture(self, adapter="ct-pose"):
        data = ct_payload() if adapter == "ct-pose" else mra_payload()
        assets = []
        for name, role, content in (
            ("data.json", "derived-display", json.dumps(data)),
            ("receipt.json", "provenance", "{}"),
            ("LICENSE.txt", "license", "synthetic test license"),
        ):
            path = self.root / name
            path.write_text(content)
            assets.append(
                {
                    "path": name,
                    "role": role,
                    "bytes": path.stat().st_size,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
        manifest = {
            "schema": 1,
            "id": "tiny",
            "entry_id": "tiny-entry",
            "attempt": "tiny-attempt",
            "saved_state": "saved" if adapter == "ct-pose" else "165",
            "adapter": adapter,
            "coordinates": "LPS-mm" if adapter == "ct-pose" else "RAS-mm",
            "notice": "Synthetic witness",
            "recovery": "Restore selected inputs",
            "assets": assets,
        }
        (self.root / "manifest.json").write_text(json.dumps(manifest))
        (self.root / "source.md").write_text("Synthetic source")
        header = {
            "schema": 2,
            "id": "tiny",
            "title": "Tiny trace",
            "locale": "en",
            "purpose": "Test evidence",
            "scope": "Synthetic only",
            "recipe": "native-trace-v1",
            "manifest": "manifest.json",
            "fps": 24,
            "reference_policy": "reader-reference-reveal",
            "source_class": "source-derived-teaching",
            "source_locators": ["source.md"],
        }
        state = "saved" if adapter == "ct-pose" else "165"
        beats = [
            {
                "id": "inspect",
                "scene": "input",
                "frames": 2,
                "caption": "Inspect",
                "narration": "Observe",
                "visual": "Input",
                "state": state,
                "trace_steps": [1],
                "reference": False,
            },
            {
                "id": "reveal",
                "scene": "reference",
                "frames": 3,
                "caption": "Reveal",
                "narration": "Compare",
                "visual": "Reference",
                "state": state,
                "trace_steps": [1],
                "reference": True,
            },
        ]
        self.write_story(header, beats)
        return data, manifest, header, beats

    def write_story(self, header, beats):
        self.story.write_text(
            "---\n"
            + json.dumps(header)
            + "\n---\n\n# Tiny\n\n"
            + "\n\n".join("```beat\n" + json.dumps(beat) + "\n```" for beat in beats)
        )

    def test_compile_pins_sources_and_preserves_discrete_timeline(self):
        self.fixture()
        result = compile_trace(self.root, Path("trace.story.md"))
        self.assertEqual(result["availability"], "available")
        self.assertEqual(result["status"], "compiled-native-trace")
        self.assertEqual(result["plan"]["durationFrames"], 5)
        self.assertEqual(
            [(b["startFrame"], b["endFrame"]) for b in result["plan"]["beats"]], [(0, 2), (2, 5)]
        )
        self.assertIn("source.md", result["dependencies"])
        (self.root / "data.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "Changed native asset"):
            compile_trace(self.root, Path("trace.story.md"))

    def test_canonical_reader_view_rejects_stale_asset_availability(self):
        self.fixture()
        compiler = self.root / "src/tb3_medical/explainers/native_trace.py"
        compiler.parent.mkdir(parents=True)
        compiler.write_text("test compiler")
        with patch("tb3_medical.explanation_stories.compiler_hashes", return_value={}):
            plan, view = compile_components(self.root, self.story)
            self.assertEqual(view["family"], "native-trace")
            self.assertEqual(view["availability"], "available")
            self.assertEqual(plan["asset_pack"], "tiny")
            self.assertEqual(compile_view(self.root, plan), view)
            self.assertNotIn("reference", view["payload"]["observed"])
            (self.root / "data.json").unlink()
            with self.assertRaisesRegex(ValueError, "availability changed"):
                compile_view(self.root, plan)
            missing_plan, missing_view = compile_components(self.root, self.story)
            self.assertEqual(missing_view["availability"], "missing-local-assets")
            self.assertIsNone(missing_view["payload"])
            self.assertEqual(missing_view["missing"], ["data.json"])
            self.assertEqual(missing_plan["beats"], plan["beats"])

    def test_reader_contract_rejects_malformed_trace_action(self):
        from tb3_medical.presentation_contracts import validate_native_trace_view

        self.fixture()
        compiler = self.root / "src/tb3_medical/explainers/native_trace.py"
        compiler.parent.mkdir(parents=True)
        compiler.write_text("test compiler")
        with patch("tb3_medical.explanation_stories.compiler_hashes", return_value={}):
            _, view = compile_components(self.root, self.story)
        view["payload"]["observed"]["trace"][0]["step"] = "not a step"
        with self.assertRaises(ValueError):
            validate_native_trace_view(view)

    def test_same_length_asset_tampering_rejects_sha_mismatch(self):
        self.fixture()
        receipt = self.root / "receipt.json"
        before = receipt.stat().st_size
        receipt.write_text("[]")
        self.assertEqual(receipt.stat().st_size, before)
        with self.assertRaisesRegex(ValueError, "Changed native asset: receipt.json"):
            compile_trace(self.root, Path("trace.story.md"))

    def test_missing_assets_require_explicit_mode_and_never_hide_tampering(self):
        self.fixture()
        (self.root / "LICENSE.txt").unlink()
        with self.assertRaisesRegex(ValueError, "Missing native assets"):
            compile_trace(self.root, Path("trace.story.md"))
        result = compile_trace(self.root, Path("trace.story.md"), allow_missing=True)
        self.assertEqual(result["missing"], ["LICENSE.txt"])
        self.assertIsNone(result["payload"])
        (self.root / "receipt.json").write_text("changed")
        with self.assertRaisesRegex(ValueError, "Changed native asset"):
            compile_trace(self.root, Path("trace.story.md"), allow_missing=True)

    def test_asset_paths_cannot_escape_root(self):
        _, manifest, _, _ = self.fixture()
        manifest["assets"][0]["path"] = "../outside.json"
        (self.root / "manifest.json").write_text(json.dumps(manifest))
        with self.assertRaises(MedicalError):
            compile_trace(self.root, Path("trace.story.md"), allow_missing=True)

    def test_frame_and_affine_rejections(self):
        data, manifest, _, _ = self.fixture()
        manifest["coordinates"] = "RAS-mm"
        with self.assertRaisesRegex(ValidationError, "coordinate frame"):
            Manifest.model_validate(manifest)
        manifest["coordinates"] = "LPS-mm"
        model = Manifest.model_validate(manifest)
        for affine in (
            [[0] * 4] * 4,
            [[float("nan"), 0, 0, 0], *IDENTITY[1:]],
            [*IDENTITY[:3], [0, 0, 1, 1]],
        ):
            with self.subTest(affine=affine), self.assertRaises(ValueError):
                project_payload({**data, "affine": affine}, model)

    def test_ct_projection_separates_private_diagnostics_and_normalizes_trace(self):
        data, manifest, _, _ = self.fixture()
        result = project_payload(data, Manifest.model_validate(manifest))
        self.assertNotIn("private_extra", json.dumps(result))
        self.assertNotIn("reference_pose", result["input"])
        self.assertNotIn("frozen_metrics", result["observed"])
        self.assertNotIn("diagnostic", result["observed"]["states"][0])
        self.assertEqual(result["reference"]["state_diagnostics"]["saved"], {"rms_mm": 0.25})
        self.assertEqual(result["observed"]["trace"][0]["calls"], ["inspect"])

    def test_chapters_require_retained_steps_states_and_final_only_reference(self):
        _, _, header, beats = self.fixture()
        for mutation in ("state", "step", "reference"):
            changed = copy.deepcopy(beats)
            if mutation == "state":
                changed[0]["state"] = "invented"
            elif mutation == "step":
                changed[0]["trace_steps"] = [9]
            else:
                changed[0]["reference"] = True
            self.write_story(header, changed)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                compile_trace(self.root, Path("trace.story.md"))

    def test_mra_projection_and_array_contact_saved_edit_guards(self):
        data, manifest, _, _ = self.fixture("mra-repair")
        model = Manifest.model_validate(manifest)
        result = project_payload(data, model)
        self.assertEqual(result["observed"]["trace"][0]["calls"], ["union"])
        self.assertNotIn("initial", result["input"])
        self.assertNotIn("residual", result["observed"])
        for mutation in (
            "length",
            "binary",
            "count",
            "duplicate",
            "contact",
            "existing",
            "outside",
        ):
            changed = copy.deepcopy(data)
            if mutation == "length":
                changed["volume"] = compressed([0])
            elif mutation == "binary":
                changed["mask"] = compressed([2] + [0] * 7)
            elif mutation == "count":
                changed["states"][0]["count"] = 3
            elif mutation == "duplicate":
                changed["states"][0]["indices"] = [1, 1]
            elif mutation == "contact":
                changed["states"][0]["contacts"] = [[3]]
            elif mutation == "existing":
                changed["added"] = [0]
            else:
                changed["added"] = [3]
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                project_payload(changed, model)

    def test_mra_candidates_remain_inside_editable_unmasked_domain(self):
        data, manifest, _, _ = self.fixture("mra-repair")
        for indices in ([0, 1], [1, 3]):
            changed = copy.deepcopy(data)
            changed["states"][0]["indices"] = indices
            changed["states"][0]["contacts"] = []
            with self.subTest(indices=indices), self.assertRaises(ValueError):
                project_payload(changed, Manifest.model_validate(manifest))

    def test_mra_saved_additions_equal_the_retained_selected_component(self):
        data, manifest, _, _ = self.fixture("mra-repair")
        changed = copy.deepcopy(data)
        changed["added"] = [1]
        with self.assertRaises(ValueError):
            project_payload(changed, Manifest.model_validate(manifest))

    def test_compressed_array_rejects_trailing_stream_and_expansion(self):
        data, manifest, _, _ = self.fixture("mra-repair")
        for encoded in (
            compressed(range(9)),
            base64.b64encode(gzip.compress(bytes(range(8))) + gzip.compress(b"extra")).decode(),
        ):
            with self.subTest(encoded=encoded), self.assertRaises(ValueError):
                project_payload({**data, "volume": encoded}, Manifest.model_validate(manifest))


if __name__ == "__main__":
    unittest.main()
