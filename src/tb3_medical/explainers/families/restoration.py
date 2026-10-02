"""One restoration family, with scientific differences kept in authored records."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, StrictInt

from ... import storage
from ...presentation_contracts import (
    RestorationGeometry,
    RestorationView,
    StoryPlan,
    validate_explainer_view,
)
from ..assets import check_dependencies, symbolic_bundle

DEFINITIONS = "presentation/explainers/restoration.json"


class Definition(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    label: str = Field(min_length=1)
    pack: str = Field(min_length=1)
    geometry: RestorationGeometry


class Definitions(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: StrictInt = Field(alias="schema", ge=1, le=1)
    definitions: dict[str, Definition]


def compile_view(root: Path, plan: StoryPlan) -> RestorationView | None:
    definitions = Definitions.model_validate(storage.read(root / DEFINITIONS))
    definition = definitions.definitions.get(plan["recipe"])
    if definition is None:
        return None
    check_dependencies(root, plan["dependencies"])
    if plan["asset_pack"] != definition.pack or plan["reference_policy"] != "no-reference-assets":
        raise ValueError("Restoration definition and story asset/reference binding differ")
    if [beat.get("scene") for beat in plan["beats"]] != [
        "input",
        "helper",
        "operation",
        "output",
        "limits",
    ]:
        raise ValueError("Restoration requires the five ordered protocol chapters")
    bundle, manifest = symbolic_bundle(root, definition.pack)
    records = {
        name: storage.read(manifest.parent / (name + ".json"))
        for name in ("source", "helper", "operation", "output")
    }
    # These remain contract records, never fabricated input/output/reference pixels.
    for name, absent_fields in {
        "source": ("pixels", "private_reference", "native_geometry", "patient"),
        "helper": ("reference", "weights"),
        "output": ("prediction", "reference", "score", "shape"),
    }.items():
        if any(records[name][field] is not None for field in absent_fields):
            raise ValueError(f"Unexpected observed evidence in symbolic {name}")
    if records["operation"]["executed"] is not False or len(records["operation"]["steps"]) != 4:
        raise ValueError("Restoration describes four unexecuted protocol steps")
    fields = {
        "source": ("notice", "input", "units", "simulation", "excluded"),
        "helper": ("lite", "standard", "window", "source_claims"),
        "operation": ("steps", "limitations"),
        "output": ("path", "format", "coverage", "boundary", "rules"),
    }
    dependencies = dict(plan["dependencies"])
    paths = [root / DEFINITIONS, manifest, root / "src/tb3_medical/presentation_contracts.py"]
    paths.extend((root / "src/tb3_medical/explainers").rglob("*.py"))
    dependencies.update({path.relative_to(root).as_posix(): storage.sha(path) for path in paths})
    dependencies.update({asset["path"]: asset["sha256"] for asset in bundle["assets"]})
    check_dependencies(root, dependencies)
    return validate_explainer_view(
        {
            "family": "restoration-protocol",
            "version": 1,
            "label": definition.label,
            **{name: {key: records[name][key] for key in keys} for name, keys in fields.items()},
            "geometry": definition.geometry,
            "bundle": bundle,
            "dependencies": dependencies,
        }
    )
