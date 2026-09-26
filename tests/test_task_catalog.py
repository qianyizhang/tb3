"""Taxonomy integrity and ownership, independent of scientific outcomes."""

import json
import tempfile
import unittest
from pathlib import Path

from tb3_medical import task_briefs, task_catalog
from tb3_medical.errors import MedicalError


class TaskCatalogTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))

    def fixture(self):
        self.write(
            "taxonomy.json",
            {
                "categories": {
                    "segmentation": {"title": "Segment"},
                    "data-engineering": {"title": "Decode"},
                },
                "roles": {"task": "Agent task", "tool-calibration": "Tool calibration"},
                "agent_work": {"direct": "Solve a case", "none": "No agent task"},
            },
        )
        self.entry = {
            "id": "segment",
            "category": "segmentation",
            "role": "task",
            "agent_work": "direct",
            "owner_group": "anatomy",
            "repository_id": "tb3",
            "brief": "brief.md",
            "experiments": [{"id": "anatomy-study", "scope": "One supplied CT, original contract"}],
        }
        self.write("leaf.json", {"entries": [self.entry]})
        self.write(
            "catalog.json",
            {
                "taxonomy": "taxonomy.json",
                "collections": ["leaf.json"],
                "require_experiment_coverage": True,
            },
        )
        folder = self.root / "groups/anatomy/experiments/study"
        folder.mkdir(parents=True)
        (folder / "experiment.toml").write_text(
            'id="anatomy-study"\ngroup_id="anatomy"\ntitle="A study"\nprotocol="protocol.md"\n'
            '[[tasks]]\nid="native-case"\n'
        )
        (folder / "protocol.md").write_text("# Exact retained protocol\n")
        return folder

    def load(self):
        data = task_catalog.collection(self.root, "catalog.json")
        task_catalog.classify(self.root, data)
        return data

    def test_composition_resolves_experiments_without_mutating_them(self):
        folder = self.fixture()
        before = {p: p.read_bytes() for p in folder.iterdir()}
        data = self.load()
        study = data["entries"][0]["studies"][0]
        self.assertEqual(study["tasks"], ["native-case"])
        self.assertEqual(study["protocol"], "groups/anatomy/experiments/study/protocol.md")
        self.assertEqual(before, {p: p.read_bytes() for p in folder.iterdir()})
        duplicate = folder.parent / "duplicate"
        duplicate.mkdir()
        (duplicate / "experiment.toml").write_bytes((folder / "experiment.toml").read_bytes())
        with self.assertRaisesRegex(MedicalError, "Duplicate experiment ID"):
            self.load()

    def test_no_orphan_experiment_and_no_silent_unclassified_entry(self):
        self.fixture()
        for field, value, message in (
            ("category", "Anatomy", "category"),
            ("role", "completed", "role"),
            ("agent_work", "fast", "agent_work"),
            ("operations", ["made-up"], "secondary operations"),
            ("operations", ["segmentation"], "secondary operations"),
            ("owner_group", "another", "another research owner"),
            ("experiments", [], "missing task navigation"),
            ("experiments", [{"id": "BR-025", "scope": "ambiguous alias"}], "unscoped experiment"),
            ("experiments", [{"id": "anatomy-study"}], "unscoped experiment"),
        ):
            with self.subTest(field=field, value=value):
                self.write("leaf.json", {"entries": [{**self.entry, field: value}]})
                with self.assertRaisesRegex(MedicalError, message):
                    self.load()

    def test_supporting_role_is_not_an_agent_task_and_many_scoped_links_are_allowed(self):
        self.fixture()
        support = {**self.entry, "id": "calibration", "role": "tool-calibration"}
        self.write("leaf.json", {"entries": [self.entry, support]})
        with self.assertRaisesRegex(MedicalError, "supporting research"):
            self.load()
        support["agent_work"] = "none"
        support["experiments"] = [
            {"id": "anatomy-study", "scope": "Calibration portion of mixed study"}
        ]
        self.write("leaf.json", {"entries": [self.entry, support]})
        self.assertEqual(len(self.load()["entries"]), 2)

    def test_family_cannot_silently_merge_different_operations(self):
        self.fixture()
        self.entry["task_family"] = "related"
        other = {**self.entry, "id": "decoder", "category": "data-engineering"}
        leaf = {
            "entries": [self.entry, other],
            "task_families": {"related": {"title": "Related", "selector": "Contract"}},
        }
        self.write("leaf.json", leaf)
        with self.assertRaisesRegex(MedicalError, "crosses repository or task axes"):
            self.load()
        leaf["task_families"] = {}
        self.write("leaf.json", leaf)
        with self.assertRaisesRegex(MedicalError, "unknown or incomplete task family"):
            self.load()

    def test_collection_cycles_conflicts_and_parent_scaffolding_fail(self):
        self.fixture()
        self.write("leaf.json", {"collections": ["catalog.json"]})
        with self.assertRaisesRegex(MedicalError, "cycle"):
            self.load()
        self.write(
            "leaf.json", {"task_families": {"x": {"title": "First"}}, "collections": ["other.json"]}
        )
        self.write("other.json", {"task_families": {"x": {"title": "Different"}}})
        with self.assertRaisesRegex(MedicalError, "Conflicting catalogue"):
            self.load()
        with self.assertRaisesRegex(MedicalError, "group-owned leaf"):
            task_briefs.new(
                self.root, "new", "Task", "Repo", "segmentation", "new.md", "catalog.json"
            )
        self.assertFalse((self.root / "new.md").exists())
