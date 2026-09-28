"""Compile group-owned explanation scripts; no model calls or validator I/O."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Annotated, Literal, Self, cast

import yaml  # type: ignore[import-untyped]
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    TypeAdapter,
    model_validator,
)

from . import storage
from .errors import MedicalError
from .presentation_contracts import StoryBeat, StoryPlan
from .types import Document

# Explicit compiler identity stays with selected plans, not renderer bundle freshness.
COMPILER_SOURCES = (
    "src/tb3_medical/explanation_stories.py",
    "src/tb3_medical/presentation_contracts.py",
    "src/tb3_medical/storage.py",
    "src/tb3_medical/errors.py",
    "src/tb3_medical/types.py",
    "pyproject.toml",
    "uv.lock",
)


def compiler_hashes(root: Path) -> dict[str, str]:
    return {name: storage.sha(storage.inside(root, name)) for name in COMPILER_SOURCES}


CHANNELS = ("context", "route", "ribbon", "cursor", "unfold", "output")
RECIPE_PACKS = {
    "imaging101-eht-features-dynamic-v1": "retained-imaging101-eht-features-dynamic-v1",
    "imaging101-eht-dynamic-v1": "retained-imaging101-eht-dynamic-v1",
    "imaging101-eht-uq-v1": "retained-imaging101-eht-uq-v1",
    "imaging101-dti-v1": "retained-imaging101-dti-v1",
    "imaging101-deflectometry-v1": "retained-imaging101-deflectometry-v1",
    "imaging101-fan-beam-v1": "retained-imaging101-fan-beam-v1",
    "imaging101-dual-energy-v1": "retained-imaging101-dual-energy-v1",
    "imaging101-ptychography-v1": "retained-imaging101-ptychography-v1",
    "imaging101-nlos-v1": "retained-imaging101-nlos-v1",
    "imaging101-cars-v1": "retained-imaging101-cars-v1",
    "rex-topcow-v1": "retained-rex-topcow-v1",
    "automed-multiorgan-v1": "retained-automed-multiorgan-v1",
    "bcer-workflow-v1": "retained-bcer-workflow-v1",
    "abra-annotation-v1": "retained-abra-annotation-v1",
    "ct-context-v1": "retained-ct-context-v1",
    "history-sourcing-v1": "retained-history-sourcing-v1",
    "mri-importer-v1": "retained-mri-importer-v1",
    "localized-ct-v1": "retained-localized-ct-v1",
    "aneurysm-localization-v1": "retained-aneurysm-localization-v1",
    "segmentation-calibration-v1": "retained-segmentation-calibration-v1",
    "dental-v3-v1": "retained-dental-v3-v1",
    "dental-v2-v1": "retained-dental-v2-v1",
    "dental-original-v1": "retained-dental-original-v1",
    "ct-organ-v1": "retained-ct-organ-v1",
    "named-landmarks-v1": "retained-named-landmarks-v1",
    "clinical-cavity-v1": "retained-clinical-cavity-v1",
    "longitudinal-ct-revised-v1": "retained-longitudinal-ct-revised-v1",
    "longitudinal-ct-original-v1": "retained-longitudinal-ct-original-v1",
    "longitudinal-mri-v1": "retained-longitudinal-mri-v1",
    "tiger-context-v1": "retained-tiger-context-v1",
    "hubmap-inventory-v1": "retained-hubmap-inventory-v1",
    "topbrain-screen-v1": "retained-topbrain-screen-v1",
    "airway-repair-v1": "retained-airway-repair-v1",
    "vessel-source-v1": "retained-vessel-source-v1",
    "resect-pilot-v1": "retained-resect-pilot-v1",
    "resect-correspondence-v1": "retained-resect-v1",
    "topology-v1": "topology-v1",
    "correspondence-v1": "correspondence-v1",
    "multiscale-v1": "multiscale-v1",
    "shape-material-v1": "shape-material-v1",
    "local-edit-v1": "local-edit-v1",
    "longitudinal-v1": "longitudinal-v1",
    "inverse-v1": "inverse-problems-v1",
    "anatomy-audit-v1": "retained-anatomy-v1",
    "anatomy-identity-v1": "retained-anatomy-v1",
    "mixed-tissue-v1": "retained-mixed-tissue-v1",
    "prototype-identity-v1": "retained-prototype-identity-v1",
    "mask-screen-v1": "retained-mask-screen-v1",
    "anatomy-curation-v1": "retained-anatomy-curation-v1",
    "respiratory-v1": "retained-respiratory-v1",
    "registration-analysis-v1": "retained-registration-analysis-v1",
}
# Public input/contract packs carry no hidden reference assets.
SOURCE_INPUT_PACKS = {
    "retained-bcer-workflow-v1": (
        "source-slices",
        None,
        {"inputs.json", "contract.json", "NOTICE.md", "DATA-LICENSE.txt", "BCER-LICENSE.txt"},
    ),
}
SOURCE_REFERENCE_PACKS = {
    "retained-imaging101-eht-features-dynamic-v1": (
        "source-records",
        "reference.json",
        {
            "inputs.json",
            "reference.json",
            "contract.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
            "BENCHMARK-LICENSE.txt",
        },
    ),
    "retained-imaging101-eht-dynamic-v1": (
        "source-records",
        "reference.json",
        {
            "inputs.json",
            "reference.json",
            "contract.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
            "BENCHMARK-LICENSE.txt",
        },
    ),
    "retained-imaging101-eht-uq-v1": (
        "source-records",
        "reference.json",
        {
            "inputs.json",
            "reference.json",
            "contract.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
            "BENCHMARK-LICENSE.txt",
        },
    ),
    "retained-imaging101-dti-v1": (
        "source-records",
        "reference.json",
        {
            "inputs.json",
            "reference.json",
            "contract.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
            "BENCHMARK-LICENSE.txt",
        },
    ),
    "retained-imaging101-deflectometry-v1": (
        "source-records",
        "reference.json",
        {
            "inputs.json",
            "reference.json",
            "contract.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
            "BENCHMARK-LICENSE.txt",
        },
    ),
    "retained-imaging101-fan-beam-v1": (
        "source-records",
        "reference.json",
        {
            "inputs.json",
            "reference.json",
            "contract.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
            "UPSTREAM-GPL-2.0.txt",
            "BENCHMARK-LICENSE.txt",
        },
    ),
    "retained-imaging101-dual-energy-v1": (
        "source-records",
        "reference.json",
        {
            "inputs.json",
            "reference.json",
            "contract.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
            "BENCHMARK-LICENSE.txt",
        },
    ),
    "retained-imaging101-ptychography-v1": (
        "source-records",
        "reference.json",
        {
            "inputs.json",
            "reference.json",
            "contract.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
            "BENCHMARK-LICENSE.txt",
        },
    ),
    "retained-imaging101-nlos-v1": (
        "source-records",
        "reference.json",
        {
            "inputs.json",
            "reference.json",
            "contract.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
            "BENCHMARK-LICENSE.txt",
        },
    ),
    "retained-imaging101-cars-v1": (
        "source-records",
        "reference.json",
        {"inputs.json", "reference.json", "contract.json", "NOTICE.md", "DATA-LICENSE.txt"},
    ),
    "retained-rex-topcow-v1": (
        "source-slices",
        "reference.json",
        {"inputs.json", "reference.json", "contract.json", "NOTICE.md", "DATA-LICENSE.txt"},
    ),
    "retained-automed-multiorgan-v1": (
        "source-slices",
        "reference.json",
        {"inputs.json", "reference.json", "contract.json", "NOTICE.md", "DATA-LICENSE.txt"},
    ),
    "retained-abra-annotation-v1": (
        "source-slices",
        "reference.json",
        {"inputs.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"},
    ),
    "retained-ct-context-v1": (
        "source-slices",
        "reference.json",
        {"inputs.json", "output.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"},
    ),
    "retained-history-sourcing-v1": (
        "source-records",
        "reference.json",
        {"source.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"},
    ),
    "retained-mri-importer-v1": (
        "source-slices",
        "reference.json",
        {"inputs.json", "output.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"},
    ),
    "retained-localized-ct-v1": (
        "source-slices",
        "reference.json",
        {
            "baseline.json",
            "followup.json",
            "output.json",
            "reference.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
        },
    ),
    "retained-aneurysm-localization-v1": (
        "source-slices",
        "reference.json",
        {
            "n01.json",
            "n02.json",
            "n03.json",
            "output.json",
            "reference.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
        },
    ),
    "retained-segmentation-calibration-v1": (
        "source-slices",
        "reference.json",
        {
            "source.json",
            "output.json",
            "reference.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
            "LABEL-LICENSE.txt",
        },
    ),
    "retained-dental-v3-v1": (
        "source-slices",
        "reference.json",
        {"source.json", "output.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"},
    ),
    "retained-dental-v2-v1": (
        "source-slices",
        "reference.json",
        {"source.json", "output.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"},
    ),
    "retained-dental-original-v1": (
        "source-slices",
        "reference.json",
        {"source.json", "output.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"},
    ),
    "retained-ct-organ-v1": (
        "source-slices",
        "reference.json",
        {
            "source.json",
            "output.json",
            "reference.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
            "LABEL-LICENSE.txt",
        },
    ),
    "retained-named-landmarks-v1": (
        "source-slices",
        "reference.json",
        {
            "source.json",
            "output.json",
            "reference.json",
            "NOTICE.md",
            "AFIDS-CC0.txt",
            "VERSE-CC-BY-SA.txt",
        },
    ),
    "retained-clinical-cavity-v1": (
        "source-slices",
        "reference.json",
        {"source.json", "output.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"},
    ),
    "retained-longitudinal-ct-revised-v1": (
        "source-slices",
        "reference.json",
        {
            "source.json",
            "case1-baseline.json",
            "case1-followup.json",
            "case2-baseline.json",
            "case2-followup.json",
            "reference.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
        },
    ),
    "retained-longitudinal-ct-original-v1": (
        "source-slices",
        "reference.json",
        {
            "source.json",
            "baseline.json",
            "followup.json",
            "reference.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
        },
    ),
    "retained-longitudinal-mri-v1": (
        "source-slices",
        "reference.json",
        {"source.json", "p02.json", "p03.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"},
    ),
    "retained-tiger-context-v1": (
        "source-slices",
        "reference.json",
        {
            "source.json",
            "roi1.json",
            "roi2.json",
            "roi3.json",
            "reference.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
        },
    ),
    "retained-hubmap-inventory-v1": (
        "source-slices",
        "reference.json",
        {
            "source.json",
            "detail.json",
            "tiles.json",
            "helpers.json",
            "reference.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
        },
    ),
    "retained-topbrain-screen-v1": (
        "source-slices",
        "reference.json",
        {
            "case-004.json",
            "case-006.json",
            "case-007.json",
            "case-011.json",
            "case-012.json",
            "reference.json",
            "output.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
        },
    ),
    "retained-airway-repair-v1": (
        "source-slices",
        "reference.json",
        {
            "geometry.json",
            "mask-A01.json",
            "mask-A02.json",
            "output.json",
            "reference.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
        },
    ),
    "retained-vessel-source-v1": (
        "source-slices",
        "reference.json",
        {
            "geometry.json",
            "reference.json",
            "output.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
            "GRAPH-TERMS.txt",
        },
    ),
    "retained-resect-pilot-v1": (
        "source-slices",
        "reference.json",
        {
            "geometry.json",
            "trace.json",
            "output.json",
            "reference.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
        },
    ),
    "retained-resect-v1": (
        "source-slices",
        "reference.json",
        {
            "geometry.json",
            "helpers.json",
            "reference.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
            "LABEL-LICENSE.txt",
        },
    ),
    "retained-registration-analysis-v1": (
        "source-slices",
        "reference.json",
        {"geometry.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"},
    ),
    "retained-respiratory-v1": (
        "source-slices",
        "reference.json",
        {"geometry.json", "output.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"},
    ),
    "retained-anatomy-curation-v1": (
        "source-points",
        "reference.json",
        {"geometry.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"},
    ),
    "retained-mask-screen-v1": (
        "source-points",
        "reference.json",
        {"geometry.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt", "LABEL-LICENSE.txt"},
    ),
    "retained-mixed-tissue-v1": (
        "source-slices",
        "fixture.json",
        {
            "fixture.json",
            "axial.png",
            "coronal.png",
            "sagittal.png",
            "NOTICE.md",
            "DATA-LICENSE.txt",
            "LABEL-LICENSE.txt",
        },
    ),
    "retained-prototype-identity-v1": (
        "source-points",
        "reference.json",
        {
            "geometry.json",
            "reference.json",
            "vocabulary.json",
            "NOTICE.md",
            "DATA-LICENSE.txt",
            "LABEL-LICENSE.txt",
        },
    ),
}
SCOPE = (
    "Synthetic teaching fixture · one sampling ribbon only. Does not demonstrate local mask "
    "repair, eight CT planes, closed mesh production or full BR030 verification. "
    "Fixture coordinates: m; real task outputs: mm."
)


class UniqueLoader(yaml.SafeLoader):  # type: ignore[misc]
    # PyYAML is confined to the untyped parse boundary; Pydantic checks its output.
    """Reject duplicate keys instead of silently keeping the last occurrence."""


def _mapping(loader: UniqueLoader, node: yaml.MappingNode) -> dict[str, object]:
    result: dict[str, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str) or key in result:
            raise ValueError(f"Duplicate or non-string YAML key: {key}")
        result[key] = loader.construct_object(value_node)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


class Closed(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)


Unit = Annotated[StrictFloat, Field(ge=0, le=1)]
Pair = tuple[Unit, Unit]
Text = Annotated[str, Field(strict=True, min_length=1)]


class TopologyChannels(Closed):
    focus: Pair
    trace: Pair
    inventory: Pair


class CorrespondenceChannels(Closed):
    transform: Pair
    query: Pair
    residual: Pair


class MaterialChannels(Closed):
    phase: Pair
    markers: Pair
    alternative: Pair


class LongitudinalChannels(Closed):
    visits: Pair
    links: Pair
    coverage: Pair


class MultiscaleChannels(Closed):
    viewport: Pair
    selections: Pair
    coverage: Pair
    outputs: Pair


class InverseChannels(Closed):
    observations: Pair
    reconstruction: Pair
    residual: Pair


class AnatomyChannels(Closed):
    focus: Pair
    evidence: Pair
    output: Pair


class IdentityChannels(Closed):
    focus: Pair
    inventory: Pair
    reveal: Pair


class AirwayRepairChannels(Closed):
    view: Pair
    output: Pair
    reference: Pair


class LongitudinalCtRevisedChannels(Closed):
    view: Pair
    output: Pair
    reference: Pair


class LongitudinalCtOriginalChannels(Closed):
    view: Pair
    output: Pair
    reference: Pair


class LongitudinalMriChannels(Closed):
    view: Pair
    output: Pair
    reference: Pair


class TigerContextChannels(Closed):
    view: Pair
    reference: Pair


class HubmapInventoryChannels(Closed):
    view: Pair
    reference: Pair


class TopbrainScreenChannels(Closed):
    view: Pair
    output: Pair
    reference: Pair


class VesselSourceChannels(Closed):
    scan: Pair
    reference: Pair
    output: Pair


class ResectPilotChannels(Closed):
    view: Pair
    output: Pair
    reference: Pair


class ResectChannels(Closed):
    scan: Pair
    helper: Pair
    output: Pair
    reference: Pair


class RegistrationAnalysisChannels(Closed):
    reference: Pair
    bounds: Pair
    curve: Pair


class Imaging101EhtFeaturesDynamicChannels(Closed):
    view: Pair
    reference: Pair


class Imaging101EhtDynamicChannels(Closed):
    view: Pair
    reference: Pair


class Imaging101EhtUqChannels(Closed):
    view: Pair
    reference: Pair


class Imaging101DtiChannels(Closed):
    view: Pair
    reference: Pair


class Imaging101DeflectometryChannels(Closed):
    view: Pair
    reference: Pair


class Imaging101FanBeamChannels(Closed):
    view: Pair
    reference: Pair


class Imaging101DualEnergyChannels(Closed):
    view: Pair
    reference: Pair


class Imaging101PtychographyChannels(Closed):
    view: Pair
    reference: Pair


class Imaging101NlosChannels(Closed):
    view: Pair
    reference: Pair


class Imaging101CarsChannels(Closed):
    view: Pair
    reference: Pair


class RexTopcowChannels(Closed):
    view: Pair
    reference: Pair


class AutomedMultiorganChannels(Closed):
    view: Pair
    reference: Pair


class BcerWorkflowChannels(Closed):
    view: Pair


class AbraAnnotationChannels(Closed):
    view: Pair
    helper: Pair
    output: Pair
    reference: Pair


class CtContextChannels(Closed):
    view: Pair
    output: Pair
    reference: Pair


class HistorySourcingChannels(Closed):
    view: Pair
    output: Pair
    reference: Pair


class MriImporterChannels(Closed):
    view: Pair
    output: Pair
    reference: Pair


class LocalizedCtChannels(Closed):
    view: Pair
    output: Pair
    reference: Pair


class AneurysmChannels(Closed):
    view: Pair
    output: Pair
    reference: Pair


class SegmentationCalibrationChannels(Closed):
    view: Pair
    condition: Pair
    box: Pair
    output: Pair
    reference: Pair


class DentalV3Channels(Closed):
    view: Pair
    helper: Pair
    transfer: Pair
    output: Pair
    reference: Pair
    stage: Pair


class DentalV2Channels(Closed):
    view: Pair
    helper: Pair
    transfer: Pair
    output: Pair
    reference: Pair
    stage: Pair


class DentalOriginalChannels(Closed):
    view: Pair
    output: Pair
    reference: Pair
    diagnostic: Pair
    gate: Pair


class CtOrganChannels(Closed):
    view: Pair
    output: Pair
    reference: Pair


class NamedLandmarksChannels(Closed):
    view: Pair
    output: Pair
    reference: Pair


class ClinicalCavityChannels(Closed):
    phase: Pair
    helper: Pair
    output: Pair
    reference: Pair


class RespiratoryChannels(Closed):
    depth: Pair
    output: Pair
    reference: Pair


class CurationChannels(Closed):
    reference: Pair
    focus: Pair


class MaskScreenChannels(Closed):
    measure: Pair
    prediction: Pair
    reference: Pair
    focus: Pair


class MixedTissueChannels(Closed):
    conditions: Pair
    plane: Pair
    overlay: Pair
    reference: Pair
    witness: Pair


class EditChannels(Closed):
    domain: Pair
    correction: Pair
    control: Pair


class ExpansionBeat[Channels: Closed](Closed):
    id: Annotated[str, Field(strict=True, pattern=r"^[a-z0-9-]+$")]
    frames: Annotated[StrictInt, Field(ge=2, le=3600)]
    caption: Text
    narration: Text
    visual: Text
    channels: Channels
    cut: Literal["continuous", "intentional-cut"] = "continuous"


class Story[Channels: Closed](Closed):
    schema_version: Annotated[StrictInt, Field(alias="schema", ge=2, le=2)]
    id: Annotated[str, Field(strict=True, pattern=r"^[a-z0-9-]+$")]
    title: Text
    locale: Literal["en"]
    purpose: Text
    scope: Text
    asset_pack: Text
    source_class: Literal["procedural-teaching", "source-derived-teaching"]
    reference_policy: Literal["no-reference-assets", "reader-reference-reveal"]
    fps: Annotated[StrictInt, Field(ge=12, le=60)]
    source_locators: Annotated[tuple[Text, ...], Field(min_length=1)]
    beats: tuple[ExpansionBeat[Channels], ...]

    @model_validator(mode="after")
    def timeline(self) -> Self:
        if not self.beats or len({b.id for b in self.beats}) != len(self.beats):
            raise ValueError("Missing or duplicate beats")
        for prev, cur in zip(self.beats, self.beats[1:], strict=False):
            if cur.cut == "continuous":
                a, b = prev.channels.model_dump(), cur.channels.model_dump()
                if any(abs(a[k][1] - b[k][0]) > 1e-9 for k in a):
                    raise ValueError(f"Unmarked channel discontinuity at {cur.id}")
        return self


class TopologyStory(Story[TopologyChannels]):
    recipe: Literal["topology-v1"]
    operation: Literal["ordered-path", "edge-inventory"]


class CorrespondenceBeat(ExpansionBeat[CorrespondenceChannels]):
    show_deformed_target: StrictBool


class CorrespondenceStory(Story[CorrespondenceChannels]):
    recipe: Literal["correspondence-v1"]
    beats: tuple[CorrespondenceBeat, ...]


class MaterialStory(Story[MaterialChannels]):
    recipe: Literal["shape-material-v1"]


class LongitudinalStory(Story[LongitudinalChannels]):
    recipe: Literal["longitudinal-v1"]


class MultiscaleStory(Story[MultiscaleChannels]):
    recipe: Literal["multiscale-v1"]
    operation: Literal["coordinate-navigation", "supplied-patches", "annotation-coverage"]


class InverseStory(Story[InverseChannels]):
    recipe: Literal["inverse-v1"]
    acquisition: Literal["ct-parallel", "mri-cartesian"]


class AnatomyStory(Story[AnatomyChannels]):
    recipe: Literal["anatomy-audit-v1"]


class IdentityStory(Story[IdentityChannels]):
    recipe: Literal["anatomy-identity-v1"]


class PrototypeIdentityStory(Story[IdentityChannels]):
    recipe: Literal["prototype-identity-v1"]


class LongitudinalCtRevisedBeat(ExpansionBeat[LongitudinalCtRevisedChannels]):
    scene: Literal[
        "inputs",
        "rules",
        "partition",
        "inventory",
        "size",
        "context",
        "decisions",
        "newfocus",
        "events",
        "comparison",
        "output",
        "limits",
    ]


class LongitudinalCtRevisedStory(Story[LongitudinalCtRevisedChannels]):
    recipe: Literal["longitudinal-ct-revised-v1"]
    beats: tuple[LongitudinalCtRevisedBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class LongitudinalCtOriginalBeat(ExpansionBeat[LongitudinalCtOriginalChannels]):
    scene: Literal[
        "inputs",
        "instances",
        "partition",
        "focus",
        "matching",
        "links",
        "events",
        "results",
        "output",
        "limits",
    ]


class LongitudinalCtOriginalStory(Story[LongitudinalCtOriginalChannels]):
    recipe: Literal["longitudinal-ct-original-v1"]
    beats: tuple[LongitudinalCtOriginalBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class LongitudinalMriBeat(ExpansionBeat[LongitudinalMriChannels]):
    scene: Literal[
        "inputs",
        "locate",
        "phases",
        "sequences",
        "measure",
        "change",
        "reference",
        "output",
        "forecast",
        "limits",
    ]


class LongitudinalMriStory(Story[LongitudinalMriChannels]):
    recipe: Literal["longitudinal-mri-v1"]
    beats: tuple[LongitudinalMriBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class TigerContextBeat(ExpansionBeat[TigerContextChannels]):
    scene: Literal[
        "inputs",
        "conditions",
        "tissue",
        "cells",
        "assign",
        "coordinates",
        "area",
        "density",
        "output",
        "limits",
    ]


class TigerContextStory(Story[TigerContextChannels]):
    recipe: Literal["tiger-context-v1"]
    beats: tuple[TigerContextBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class HubmapInventoryBeat(ExpansionBeat[HubmapInventoryChannels]):
    scene: Literal[
        "inputs",
        "helpers",
        "detail",
        "outline",
        "coordinates",
        "duplicate",
        "area",
        "inventory",
        "conditions",
        "limits",
    ]


class HubmapInventoryStory(Story[HubmapInventoryChannels]):
    recipe: Literal["hubmap-inventory-v1"]
    beats: tuple[HubmapInventoryBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class TopbrainScreenBeat(ExpansionBeat[TopbrainScreenChannels]):
    scene: Literal[
        "inputs",
        "cohort",
        "variants",
        "contacts",
        "parent",
        "calibration",
        "cpr",
        "admission",
        "limits",
    ]


class TopbrainScreenStory(Story[TopbrainScreenChannels]):
    recipe: Literal["topbrain-screen-v1"]
    beats: tuple[TopbrainScreenBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class AirwayRepairBeat(ExpansionBeat[AirwayRepairChannels]):
    scene: Literal[
        "inputs",
        "inspect",
        "repair",
        "route",
        "cpr",
        "reference",
        "controls",
        "comparison",
        "limits",
    ]


class AirwayRepairStory(Story[AirwayRepairChannels]):
    recipe: Literal["airway-repair-v1"]
    beats: tuple[AirwayRepairBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class VesselSourceBeat(ExpansionBeat[VesselSourceChannels]):
    scene: Literal[
        "sources", "states", "inspect", "contacts", "nodes", "contract", "admission", "limits"
    ]


class VesselSourceStory(Story[VesselSourceChannels]):
    recipe: Literal["vessel-source-v1"]
    beats: tuple[VesselSourceBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class ResectPilotBeat(ExpansionBeat[ResectPilotChannels]):
    scene: Literal[
        "inputs", "cue", "inspect", "search", "output", "reference", "controls", "limits"
    ]


class ResectPilotStory(Story[ResectPilotChannels]):
    recipe: Literal["resect-pilot-v1"]
    beats: tuple[ResectPilotBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class ResectBeat(ExpansionBeat[ResectChannels]):
    scene: Literal[
        "inputs", "frame", "inspect", "helpers", "output", "reference", "cases", "limits"
    ]


class ResectStory(Story[ResectChannels]):
    recipe: Literal["resect-correspondence-v1"]
    beats: tuple[ResectBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class RegistrationAnalysisBeat(ExpansionBeat[RegistrationAnalysisChannels]):
    scene: Literal[
        "input", "replay", "composition", "support", "objective", "context", "repeats", "limits"
    ]


class RegistrationAnalysisStory(Story[RegistrationAnalysisChannels]):
    recipe: Literal["registration-analysis-v1"]
    beats: tuple[RegistrationAnalysisBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class Imaging101EhtFeaturesDynamicBeat(ExpansionBeat[Imaging101EhtFeaturesDynamicChannels]):
    scene: Literal[
        "inputs", "closures", "model", "posterior", "reference", "diagnostics", "scoring", "limits"
    ]


class Imaging101EhtFeaturesDynamicStory(Story[Imaging101EhtFeaturesDynamicChannels]):
    recipe: Literal["imaging101-eht-features-dynamic-v1"]
    beats: tuple[Imaging101EhtFeaturesDynamicBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class Imaging101EhtDynamicBeat(ExpansionBeat[Imaging101EhtDynamicChannels]):
    scene: Literal[
        "inputs", "operator", "temporal", "output", "reference", "diagnostics", "scoring", "limits"
    ]


class Imaging101EhtDynamicStory(Story[Imaging101EhtDynamicChannels]):
    recipe: Literal["imaging101-eht-dynamic-v1"]
    beats: tuple[Imaging101EhtDynamicBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class Imaging101EhtUqBeat(ExpansionBeat[Imaging101EhtUqChannels]):
    scene: Literal[
        "inputs", "closures", "prior", "samples", "output", "reference", "scoring", "limits"
    ]


class Imaging101EhtUqStory(Story[Imaging101EhtUqChannels]):
    recipe: Literal["imaging101-eht-uq-v1"]
    beats: tuple[Imaging101EhtUqBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class Imaging101DtiBeat(ExpansionBeat[Imaging101DtiChannels]):
    scene: Literal[
        "inputs", "gradients", "fit", "tensor", "output", "reference", "scoring", "limits"
    ]


class Imaging101DtiStory(Story[Imaging101DtiChannels]):
    recipe: Literal["imaging101-dti-v1"]
    beats: tuple[Imaging101DtiBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class Imaging101DeflectometryBeat(ExpansionBeat[Imaging101DeflectometryChannels]):
    scene: Literal[
        "inputs", "calibration", "phase", "geometry", "output", "reference", "scoring", "limits"
    ]


class Imaging101DeflectometryStory(Story[Imaging101DeflectometryChannels]):
    recipe: Literal["imaging101-deflectometry-v1"]
    beats: tuple[Imaging101DeflectometryBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class Imaging101FanBeamBeat(ExpansionBeat[Imaging101FanBeamChannels]):
    scene: Literal[
        "inputs", "geometry", "weights", "output", "reference", "scoring", "staging", "limits"
    ]


class Imaging101FanBeamStory(Story[Imaging101FanBeamChannels]):
    recipe: Literal["imaging101-fan-beam-v1"]
    beats: tuple[Imaging101FanBeamBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class Imaging101DualEnergyBeat(ExpansionBeat[Imaging101DualEnergyChannels]):
    scene: Literal[
        "inputs", "calibration", "forward", "output", "reference", "staging", "scoring", "limits"
    ]


class Imaging101DualEnergyStory(Story[Imaging101DualEnergyChannels]):
    recipe: Literal["imaging101-dual-energy-v1"]
    beats: tuple[Imaging101DualEnergyBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class Imaging101PtychographyBeat(ExpansionBeat[Imaging101PtychographyChannels]):
    scene: Literal[
        "inputs", "overlap", "projection", "output", "reference", "staging", "scoring", "limits"
    ]


class Imaging101PtychographyStory(Story[Imaging101PtychographyChannels]):
    recipe: Literal["imaging101-ptychography-v1"]
    beats: tuple[Imaging101PtychographyBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class Imaging101NlosBeat(ExpansionBeat[Imaging101NlosChannels]):
    scene: Literal[
        "inputs", "alignment", "stolt", "output", "reference", "staging", "scoring", "limits"
    ]


class Imaging101NlosStory(Story[Imaging101NlosChannels]):
    recipe: Literal["imaging101-nlos-v1"]
    beats: tuple[Imaging101NlosBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class Imaging101CarsBeat(ExpansionBeat[Imaging101CarsChannels]):
    scene: Literal["inputs", "staging", "forward", "fit", "reference", "scoring", "shape", "limits"]


class Imaging101CarsStory(Story[Imaging101CarsChannels]):
    recipe: Literal["imaging101-cars-v1"]
    beats: tuple[Imaging101CarsBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class RexTopcowBeat(ExpansionBeat[RexTopcowChannels]):
    scene: Literal[
        "inputs",
        "split",
        "labels",
        "submission",
        "reference",
        "metrics",
        "topology",
        "geometry",
        "ranking",
        "limits",
    ]


class RexTopcowStory(Story[RexTopcowChannels]):
    recipe: Literal["rex-topcow-v1"]
    beats: tuple[RexTopcowBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class AutomedMultiorganBeat(ExpansionBeat[AutomedMultiorganChannels]):
    scene: Literal[
        "inputs", "workflow", "remap", "geometry", "reference", "scoring", "coverage", "limits"
    ]


class AutomedMultiorganStory(Story[AutomedMultiorganChannels]):
    recipe: Literal["automed-multiorgan-v1"]
    beats: tuple[AutomedMultiorganBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class BcerWorkflowBeat(ExpansionBeat[BcerWorkflowChannels]):
    scene: Literal[
        "inputs",
        "manifest",
        "geometry",
        "dependencies",
        "artifacts",
        "metrics",
        "provenance",
        "limits",
    ]


class BcerWorkflowStory(Story[BcerWorkflowChannels]):
    recipe: Literal["bcer-workflow-v1"]
    beats: tuple[BcerWorkflowBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class AbraAnnotationBeat(ExpansionBeat[AbraAnnotationChannels]):
    scene: Literal[
        "inputs", "navigate", "coordinates", "reference", "ordinary", "oracle", "scoring", "limits"
    ]


class AbraAnnotationStory(Story[AbraAnnotationChannels]):
    recipe: Literal["abra-annotation-v1"]
    beats: tuple[AbraAnnotationBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class CtContextBeat(ExpansionBeat[CtContextChannels]):
    scene: Literal[
        "inputs", "headers", "liver", "surgery", "fields", "reference", "validator", "limits"
    ]


class CtContextStory(Story[CtContextChannels]):
    recipe: Literal["ct-context-v1"]
    beats: tuple[CtContextBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class HistorySourcingBeat(ExpansionBeat[HistorySourcingChannels]):
    scene: Literal[
        "retrieval",
        "excerpts",
        "classification",
        "candidates",
        "lineage",
        "controls",
        "reference",
        "gap",
        "limits",
    ]


class HistorySourcingStory(Story[HistorySourcingChannels]):
    recipe: Literal["history-sourcing-v1"]
    beats: tuple[HistorySourcingBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class MriImporterBeat(ExpansionBeat[MriImporterChannels]):
    scene: Literal[
        "inputs",
        "ordinals",
        "association",
        "geometry",
        "placement",
        "outputs",
        "reference",
        "controls",
        "trace",
        "limits",
    ]


class MriImporterStory(Story[MriImporterChannels]):
    recipe: Literal["mri-importer-v1"]
    beats: tuple[MriImporterBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class LocalizedCtBeat(ExpansionBeat[LocalizedCtChannels]):
    scene: Literal[
        "inputs",
        "rules",
        "axial",
        "orthogonal",
        "serial",
        "judgments",
        "outputs",
        "reference",
        "scoring",
        "context",
        "limits",
    ]


class LocalizedCtStory(Story[LocalizedCtChannels]):
    recipe: Literal["localized-ct-v1"]
    beats: tuple[LocalizedCtBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class AneurysmBeat(ExpansionBeat[AneurysmChannels]):
    scene: Literal[
        "inputs",
        "projections",
        "slabs",
        "candidate",
        "depth",
        "outputs",
        "reference",
        "miss",
        "coverage",
        "negative",
        "matching",
        "limits",
    ]


class AneurysmStory(Story[AneurysmChannels]):
    recipe: Literal["aneurysm-localization-v1"]
    beats: tuple[AneurysmBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class SegmentationCalibrationBeat(ExpansionBeat[SegmentationCalibrationChannels]):
    scene: Literal[
        "inputs",
        "sampling",
        "boxes",
        "preprocess",
        "outputs",
        "reference",
        "sensitivity",
        "duodenum",
        "controls",
        "metrics",
        "latency",
        "backend",
        "limits",
    ]


class SegmentationCalibrationStory(Story[SegmentationCalibrationChannels]):
    recipe: Literal["segmentation-calibration-v1"]
    beats: tuple[SegmentationCalibrationBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class DentalV3Beat(ExpansionBeat[DentalV3Channels]):
    scene: Literal[
        "inputs",
        "contract",
        "example",
        "transfer",
        "outputs",
        "shape",
        "metrics",
        "pulp-gain",
        "pulp-loss",
        "pulp-reach",
        "canal-crop",
        "canal-extent",
        "limits",
    ]


class DentalV3Story(Story[DentalV3Channels]):
    recipe: Literal["dental-v3-v1"]
    beats: tuple[DentalV3Beat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class DentalV2Beat(ExpansionBeat[DentalV2Channels]):
    scene: Literal[
        "inputs",
        "contract",
        "example",
        "transfer",
        "outputs",
        "identity",
        "metrics",
        "pulp-rule",
        "pulp-contents",
        "pulp-clip",
        "canals",
        "small-canals",
        "limits",
    ]


class DentalV2Story(Story[DentalV2Channels]):
    recipe: Literal["dental-v2-v1"]
    beats: tuple[DentalV2Beat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class DentalOriginalBeat(ExpansionBeat[DentalOriginalChannels]):
    scene: Literal[
        "inputs",
        "contract",
        "method",
        "output",
        "reference",
        "diagnostic",
        "metrics",
        "canals",
        "restorations",
        "pulp",
        "omissions",
        "limits",
    ]


class DentalOriginalStory(Story[DentalOriginalChannels]):
    recipe: Literal["dental-original-v1"]
    beats: tuple[DentalOriginalBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class CtOrganBeat(ExpansionBeat[CtOrganChannels]):
    scene: Literal[
        "inputs",
        "contract",
        "polygon",
        "tool",
        "output",
        "reference",
        "regressions",
        "inventory",
        "comparison",
        "slices",
        "limits",
    ]


class CtOrganStory(Story[CtOrganChannels]):
    recipe: Literal["ct-organ-v1"]
    beats: tuple[CtOrganBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class NamedLandmarksBeat(ExpansionBeat[NamedLandmarksChannels]):
    scene: Literal[
        "inputs",
        "coordinates",
        "search",
        "output",
        "reference",
        "availability",
        "condyle",
        "mri",
        "counterexample",
        "comparison",
        "conditions",
        "limits",
    ]


class NamedLandmarksStory(Story[NamedLandmarksChannels]):
    recipe: Literal["named-landmarks-v1"]
    beats: tuple[NamedLandmarksBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class ClinicalCavityBeat(ExpansionBeat[ClinicalCavityChannels]):
    scene: Literal[
        "inputs",
        "initial",
        "tracking",
        "reference",
        "patient",
        "preserved",
        "static",
        "shift",
        "judgment",
        "output",
    ]


class ClinicalCavityStory(Story[ClinicalCavityChannels]):
    recipe: Literal["clinical-cavity-v1"]
    beats: tuple[ClinicalCavityBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class RespiratoryBeat(ExpansionBeat[RespiratoryChannels]):
    scene: Literal[
        "inputs", "frame", "depth", "output", "reference", "judgment", "conditions", "limits"
    ]


class RespiratoryStory(Story[RespiratoryChannels]):
    recipe: Literal["respiratory-v1"]
    beats: tuple[RespiratoryBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class CurationBeat(ExpansionBeat[CurationChannels]):
    scene: Literal[
        "pair", "preservation", "overlap", "calibration", "reserve", "ambiguity", "admission"
    ]


class CurationStory(Story[CurationChannels]):
    recipe: Literal["anatomy-curation-v1"]
    beats: tuple[CurationBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class MaskScreenBeat(ExpansionBeat[MaskScreenChannels]):
    scene: Literal["context", "ribs-32", "ribs-74", "organs-32", "admission"]


class MaskScreenStory(Story[MaskScreenChannels]):
    recipe: Literal["mask-screen-v1"]
    beats: tuple[MaskScreenBeat, ...]

    @model_validator(mode="after")
    def scene_cuts(self) -> Self:
        for previous, current in zip(self.beats, self.beats[1:], strict=False):
            if current.scene != previous.scene and current.cut != "intentional-cut":
                raise ValueError("Changing source scenes requires an explicit cut")
        return self


class MixedTissueStory(Story[MixedTissueChannels]):
    recipe: Literal["mixed-tissue-v1"]


class EditStory(Story[EditChannels]):
    recipe: Literal["local-edit-v1"]


AnyStory = Annotated[
    TopologyStory
    | CorrespondenceStory
    | MaterialStory
    | LongitudinalStory
    | MultiscaleStory
    | InverseStory
    | EditStory
    | AnatomyStory
    | IdentityStory
    | PrototypeIdentityStory
    | LongitudinalCtRevisedStory
    | LongitudinalCtOriginalStory
    | LongitudinalMriStory
    | TigerContextStory
    | HubmapInventoryStory
    | TopbrainScreenStory
    | AirwayRepairStory
    | VesselSourceStory
    | ResectPilotStory
    | ResectStory
    | RegistrationAnalysisStory
    | Imaging101EhtFeaturesDynamicStory
    | Imaging101EhtDynamicStory
    | Imaging101EhtUqStory
    | Imaging101DtiStory
    | Imaging101DeflectometryStory
    | Imaging101FanBeamStory
    | Imaging101DualEnergyStory
    | Imaging101PtychographyStory
    | Imaging101NlosStory
    | Imaging101CarsStory
    | RexTopcowStory
    | AutomedMultiorganStory
    | BcerWorkflowStory
    | AbraAnnotationStory
    | CtContextStory
    | HistorySourcingStory
    | MriImporterStory
    | LocalizedCtStory
    | AneurysmStory
    | SegmentationCalibrationStory
    | DentalV3Story
    | DentalV2Story
    | DentalOriginalStory
    | CtOrganStory
    | NamedLandmarksStory
    | ClinicalCavityStory
    | RespiratoryStory
    | CurationStory
    | MaskScreenStory
    | MixedTissueStory,
    Field(discriminator="recipe"),
]
ADAPTER: TypeAdapter[
    TopologyStory
    | CorrespondenceStory
    | MaterialStory
    | LongitudinalStory
    | MultiscaleStory
    | InverseStory
    | EditStory
    | AnatomyStory
    | IdentityStory
    | PrototypeIdentityStory
    | LongitudinalCtRevisedStory
    | LongitudinalCtOriginalStory
    | LongitudinalMriStory
    | TigerContextStory
    | HubmapInventoryStory
    | TopbrainScreenStory
    | AirwayRepairStory
    | VesselSourceStory
    | ResectPilotStory
    | ResectStory
    | RegistrationAnalysisStory
    | Imaging101EhtFeaturesDynamicStory
    | Imaging101EhtDynamicStory
    | Imaging101EhtUqStory
    | Imaging101DtiStory
    | Imaging101DeflectometryStory
    | Imaging101FanBeamStory
    | Imaging101DualEnergyStory
    | Imaging101PtychographyStory
    | Imaging101NlosStory
    | Imaging101CarsStory
    | RexTopcowStory
    | AutomedMultiorganStory
    | BcerWorkflowStory
    | AbraAnnotationStory
    | CtContextStory
    | HistorySourcingStory
    | MriImporterStory
    | LocalizedCtStory
    | AneurysmStory
    | SegmentationCalibrationStory
    | DentalV3Story
    | DentalV2Story
    | DentalOriginalStory
    | CtOrganStory
    | NamedLandmarksStory
    | ClinicalCavityStory
    | RespiratoryStory
    | CurationStory
    | MaskScreenStory
    | MixedTissueStory
] = TypeAdapter(AnyStory)


class FixturePack(Closed):
    manifest: str = Field(min_length=1, strict=True)
    retained_files: tuple[str, ...]
    runtime_geometry: Literal["fixture.json"]

    @model_validator(mode="after")
    def complete(self) -> Self:
        if "fixture.json" not in self.retained_files or len(set(self.retained_files)) != len(
            self.retained_files
        ):
            raise ValueError("Missing fixture or duplicate dependency")
        return self


class AssetPack(Closed):
    manifest: str = Field(min_length=1, strict=True)
    retained_files: tuple[str, ...]
    runtime_geometry: Literal["geometry.json"]

    @model_validator(mode="after")
    def complete(self) -> Self:
        required = {
            "geometry.json",
            "route.json",
            "cpr-sampled.png",
            "phantom-projection.png",
            "branching-phantom-volume.npz",
        }
        if not required.issubset(self.retained_files):
            raise ValueError("Route pack is missing required fixture dependencies")
        if len(self.retained_files) != len(set(self.retained_files)):
            raise ValueError("Duplicate retained asset")
        return self


class AnatomyPack(Closed):
    manifest: str
    retained_files: tuple[str, ...]
    runtime_geometry: Literal["anatomy-assembly"]


class SourceTeachingPack(Closed):
    manifest: str
    retained_files: tuple[str, ...]
    runtime_geometry: Literal["source-slices", "source-points", "source-records"]


class PrefabIndex(Closed):
    schema_version: StrictInt = Field(alias="schema", ge=1, le=1)
    packs: dict[str, AssetPack | FixturePack | AnatomyPack | SourceTeachingPack]


class Header(Closed):
    schema_version: StrictInt = Field(alias="schema", ge=1, le=1)
    id: str = Field(pattern=r"^[a-z0-9-]+$", strict=True)
    title: str = Field(min_length=1, strict=True)
    locale: Literal["en"]
    purpose: str = Field(min_length=1, strict=True)
    recipe: Literal["route-unfold-v1"]
    asset_pack: Literal["tb3-route-kit-v1"]
    fps: StrictInt = Field(ge=12, le=60)
    reference_policy: Literal["no-reference-assets"]
    source_class: Literal["procedural-teaching"]


class Beat(Closed):
    id: str = Field(pattern=r"^[a-z0-9-]+$", strict=True)
    duration: StrictFloat = Field(gt=0, le=60)
    caption: str = Field(min_length=1, strict=True)
    narration: str = Field(min_length=1, strict=True)
    visual: str = Field(min_length=1, strict=True)
    context: tuple[StrictFloat, StrictFloat]
    route: tuple[StrictFloat, StrictFloat]
    ribbon: tuple[StrictFloat, StrictFloat]
    cursor: tuple[StrictFloat, StrictFloat]
    unfold: tuple[StrictFloat, StrictFloat]
    output: tuple[StrictFloat, StrictFloat]

    @model_validator(mode="after")
    def bounded(self) -> Self:
        for name in CHANNELS:
            if not all(0 <= value <= 1 for value in getattr(self, name)):
                raise ValueError(f"{name} must stay in [0,1]")
        return self


@dataclass(frozen=True)
class StoryDocument:
    """Parsed authoring syntax; recipe models validate its values without reading files."""

    header: dict[str, object]
    beats: tuple[dict[str, object], ...]

    @property
    def schema(self) -> int:
        version = self.header.get("schema")
        if type(version) is not int or version not in (1, 2):
            raise ValueError("Story schema must be the integer 1 or 2")
        return version


def parse_document(raw: str) -> StoryDocument:
    # Normalize line endings for syntax only. Compilation hashes and copies original bytes.
    raw = raw.replace("\r\n", "\n")
    match = re.match(r"\A---\n(.*?)\n---\n", raw, re.S)
    if not match:
        raise ValueError("Expected YAML frontmatter")

    def mapping(text: str, context: str) -> dict[str, object]:
        value = yaml.load(text, Loader=UniqueLoader)
        if not isinstance(value, dict):
            raise ValueError(f"Expected {context} mapping")
        return cast(dict[str, object], value)

    header = mapping(match[1], "frontmatter")
    if "beats" in header:
        raise ValueError("Beats belong in fenced blocks")
    # A small fence scanner keeps examples inside other code fences out of the story.
    beats = []
    fence: str | None = None
    block: list[str] | None = None
    for line in raw[match.end() :].splitlines():
        if fence is not None:
            if re.fullmatch(re.escape(fence) + r"\s*", line):
                if block is not None:
                    beats.append(mapping("\n".join(block), "beat"))
                fence, block = None, None
            elif block is not None:
                block.append(line)
        elif opening := re.match(r"^(`{3,}|~{3,})(.*)$", line):
            fence, info = opening.groups()
            if info.strip() == "beat":
                if fence != "```" or info != "beat":
                    raise ValueError("Unclosed or malformed beat block")
                block = []
            elif info.strip().startswith("beat"):
                raise ValueError("Unclosed or malformed beat block")
    if block is not None:
        raise ValueError("Unclosed or malformed beat block")
    document = StoryDocument(header, tuple(beats))
    _ = document.schema  # Validate before dispatch, including direct parse callers.
    return document


def parse_story(raw: str | StoryDocument) -> tuple[Header, tuple[Beat, ...]]:
    document = parse_document(raw) if isinstance(raw, str) else raw
    header = Header.model_validate(document.header)
    beats = tuple(Beat.model_validate(beat) for beat in document.beats)
    if not beats or len({beat.id for beat in beats}) != len(beats):
        raise ValueError("Missing beats or duplicate beat IDs")
    for beat in beats:
        frames = beat.duration * header.fps
        if round(frames) < 1 or abs(frames - round(frames)) > 1e-8:
            raise ValueError(f"{beat.id}: duration must align with fps")
    return header, beats


def parse_expansion(
    raw: str | StoryDocument,
) -> (
    TopologyStory
    | CorrespondenceStory
    | MaterialStory
    | LongitudinalStory
    | MultiscaleStory
    | InverseStory
    | EditStory
    | AnatomyStory
    | IdentityStory
    | PrototypeIdentityStory
    | LongitudinalCtRevisedStory
    | LongitudinalCtOriginalStory
    | LongitudinalMriStory
    | TigerContextStory
    | HubmapInventoryStory
    | TopbrainScreenStory
    | AirwayRepairStory
    | VesselSourceStory
    | ResectPilotStory
    | ResectStory
    | RegistrationAnalysisStory
    | Imaging101EhtFeaturesDynamicStory
    | Imaging101EhtDynamicStory
    | Imaging101EhtUqStory
    | Imaging101DtiStory
    | Imaging101DeflectometryStory
    | Imaging101FanBeamStory
    | Imaging101DualEnergyStory
    | Imaging101PtychographyStory
    | Imaging101NlosStory
    | Imaging101CarsStory
    | RexTopcowStory
    | AutomedMultiorganStory
    | BcerWorkflowStory
    | AbraAnnotationStory
    | CtContextStory
    | HistorySourcingStory
    | MriImporterStory
    | LocalizedCtStory
    | AneurysmStory
    | SegmentationCalibrationStory
    | DentalV3Story
    | DentalV2Story
    | DentalOriginalStory
    | CtOrganStory
    | NamedLandmarksStory
    | ClinicalCavityStory
    | RespiratoryStory
    | CurationStory
    | MaskScreenStory
    | MixedTissueStory
):
    document = parse_document(raw) if isinstance(raw, str) else raw
    return ADAPTER.validate_python({**document.header, "beats": document.beats})


# Compatibility is limited to these exact pre-refactor sources (0ea91a5).
# New or edited sources must declare their semantics; IDs alone never opt in.
LEGACY_SEMANTICS = {
    "groups/lesion-localization/presentation/stories/wsi-search.story.md": (
        "f17d8e4d9472d19e4413fb1518680ad14b17f8249ddd5573242c557e8fcf564d",
        "multiscale-v1",
        "coordinate-navigation",
    ),
    "groups/lesion-localization/presentation/stories/wsi-patches.story.md": (
        "2e9611245dcf9bf2bdf2be4ee639bea980cbcc8c1c1cc7e80fa1112a2b8f287b",
        "multiscale-v1",
        "supplied-patches",
    ),
    "groups/lesion-localization/presentation/stories/wsi-coverage.story.md": (
        "a1577d0e2e21c5926ac1fd7fb27c5d4511fd7c6b0fe74997d8cb05532e27896f",
        "multiscale-v1",
        "annotation-coverage",
    ),
    "groups/tubular-anatomy/presentation/stories/topology-path.story.md": (
        "a8e7306179b03715b8bf5fa88c92569178bdcd2624241e80697411bd5ad071c4",
        "topology-v1",
        "ordered-path",
    ),
    "groups/tubular-anatomy/presentation/stories/topology-inventory.story.md": (
        "ac9d6f5cd0793d4026a3271871ef831e30f130d013253293d88eacddcfe1cf32",
        "topology-v1",
        "edge-inventory",
    ),
    "groups/registration/presentation/stories/rigid-correspondence.story.md": (
        "21dd407a7ed2fdd0d56882f053d870337b79c32cac2d1d09221828142390d3af",
        "correspondence-v1",
        None,
    ),
}


def _legacy_semantics(document: StoryDocument, source: str, source_sha: str) -> StoryDocument:
    legacy = LEGACY_SEMANTICS.get(source)
    if legacy is None or (source_sha, document.header.get("recipe")) != legacy[:2]:
        return document
    if legacy[1] == "correspondence-v1":
        return StoryDocument(
            document.header,
            tuple(
                {**beat, "show_deformed_target": beat["id"] == "scope"} for beat in document.beats
            ),
        )
    return StoryDocument({**document.header, "operation": legacy[2]}, document.beats)


def resolve_assets(root: Path, pack_id: str) -> tuple[str, dict[str, str]]:
    index_path = storage.inside(root, "presentation/assets/teaching-prefabs.json")
    index = PrefabIndex.model_validate_json(index_path.read_text())
    if pack_id not in index.packs:
        raise ValueError(f"Unknown asset pack: {pack_id}")
    pack = index.packs[pack_id]
    manifest_path = storage.inside(root, pack.manifest)
    manifest = json.loads(manifest_path.read_text())
    if isinstance(pack, SourceTeachingPack):
        source_packs = {**SOURCE_REFERENCE_PACKS, **SOURCE_INPUT_PACKS}
        if pack_id not in source_packs:
            raise ValueError("Unknown source teaching pack")
        geometry, reference_file, required = source_packs[pack_id]
        frame, data_license, label_license = {
            "retained-imaging101-eht-features-dynamic-v1": (
                "source-record",
                "LicenseRef-Imaging101-EHT-feature-sources",
                "MIT",
            ),
            "retained-imaging101-eht-dynamic-v1": (
                "source-record",
                "LicenseRef-Imaging101-EHT-dynamic-sources",
                "MIT",
            ),
            "retained-imaging101-eht-uq-v1": (
                "source-record",
                "LicenseRef-Imaging101-DPI-sources",
                "MIT",
            ),
            "retained-imaging101-dti-v1": ("source-record", "MIT", "MIT"),
            "retained-imaging101-deflectometry-v1": (
                "source-record",
                "LicenseRef-Imaging101-deflectometry-sources",
                "MIT",
            ),
            "retained-imaging101-fan-beam-v1": (
                "source-record",
                "LicenseRef-Imaging101-fan-beam-sources",
                "MIT",
            ),
            "retained-imaging101-dual-energy-v1": ("source-record", "MIT", "MIT"),
            "retained-imaging101-ptychography-v1": (
                "source-record",
                "PtyLab academic/non-commercial",
                "MIT",
            ),
            "retained-imaging101-nlos-v1": (
                "source-record",
                "Stanford academic/non-commercial",
                "MIT",
            ),
            "retained-imaging101-cars-v1": ("source-record", "MIT", "MIT"),
            "retained-rex-topcow-v1": (
                "RAS",
                "LicenseRef-TopCoW-OpenDataSwiss",
                "LicenseRef-TopCoW-OpenDataSwiss",
            ),
            "retained-automed-multiorgan-v1": ("RAS", "CC-BY-4.0", "CC-BY-4.0"),
            "retained-bcer-workflow-v1": ("LPS", "CC-BY-NC-4.0", None),
            "retained-abra-annotation-v1": ("LPS", "CC-BY-3.0", "CC-BY-3.0"),
            "retained-ct-context-v1": ("RAS", "CC-BY-NC-4.0", "CC-BY-NC-4.0"),
            "retained-history-sourcing-v1": (
                "source-record",
                "LicenseRef-TB3-retained-records",
                "LicenseRef-TB3-retained-records",
            ),
            "retained-mri-importer-v1": (
                "LPS",
                "LicenseRef-TB3-authored-fixtures",
                "LicenseRef-TB3-authored-fixtures",
            ),
            "retained-localized-ct-v1": ("RAS", "CC-BY-NC-4.0", "CC-BY-NC-4.0"),
            "retained-aneurysm-localization-v1": ("native-ijk", "CC0-1.0", "CC0-1.0"),
            "retained-segmentation-calibration-v1": ("native-ijk", "CC-BY-4.0", "Apache-2.0"),
            "retained-dental-v3-v1": ("native-ijk", "CC-BY-NC-SA-4.0", None),
            "retained-dental-v2-v1": ("native-ijk", "CC-BY-NC-SA-4.0", None),
            "retained-dental-original-v1": ("native-ijk", "CC-BY-NC-SA-4.0", None),
            "retained-ct-organ-v1": ("RAS", "CC-BY-4.0", "Apache-2.0"),
            "retained-longitudinal-ct-revised-v1": ("RAS", "CC-BY-NC-4.0", "CC-BY-NC-4.0"),
            "retained-longitudinal-ct-original-v1": ("RAS", "CC-BY-NC-4.0", "CC-BY-NC-4.0"),
            "retained-longitudinal-mri-v1": ("RAS", "CC-BY-4.0", "CC-BY-4.0"),
            "retained-tiger-context-v1": ("level-0-image", "CC-BY-NC-4.0", "CC-BY-NC-4.0"),
            "retained-hubmap-inventory-v1": ("level-0-image", "CC-BY-4.0", "CC-BY-4.0"),
            "retained-topbrain-screen-v1": (
                "RAS",
                "LicenseRef-TopBrain-2026-noncommercial",
                "LicenseRef-TopBrain-2026-noncommercial",
            ),
            "retained-airway-repair-v1": ("RAS", "CC-BY-4.0", "CC-BY-4.0"),
            "retained-vessel-source-v1": (
                "RAS",
                "LicenseRef-TopCoW-2024-noncommercial",
                "LicenseRef-CoW-Centerline-CC-BY-NC",
            ),
            "retained-resect-pilot-v1": ("RAS", "CC-BY-4.0", None),
            "retained-resect-v1": ("RAS", "CC-BY-4.0", "CC-BY-NC-SA-4.0"),
            "retained-anatomy-curation-v1": ("LPS", "CC-BY-SA-4.0", "CC-BY-SA-4.0"),
            "retained-named-landmarks-v1": (
                "RAS",
                "LicenseRef-NamedLandmarkSources",
                "LicenseRef-NamedLandmarkSources",
            ),
            "retained-clinical-cavity-v1": (
                "initial-cavity-local",
                "CC-BY-NC-SA-4.0",
                "CC-BY-NC-SA-4.0",
            ),
            "retained-respiratory-v1": ("dataset-world", "CC-BY-4.0", "CC-BY-4.0"),
            "retained-registration-analysis-v1": ("dataset-world", "CC-BY-4.0", "CC-BY-4.0"),
        }.get(pack_id, ("LPS", "CC-BY-4.0", "Apache-2.0"))
        if (
            pack.runtime_geometry != geometry
            or manifest.get("id") != pack_id
            or manifest.get("license") != data_license
            or manifest.get("label_license") != label_license
            or manifest.get("frame") != frame
            or manifest.get("units")
            != (
                "fraction/pixel"
                if pack_id == "retained-imaging101-eht-features-dynamic-v1"
                else "Jy/pixel"
                if pack_id
                in {"retained-imaging101-eht-uq-v1", "retained-imaging101-eht-dynamic-v1"}
                else "mm^2/s"
                if pack_id == "retained-imaging101-dti-v1"
                else "um"
                if pack_id == "retained-imaging101-ptychography-v1"
                else "m"
                if pack_id == "retained-imaging101-nlos-v1"
                else "cm^-1"
                if pack_id == "retained-imaging101-cars-v1"
                else "record"
                if pack_id == "retained-history-sourcing-v1"
                else "voxel"
                if pack_id
                in {
                    "retained-dental-original-v1",
                    "retained-dental-v2-v1",
                    "retained-dental-v3-v1",
                    "retained-segmentation-calibration-v1",
                    "retained-aneurysm-localization-v1",
                }
                else "px"
                if pack_id
                in {
                    "retained-hubmap-inventory-v1",
                    "retained-tiger-context-v1",
                    "retained-imaging101-fan-beam-v1",
                }
                else "mm"
            )
            or manifest.get("reference_policy")
            != ("reader-reference-reveal" if reference_file else "no-reference-assets")
            or not manifest.get("sources")
            or set(pack.retained_files) != required
            or len(pack.retained_files) != len(required)
        ):
            raise ValueError(
                "Source teaching packs require exact provenance, terms and reference policy"
            )
        assets = {asset["file"]: asset for asset in manifest["assets"]}
        if set(assets) != required or len(assets) != len(manifest["assets"]):
            raise ValueError("Missing or duplicate source teaching asset")
        dependencies = {
            p.relative_to(root).as_posix(): storage.sha(p) for p in (index_path, manifest_path)
        }
        for name in pack.retained_files:
            path = storage.inside(manifest_path.parent, name)
            asset = assets[name]
            role = "reader-reference-reveal" if name == reference_file else "illustration"
            if (
                asset["provenance"] != "source-derived-teaching"
                or asset["role"] != role
                or storage.sha(path) != asset["sha256"]
                or path.stat().st_size != asset["bytes"]
            ):
                raise ValueError(f"Stale or incorrectly classified source teaching asset: {name}")
            dependencies[path.relative_to(root).as_posix()] = storage.sha(path)
        return storage.sha(manifest_path), dependencies
    if isinstance(pack, AnatomyPack):
        if pack_id != "retained-anatomy-v1" or not manifest.get("terms"):
            raise ValueError("Invalid anatomy owner or missing terms")
        required_parts = {
            "liver",
            "stomach",
            "spleen",
            "pancreas",
            "kidney_left",
            "kidney_right",
            "gallbladder",
        }
        required_files = {name + ".json" for name in required_parts} | {
            "NOTICE.md",
            "CC-BY-4.0.txt",
        }
        if set(pack.retained_files) != required_files or len(pack.retained_files) != len(
            required_files
        ):
            raise ValueError("Anatomy assembly requires its exact parts and notices")
        frames = {json.dumps(manifest["assets"][name]["affine"]) for name in required_parts}
        cases = {
            manifest["assets"][name]["source"].split("/segmentations/")[0]
            for name in required_parts
        }
        if len(frames) != 1 or len(cases) != 1:
            raise ValueError("Anatomy parts must share a source case and physical frame")
        dependencies = {
            p.relative_to(root).as_posix(): storage.sha(p) for p in (index_path, manifest_path)
        }
        for name in pack.retained_files:
            path = storage.inside(manifest_path.parent, name)
            if name.endswith(".json"):
                asset = manifest["assets"][path.stem]
                if (
                    storage.sha(path) != asset["asset_sha256"]
                    or path.stat().st_size != asset["bytes"]
                ):
                    raise ValueError(f"Stale anatomy asset: {name}")
            dependencies[path.relative_to(root).as_posix()] = storage.sha(path)
        return storage.sha(manifest_path), dependencies
    if isinstance(pack, FixturePack):
        if (
            manifest.get("license") != "CC0-1.0"
            or not manifest.get("frame")
            or not manifest.get("units")
        ):
            raise ValueError("Fixture terms or coordinate frame missing")
        required = {
            "local-edit-v1": {
                "fixture.json",
                "masks.npz",
                "supplied-mask.png",
                "corrected-mask.png",
                "editable-domain.png",
                "unchanged-control.png",
            },
            "inverse-problems-v1": {
                "fixture.json",
                "arrays.npz",
                "ct-sinogram.png",
                "ct-reconstruction.png",
                "mri-kspace.png",
                "mri-sampled.png",
                "mri-zero-filled.png",
                "object.png",
            },
        }.get(pack_id, {"fixture.json"})
        if not required.issubset(pack.retained_files):
            raise ValueError("Recipe pack missing required dependencies")
    if manifest["id"] != pack_id:
        raise ValueError("Asset pack mismatch")
    dependencies = {
        p.relative_to(root).as_posix(): storage.sha(p) for p in (index_path, manifest_path)
    }
    assets = {asset["file"]: asset for asset in manifest["assets"]}
    if len(assets) != len(manifest["assets"]):
        raise ValueError("Duplicate manifest asset")
    for name in pack.retained_files:
        asset = assets[name]
        if asset["provenance"] != "procedural-teaching" or asset["role"] != "illustration":
            raise ValueError("Pilot prohibits reference or non-teaching assets")
        path = storage.inside(manifest_path.parent, name)
        if storage.sha(path) != asset["sha256"] or path.stat().st_size != asset["bytes"]:
            raise ValueError(f"Stale asset: {name}")
        dependencies[path.relative_to(root).as_posix()] = storage.sha(path)
    return storage.sha(manifest_path), dependencies


def compile_story(root: Path, path: Path) -> StoryPlan:
    relative = path.relative_to(root) if path.is_absolute() else path
    root = root.resolve()
    path = storage.inside(root, relative)
    source = path.relative_to(root).as_posix()
    source_sha = storage.sha(path)
    raw = path.read_text()
    if "[[AUTHOR:" in raw:
        raise ValueError("Unfinished story draft: replace every [[AUTHOR:...]] field")
    compiler = compiler_hashes(root)
    document = parse_document(raw)
    if document.schema == 2:
        story = parse_expansion(_legacy_semantics(document, source, source_sha))
        expected_pack = RECIPE_PACKS[story.recipe]
        if story.asset_pack != expected_pack:
            raise ValueError("Recipe asset pack mismatch")
        if (
            story.asset_pack == "retained-anatomy-v1"
            or story.asset_pack in SOURCE_REFERENCE_PACKS
            or story.asset_pack in SOURCE_INPUT_PACKS
        ) != (story.source_class == "source-derived-teaching"):
            raise ValueError("Recipe provenance mismatch")
        if (story.asset_pack in SOURCE_REFERENCE_PACKS) != (
            story.reference_policy == "reader-reference-reveal"
        ):
            raise ValueError("Recipe reference policy mismatch")
        manifest_hash, dependencies = resolve_assets(root, story.asset_pack)
        if story.recipe == "topology-v1":
            _, route_dependencies = resolve_assets(root, "tb3-route-kit-v1")
            dependencies.update(route_dependencies)
        dependencies.update(compiler)
        dependencies[path.relative_to(root).as_posix()] = source_sha
        for locator in story.source_locators:
            source_path = storage.inside(root, locator)
            if not source_path.is_file():
                raise ValueError(f"Missing story source: {locator}")
            dependencies[source_path.relative_to(root).as_posix()] = storage.sha(source_path)
        result = story.model_dump(mode="json", by_alias=True)
        at = 0
        for beat in result["beats"]:
            beat["startFrame"] = at
            at += beat["frames"]
            beat["endFrame"] = at
        _check_dependencies(root, dependencies)
        result.update(
            durationFrames=at,
            source_sha256=source_sha,
            asset_manifest_sha256=manifest_hash,
            dependencies=dependencies,
        )
        return cast(StoryPlan, result)
    header, beats = parse_story(document)
    manifest_hash, dependencies = resolve_assets(root, header.asset_pack)
    dependencies.update(compiler)
    dependencies[path.relative_to(root).as_posix()] = source_sha
    at = 0
    projected: list[StoryBeat] = []
    for beat in beats:
        end = at + round(beat.duration * header.fps)
        projected.append(cast(StoryBeat, {**beat.model_dump(), "startFrame": at, "endFrame": end}))
        at = end
    _check_dependencies(root, dependencies)
    return cast(
        StoryPlan,
        {
            **header.model_dump(by_alias=True),
            "durationFrames": at,
            "beats": projected,
            "source_sha256": source_sha,
            "asset_manifest_sha256": manifest_hash,
            "dependencies": dependencies,
            "scope": SCOPE,
        },
    )


def resolve_stories(root: Path, entries: list[Document]) -> dict[str, StoryPlan]:
    plans: dict[str, StoryPlan] = {}
    for entry in entries:
        illustration = entry.get("illustration")
        if not isinstance(illustration, dict):
            continue
        story_id = illustration.get("story_id")
        if story_id is None:
            continue
        if not isinstance(story_id, str) or not re.fullmatch(r"[a-z0-9-]+", story_id):
            raise MedicalError("Invalid explanation story ID")
        matches = list(root.glob(f"groups/*/presentation/stories/{story_id}.story.md")) + list(
            root.glob(f"presentation/external-tasks/stories/{story_id}.story.md")
        )
        if len(matches) != 1:
            raise MedicalError(f"Unknown or ambiguous explanation story: {story_id}")
        plan = compile_story(root, matches[0])
        if plan["id"] != story_id:
            raise MedicalError("Story binding and script ID differ")
        plans[story_id] = plan
    return plans


def write_projections(plan: StoryPlan, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "plan.json").write_text(json.dumps(plan, indent=2) + "\n")

    def stamp(frame: int, sep: str) -> str:
        ms = round(frame / plan["fps"] * 1000)
        return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02}{sep}{ms % 1000:03}"

    for ext, sep in (("vtt", "."), ("srt", ",")):
        text = "WEBVTT\n\n" if ext == "vtt" else ""
        for i, beat in enumerate(plan["beats"]):
            text += (
                f"{i + 1}\n{stamp(beat['startFrame'], sep)} --> "
                f"{stamp(beat['endFrame'], sep)}\n{beat['caption']}\n\n"
            )
        (output / f"captions.{ext}").write_text(text)
    (output / "transcript.md").write_text(
        "# "
        + plan["title"]
        + "\n\n"
        + plan["scope"]
        + "\n\n"
        + "\n\n".join(
            f"## {beat['id']} · {beat['caption']}\n\n{beat['narration']}" for beat in plan["beats"]
        )
        + "\n"
    )


def build_export(root: Path, story_id: str, output: Path) -> StoryPlan:
    """Assemble a standalone composed view from the same plan and checked frontend."""
    plans = resolve_stories(root, [{"illustration": {"story_id": story_id}}])
    plan = plans[story_id]
    write_export(root, plan, output)
    return plan


def write_export(root: Path, plan: StoryPlan, output: Path) -> None:
    """Project an explicitly compiled plan to the shared standalone view."""
    from . import frontend

    root = root.resolve()
    _check_dependencies(root, plan["dependencies"])
    script, css = frontend.assets(root, "explainer-export")
    write_projections(plan, output)
    source = next(name for name in plan["dependencies"] if name.endswith(".story.md"))
    (output / "canonical.story.md").write_bytes((root / source).read_bytes())
    common = (root / "presentation/ui.css").read_text()
    payload = json.dumps(plan).replace("<", "\\u003c").replace("&", "\\u0026")
    script = re.sub(r"</script", r"<\\/script", script, flags=re.I)
    (output / "index.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{escape(plan['title'])}</title>"
        f'<style>{common}\n{css}\nbody{{margin:0}}</style><div id="root"></div>'
        f'<script id="story-plan" type="application/json">{payload}</script>'
        f"<script>{script}</script></html>"
    )
    _check_dependencies(root, plan["dependencies"])
    frontend.assets(root, "explainer-export")


def _check_dependencies(root: Path, dependencies: dict[str, str]) -> None:
    for name, expected in dependencies.items():
        if storage.sha(storage.inside(root, name)) != expected:
            raise ValueError(f"Compiled story dependency changed: {name}")
