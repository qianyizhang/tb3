"""Sign-off requires current evidence and cannot turn a regression into completion."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tb3_medical import explainer_reviews as reviews
from tb3_medical import storage, story_batches
from tb3_medical.errors import MedicalError


class ExplainerReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.batch = self.root / "batch"
        self.export = self.batch / "story"
        self.export.mkdir(parents=True)
        self.collection = self.root / "collection"
        self.collection.mkdir()
        self.ledger = self.root / "presentation/EXPLAINER-LEDGER.json"
        self.scope = self.root / "presentation/EXPLAINER-SCOPE.json"
        storage.write_new(
            self.scope, {"entries": [{"entry_id": "entry", "automatic_completion": True}]}
        )
        storage.write_new(
            self.ledger,
            {
                "entries": [
                    {
                        "entry_id": "entry",
                        "reviewed_disposition": "reviewed-scripted-planar",
                        "brief": "brief.md",
                    }
                ],
                "counts": {"reviewed-scripted-planar": 1},
                "history": ["preserve"],
            },
        )
        (self.root / "brief.md").write_text("Source explanation")
        self.packet = self.root / "packet.json"
        self.make_packet()
        entry = story_batches.BatchEntry(
            entry_id="entry",
            story_id="story",
            recipe="local-edit-v1",
            frames=24,
            fps=24,
            dependencies={},
        )
        batch = story_batches.Batch(
            entries=(entry,),
            stills_only=False,
            frontend_inputs={},
            frontend_manifest_sha256="a" * 64,
            dependencies={},
        )
        storage.write_new(self.batch / "batch.json", batch.model_dump(mode="json"))
        for file in ("receipt.json", "plan.json", "story.mp4", "index.html"):
            (self.export / file).write_text("Fixture " + file)
        image = self.collection / "image.png"
        image.write_bytes(b"image fixture")
        self.collection_path = self.collection / "review.json"
        storage.write_new(
            self.collection_path,
            {
                "schema": 1,
                "errors": [],
                "status": "pending-human-review",
                "storyId": "story",
                "export": str(self.export),
                "sourceReceiptSha256": storage.sha(self.export / "receipt.json"),
                "planSha256": storage.sha(self.export / "plan.json"),
                "videoSha256": storage.sha(self.export / "story.mp4"),
                "canonicalStills": [{"file": "image.png", "sha256": storage.sha(image)}],
                "samples": [],
                "playback": {
                    "completion": {"ended": True, "rate": 1},
                    "metadata": {"rate": 1},
                    "pageErrors": [],
                    "remoteRequests": [],
                    "seeks": [{"file": "image.png", "sha256": storage.sha(image)}] * 3,
                },
            },
        )
        matrix = self.root / "matrix.json"
        (self.export / "frame.png").write_bytes(b"browser image")
        storage.write_new(
            matrix,
            {
                "errors": [],
                "remote_requests": [],
                "stories": [
                    {
                        "id": "story",
                        "fallback": True,
                        "locales": ["en", "zh-CN"],
                        "frames": [
                            {
                                "locale": locale,
                                "frame": frame,
                                "file": "frame.png",
                                "sha256": storage.sha(self.export / "frame.png"),
                            }
                            for locale in ("en", "zh-CN")
                            for frame in (0, 23)
                        ],
                    }
                ],
            },
        )
        browser_paths = [
            "tests/explanation_expansion_browser.cjs",
            "presentation/tooling/browser.mts",
            "scripts/review_explainer_browser.mts",
            "explorer.html",
        ]
        for name in browser_paths:
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("Browser fixture")
        browser_paths += [
            "batch/batch.json",
            "batch/story/plan.json",
            "batch/story/receipt.json",
            "batch/story/index.html",
        ]
        witness = self.root / "browser-witness.json"
        storage.write_new(
            witness,
            {
                "schema": 1,
                "kind": "explainer-browser-witness",
                "explorer": "explorer.html",
                "matrix": {"path": "matrix.json", "sha256": storage.sha(matrix)},
                "sources": {name: storage.sha(self.root / name) for name in browser_paths},
            },
        )
        self.inspection = self.root / "inspection.json"
        storage.write_new(
            self.inspection,
            {
                "schema": 1,
                "entry_id": "entry",
                "reviewer": "assistant",
                "reviewed_at": "2026-09-29",
                "scope": "Synthetic tooling test",
                "observations": ["Explicit inspection"],
                "limits": ["No scientific claim"],
                "checks": dict.fromkeys(reviews.CHECKS, True),
                "inspected_images": {"collection/image.png": storage.sha(image)},
                "collection": {
                    "path": "collection/review.json",
                    "sha256": storage.sha(self.collection_path),
                },
                "browser_matrix": {"path": "browser-witness.json", "sha256": storage.sha(witness)},
                "rendered_mode": "planar",
            },
        )
        self.output = self.root / "signoff.json"
        queue = patch.object(
            reviews.explainer_queue, "inspect_queue", return_value={"summary": {"core": 1}}
        )
        queue.start()
        self.addCleanup(queue.stop)
        check = patch.object(
            reviews.story_batches, "check", return_value={"ok": True, "issues": []}
        )
        self.check = check.start()
        self.addCleanup(check.stop)

    def make_packet(self, mode="regression"):
        storage.atomic_write(
            self.packet,
            {
                "entry_id": "entry",
                "mode": mode,
                "source_sha256": {"brief.md": storage.sha(self.root / "brief.md")},
                "scope": {
                    "path": str(self.scope.relative_to(self.root)),
                    "sha256": storage.sha(self.scope),
                },
                "ledger": {
                    "path": str(self.ledger.relative_to(self.root)),
                    "sha256": storage.sha(self.ledger),
                },
            },
        )

    def record(self, accept=False):
        return reviews.record(
            self.root, self.packet, self.batch, self.inspection, self.output, accept=accept
        )

    def test_regression_signoff_preserves_ledger_and_requires_decode(self):
        before = self.ledger.read_bytes()
        result = self.record()
        self.assertFalse(result["accepted"])
        self.assertEqual(before, self.ledger.read_bytes())
        self.check.assert_called_once_with(self.root, self.batch, decode=True)
        with self.assertRaisesRegex(MedicalError, "fresh"):
            self.record()

    def test_regression_cannot_accept(self):
        with self.assertRaisesRegex(MedicalError, "Regression cannot"):
            self.record(accept=True)
        self.assertFalse(self.output.exists())

    def test_stale_packet_and_changed_image_are_rejected(self):
        (self.root / "brief.md").write_text("Changed source")
        with self.assertRaisesRegex(MedicalError, "Packet source changed"):
            self.record()
        self.make_packet()
        (self.collection / "image.png").write_bytes(b"changed")
        with self.assertRaisesRegex(MedicalError, "Changed inspected image"):
            self.record()

    def test_browser_evidence_must_match_current_harness(self):
        (self.root / "tests/explanation_expansion_browser.cjs").write_text("Changed harness")
        with self.assertRaisesRegex(MedicalError, "Browser witness source changed"):
            self.record()

    def test_bare_browser_matrix_is_insufficient(self):
        inspection = storage.read_object(self.inspection)
        inspection["browser_matrix"] = {
            "path": "matrix.json",
            "sha256": storage.sha(self.root / "matrix.json"),
        }
        storage.atomic_write(self.inspection, inspection)
        with self.assertRaisesRegex(MedicalError, "batch-bound"):
            self.record()

    def test_missing_inspection_and_incomplete_playback_are_rejected(self):
        inspection = storage.read_object(self.inspection)
        inspection["checks"]["mobile"] = False
        storage.atomic_write(self.inspection, inspection)
        with self.assertRaisesRegex(MedicalError, "every required surface"):
            self.record()
        inspection["checks"]["mobile"] = True
        collection = storage.read_object(self.collection_path)
        collection["playback"]["completion"]["ended"] = False
        storage.atomic_write(self.collection_path, collection)
        inspection["collection"]["sha256"] = storage.sha(self.collection_path)
        storage.atomic_write(self.inspection, inspection)
        with self.assertRaisesRegex(MedicalError, "normal-speed"):
            self.record()

    def test_production_requires_ready_status_and_changes_only_selected_entry(self):
        ledger = storage.read_object(self.ledger)
        ledger["entries"][0]["reviewed_disposition"] = "blocked-source-input"
        storage.atomic_write(self.ledger, ledger)
        self.make_packet("production")
        with self.assertRaisesRegex(MedicalError, "unblocked"):
            self.record(accept=True)
        ledger["entries"][0]["reviewed_disposition"] = "pending-operation-review"
        other = {
            "entry_id": "other",
            "reviewed_disposition": "blocked-source-input",
            "blocking_dependency": "retained",
        }
        ledger["entries"].append(other)
        storage.atomic_write(self.ledger, ledger)
        self.make_packet("production")
        with patch.object(reviews.task_briefs, "_brief_projection", return_value={"input": "test"}):
            self.assertTrue(self.record(accept=True)["accepted"])
        updated = json.loads(self.ledger.read_text())
        self.assertEqual(updated["entries"][1], other)
        self.assertEqual(updated["history"], ["preserve"])
        self.assertEqual(
            updated["counts"], {"reviewed-scripted-planar": 1, "blocked-source-input": 1}
        )
