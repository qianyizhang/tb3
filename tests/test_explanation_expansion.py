"""Discriminated scripts retain v1 and fail closed at new source/recipe boundaries."""

import copy
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories
from tb3_medical import task_briefs

ROOT = Path(__file__).resolve().parents[1]


class ExpansionTests(unittest.TestCase):
    def test_all_expansion_sources_and_projection(self):
        for path in [
            *ROOT.glob("groups/*/presentation/stories/*.story.md"),
            *ROOT.glob("presentation/external-tasks/stories/*.story.md"),
        ]:
            plan = stories.compile_story(ROOT, path)
            self.assertEqual(plan["beats"][-1]["endFrame"], plan["durationFrames"])
            if plan["recipe"] == "imaging-ultrasound-sos-v1":
                self.assertEqual(plan["reference_policy"], "no-reference-assets")
                self.assertTrue(
                    all(b["channels"]["reference"] == [0.0, 0.0] for b in plan["beats"])
                )
            self.assertEqual(
                plan["reference_policy"],
                "reader-reference-reveal"
                if plan["recipe"]
                in {
                    "automed-medxpert-mm-v1",
                    "imaging101-poisson-v1",
                    "imaging101-photoacoustic-tomography-v1",
                    "imaging101-varnet-v1",
                    "imaging101-sense-v1",
                    "imaging101-noncartesian-v1",
                    "imaging101-pnp-admm-v1",
                    "imaging101-t2-mapping-v1",
                    "imaging101-pet-mlem-v1",
                    "imaging101-plane-wave-ultrasound-v1",
                    "imaging101-pnp-mri-reconstruction-v1",
                    "imaging101-usct-fwi-v1",
                    "imaging101-wavelet-v1",
                    "bcer-superres-v1",
                    "automed-kvasir-v1",
                    "automed-pathvqa-v1",
                    "automed-omni-v1",
                    "bcer-denoise-v1",
                    "bcer-grappa-v1",
                    "automed-slake-v1",
                    "mixed-tissue-v1",
                    "prototype-identity-v1",
                    "mask-screen-v1",
                    "anatomy-curation-v1",
                    "ct-context-v1",
                    "imaging101-eht-original-v1",
                    "imaging101-eht-features-dynamic-v1",
                    "imaging101-eht-dynamic-v1",
                    "imaging101-eht-uq-v1",
                    "imaging101-dti-v1",
                    "imaging101-deflectometry-v1",
                    "imaging101-fan-beam-v1",
                    "imaging101-dual-energy-v1",
                    "imaging101-ptychography-v1",
                    "imaging101-nlos-v1",
                    "imaging101-cars-v1",
                    "rex-topcow-v1",
                    "automed-multiorgan-v1",
                    "abra-annotation-v1",
                    "history-sourcing-v1",
                    "mri-importer-v1",
                    "localized-ct-v1",
                    "aneurysm-localization-v1",
                    "segmentation-calibration-v1",
                    "dental-v3-v1",
                    "dental-v2-v1",
                    "dental-original-v1",
                    "ct-organ-v1",
                    "named-landmarks-v1",
                    "cardiac-contour-v1",
                    "cardiac-anchor-v1",
                    "automed-full-spleen-v1",
                    "automed-full-kidney-v1",
                    "automed-full-liver-v1",
                    "cardiac-material-v1",
                    "automed-full-heart-seg-v1",
                    "automed-full-colon-seg-v1",
                    "automed-full-aeropath-seg-v1",
                    "automed-full-grazpedwri-detection-v1",
                    "automed-full-dentex-detection-v1",
                    "automed-full-bccd-detection-v1",
                    "rex-topcow-mr-edges-v1",
                    "rex-topcow-ct-edges-v1",
                    "rex-topcow-mr-box-v1",
                    "rex-topcow-ct-box-v1",
                    "rex-topcow-mr-seg-v1",
                    "rex-isles22-v1",
                    "rexmle-dentex-v1",
                    "abra-longitudinal-v1",
                    "automed-kidney-v1",
                    "report-reading-v1",
                    "cardiac-mask-mechanics-v1",
                    "cardiac-real-echo-v1",
                    "clinical-cavity-v1",
                    "respiratory-v1",
                    "registration-analysis-v1",
                    "resect-correspondence-v1",
                    "resect-pilot-v1",
                    "vessel-source-v1",
                    "airway-repair-v1",
                    "topbrain-screen-v1",
                    "hubmap-inventory-v1",
                    "tiger-context-v1",
                    "longitudinal-mri-v1",
                    "longitudinal-ct-original-v1",
                    "longitudinal-ct-revised-v1",
                }
                else "no-reference-assets",
            )
            if plan["schema"] == 2:
                for locator in plan["source_locators"]:
                    self.assertIn(locator, plan["dependencies"])
                self.assertNotIn("BR030", plan["scope"])

    def test_recipe_channels_and_continuity_fail_closed(self):
        path = ROOT / "groups/registration/presentation/stories/rigid-correspondence.story.md"
        raw = path.read_text().replace("frames:", "show_deformed_target: false\nframes:")
        for bad in [
            raw.replace("schema: 2", "schema: 2\nunknown: true"),
            raw.replace("locale: en", "locale: en\nlocale: en"),
            raw.replace("frames: 120", "frames: true", 1),
            raw.replace("transform:", "route:", 1),
            raw.replace("recipe: correspondence-v1", "recipe: missing"),
            raw.replace("no-reference-assets", "include-reference"),
        ]:
            with self.assertRaises(ValueError):
                stories.parse_expansion(bad)
        model = stories.parse_expansion(raw)
        data = copy.deepcopy(model.model_dump())
        data["beats"][1]["channels"]["transform"] = (0.5, 1.0)
        with self.assertRaises(ValueError):
            type(model).model_validate(data)

    def test_source_screen_scene_changes_require_explicit_cuts(self):
        for group, name in [
            (None, "imaging101-eht-original"),
            (None, "imaging101-eht-features-dynamic"),
            (None, "imaging101-eht-dynamic"),
            (None, "imaging101-eht-uq"),
            (None, "imaging101-dti"),
            (None, "imaging101-deflectometry"),
            (None, "imaging101-fan-beam"),
            (None, "imaging101-dual-energy"),
            (None, "imaging101-ptychography"),
            (None, "imaging101-nlos"),
            (None, "imaging101-cars"),
            (None, "rex-topcow"),
            (None, "automed-multiorgan"),
            (None, "bcer-workflow"),
            (None, "abra-annotation"),
            ("anatomy-audit", "mask-reasoning-study"),
            ("anatomy-audit", "anatomy-curation"),
            ("anatomy-audit", "history-sourcing"),
            ("anatomy-audit", "mri-importer"),
            ("longitudinal-reading", "ct-context"),
            ("longitudinal-reading", "localized-ct"),
            ("lesion-localization", "aneurysm-localization"),
            ("anatomy-audit", "segmentation-calibration"),
            ("anatomy-audit", "dental-v3"),
            ("anatomy-audit", "dental-v2"),
            ("anatomy-audit", "dental-original"),
            ("anatomy-audit", "ct-organ-segmentation"),
            ("anatomical-landmarks", "named-landmarks"),
            ("cardiac-motion", "cardiac-contour-feasibility"),
            ("cardiac-motion", "cardiac-anchor-feasibility"),
            ("cardiac-motion", "cardiac-material-feasibility"),
            (None, "automedbench-full-heart-seg-task"),
            (None, "automedbench-full-feta-seg-task"),
            (None, "automedbench-full-colon-seg-task"),
            (None, "automedbench-full-hepaticvessel-seg-task"),
            (None, "automedbench-full-kidney-seg-task"),
            (None, "automedbench-full-liver-seg-task"),
            (None, "automedbench-full-pancreas-oar-seg-task"),
            (None, "automedbench-full-pancreas-seg-task"),
            (None, "automedbench-full-panther-t1-seg-task"),
            (None, "automedbench-full-panther-t2-seg-task"),
            (None, "automedbench-full-prostate-seg-task"),
            (None, "automedbench-full-spleen-seg-task"),
            (None, "automedbench-full-tsg-multiorgan-seg-task"),
            (None, "healthagentbench"),
            (None, "radagent"),
            (None, "healthagentbench-tumor-tiles"),
            (None, "healthagentbench-cxr-correction"),
            (None, "bcer-medium-brain-grade-classify"),
            (None, "bcer-long-cardiac-full"),
            (None, "bcer-long-brain-full"),
            (None, "automedbench-full-aeropath-seg-task"),
            (None, "automedbench-full-vindr-cxr-det-task"),
            (None, "automedbench-full-grazpedwri-det-task"),
            (None, "automedbench-full-dentex-det-task"),
            (None, "automedbench-full-bccd-det-task"),
            (None, "rexmle-topcow-track2-task3"),
            (None, "rexmle-topcow-track1-task3"),
            (None, "rexmle-topcow-track2-task2"),
            (None, "rexmle-topcow-track1-task2"),
            (None, "rexmle-topcow-track2-task1"),
            (None, "rexmle-topbrain-track2"),
            (None, "rexmle-topbrain-track1"),
            (None, "rexmle-seg-a"),
            (None, "rexmle-puma-track2-task2"),
            (None, "rexmle-puma-track1-task2"),
            (None, "rexmle-puma-track1-task1"),
            (None, "rexmle-panther-task2"),
            (None, "rexmle-panther-task1"),
            (None, "rexmle-neurips-cellseg"),
            (None, "rexmle-isles22"),
            (None, "rexmle-dentex"),
            (None, "abra-longitudinal"),
            (None, "bcer-medium-register-prostate"),
            (None, "bcer-short-segment-brain"),
            (None, "automedbench"),
            ("longitudinal-reading", "report-backed-reading"),
            ("cardiac-motion", "mask-to-mechanics"),
            ("cardiac-motion", "real-echo-reconstruction"),
            ("cardiac-motion", "clinical-cavity-adaptation"),
            ("registration", "respiratory-correspondence"),
            ("registration", "registration-failure-analysis"),
            ("registration", "resect-point-correspondence"),
            ("registration", "resect-point-pilot"),
            ("tubular-anatomy", "vessel-source-screen"),
            ("tubular-anatomy", "airway-repair"),
            ("tubular-anatomy", "topbrain-screen"),
            ("lesion-localization", "hubmap-inventory"),
            ("lesion-localization", "tiger-context"),
            ("longitudinal-reading", "longitudinal-mri"),
            ("longitudinal-reading", "longitudinal-ct-original"),
            ("longitudinal-reading", "longitudinal-ct-revised"),
        ]:
            path = ROOT / (
                f"groups/{group}/presentation/stories/{name}.story.md"
                if group
                else f"presentation/external-tasks/stories/{name}.story.md"
            )
            model = stories.parse_expansion(path.read_text())
            data = copy.deepcopy(model.model_dump(by_alias=True))
            index = next(
                i
                for i, beat in enumerate(data["beats"])
                if i and beat["scene"] != data["beats"][i - 1]["scene"]
            )
            data["beats"][index]["cut"] = "continuous"
            # Hold numeric channels continuous so only the scene boundary is invalid.
            for beat in data["beats"]:
                beat["channels"] = dict.fromkeys(beat["channels"], (0.0, 0.0))
            with self.assertRaisesRegex(ValueError, "Changing source scenes"):
                type(model).model_validate(data)

    def test_curation_pack_rejects_wrong_source_terms(self):
        import json
        from unittest.mock import patch

        path = ROOT / "presentation/task-explorer/anatomy-curation/manifest.json"
        for key in ("license", "label_license"):
            manifest = json.loads(path.read_text())
            manifest[key] = "CC-BY-4.0"
            with patch.object(stories.json, "loads", return_value=manifest):
                with self.assertRaisesRegex(ValueError, "exact provenance, terms"):
                    stories.resolve_assets(ROOT, "retained-anatomy-curation-v1")

    def test_respiratory_pack_rejects_mislabeled_frame_and_terms(self):
        import json
        from unittest.mock import patch

        for name in [
            "respiratory",
            "registration-analysis",
            "segmentation-calibration",
            "ct-context",
            "imaging101-eht-original",
            "imaging101-eht-features-dynamic",
            "imaging101-eht-dynamic",
            "imaging101-eht-uq",
            "imaging101-dti",
            "imaging101-deflectometry",
            "imaging101-fan-beam",
            "imaging101-dual-energy",
            "imaging101-ptychography",
            "imaging101-nlos",
            "imaging101-cars",
            "rex-topcow",
            "automed-multiorgan",
            "bcer-workflow",
            "abra-annotation",
            "history-sourcing",
            "mri-importer",
            "localized-ct",
            "aneurysm-localization",
            "dental-v3",
            "dental-original",
            "ct-organ",
            "named-landmarks",
            "resect",
            "resect-pilot",
            "vessel-source",
            "airway-repair",
            "topbrain-screen",
            "hubmap-inventory",
            "tiger-context",
            "longitudinal-mri",
            "longitudinal-ct-original",
            "longitudinal-ct-revised",
        ]:
            path = ROOT / f"presentation/task-explorer/{name}/manifest.json"
            for key, value in [
                (
                    "frame",
                    "RAS"
                    if name in {"mri-importer", "abra-annotation", "bcer-workflow"}
                    else "LPS",
                ),
                (
                    "label_license",
                    "CC0-1.0" if name in {"ct-organ", "segmentation-calibration"} else "Apache-2.0",
                ),
                (
                    "units",
                    "mm"
                    if name in {"hubmap-inventory", "tiger-context", "imaging101-fan-beam"}
                    else "px",
                ),
            ]:
                manifest = json.loads(path.read_text())
                manifest[key] = value
                with patch.object(stories.json, "loads", return_value=manifest):
                    with self.assertRaisesRegex(ValueError, "exact provenance, terms"):
                        stories.resolve_assets(ROOT, f"retained-{name}-v1")

    def test_isles_reference_images_cannot_be_reclassified_as_input(self):
        import json
        from unittest.mock import patch

        path = ROOT / "presentation/task-explorer/rex-isles22/manifest.json"
        for target, bad_role in [
            ("images/reference-mask-04.png", "illustration"),
            ("images/dwi-04.png", "reader-reference-reveal"),
        ]:
            manifest = json.loads(path.read_text())
            asset = next(a for a in manifest["assets"] if a["file"] == target)
            asset["role"] = bad_role
            with self.subTest(asset=target):
                with patch.object(stories.json, "loads", return_value=manifest):
                    with self.assertRaisesRegex(
                        ValueError, "incorrectly classified source teaching asset"
                    ):
                        stories.resolve_assets(ROOT, "retained-rex-isles22-v1")

    def test_topcow_reference_images_cannot_be_reclassified_as_input(self):
        import json
        from unittest.mock import patch

        path = ROOT / "presentation/task-explorer/rex-vascular-topcow-mr-seg/manifest.json"
        for target, bad_role in [
            ("images/reference-04.png", "illustration"),
            ("images/input-04.png", "reader-reference-reveal"),
        ]:
            manifest = json.loads(path.read_text())
            asset = next(a for a in manifest["assets"] if a["file"] == target)
            asset["role"] = bad_role
            with self.subTest(asset=target):
                with patch.object(stories.json, "loads", return_value=manifest):
                    with self.assertRaisesRegex(
                        ValueError, "incorrectly classified source teaching asset"
                    ):
                        stories.resolve_assets(ROOT, "retained-rex-topcow-mr-seg-v1")

    def test_topcow_roi_reference_images_cannot_be_reclassified_as_input(self):
        import json
        from unittest.mock import patch

        path = ROOT / "presentation/task-explorer/rex-topcow-ct-box/manifest.json"
        for target, bad_role in [
            ("images/reference-roi-04.png", "illustration"),
            ("images/input-04.png", "reader-reference-reveal"),
        ]:
            manifest = json.loads(path.read_text())
            asset = next(a for a in manifest["assets"] if a["file"] == target)
            asset["role"] = bad_role
            with self.subTest(asset=target):
                with patch.object(stories.json, "loads", return_value=manifest):
                    with self.assertRaisesRegex(
                        ValueError, "incorrectly classified source teaching asset"
                    ):
                        stories.resolve_assets(ROOT, "retained-rex-topcow-ct-box-v1")

    def test_public_input_pack_has_no_hidden_reference(self):
        import json
        from unittest.mock import patch

        manifest = json.loads(
            (ROOT / "presentation/task-explorer/bcer-workflow/manifest.json").read_text()
        )
        self.assertTrue(all(a["role"] == "illustration" for a in manifest["assets"]))
        manifest["reference_policy"] = "reader-reference-reveal"
        with patch.object(stories.json, "loads", return_value=manifest):
            with self.assertRaisesRegex(ValueError, "exact provenance, terms"):
                stories.resolve_assets(ROOT, "retained-bcer-workflow-v1")

    def test_nested_planar_binding_survives_projection(self):
        data = task_briefs.load(ROOT)
        for entry_id, story_id in [
            ("wsi-hiesd-patches", "wsi-patches"),
            ("wsi-hiesd-map", "wsi-coverage"),
        ]:
            entry = next(e for e in data["entries"] if e["id"] == entry_id)
            self.assertEqual(entry["illustration"]["story_id"], story_id)
            self.assertEqual(data["explanation_stories"][story_id]["recipe"], "multiscale-v1")
            self.assertTrue(entry["reference"])

    def test_legacy_compatibility_is_source_pinned_and_new_semantics_are_explicit(self):
        import json
        import tempfile

        import yaml

        baseline = json.loads((ROOT / "tests/fixtures/story-baseline.json").read_text())
        for witness in baseline["stories"]:
            path = ROOT / witness["source"]
            plan = stories.compile_story(ROOT, path)
            self.assertEqual(plan["source_sha256"], witness["source_sha256"])
            if witness["source"] not in stories.LEGACY_SEMANTICS:
                continue
            with self.subTest(story=plan["id"]):
                raw = path.read_text()
                with self.assertRaises(ValueError):
                    stories.parse_expansion(raw)
                document = stories.parse_document(raw)
                header = dict(document.header)
                beats = [dict(beat) for beat in document.beats]
                if plan["recipe"] == "correspondence-v1":
                    for beat, compiled in zip(beats, plan["beats"], strict=True):
                        beat["show_deformed_target"] = compiled["show_deformed_target"]
                else:
                    header["operation"] = plan["operation"]
                explicit = stories.parse_expansion(stories.StoryDocument(header, tuple(beats)))
                header["id"] = "renamed-story"
                for i, beat in enumerate(beats):
                    beat["id"] = f"renamed-{i}"
                renamed = stories.parse_expansion(stories.StoryDocument(header, tuple(beats)))
                self.assertEqual(
                    [beat.channels for beat in explicit.beats],
                    [beat.channels for beat in renamed.beats],
                )
                with tempfile.TemporaryDirectory(dir=ROOT / ".local") as temp:
                    draft = Path(temp) / path.name
                    draft.write_text(raw)
                    with self.assertRaises(ValueError):
                        stories.compile_story(ROOT, draft)
                    # Copying a familiar ID never activates compatibility, even at a new path.
                    text = "---\n" + yaml.safe_dump(header) + "---\n"
                    text += "\n".join("```beat\n" + yaml.safe_dump(b) + "```" for b in beats)
                    draft.write_text(text)
                    self.assertEqual(stories.compile_story(ROOT, draft)["id"], "renamed-story")
                bad = dict(header, operation="unsupported")
                with self.assertRaises(ValueError):
                    stories.parse_expansion(stories.StoryDocument(bad, tuple(beats)))

    def test_malformed_document_and_fenced_examples(self):
        raw = (ROOT / "presentation/external-tasks/stories/ct-forward.story.md").read_text()
        original = stories.parse_expansion(raw)
        self.assertEqual(stories.parse_expansion(raw.replace("\n", "\r\n")), original)
        example = "\n````markdown\n```beat\nnot: a real beat\n```\n````\n"
        self.assertEqual(stories.parse_expansion(raw + example), original)
        for bad in (
            "---\n[]\n---\n",
            "---\nnull\n---\n",
            raw + "\n```beat\n[]\n```\n",
            raw + "\n```beat\nnull\n```\n",
            raw.replace("  observations:\n", "  observations: [0, 0]\n  observations:\n", 1),
            raw + "\n```beat \nid: unfinished\n```\n",
            raw + "\n```beat\nid: unclosed\n",
        ):
            with self.subTest(raw=bad[-120:]), self.assertRaises(ValueError):
                stories.parse_expansion(bad)
