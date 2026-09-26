"""Batch receipts reject stale/tampered output and retain the first launch failure."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tb3_medical import frontend, storage
from tb3_medical import story_batches as batches
from tb3_medical.errors import MedicalError


class StoryBatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.output = self.root / "batch"
        self.output.mkdir()
        (self.root / "source.md").write_text("Original source")
        manifest = self.root / frontend.BUILD_DIR / "manifest.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text("{}")
        self.dependencies = {"source.md": storage.sha(self.root / "source.md")}
        self.batch = batches.Batch(
            entries=tuple(
                batches.BatchEntry(
                    entry_id=name,
                    story_id=name,
                    recipe="multiscale-v1",
                    frames=120,
                    fps=24,
                    dependencies=self.dependencies,
                )
                for name in ("first", "second")
            ),
            stills_only=True,
            frontend_inputs=self.dependencies,
            frontend_manifest_sha256=storage.sha(manifest),
            dependencies=self.dependencies,
        )
        storage.write_new(self.output / "batch.json", self.batch.model_dump(mode="json"))
        patcher = patch.object(
            frontend,
            "input_hashes",
            side_effect=lambda root: {"source.md": storage.sha(root / "source.md")},
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def export_fixture(self):
        for entry in self.batch.entries:
            folder = self.output / entry.story_id
            folder.mkdir()
            for name in batches.REQUIRED_OUTPUTS:
                (folder / name).write_text("Synthetic artifact")
            (folder / "plan.json").write_text(
                json.dumps({"schema": 2, "id": entry.story_id, "dependencies": self.dependencies})
            )
            receipt = {
                "schema": 1,
                "story": entry.story_id,
                "dependencies": self.dependencies,
                "frontend_manifest_sha256": self.batch.frontend_manifest_sha256,
                "errors": [],
                "outputs": {
                    name: {
                        "sha256": storage.sha(folder / name),
                        "bytes": (folder / name).stat().st_size,
                    }
                    for name in batches.REQUIRED_OUTPUTS
                },
            }
            storage.write_new(folder / "receipt.json", receipt)

    def test_verified_bytes_do_not_assign_visual_acceptance(self):
        self.export_fixture()
        result = batches.check(self.root, self.output)
        self.assertTrue(result["ok"], result["issues"])
        self.assertEqual(result["visual_review"], "pending")
        (self.output / "first/captions.vtt").write_text("Changed output")
        changed = batches.check(self.root, self.output)
        self.assertFalse(changed["ok"])
        self.assertTrue(any("fingerprint" in issue for issue in changed["issues"]))

    def test_current_source_drift_does_not_rewrite_historical_receipts(self):
        self.export_fixture()
        before = (self.output / "first/receipt.json").read_bytes()
        (self.root / "source.md").write_text("Revised source")
        result = batches.check(self.root, self.output)
        self.assertFalse(result["ok"])
        self.assertTrue(any("Source changed" in issue for issue in result["issues"]))
        self.assertEqual(before, (self.output / "first/receipt.json").read_bytes())

    def test_first_browser_failure_stops_batch_and_cannot_be_retried_in_place(self):
        def fail(command, *, cwd, stdout, stderr, env):
            self.assertEqual(env["TB3_PYTHON"], sys.executable)
            stdout.write("browserType.launch: registration failed\n")
            return subprocess.CompletedProcess(command, 1)

        with patch.object(subprocess, "run", side_effect=fail) as launch:
            with self.assertRaisesRegex(MedicalError, "browser_startup_failed"):
                batches.run(self.root, self.output)
            self.assertEqual(launch.call_count, 1)
        saved = storage.read_object(self.output / "execution.json")
        self.assertFalse(saved["ok"])
        self.assertEqual(len(saved["exports"]), 1)
        self.assertTrue((self.output / "first.log").is_file())
        with self.assertRaisesRegex(MedicalError, "already attempted"):
            batches.run(self.root, self.output)

    def test_source_change_after_one_export_prevents_the_next_launch(self):
        def change_source(command, *, cwd, stdout, stderr, env):
            (self.root / "source.md").write_text("Changed while exporter was running")
            return subprocess.CompletedProcess(command, 0)

        with patch.object(subprocess, "run", side_effect=change_source) as launch:
            with self.assertRaisesRegex(MedicalError, "Source changed during batch"):
                batches.run(self.root, self.output)
            self.assertEqual(launch.call_count, 1)
        saved = storage.read_object(self.output / "execution.json")
        self.assertFalse(saved["ok"])
        self.assertEqual(len(saved["exports"]), 1)

    def test_missing_required_output_and_unsafe_receipt_path_fail(self):
        self.export_fixture()
        path = self.output / "first/receipt.json"
        receipt = storage.read_object(path)
        del receipt["outputs"]["transcript.md"]
        storage.atomic_write(path, receipt)
        self.assertFalse(batches.check(self.root, self.output)["ok"])
        receipt["outputs"]["transcript.md"] = {
            "sha256": storage.sha(path.parent / "transcript.md"),
            "bytes": (path.parent / "transcript.md").stat().st_size,
        }
        receipt["outputs"]["../outside"] = {"sha256": "x", "bytes": 0}
        storage.atomic_write(path, receipt)
        self.assertTrue(
            any(
                "unsafe output" in issue
                for issue in batches.check(self.root, self.output)["issues"]
            )
        )

    def test_real_exporter_receipt_preserves_all_producer_metadata(self):
        source = Path(__file__).parent / "fixtures/story-export-receipt.json"
        raw = json.loads(source.read_text())
        receipt = batches.read_receipt(source)
        self.assertEqual(receipt.model_dump(mode="json", by_alias=True, exclude_unset=True), raw)
        self.assertEqual(receipt.story, "rigid-correspondence")

    def test_malformed_receipts_fail_at_ingress(self):
        import copy

        self.export_fixture()
        path = self.output / "first/receipt.json"
        original = storage.read_object(path)
        for outputs in ([], None, "bad", {"first.png": None}, {"first.png": []}):
            receipt = dict(original, outputs=outputs)
            storage.atomic_write(path, receipt)
            result = batches.check(self.root, self.output)
            self.assertFalse(result["ok"])
            self.assertTrue(any("validation error" in issue for issue in result["issues"]))
        for field in (
            "schema",
            "story",
            "dependencies",
            "frontend_manifest_sha256",
            "errors",
            "outputs",
        ):
            receipt = dict(original)
            del receipt[field]
            storage.atomic_write(path, receipt)
            self.assertFalse(batches.check(self.root, self.output)["ok"])
        for size in (True, -1, "10", 1.5):
            receipt = copy.deepcopy(original)
            receipt["outputs"]["first.png"]["bytes"] = size
            storage.atomic_write(path, receipt)
            self.assertFalse(batches.check(self.root, self.output)["ok"])
        for name in ("../outside", "/tmp/x", "..", ".", "", "a\\b", "C:foo", "bad\0name"):
            receipt = copy.deepcopy(original)
            receipt["outputs"][name] = {"sha256": "f" * 64, "bytes": 0}
            storage.atomic_write(path, receipt)
            result = batches.check(self.root, self.output)
            self.assertTrue(any("unsafe output name" in issue for issue in result["issues"]))
        for field, value in (
            ("schema", True),
            ("schema", "1"),
            ("errors", [False]),
            ("frontend_manifest_sha256", "not-a-hash"),
            ("dependencies", {"x": "bad"}),
        ):
            storage.atomic_write(path, dict(original, **{field: value}))
            self.assertFalse(batches.check(self.root, self.output)["ok"])

    def test_wrong_identity_errors_missing_files_and_symlinks_remain_failures(self):
        self.export_fixture()
        path = self.output / "first/receipt.json"
        original = storage.read_object(path)
        for key, value in (
            ("story", "wrong"),
            ("dependencies", {}),
            ("errors", ["retained capture failure"]),
            ("frontend_manifest_sha256", "f" * 64),
        ):
            storage.atomic_write(path, dict(original, **{key: value}))
            self.assertFalse(batches.check(self.root, self.output)["ok"])
        storage.atomic_write(path, original)
        artifact = path.parent / "first.png"
        artifact.unlink()
        self.assertFalse(batches.check(self.root, self.output)["ok"])
        artifact.symlink_to(path.parent / "poster.png")
        result = batches.check(self.root, self.output)
        self.assertTrue(any("symlink" in issue for issue in result["issues"]))

    def test_decode_checks_dimensions_timing_and_decoder_failure(self):
        stream = {
            "codec_name": "h264",
            "width": 1280,
            "height": 720,
            "nb_read_frames": "120",
            "r_frame_rate": "24/1",
        }
        entry = self.batch.entries[0]

        def probe(command, **kwargs):
            return subprocess.CompletedProcess(command, 0, json.dumps({"streams": [stream]}))

        with patch.object(subprocess, "run", side_effect=probe):
            batches._decode(self.output / "video.mp4", entry)
        for key, value in (
            ("codec_name", "vp9"),
            ("width", 640),
            ("height", 360),
            ("nb_read_frames", "119"),
            ("r_frame_rate", "25/1"),
        ):
            invalid = {**stream, key: value}
            with (
                self.subTest(key=key),
                patch.object(
                    subprocess,
                    "run",
                    return_value=subprocess.CompletedProcess(
                        [], 0, json.dumps({"streams": [invalid]})
                    ),
                ),
            ):
                with self.assertRaises(ValueError):
                    batches._decode(self.output / "video.mp4", entry)
        with patch.object(
            subprocess,
            "run",
            side_effect=[
                subprocess.CompletedProcess([], 0, json.dumps({"streams": [stream]})),
                subprocess.CalledProcessError(1, "ffmpeg"),
            ],
        ):
            with self.assertRaises(subprocess.CalledProcessError):
                batches._decode(self.output / "video.mp4", entry)
