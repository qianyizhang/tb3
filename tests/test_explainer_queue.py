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
            "needs_resolution": 0,
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

    def test_resolution_lane_and_external_evidence(self) -> None:
        root = self.root
        ledger_path = root / explainer_queue.LEDGER
        ledger = storage.read_object(ledger_path)
        ledger["entries"][1]["dependency_resolution"] = {
            "state": "needs-resolution",
            "category": "source-input",
            "attempt_status": "not-yet-attempted",
            "next_action": "Try local native source recovery",
        }
        ledger["entries"][0]["reviewed_disposition"] = "blocked-source-contract"
        ledger["entries"][0]["blocking_dependency"] = "Earlier broad blocker"
        ledger["entries"][0]["dependency_resolution"] = {
            "state": "external-blocked",
            "category": "source-contract",
            "attempt_status": "contacted-rights-holder",
            "next_action": "Await permission or use a symbolic fallback with a source warning",
            "evidence": "Rights request logged",
            "reopen_condition": "Written permission received",
        }
        ledger_path.write_text(json.dumps(ledger))
        queue = explainer_queue.inspect_queue(root)
        assert queue["summary"]["needs_resolution"] == 1
        assert queue["summary"]["deferred"] == 1
        assert queue["resolution_ids"] == ["second-blocked"]
        assert [row["entry_id"] for row in queue["deferred"]] == ["first-ready"]
        register = explainer_queue.render_dependency_register(queue)
        assert register.index("## second-blocked") < register.index("## first-ready")
        assert "Try local native source recovery" in register
        assert "Earlier broad blocker" in register
        assert "Rights request logged" in register
        with self.assertRaisesRegex(MedicalError, "needs-resolution"):
            explainer_queue.prepare(root, "second-blocked", "packet-resolution")
        explainer_queue.defer_blocked(
            root, actor="assistant", source="follow-up", date="2026-09-29"
        )
        updated = storage.read_object(ledger_path)
        assert (
            updated["entries"][1]["dependency_resolution"]
            == ledger["entries"][1]["dependency_resolution"]
        )
        assert "dependency_deferral" not in updated["entries"][1]
        assert (
            updated["entries"][0]["dependency_resolution"]
            == ledger["entries"][0]["dependency_resolution"]
        )
        assert "dependency_deferral" not in updated["entries"][0]

    def test_invalid_resolution_metadata_fails_closed(self) -> None:
        root = self.root
        ledger_path = root / explainer_queue.LEDGER
        for resolution, expected in (
            (
                {
                    "state": ["needs-resolution"],
                    "category": "input",
                    "attempt_status": "tried",
                    "next_action": "Retry",
                },
                "state",
            ),
            (
                {
                    "state": "unknown",
                    "category": "input",
                    "attempt_status": "tried",
                    "next_action": "Retry",
                },
                "state",
            ),
            (
                {
                    "state": "needs-resolution",
                    "category": "",
                    "attempt_status": "tried",
                    "next_action": "Retry",
                },
                "category",
            ),
            (
                {
                    "state": "needs-resolution",
                    "category": "input",
                    "attempt_status": "",
                    "next_action": "Retry",
                },
                "attempt_status",
            ),
            (
                {
                    "state": "needs-resolution",
                    "category": "input",
                    "attempt_status": "tried",
                    "next_action": "",
                },
                "next_action",
            ),
            (
                {
                    "state": "external-blocked",
                    "category": "input",
                    "attempt_status": "tried",
                    "next_action": "Retry",
                    "reopen_condition": "Input arrives",
                },
                "evidence",
            ),
            (
                {
                    "state": "external-blocked",
                    "category": "input",
                    "attempt_status": "tried",
                    "next_action": "Retry",
                    "evidence": "Request logged",
                },
                "reopen_condition",
            ),
        ):
            ledger = copy.deepcopy(self.ledger)
            ledger["entries"][1]["dependency_resolution"] = resolution
            ledger_path.write_text(json.dumps(ledger))
            with self.subTest(expected=expected), self.assertRaisesRegex(MedicalError, expected):
                explainer_queue.inspect_queue(root)

    def test_former_blocker_requires_archived_attempt_and_symbolic_warning(self) -> None:
        root = self.root
        ledger_path = root / explainer_queue.LEDGER
        receipt_relative = "presentation/first-ready/source-resolution.json"
        receipt_path = root / receipt_relative
        receipt_path.write_text(
            json.dumps(
                {
                    "schema": 1,
                    "kind": "explainer-source-resolution",
                    "entry_id": "first-ready",
                    "attempts": [
                        {
                            "action": "Tried source download",
                            "source": "Official dataset page",
                            "outcome": "Actual image unavailable locally",
                            "attempted_at": "2026-09-29",
                        }
                    ],
                }
            )
        )
        valid = copy.deepcopy(self.ledger)
        row = valid["entries"][0]
        row.update(
            dependency_resolution_history=[
                {
                    "state": "needs-resolution",
                    "category": "source-input",
                    "attempt_status": "attempted",
                    "next_action": "Use symbolic view",
                }
            ],
            illustration_basis="symbolic",
            actual_data_gap="Actual image unavailable locally",
            acquisition_route="Request actual scan from official dataset page",
            source_resolution_receipt=receipt_relative,
            source_review={
                "receipt": receipt_relative,
                "receipt_sha256": storage.sha(receipt_path),
            },
            warning_text="Symbolic view: obtain the actual scan from the official dataset page.",
        )
        active = copy.deepcopy(valid)
        active["entries"][0]["dependency_resolution"] = {
            "state": "needs-resolution",
            "category": "source-input",
            "attempt_status": "attempted",
            "next_action": "Use symbolic view",
        }
        ledger_path.write_text(json.dumps(active))
        with self.assertRaisesRegex(MedicalError, "must be archived"):
            explainer_queue.inspect_queue(root)
        missing_history = copy.deepcopy(valid)
        missing_history["entries"][0].pop("dependency_resolution_history")
        missing_history["entries"][0]["dependency_deferral"] = {"status": "deferred-follow-up"}
        ledger_path.write_text(json.dumps(missing_history))
        with self.assertRaisesRegex(MedicalError, "resolution history"):
            explainer_queue.inspect_queue(root)
        for field, expected in (
            ("illustration_basis", "illustration basis"),
            ("warning_text", "warning_text"),
            ("source_resolution_receipt", "source_resolution_receipt"),
        ):
            missing = copy.deepcopy(valid)
            missing["entries"][0].pop(field)
            ledger_path.write_text(json.dumps(missing))
            with self.subTest(field=field), self.assertRaisesRegex(MedicalError, expected):
                explainer_queue.inspect_queue(root)
        ledger_path.write_text(json.dumps(valid))
        queue = explainer_queue.inspect_queue(root)
        assert "first-ready" in queue["ready_ids"]
        packet = explainer_queue.prepare(root, "first-ready", "packet-symbolic")
        assert packet["mode"] == "production"
        assert packet["source_sha256"][receipt_relative] == storage.sha(receipt_path)

    def test_ready_transition_rejects_source_receipt_mismatch(self) -> None:
        root = self.root
        ledger_path = root / explainer_queue.LEDGER
        receipt_relative = "presentation/first-ready/source-resolution.json"
        receipt_path = root / receipt_relative
        receipt = {
            "schema": 1,
            "kind": "explainer-source-resolution",
            "entry_id": "first-ready",
            "attempts": [
                {
                    "action": "Requested source",
                    "source": "Official page",
                    "outcome": "Unavailable",
                    "attempted_at": "2026-09-29",
                }
            ],
        }
        receipt_path.write_text(json.dumps(receipt))
        valid = copy.deepcopy(self.ledger)
        valid["entries"][0].update(
            dependency_resolution_history=[
                {
                    "state": "needs-resolution",
                    "category": "source-input",
                    "attempt_status": "attempted",
                    "next_action": "Use symbolic view",
                }
            ],
            illustration_basis="mixed",
            actual_data_gap="Actual image unavailable",
            acquisition_route="Official access request",
            source_resolution_receipt=receipt_relative,
            source_review={
                "receipt": receipt_relative,
                "receipt_sha256": storage.sha(receipt_path),
            },
            warning_text="Only symbolic geometry is shown; request the image through the official page.",
        )
        wrong_path = copy.deepcopy(valid)
        wrong_path["entries"][0]["source_resolution_receipt"] = "presentation/other.json"
        ledger_path.write_text(json.dumps(wrong_path))
        with self.assertRaisesRegex(MedicalError, "differs from source review"):
            explainer_queue.inspect_queue(root)
        wrong_hash = copy.deepcopy(valid)
        wrong_hash["entries"][0]["source_review"]["receipt_sha256"] = "0" * 64
        ledger_path.write_text(json.dumps(wrong_hash))
        with self.assertRaisesRegex(MedicalError, "Changed source review receipt"):
            explainer_queue.inspect_queue(root)
        no_pin = copy.deepcopy(valid)
        no_pin["entries"][0].pop("source_review")
        ledger_path.write_text(json.dumps(no_pin))
        with self.assertRaisesRegex(MedicalError, "Missing source review receipt"):
            explainer_queue.inspect_queue(root)
        empty_attempts = copy.deepcopy(receipt)
        empty_attempts["attempts"] = []
        receipt_path.write_text(json.dumps(empty_attempts))
        no_attempt = copy.deepcopy(valid)
        no_attempt["entries"][0]["source_review"]["receipt_sha256"] = storage.sha(receipt_path)
        ledger_path.write_text(json.dumps(no_attempt))
        with self.assertRaisesRegex(MedicalError, "needs attempts"):
            explainer_queue.inspect_queue(root)
        receipt["entry_id"] = "someone-else"
        receipt_path.write_text(json.dumps(receipt))
        valid["entries"][0]["source_review"]["receipt_sha256"] = storage.sha(receipt_path)
        ledger_path.write_text(json.dumps(valid))
        with self.assertRaisesRegex(MedicalError, "receipt entry differs"):
            explainer_queue.inspect_queue(root)

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
