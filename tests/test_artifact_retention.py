"""Recovery preserves occurrences while storing identical bytes once."""

import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from pydantic import ValidationError

from tb3_medical import artifact_retention as a
from tb3_medical import cli, storage
from tb3_medical.errors import MedicalError


class ArtifactRetentionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.source = self.root / "evidence"
        self.source.mkdir()
        (self.source / "accepted.html").write_bytes(b"exact shared bytes\n" * 100)
        (self.source / "failed.html").write_bytes((self.source / "accepted.html").read_bytes())
        (self.source / "failed.html").chmod(0o640)
        (self.source / "empty.json").write_bytes(b"")
        self.job = self.root / "job.json"
        self.plan = self.root / "plan.json"
        self.store = self.root / "store"
        self.receipt = self.root / "receipt.json"
        a.init_job(
            ["evidence"], id="trial", owner="test", source_task="test:retention", output=self.job
        )
        self.update_job()

    def update_job(self, **changes):
        job = json.loads(self.job.read_text())
        job["scopes"][0].update(
            state="closed", role="attempt-evidence", retention="archive", reason="Completed test"
        )
        job.update(changes)
        self.job.write_text(json.dumps(job))

    def make_plan(self):
        return a.plan(self.root, self.job, self.plan)

    def pack(self):
        return a.pack(self.root, self.plan, self.store, self.receipt)

    def test_dedup_restores_independent_paths_modes_times_and_empty_file(self):
        originals = {
            p.name: (p.read_bytes(), p.stat().st_mode & 0o777, p.stat().st_mtime_ns)
            for p in self.source.iterdir()
        }
        report = self.make_plan()
        self.assertEqual((report["files"], report["objects"]), (3, 2))
        self.assertEqual(report["duplicate_logical_bytes"], len(originals["accepted.html"][0]))
        packed = self.pack()
        self.assertEqual(len(list(self.store.glob("objects/*/*.gz"))), 2)
        self.assertFalse(packed["retirement_authorized"])
        self.assertTrue(a.verify(self.plan, self.store)["verified"])
        restored = self.root / "restored"
        a.restore(self.plan, self.store, restored)
        for name, (data, mode, mtime) in originals.items():
            p = restored / "evidence" / name
            self.assertEqual(
                (p.read_bytes(), p.stat().st_mode & 0o777, p.stat().st_mtime_ns),
                (data, mode, mtime),
            )
            self.assertEqual((self.source / name).read_bytes(), data)
        self.assertNotEqual(
            (restored / "evidence/accepted.html").stat().st_ino,
            (restored / "evidence/failed.html").stat().st_ino,
        )
        self.assertFalse((restored / ".artifact-restore-incomplete").exists())
        second = a.pack(self.root, self.plan, self.store, self.root / "receipt-2.json")
        self.assertEqual(second["added_stored_bytes"], 0)

    def test_recovery_needs_no_original_checkout_or_job(self):
        self.make_plan()
        packed = self.pack()
        self.job.unlink()
        self.plan.unlink()
        for p in self.source.iterdir():
            p.unlink()
        a.restore(Path(packed["manifest"]), self.store, self.root / "recovery")
        self.assertEqual(
            (self.root / "recovery/evidence/accepted.html").read_bytes(),
            b"exact shared bytes\n" * 100,
        )

    def test_sources_changed_after_plan_block_packing(self):
        self.make_plan()
        (self.source / "accepted.html").write_bytes(b"modified")
        with self.assertRaisesRegex(MedicalError, "differs from plan"):
            self.pack()
        self.assertFalse(self.store.exists())

    def test_membership_change_blocks_packing(self):
        self.make_plan()
        (self.source / "new.txt").write_text("new")
        with self.assertRaisesRegex(MedicalError, "membership changed"):
            self.pack()
        self.assertFalse(self.receipt.exists())

    def test_changed_source_during_pack_never_publishes_success(self):
        self.make_plan()
        original = a._check_object

        def check(*args, **kwargs):
            original(*args, **kwargs)
            (self.source / "failed.html").write_text("changed concurrently")

        with (
            mock.patch.object(a, "_check_object", side_effect=check),
            self.assertRaisesRegex(MedicalError, "changed during packing"),
        ):
            self.pack()
        self.assertFalse(self.receipt.exists())
        self.assertFalse(list(self.store.glob("manifests/*.json")))

    def test_corrupt_object_blocks_verify_restore_and_reuse(self):
        self.make_plan()
        self.pack()
        obj = next(self.store.glob("objects/*/*.gz"))
        obj.chmod(0o644)
        obj.write_bytes(b"not gzip")
        with self.assertRaises((OSError, MedicalError)):
            a.verify(self.plan, self.store)
        with self.assertRaises((OSError, MedicalError)):
            a.restore(self.plan, self.store, self.root / "recovery")
        self.assertFalse((self.root / "recovery").exists())
        with self.assertRaises((OSError, MedicalError)):
            a.pack(self.root, self.plan, self.store, self.root / "new-receipt.json")

    def test_default_unknown_active_scope_cannot_pack(self):
        job = json.loads(self.job.read_text())
        job["scopes"] = [{"path": "evidence"}]
        self.job.write_text(json.dumps(job))
        self.make_plan()
        with self.assertRaisesRegex(MedicalError, "closed, classified"):
            self.pack()

    def test_limits_stop_before_hash_or_publication(self):
        for limits in ({"max_files": 2}, {"max_bytes": 1}):
            self.update_job(**limits)
            with (
                mock.patch.object(
                    a, "_read_source", side_effect=AssertionError("hashed too early")
                ),
                self.assertRaisesRegex(MedicalError, "exceeds job limits"),
            ):
                self.make_plan()
            self.assertFalse(self.plan.exists())

    def test_symlinks_and_special_files_are_not_followed(self):
        (self.source / "alias").symlink_to(self.job)
        with self.assertRaisesRegex(MedicalError, "Only regular"):
            self.make_plan()
        (self.source / "alias").unlink()
        os.mkfifo(self.source / "pipe")
        with self.assertRaisesRegex(MedicalError, "Only regular"):
            self.make_plan()

    def test_job_rejects_overlaps_and_traversal(self):
        for paths in (["evidence", "evidence/accepted.html"], ["../escape"], ["."], ["/absolute"]):
            with self.assertRaises(ValidationError):
                a.Job(id="x", owner="x", source_task="x", scopes=[a.Scope(path=p) for p in paths])

    def test_restore_rejects_manifest_path_traversal_duplicate_or_conflict(self):
        self.make_plan()
        original = json.loads(self.plan.read_text())
        for path in ("../escape", "/absolute", "evidence", original["files"][1]["path"]):
            changed = json.loads(json.dumps(original))
            changed["files"][0]["path"] = path
            self.plan.write_text(json.dumps(changed))
            with self.assertRaises(ValidationError):
                a.restore(self.plan, self.store, self.root / "recovery")
        self.assertFalse((self.root / "recovery").exists())

    def test_fresh_destinations_and_store_boundaries(self):
        self.make_plan()
        with self.assertRaisesRegex(MedicalError, "separate"):
            a.pack(self.root, self.plan, self.source / "store", self.receipt)
        self.store.mkdir()
        (self.store / "unknown").write_text("keep")
        with self.assertRaisesRegex(MedicalError, "unmarked"):
            self.pack()
        with self.assertRaisesRegex(MedicalError, "fresh"):
            a.restore(self.plan, self.store, self.source)

    def test_identical_bytes_keep_distinct_scope_roles(self):
        job = json.loads(self.job.read_text())
        common = {"state": "closed", "retention": "keep", "reason": "Exact evidence"}
        job["scopes"] = [
            dict(path="evidence/accepted.html", role="accepted-evidence", **common),
            dict(path="evidence/failed.html", role="attempt-evidence", **common),
        ]
        self.job.write_text(json.dumps(job))
        result = self.make_plan()
        self.assertEqual(result["objects"], 1)
        manifest = storage.read_object(self.plan)
        self.assertEqual(
            [s["role"] for s in manifest["job"]["scopes"]],
            ["accepted-evidence", "attempt-evidence"],
        )
        self.assertEqual([f["scope"] for f in manifest["files"]], [0, 1])

    def test_truncated_or_overlong_object_is_rejected(self):
        import gzip

        self.make_plan()
        self.pack()
        item = storage.read_object(self.plan)["files"][0]
        obj = a._object(self.store, item["sha256"])
        raw = obj.read_bytes()
        obj.chmod(0o644)
        obj.write_bytes(raw[:-5])
        with self.assertRaisesRegex(MedicalError, "Truncated"):
            a.verify(self.plan, self.store)
        obj.write_bytes(gzip.compress(b"x" * (item["bytes"] + 1)))
        with self.assertRaisesRegex(MedicalError, "length exceeds"):
            a.verify(self.plan, self.store)

    def test_restore_interruption_retains_incomplete_marker(self):
        self.make_plan()
        self.pack()
        original = a._check_object

        def fail_on_write(path, digest, size, output=None):
            if output:
                raise OSError("simulated full disk")
            original(path, digest, size, output)

        target = self.root / "partial"
        with (
            mock.patch.object(a, "_check_object", side_effect=fail_on_write),
            self.assertRaises(OSError),
        ):
            a.restore(self.plan, self.store, target)
        self.assertTrue((target / ".artifact-restore-incomplete").is_file())
        self.assertTrue((self.source / "accepted.html").is_file())

    def test_recovery_cli_does_not_require_a_workbench(self):
        self.make_plan()
        packed = self.pack()
        target = self.root / "cli-recovery"
        with (
            mock.patch.object(cli.c, "workspace", side_effect=AssertionError("needs checkout")),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            result = cli.main(
                [
                    "artifacts",
                    "restore",
                    packed["manifest"],
                    "--store",
                    str(self.store),
                    "--output",
                    str(target),
                ]
            )
        self.assertEqual(result, 0)
        self.assertEqual(
            (target / "evidence/accepted.html").read_bytes(),
            (self.source / "accepted.html").read_bytes(),
        )

    def prepare_retirement(self):
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)
        self.make_plan()
        self.pack()
        recovery = self.root / "recovery"
        a.restore(self.plan, self.store, recovery)
        return recovery

    def retire(self, recovery, **kwargs):
        return a.retire(
            self.root,
            self.plan,
            self.store,
            recovery,
            self.root / "retirement",
            expected_sha256=kwargs.get("digest", storage.sha(self.plan)),
            authorization=kwargs.get("authorization", "user:test-request"),
        )

    def test_retirement_keeps_recovery_and_publishes_manifest_mapping(self):
        recovery = self.prepare_retirement()
        result = self.retire(recovery)
        self.assertEqual(result["retired_files"], 3)
        self.assertEqual(list(self.source.iterdir()), [])
        self.assertTrue((recovery / "evidence/accepted.html").is_file())
        self.assertTrue(a.verify(self.plan, self.store)["verified"])
        self.assertTrue((self.root / "retirement/intent.json").is_file())
        self.assertEqual(len((self.root / "retirement/events.jsonl").read_text().splitlines()), 3)

    def test_retirement_rejects_missing_authority_wrong_plan_or_changed_recovery(self):
        recovery = self.prepare_retirement()
        for kwargs in ({"authorization": ""}, {"digest": "0" * 64}):
            with self.assertRaises(MedicalError):
                self.retire(recovery, **kwargs)
        (recovery / "evidence/accepted.html").write_bytes(b"wrong")
        with self.assertRaisesRegex(MedicalError, "Restored occurrence differs"):
            self.retire(recovery)
        self.assertEqual(len(list(self.source.iterdir())), 3)
        self.assertFalse((self.root / "retirement").exists())

    def test_retirement_rejects_tracked_files(self):
        recovery = self.prepare_retirement()
        subprocess.run(["git", "-C", str(self.root), "add", "evidence/accepted.html"], check=True)
        with self.assertRaisesRegex(MedicalError, "Tracked files"):
            self.retire(recovery)
        self.assertEqual(len(list(self.source.iterdir())), 3)

    def test_explicit_exclusions_preserve_referenced_files_and_symlinks(self):
        (self.source / "link").symlink_to(self.job)
        job = json.loads(self.job.read_text())
        job["scopes"][0]["exclusions"] = {
            "evidence/link": "External environment remains local",
            "evidence/accepted.html": "Live evidence reference",
        }
        self.job.write_text(json.dumps(job))
        recovery = self.prepare_retirement()
        self.assertEqual(storage.read_object(self.plan)["files"][0]["path"], "evidence/empty.json")
        self.retire(recovery)
        self.assertTrue((self.source / "accepted.html").is_file())
        self.assertTrue((self.source / "link").is_symlink())

    def test_cli_init_and_plan_are_usable(self):
        (self.root / "workbench.toml").write_text("")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = cli.main(
                [
                    "--root",
                    str(self.root),
                    "artifacts",
                    "plan",
                    str(self.job),
                    "--output",
                    str(self.plan),
                ]
            )
        self.assertEqual(result, 0)
        self.assertEqual(json.loads(output.getvalue())["files"], 3)
        self.assertEqual(storage.read_object(self.plan)["job"]["source_task"], "test:retention")
