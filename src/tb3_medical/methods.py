"""The two maintained experiment methods behind the CLI and workflow services.

Adapters own task-specific preparation, scoring and views. The workflow retains
ownership of execution, provenance and review records. Selection is explicit;
adding a method requires implementing this interface and adding one factory case.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from . import core, landmarks, score_ct, score_mri, task_package
from .types import Document, Pathish


class ExperimentMethod(Protocol):
    def prepare(
        self,
        spec: Document,
        execute: bool,
        *,
        input_root: Pathish | None = None,
        output: Pathish | None = None,
    ) -> Document: ...

    def evaluate(self, case: str, answer: Pathish, python: str) -> Document: ...

    def replay(self, case: str | None, python: str) -> Document: ...

    def view(self, case: str, output: Pathish | None) -> Document: ...


@dataclass(frozen=True)
class LandmarkMethod:
    root: Path
    experiment: Document

    def prepare(
        self,
        spec: Document,
        execute: bool,
        *,
        input_root: Pathish | None = None,
        output: Pathish | None = None,
    ) -> Document:
        if input_root is not None or output is not None:
            raise core.MedicalError(
                "Use med bundle with --input-root for a portable landmark recovery; "
                "native prepare uses its declared landmark inputs"
            )
        return landmarks.prepare_case(self.root, self.experiment, spec, execute)

    def evaluate(self, case: str, answer: Pathish, python: str) -> Document:
        inputs = landmarks.case_inputs(self.root, self.experiment, case)
        truth = next(e for e in inputs["files"] if e["destination"] == "tests/truth.json")
        core.verify_inputs(self.root, [truth])
        score = score_mri.score if inputs["scorer"] == "mri" else score_ct.score
        return score(
            core.read(Path(answer) / "landmarks.json"),
            core.read(core.inside(self.root, truth["path"])),
        )

    def replay(self, case: str | None, python: str) -> Document:
        return landmarks.replay(self.root, self.experiment, case)

    def view(self, case: str, output: Pathish | None) -> Document:
        return landmarks.view(self.root, self.experiment, case, output)


@dataclass(frozen=True)
class PackageMethod:
    root: Path
    experiment: Document

    def _bundle(self, case: str) -> Path:
        identity: str = self.experiment["id"]
        return self.root / ".local/reproduction" / identity / case

    def prepare(
        self,
        spec: Document,
        execute: bool,
        *,
        input_root: Pathish | None = None,
        output: Pathish | None = None,
    ) -> Document:
        destination = output or self._bundle(spec["id"])
        recipe = self.experiment["reproduction_manifest"]
        if not execute:
            manifest = core.read(core.inside(self.root, recipe))
            selected = [e for e in manifest["files"] if e.get("case") in (None, spec["id"])]
            return {
                "case": spec["id"],
                "destination": str(destination),
                "executed": False,
                "files": len(selected),
                "bytes": sum(e["size"] for e in selected),
                "acquisition": str(Path(recipe).parent / "acquisition.md"),
            }
        return task_package.materialize(
            self.root, recipe, destination, case=spec["id"], input_root=input_root
        )

    def evaluate(self, case: str, answer: Pathish, python: str) -> Document:
        bundle = self._bundle(case)
        return task_package.evaluate(
            bundle, core.read(bundle / "manifest.json"), case, answer, python
        )

    def replay(self, case: str | None, python: str) -> Document:
        # The workflow owns append-only replay observations, not this adapter.
        from .workflow import replay_package

        cases = [case] if case else [task["id"] for task in self.experiment["tasks"]]
        outputs = []
        for name in cases:
            bundle = self._bundle(name)
            outputs.append(
                replay_package(
                    self.root,
                    self.experiment,
                    bundle,
                    core.read(bundle / "manifest.json"),
                    name,
                    python,
                )
            )
        return {"cases": outputs, "all_match": all(item["all_match"] for item in outputs)}

    def view(self, case: str, output: Pathish | None) -> Document:
        bundle = self._bundle(case)
        result = task_package.inspect(
            bundle,
            core.read(bundle / "manifest.json"),
            case,
            output or self.root / ".local/views" / f"{self.experiment['id']}-{case}.html",
        )
        return {"cases": [result]}


def method_for(root: Pathish, experiment: Document) -> ExperimentMethod:
    """Resolve only maintained methods; historical records are not executable."""
    match experiment.get("method"):
        case "landmarks":
            return LandmarkMethod(Path(root), experiment)
        case "task_package":
            return PackageMethod(Path(root), experiment)
        case _:
            raise core.MedicalError("No maintained method is declared for this experiment")
