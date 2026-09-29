"""Behavioral boundaries for the scope-aware explainer queue."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tb3_medical import explainer_queue, storage
from tb3_medical.errors import MedicalError


def _fixture(tmp_path: Path) -> tuple[Path, dict[str, object], dict[str, object]]:
    root = tmp_path
    presentation = root / "presentation"
    presentation.mkdir()
    groups = [
        {"group_id": "second", "scope": "core"},
        {"group_id": "first", "scope": "core"},
        {"group_id": "outside", "scope": "candidate"},
    ]
    assignments = [
        ("first-ready", "first", True, "pending-operation-review", None),
        ("second-blocked", "second", True, "blocked-source-input", "Missing native input"),
        ("second-ready", "second", True, "pending-operation-review", None),
        ("first-reviewed", "first", True, "reviewed-scripted-planar", None),
        ("outside-blocked", "outside", False, "blocked-source-contract", "Terms unresolved"),
    ]
    scope_rows = []
    ledger_rows = []
    for entry_id, group_id, automatic, status, reason in assignments:
        catalogue = f"presentation/{entry_id}/catalog.json"
        brief = f"presentation/{entry_id}/brief.md"
        (root / catalogue).parent.mkdir(parents=True, exist_ok=True)
        (root / catalogue).write_text(
            json.dumps(
                {
                    "entries": [
                        {
                            "id": entry_id,
                            "brief": brief,
                            "illustration": {"story_id": "finished"}
                            if entry_id == "first-reviewed"
                            else {},
                        }
                    ]
                }
            )
        )
        (root / brief).write_text(entry_id)
        scope_rows.append(
            {
                "entry_id": entry_id,
                "group_id": group_id,
                "automatic_completion": automatic,
                "brief": brief,
                "brief_sha256": storage.sha(root / brief),
            }
        )
        ledger_rows.append(
            {
                "entry_id": entry_id,
                "reviewed_disposition": status,
                "blocking_dependency": reason,
                "remaining_work": f"Resolve {entry_id}" if reason else "Inspect the story",
                "catalogue": catalogue,
                "brief": brief,
                "story_id": "finished" if entry_id == "first-reviewed" else None,
                "custom_history": ["kept"],
            }
        )
    story = root / "presentation/legacy/finished.story.md"
    story.parent.mkdir()
    story.write_text("reviewed story")
    scope: dict[str, object] = {
        "schema": 1,
        "groups": groups,
        "entries": scope_rows,
        "status_snapshot": {"sha256": "0" * 64, "core_reviewed": 1, "core_unfinished": 3},
    }
    ledger: dict[str, object] = {"schema": 1, "entries": ledger_rows, "counts": {"retained": 5}}
    (presentation / "EXPLAINER-SCOPE.json").write_text(json.dumps(scope, ensure_ascii=False))
    (presentation / "EXPLAINER-LEDGER.json").write_text(json.dumps(ledger, ensure_ascii=False))
    return root, scope, ledger


class ExplainerQueueTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root, self.scope, self.ledger = _fixture(Path(temporary.name))

    def test_scope_order_exclusion_and_blockers(self) -> None:
        root = self.root
        queue = explainer_queue.inspect_queue(root)
        assert queue["ready_ids"] == ["second-ready", "first-ready"]
        assert queue["summary"] == {
            "catalogue": 5,
            "core": 4,
            "ready": 2,
            "deferred": 1,
            "reviewed_core": 1,
            "excluded": 1,
        }
        assert [row["entry_id"] for row in queue["deferred"]] == ["second-blocked"]
        assert queue["deferred"][0]["reason"] == "Missing native input"
        assert queue["deferred"][0]["next_action"] == "Resolve second-blocked"
        assert queue["warnings"] == [
            "Scope audit ledger hash differs from current ledger; queue uses current ledger status."
        ]
        register = explainer_queue.render_dependency_register(queue)
        assert "Missing native input" in register
        assert "Resolve second-blocked" in register
        assert "outside-blocked" not in register
        (root / "presentation/first-ready/brief.md").write_text("changed")
        assert any(
            "Scope brief hash differs from current file: first-ready" in warning
            for warning in explainer_queue.inspect_queue(root)["warnings"]
        )

    def test_validation_fails_closed(self) -> None:
        root, scope, ledger = self.root, self.scope, self.ledger
        scope_path = root / explainer_queue.SCOPE
        ledger_path = root / explainer_queue.LEDGER
        duplicate = copy.deepcopy(scope)
        duplicate["entries"].append(copy.deepcopy(duplicate["entries"][0]))
        scope_path.write_text(json.dumps(duplicate))
        with self.assertRaisesRegex(MedicalError, "Duplicate scope"):
            explainer_queue.inspect_queue(root)
        scope_path.write_text(json.dumps(scope))
        missing = copy.deepcopy(ledger)
        missing["entries"].pop()
        ledger_path.write_text(json.dumps(missing))
        with self.assertRaisesRegex(MedicalError, "IDs differ"):
            explainer_queue.inspect_queue(root)
        bad = copy.deepcopy(ledger)
        bad["entries"][1]["blocking_dependency"] = ""
        ledger_path.write_text(json.dumps(bad))
        with self.assertRaisesRegex(MedicalError, "blocking_dependency"):
            explainer_queue.inspect_queue(root)
        bad = copy.deepcopy(ledger)
        bad["entries"][0]["reviewed_disposition"] = "mystery"
        ledger_path.write_text(json.dumps(bad))
        with self.assertRaisesRegex(MedicalError, "Unknown explainer status"):
            explainer_queue.inspect_queue(root)
        bad = copy.deepcopy(ledger)
        bad["entries"][0]["blocking_dependency"] = "Still missing source"
        ledger_path.write_text(json.dumps(bad))
        with self.assertRaisesRegex(MedicalError, "Pending entry still has a blocking dependency"):
            explainer_queue.inspect_queue(root)

    def test_prepare_enforces_mode_and_exclusive_packet(self) -> None:
        root = self.root
        with self.assertRaisesRegex(MedicalError, "deferred"):
            explainer_queue.prepare(root, "second-blocked", "packet-blocked")
        with self.assertRaisesRegex(MedicalError, "excluded"):
            explainer_queue.prepare(root, "outside-blocked", "packet-outside")
        with self.assertRaisesRegex(MedicalError, "reviewed"):
            explainer_queue.prepare(root, "first-reviewed", "packet-reviewed")
        with self.assertRaisesRegex(MedicalError, "ready"):
            explainer_queue.prepare(root, "first-ready", "packet-regression", regression=True)
        production = explainer_queue.prepare(root, "first-ready", "packet-production")
        assert production["mode"] == "production"
        assert production["acceptance_eligible"] is True
        assert production["source_sha256"][production["sources"]["brief"]["path"]]
        assert (root / "packet-production/packet.json").is_file()
        with self.assertRaisesRegex(MedicalError, "already exists"):
            explainer_queue.prepare(root, "first-ready", "packet-production")
        with patch.object(
            explainer_queue.explanation_stories,
            "resolve_stories",
            return_value={
                "finished": {"dependencies": {"presentation/legacy/finished.story.md": "0" * 64}}
            },
        ):
            regression = explainer_queue.prepare(
                root, "first-reviewed", "packet-reviewed", regression=True
            )
        assert regression["mode"] == "regression"
        assert regression["acceptance_eligible"] is False
        assert "no new acceptance" in regression["purpose"]
        assert regression["sources"]["story"]["path"] == "presentation/legacy/finished.story.md"
        ledger_path = root / explainer_queue.LEDGER
        ledger = storage.read_object(ledger_path)
        ledger["entries"][3]["story_id"] = "stale-binding"
        ledger_path.write_text(json.dumps(ledger))
        with self.assertRaisesRegex(MedicalError, "Reviewed story binding differs"):
            explainer_queue.prepare(root, "first-reviewed", "packet-stale", regression=True)

    def test_declared_source_review_receipt_must_match(self) -> None:
        root = self.root
        ledger_path = root / explainer_queue.LEDGER
        ledger = storage.read_object(ledger_path)
        receipt_relative = "presentation/reviews/source-audit.json"
        ledger["entries"][0]["source_review"] = {
            "receipt": receipt_relative,
            "receipt_sha256": "0" * 64,
        }
        ledger_path.write_text(json.dumps(ledger))
        with self.assertRaisesRegex(MedicalError, "Missing source review receipt"):
            explainer_queue.prepare(root, "first-ready", "packet-missing")
        receipt = root / receipt_relative
        receipt.parent.mkdir(parents=True)
        receipt.write_text('{"checked": true}')
        with self.assertRaisesRegex(MedicalError, "Changed source review receipt"):
            explainer_queue.prepare(root, "first-ready", "packet-mismatched")
        ledger["entries"][0]["source_review"]["receipt_sha256"] = storage.sha(receipt)
        ledger_path.write_text(json.dumps(ledger))
        packet = explainer_queue.prepare(root, "first-ready", "packet-matched")
        assert packet["source_sha256"][receipt_relative] == storage.sha(receipt)
        # Legacy source audits use `sha256` for this same receipt pin.
        legacy = ledger["entries"][0]["source_review"]
        legacy["sha256"] = legacy.pop("receipt_sha256")
        ledger_path.write_text(json.dumps(ledger))
        packet = explainer_queue.prepare(root, "first-ready", "packet-legacy")
        assert packet["source_sha256"][receipt_relative] == storage.sha(receipt)

    def test_deferral_is_idempotent_and_preserves_history(self) -> None:
        root, ledger = self.root, self.ledger
        ledger_path = root / explainer_queue.LEDGER
        first = explainer_queue.defer_blocked(
            root, actor="assistant", source="session-next", date="2026-09-29"
        )
        assert first["annotated"] == 1
        after = storage.read_object(ledger_path)
        assert after["counts"] == ledger["counts"]
        assert after["entries"][1]["custom_history"] == ["kept"]
        assert after["entries"][1]["dependency_deferral"] == {
            "actor": "assistant",
            "source": "session-next",
            "date": "2026-09-29",
            "reason": "Missing native input",
            "next_action": "Resolve second-blocked",
            "status": "deferred-follow-up",
        }
        assert "dependency_deferral" not in after["entries"][4]
        bytes_after = ledger_path.read_bytes()
        second = explainer_queue.defer_blocked(
            root, actor="assistant", source="session-next", date="2026-09-29"
        )
        assert second["annotated"] == 0
        assert ledger_path.read_bytes() == bytes_after
        with self.assertRaisesRegex(MedicalError, "Conflicting dependency deferral"):
            explainer_queue.defer_blocked(
                root, actor="assistant", source="other", date="2026-09-29"
            )


if __name__ == "__main__":
    unittest.main()
