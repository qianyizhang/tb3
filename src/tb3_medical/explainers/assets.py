"""Resolve the selected asset closure without acquiring or interpreting medical data."""

from pathlib import Path
from typing import cast

from .. import storage
from ..presentation_contracts import ExplainerAsset, ExplainerBundle


def check_dependencies(root: Path, dependencies: dict[str, str]) -> None:
    for name, expected in dependencies.items():
        if storage.sha(storage.inside(root, name)) != expected:
            raise ValueError(f"Compiled story dependency changed: {name}")


def symbolic_bundle(root: Path, pack_id: str) -> tuple[ExplainerBundle, Path]:
    index = storage.read(root / "presentation/assets/teaching-prefabs.json")
    path = storage.inside(root, index["packs"][pack_id]["manifest"])
    manifest = storage.read(path)
    if (
        manifest["id"] != pack_id
        or manifest["source_class"] != "symbolic-protocol"
        or manifest["reference_policy"] != "no-reference-assets"
    ):
        raise ValueError("Restoration requires a symbolic bundle without reference assets")
    roles = {
        "source.json": "input-contract",
        "helper.json": "helper-contract",
        "operation.json": "operation-contract",
        "output.json": "output-contract",
        "NOTICE.md": "license",
        "DATA-LICENSE.txt": "license",
    }
    if len(manifest["assets"]) != len(roles) or {
        asset["file"] for asset in manifest["assets"]
    } != set(roles):
        raise ValueError("Restoration bundle must contain exactly its six declared records")
    assets: list[ExplainerAsset] = []
    for asset in manifest["assets"]:
        source = storage.inside(path.parent, asset["file"])
        if (
            asset["role"] != "illustration"
            or asset["provenance"] != "symbolic-protocol"
            or storage.sha(source) != asset["sha256"]
            or source.stat().st_size != asset["bytes"]
        ):
            raise ValueError(f"Changed restoration asset: {source.name}")
        assets.append(
            cast(
                ExplainerAsset,
                {
                    "path": source.relative_to(root).as_posix(),
                    "sha256": asset["sha256"],
                    "bytes": asset["bytes"],
                    "role": roles[source.name],
                },
            )
        )
    return {
        "id": pack_id,
        "basis": "symbolic-protocol",
        "reference_policy": "no-reference-assets",
        "units": manifest["units"],
        "coordinates": manifest["frame"],
        "license": manifest["license"],
        "notice": (path.parent / "NOTICE.md").read_text(),
        "license_text": (path.parent / "DATA-LICENSE.txt").read_text(),
        "assets": assets,
    }, path
