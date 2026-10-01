"""Versioned browser payloads: Python authority, validation and generated TS types.

These are presentation projections, not replacements for scientific record schemas.
Additional source fields survive projection; only declared browser fields are required.
"""

from __future__ import annotations

import argparse
import json
import types
from pathlib import Path
from typing import (
    Literal,
    NotRequired,
    TypedDict,
    cast,
    get_args,
    get_origin,
    get_type_hints,
    is_typeddict,
)

from .errors import MedicalError
from .types import Document

VisualRole = Literal["input", "helpers", "answer"]
TaskTab = Literal["overview", "requirements", "examples", "sources"]
BrowseView = Literal["capability", "repository"]
ResearchLane = Literal["tasks", "supporting", "all"]
BriefField = Literal[
    "goal",
    "value",
    "raw",
    "helpers",
    "output",
    "challenge",
    "spec",
    "tools",
    "score",
    "reference",
    "families",
    "gap",
    "case_note",
]


class StoryBeat(TypedDict):
    id: str
    duration: float
    caption: str
    narration: str
    visual: str
    context: tuple[float, float]
    route: tuple[float, float]
    ribbon: tuple[float, float]
    cursor: tuple[float, float]
    unfold: tuple[float, float]
    output: tuple[float, float]
    startFrame: int
    endFrame: int


class RouteStoryPlan(TypedDict):
    schema: Literal[1]
    id: str
    title: str
    locale: Literal["en"]
    purpose: str
    recipe: Literal["route-unfold-v1"]
    asset_pack: Literal["tb3-route-kit-v1"]
    fps: int
    reference_policy: Literal["no-reference-assets"]
    source_class: Literal["procedural-teaching"]
    durationFrames: int
    source_sha256: str
    asset_manifest_sha256: str
    dependencies: dict[str, str]
    scope: str
    beats: list[StoryBeat]


class ExpansionPlan(TypedDict):
    schema: Literal[2]
    id: str
    title: str
    locale: Literal["en"]
    purpose: str
    scope: str
    asset_pack: str
    source_class: Literal["procedural-teaching", "source-derived-teaching", "symbolic-protocol"]
    reference_policy: Literal["no-reference-assets", "reader-reference-reveal"]
    fps: int
    source_locators: list[str]
    durationFrames: int
    source_sha256: str
    asset_manifest_sha256: str
    dependencies: dict[str, str]


class ExpansionBeat(TypedDict):
    id: str
    frames: int
    caption: str
    narration: str
    visual: str
    cut: Literal["continuous", "intentional-cut"]
    startFrame: int
    endFrame: int


class TopologyChannels(TypedDict):
    focus: tuple[float, float]
    trace: tuple[float, float]
    inventory: tuple[float, float]


class TopologyBeat(ExpansionBeat):
    channels: TopologyChannels


class TopologyPlan(ExpansionPlan):
    recipe: Literal["topology-v1"]
    operation: Literal["ordered-path", "edge-inventory"]
    beats: list[TopologyBeat]


class CorrespondenceChannels(TypedDict):
    transform: tuple[float, float]
    query: tuple[float, float]
    residual: tuple[float, float]


class CorrespondenceBeat(ExpansionBeat):
    show_deformed_target: bool
    channels: CorrespondenceChannels


class CorrespondencePlan(ExpansionPlan):
    recipe: Literal["correspondence-v1"]
    beats: list[CorrespondenceBeat]


class MaterialChannels(TypedDict):
    phase: tuple[float, float]
    markers: tuple[float, float]
    alternative: tuple[float, float]


class MaterialBeat(ExpansionBeat):
    channels: MaterialChannels


class MaterialPlan(ExpansionPlan):
    recipe: Literal["shape-material-v1"]
    beats: list[MaterialBeat]


class LongitudinalChannels(TypedDict):
    visits: tuple[float, float]
    links: tuple[float, float]
    coverage: tuple[float, float]


class LongitudinalBeat(ExpansionBeat):
    channels: LongitudinalChannels


class LongitudinalPlan(ExpansionPlan):
    recipe: Literal["longitudinal-v1"]
    beats: list[LongitudinalBeat]


class MultiscaleChannels(TypedDict):
    viewport: tuple[float, float]
    selections: tuple[float, float]
    coverage: tuple[float, float]
    outputs: tuple[float, float]


class MultiscaleBeat(ExpansionBeat):
    channels: MultiscaleChannels


class MultiscalePlan(ExpansionPlan):
    recipe: Literal["multiscale-v1"]
    operation: Literal["coordinate-navigation", "supplied-patches", "annotation-coverage"]
    beats: list[MultiscaleBeat]


class InverseChannels(TypedDict):
    observations: tuple[float, float]
    reconstruction: tuple[float, float]
    residual: tuple[float, float]


class InverseBeat(ExpansionBeat):
    channels: InverseChannels


class InversePlan(ExpansionPlan):
    recipe: Literal["inverse-v1"]
    beats: list[InverseBeat]
    acquisition: Literal["ct-parallel", "mri-cartesian"]


class EditChannels(TypedDict):
    domain: tuple[float, float]
    correction: tuple[float, float]
    control: tuple[float, float]


class EditBeat(ExpansionBeat):
    channels: EditChannels


class EditPlan(ExpansionPlan):
    recipe: Literal["local-edit-v1"]
    beats: list[EditBeat]


class AnatomyChannels(TypedDict):
    focus: tuple[float, float]
    evidence: tuple[float, float]
    output: tuple[float, float]


class AnatomyBeat(ExpansionBeat):
    channels: AnatomyChannels


class AnatomyPlan(ExpansionPlan):
    recipe: Literal["anatomy-audit-v1"]
    beats: list[AnatomyBeat]


class IdentityChannels(TypedDict):
    focus: tuple[float, float]
    inventory: tuple[float, float]
    reveal: tuple[float, float]


class IdentityBeat(ExpansionBeat):
    channels: IdentityChannels


class IdentityPlan(ExpansionPlan):
    recipe: Literal["anatomy-identity-v1"]
    beats: list[IdentityBeat]


class PrototypeIdentityPlan(ExpansionPlan):
    recipe: Literal["prototype-identity-v1"]
    beats: list[IdentityBeat]


class AirwayRepairChannels(TypedDict):
    view: tuple[float, float]
    reference: tuple[float, float]
    output: tuple[float, float]


class AirwayRepairBeat(ExpansionBeat):
    channels: AirwayRepairChannels
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


class AirwayRepairPlan(ExpansionPlan):
    recipe: Literal["airway-repair-v1"]
    beats: list[AirwayRepairBeat]


class LongitudinalCtRevisedChannels(TypedDict):
    view: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class LongitudinalCtRevisedBeat(ExpansionBeat):
    channels: LongitudinalCtRevisedChannels
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


class LongitudinalCtRevisedPlan(ExpansionPlan):
    recipe: Literal["longitudinal-ct-revised-v1"]
    beats: list[LongitudinalCtRevisedBeat]


class LongitudinalCtOriginalChannels(TypedDict):
    view: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class LongitudinalCtOriginalBeat(ExpansionBeat):
    channels: LongitudinalCtOriginalChannels
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


class LongitudinalCtOriginalPlan(ExpansionPlan):
    recipe: Literal["longitudinal-ct-original-v1"]
    beats: list[LongitudinalCtOriginalBeat]


class LongitudinalMriChannels(TypedDict):
    view: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class LongitudinalMriBeat(ExpansionBeat):
    channels: LongitudinalMriChannels
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


class LongitudinalMriPlan(ExpansionPlan):
    recipe: Literal["longitudinal-mri-v1"]
    beats: list[LongitudinalMriBeat]


class TigerContextChannels(TypedDict):
    view: tuple[float, float]
    reference: tuple[float, float]


class HubmapInventoryChannels(TypedDict):
    view: tuple[float, float]
    reference: tuple[float, float]


class TigerContextBeat(ExpansionBeat):
    channels: TigerContextChannels
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


class TigerContextPlan(ExpansionPlan):
    recipe: Literal["tiger-context-v1"]
    beats: list[TigerContextBeat]


class HubmapInventoryBeat(ExpansionBeat):
    channels: HubmapInventoryChannels
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


class HubmapInventoryPlan(ExpansionPlan):
    recipe: Literal["hubmap-inventory-v1"]
    beats: list[HubmapInventoryBeat]


class TopbrainScreenChannels(TypedDict):
    view: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class TopbrainScreenBeat(ExpansionBeat):
    channels: TopbrainScreenChannels
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


class TopbrainScreenPlan(ExpansionPlan):
    recipe: Literal["topbrain-screen-v1"]
    beats: list[TopbrainScreenBeat]


class VesselSourceChannels(TypedDict):
    scan: tuple[float, float]
    reference: tuple[float, float]
    output: tuple[float, float]


class VesselSourceBeat(ExpansionBeat):
    channels: VesselSourceChannels
    scene: Literal[
        "sources", "states", "inspect", "contacts", "nodes", "contract", "admission", "limits"
    ]


class VesselSourcePlan(ExpansionPlan):
    recipe: Literal["vessel-source-v1"]
    beats: list[VesselSourceBeat]


class ResectPilotChannels(TypedDict):
    view: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class ResectPilotBeat(ExpansionBeat):
    channels: ResectPilotChannels
    scene: Literal[
        "inputs", "cue", "inspect", "search", "output", "reference", "controls", "limits"
    ]


class ResectPilotPlan(ExpansionPlan):
    recipe: Literal["resect-pilot-v1"]
    beats: list[ResectPilotBeat]


class ResectChannels(TypedDict):
    reference: tuple[float, float]
    scan: tuple[float, float]
    helper: tuple[float, float]
    output: tuple[float, float]


class ResectBeat(ExpansionBeat):
    channels: ResectChannels
    scene: Literal[
        "inputs", "frame", "inspect", "helpers", "output", "reference", "cases", "limits"
    ]


class ResectPlan(ExpansionPlan):
    recipe: Literal["resect-correspondence-v1"]
    beats: list[ResectBeat]


class RegistrationAnalysisChannels(TypedDict):
    reference: tuple[float, float]
    bounds: tuple[float, float]
    curve: tuple[float, float]


class RegistrationAnalysisBeat(ExpansionBeat):
    channels: RegistrationAnalysisChannels
    scene: Literal[
        "input", "replay", "composition", "support", "objective", "context", "repeats", "limits"
    ]


class RegistrationAnalysisPlan(ExpansionPlan):
    recipe: Literal["registration-analysis-v1"]
    beats: list[RegistrationAnalysisBeat]


class Imaging101EhtOriginalChannels(TypedDict):
    view: tuple[float, float]
    reference: tuple[float, float]


class Imaging101EhtOriginalBeat(ExpansionBeat):
    channels: Imaging101EhtOriginalChannels
    scene: Literal[
        "inputs", "closures", "observables", "imaging", "outputs", "reference", "scoring", "limits"
    ]


class Imaging101EhtOriginalPlan(ExpansionPlan):
    recipe: Literal["imaging101-eht-original-v1"]
    beats: list[Imaging101EhtOriginalBeat]


class Imaging101EhtFeaturesDynamicChannels(TypedDict):
    view: tuple[float, float]
    reference: tuple[float, float]


class Imaging101EhtFeaturesDynamicBeat(ExpansionBeat):
    channels: Imaging101EhtFeaturesDynamicChannels
    scene: Literal[
        "inputs", "closures", "model", "posterior", "reference", "diagnostics", "scoring", "limits"
    ]


class Imaging101EhtFeaturesDynamicPlan(ExpansionPlan):
    recipe: Literal["imaging101-eht-features-dynamic-v1"]
    beats: list[Imaging101EhtFeaturesDynamicBeat]


class Imaging101EhtDynamicChannels(TypedDict):
    view: tuple[float, float]
    reference: tuple[float, float]


class Imaging101EhtDynamicBeat(ExpansionBeat):
    channels: Imaging101EhtDynamicChannels
    scene: Literal[
        "inputs", "operator", "temporal", "output", "reference", "diagnostics", "scoring", "limits"
    ]


class Imaging101EhtDynamicPlan(ExpansionPlan):
    recipe: Literal["imaging101-eht-dynamic-v1"]
    beats: list[Imaging101EhtDynamicBeat]


class Imaging101EhtUqChannels(TypedDict):
    view: tuple[float, float]
    reference: tuple[float, float]


class Imaging101EhtUqBeat(ExpansionBeat):
    channels: Imaging101EhtUqChannels
    scene: Literal[
        "inputs", "closures", "prior", "samples", "output", "reference", "scoring", "limits"
    ]


class Imaging101EhtUqPlan(ExpansionPlan):
    recipe: Literal["imaging101-eht-uq-v1"]
    beats: list[Imaging101EhtUqBeat]


class Imaging101DtiChannels(TypedDict):
    view: tuple[float, float]
    reference: tuple[float, float]


class Imaging101DtiBeat(ExpansionBeat):
    channels: Imaging101DtiChannels
    scene: Literal[
        "inputs", "gradients", "fit", "tensor", "output", "reference", "scoring", "limits"
    ]


class Imaging101DtiPlan(ExpansionPlan):
    recipe: Literal["imaging101-dti-v1"]
    beats: list[Imaging101DtiBeat]


class Imaging101DeflectometryChannels(TypedDict):
    view: tuple[float, float]
    reference: tuple[float, float]


class Imaging101DeflectometryBeat(ExpansionBeat):
    channels: Imaging101DeflectometryChannels
    scene: Literal[
        "inputs", "calibration", "phase", "geometry", "output", "reference", "scoring", "limits"
    ]


class Imaging101DeflectometryPlan(ExpansionPlan):
    recipe: Literal["imaging101-deflectometry-v1"]
    beats: list[Imaging101DeflectometryBeat]


class Imaging101FanBeamChannels(TypedDict):
    view: tuple[float, float]
    reference: tuple[float, float]


class Imaging101FanBeamBeat(ExpansionBeat):
    channels: Imaging101FanBeamChannels
    scene: Literal[
        "inputs", "geometry", "weights", "output", "reference", "scoring", "staging", "limits"
    ]


class Imaging101FanBeamPlan(ExpansionPlan):
    recipe: Literal["imaging101-fan-beam-v1"]
    beats: list[Imaging101FanBeamBeat]


class Imaging101DualEnergyChannels(TypedDict):
    view: tuple[float, float]
    reference: tuple[float, float]


class Imaging101DualEnergyBeat(ExpansionBeat):
    channels: Imaging101DualEnergyChannels
    scene: Literal[
        "inputs", "calibration", "forward", "output", "reference", "staging", "scoring", "limits"
    ]


class Imaging101DualEnergyPlan(ExpansionPlan):
    recipe: Literal["imaging101-dual-energy-v1"]
    beats: list[Imaging101DualEnergyBeat]


class Imaging101PtychographyChannels(TypedDict):
    view: tuple[float, float]
    reference: tuple[float, float]


class Imaging101PtychographyBeat(ExpansionBeat):
    channels: Imaging101PtychographyChannels
    scene: Literal[
        "inputs", "overlap", "projection", "output", "reference", "staging", "scoring", "limits"
    ]


class Imaging101PtychographyPlan(ExpansionPlan):
    recipe: Literal["imaging101-ptychography-v1"]
    beats: list[Imaging101PtychographyBeat]


class Imaging101NlosChannels(TypedDict):
    view: tuple[float, float]
    reference: tuple[float, float]


class Imaging101NlosBeat(ExpansionBeat):
    channels: Imaging101NlosChannels
    scene: Literal[
        "inputs", "alignment", "stolt", "output", "reference", "staging", "scoring", "limits"
    ]


class Imaging101NlosPlan(ExpansionPlan):
    recipe: Literal["imaging101-nlos-v1"]
    beats: list[Imaging101NlosBeat]


class Imaging101CarsChannels(TypedDict):
    view: tuple[float, float]
    reference: tuple[float, float]


class Imaging101CarsBeat(ExpansionBeat):
    channels: Imaging101CarsChannels
    scene: Literal["inputs", "staging", "forward", "fit", "reference", "scoring", "shape", "limits"]


class Imaging101CarsPlan(ExpansionPlan):
    recipe: Literal["imaging101-cars-v1"]
    beats: list[Imaging101CarsBeat]


class RexTopcowChannels(TypedDict):
    view: tuple[float, float]
    reference: tuple[float, float]


class RexTopcowBeat(ExpansionBeat):
    channels: RexTopcowChannels
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


class RexTopcowPlan(ExpansionPlan):
    recipe: Literal["rex-topcow-v1"]
    beats: list[RexTopcowBeat]


class AutomedMultiorganChannels(TypedDict):
    view: tuple[float, float]
    reference: tuple[float, float]


class AutomedMultiorganBeat(ExpansionBeat):
    channels: AutomedMultiorganChannels
    scene: Literal[
        "inputs", "workflow", "remap", "geometry", "reference", "scoring", "coverage", "limits"
    ]


class AutomedMultiorganPlan(ExpansionPlan):
    recipe: Literal["automed-multiorgan-v1"]
    beats: list[AutomedMultiorganBeat]


class BcerWorkflowChannels(TypedDict):
    view: tuple[float, float]


class BcerWorkflowBeat(ExpansionBeat):
    channels: BcerWorkflowChannels
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


class BcerWorkflowPlan(ExpansionPlan):
    recipe: Literal["bcer-workflow-v1"]
    beats: list[BcerWorkflowBeat]


class AbraAnnotationChannels(TypedDict):
    view: tuple[float, float]
    helper: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class AbraAnnotationBeat(ExpansionBeat):
    channels: AbraAnnotationChannels
    scene: Literal[
        "inputs", "navigate", "coordinates", "reference", "ordinary", "oracle", "scoring", "limits"
    ]


class AbraAnnotationPlan(ExpansionPlan):
    recipe: Literal["abra-annotation-v1"]
    beats: list[AbraAnnotationBeat]


class CtContextChannels(TypedDict):
    view: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class CtContextBeat(ExpansionBeat):
    channels: CtContextChannels
    scene: Literal[
        "inputs", "headers", "liver", "surgery", "fields", "reference", "validator", "limits"
    ]


class CtContextPlan(ExpansionPlan):
    recipe: Literal["ct-context-v1"]
    beats: list[CtContextBeat]


class HistorySourcingChannels(TypedDict):
    view: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class HistorySourcingBeat(ExpansionBeat):
    channels: HistorySourcingChannels
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


class HistorySourcingPlan(ExpansionPlan):
    recipe: Literal["history-sourcing-v1"]
    beats: list[HistorySourcingBeat]


class MriImporterChannels(TypedDict):
    view: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class MriImporterBeat(ExpansionBeat):
    channels: MriImporterChannels
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


class MriImporterPlan(ExpansionPlan):
    recipe: Literal["mri-importer-v1"]
    beats: list[MriImporterBeat]


class LocalizedCtChannels(TypedDict):
    view: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class LocalizedCtBeat(ExpansionBeat):
    channels: LocalizedCtChannels
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


class LocalizedCtPlan(ExpansionPlan):
    recipe: Literal["localized-ct-v1"]
    beats: list[LocalizedCtBeat]


class AneurysmChannels(TypedDict):
    view: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class AneurysmBeat(ExpansionBeat):
    channels: AneurysmChannels
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


class AneurysmPlan(ExpansionPlan):
    recipe: Literal["aneurysm-localization-v1"]
    beats: list[AneurysmBeat]


class SegmentationCalibrationChannels(TypedDict):
    view: tuple[float, float]
    condition: tuple[float, float]
    box: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class SegmentationCalibrationBeat(ExpansionBeat):
    channels: SegmentationCalibrationChannels
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


class SegmentationCalibrationPlan(ExpansionPlan):
    recipe: Literal["segmentation-calibration-v1"]
    beats: list[SegmentationCalibrationBeat]


class DentalV3Channels(TypedDict):
    view: tuple[float, float]
    helper: tuple[float, float]
    transfer: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]
    stage: tuple[float, float]


class DentalV3Beat(ExpansionBeat):
    channels: DentalV3Channels
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


class DentalV3Plan(ExpansionPlan):
    recipe: Literal["dental-v3-v1"]
    beats: list[DentalV3Beat]


class DentalV2Channels(TypedDict):
    view: tuple[float, float]
    helper: tuple[float, float]
    transfer: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]
    stage: tuple[float, float]


class DentalV2Beat(ExpansionBeat):
    channels: DentalV2Channels
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


class DentalV2Plan(ExpansionPlan):
    recipe: Literal["dental-v2-v1"]
    beats: list[DentalV2Beat]


class DentalOriginalChannels(TypedDict):
    diagnostic: tuple[float, float]
    gate: tuple[float, float]
    view: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class DentalOriginalBeat(ExpansionBeat):
    channels: DentalOriginalChannels
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


class DentalOriginalPlan(ExpansionPlan):
    recipe: Literal["dental-original-v1"]
    beats: list[DentalOriginalBeat]


class CtOrganChannels(TypedDict):
    view: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class CtOrganBeat(ExpansionBeat):
    channels: CtOrganChannels
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


class CtOrganPlan(ExpansionPlan):
    recipe: Literal["ct-organ-v1"]
    beats: list[CtOrganBeat]


class NamedLandmarksChannels(TypedDict):
    view: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class NamedLandmarksBeat(ExpansionBeat):
    channels: NamedLandmarksChannels
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


class NamedLandmarksPlan(ExpansionPlan):
    recipe: Literal["named-landmarks-v1"]
    beats: list[NamedLandmarksBeat]


class CardiacContourChannels(TypedDict):
    phase: tuple[float, float]
    helper: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class CardiacContourBeat(ExpansionBeat):
    channels: CardiacContourChannels
    scene: Literal["inputs", "views", "reconstruct", "withheld", "curves", "depth", "limits"]


class CardiacContourPlan(ExpansionPlan):
    recipe: Literal["cardiac-contour-v1"]
    beats: list[CardiacContourBeat]


class CardiacRealEchoChannels(TypedDict):
    phase: tuple[float, float]
    planes: tuple[float, float]
    output: tuple[float, float]
    alternative: tuple[float, float]
    review: tuple[float, float]
    control: tuple[float, float]


class CardiacRealEchoBeat(ExpansionBeat):
    channels: CardiacRealEchoChannels
    scene: Literal[
        "inputs",
        "geometry",
        "interpretation",
        "reconstruction",
        "alternatives",
        "review",
        "controls",
        "limits",
    ]


class CardiacRealEchoPlan(ExpansionPlan):
    recipe: Literal["cardiac-real-echo-v1"]
    beats: list[CardiacRealEchoBeat]


class MaskMechanicsChannels(TypedDict):
    phase: tuple[float, float]
    condition: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]
    clinical: tuple[float, float]


class MaskMechanicsBeat(ExpansionBeat):
    channels: MaskMechanicsChannels
    scene: Literal[
        "input-masks",
        "input-images",
        "mesh-construction",
        "fixed-connectivity",
        "deformation-gradient",
        "occupancy",
        "material-ambiguity",
        "reference-probes",
        "clinical-transfer",
        "limits",
    ]


class MaskMechanicsPlan(ExpansionPlan):
    recipe: Literal["cardiac-mask-mechanics-v1"]
    beats: list[MaskMechanicsBeat]


class ReportReadingChannels(TypedDict):
    phase: tuple[float, float]
    helper: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class ReportReadingBeat(ExpansionBeat):
    channels: ReportReadingChannels
    scene: Literal["availability", "input", "viewer", "answer", "reference", "comparison", "limits"]


class ReportReadingPlan(ExpansionPlan):
    recipe: Literal["report-reading-v1"]
    beats: list[ReportReadingBeat]


class AutomedKidneyChannels(TypedDict):
    view: tuple[float, float]
    helper: tuple[float, float]
    step: tuple[float, float]
    reference: tuple[float, float]
    fixture: tuple[float, float]


class AutomedKidneyBeat(ExpansionBeat):
    channels: AutomedKidneyChannels
    scene: Literal["inputs", "assistance", "workflow", "schema", "reference", "contract", "limits"]


class AutomedKidneyPlan(ExpansionPlan):
    recipe: Literal["automed-kidney-v1"]
    beats: list[AutomedKidneyBeat]


class BcerBrainChannels(TypedDict):
    view: tuple[float, float]


class BcerBrainBeat(ExpansionBeat):
    channels: BcerBrainChannels
    scene: Literal["inputs", "identify", "segment", "labels", "checks", "limits"]


class BcerBrainPlan(ExpansionPlan):
    recipe: Literal["bcer-brain-v1"]
    beats: list[BcerBrainBeat]


class BcerProstateChannels(TypedDict):
    view: tuple[float, float]
    moving: tuple[float, float]
    operation: tuple[float, float]
    swap: tuple[float, float]


class BcerProstateBeat(ExpansionBeat):
    channels: BcerProstateChannels
    scene: Literal[
        "availability", "inputs", "select", "coordinates", "resample", "contract", "limits"
    ]


class BcerProstatePlan(ExpansionPlan):
    recipe: Literal["bcer-prostate-registration-v1"]
    beats: list[BcerProstateBeat]


class AbraLongitudinalChannels(TypedDict):
    baseline: tuple[float, float]
    followup: tuple[float, float]
    task: tuple[float, float]
    reference: tuple[float, float]


class AbraLongitudinalBeat(ExpansionBeat):
    channels: AbraLongitudinalChannels
    scene: Literal["inputs", "metadata", "counts", "browse", "submit", "reference", "limits"]


class AbraLongitudinalPlan(ExpansionPlan):
    recipe: Literal["abra-longitudinal-v1"]
    beats: list[AbraLongitudinalBeat]


class RexDentexChannels(TypedDict):
    box: tuple[float, float]
    labels: tuple[float, float]
    reference: tuple[float, float]


class RexDentexBeat(ExpansionBeat):
    channels: RexDentexChannels
    scene: Literal["input", "localize", "encode", "reference", "audit"]


class RexDentexPlan(ExpansionPlan):
    recipe: Literal["rexmle-dentex-v1"]
    beats: list[RexDentexBeat]


class RexIslesChannels(TypedDict):
    slice: tuple[float, float]
    flair: tuple[float, float]
    reference: tuple[float, float]


class RexIslesBeat(ExpansionBeat):
    channels: RexIslesChannels
    scene: Literal["inputs", "geometry", "output", "reference", "limits"]


class RexIslesPlan(ExpansionPlan):
    recipe: Literal["rex-isles22-v1"]
    beats: list[RexIslesBeat]


class RexCellsegChannels(TypedDict):
    helper: tuple[float, float]
    instance: tuple[float, float]
    metric: tuple[float, float]


class RexCellsegBeat(ExpansionBeat):
    channels: RexCellsegChannels
    scene: Literal["input", "helper", "instances", "submission", "scoring", "limits"]


class RexCellsegPlan(ExpansionPlan):
    recipe: Literal["rexmle-neurips-cellseg-v1"]
    beats: list[RexCellsegBeat]


class RexPantherTask1Channels(TypedDict):
    grid: tuple[float, float]
    reference: tuple[float, float]


class RexPantherTask1Beat(ExpansionBeat):
    channels: RexPantherTask1Channels
    scene: Literal["input", "geometry", "output", "reference", "limits"]


class RexPantherTask1Plan(ExpansionPlan):
    recipe: Literal["rex-panther-task1-v1"]
    beats: list[RexPantherTask1Beat]


class RexPantherTask2Channels(TypedDict):
    grid: tuple[float, float]
    reference: tuple[float, float]


class RexPantherTask2Beat(ExpansionBeat):
    channels: RexPantherTask2Channels
    scene: Literal["input", "geometry", "output", "reference", "limits"]


class RexPantherTask2Plan(ExpansionPlan):
    recipe: Literal["rex-panther-task2-v1"]
    beats: list[RexPantherTask2Beat]


class RexPumaTrack1Task1Channels(TypedDict):
    helper: tuple[float, float]
    focus: tuple[float, float]
    metric: tuple[float, float]


class RexPumaTrack1Task1Beat(ExpansionBeat):
    channels: RexPumaTrack1Task1Channels
    scene: Literal["input", "helper", "operation", "submission", "scoring", "limits"]


class RexPumaTrack1Task1Plan(ExpansionPlan):
    recipe: Literal["rexmle-puma-track1-task1-v1"]
    beats: list[RexPumaTrack1Task1Beat]


class RexPumaTrack1Task2Channels(TypedDict):
    helper: tuple[float, float]
    focus: tuple[float, float]
    metric: tuple[float, float]


class RexPumaTrack1Task2Beat(ExpansionBeat):
    channels: RexPumaTrack1Task2Channels
    scene: Literal["input", "helper", "operation", "submission", "scoring", "limits"]


class RexPumaTrack1Task2Plan(ExpansionPlan):
    recipe: Literal["rexmle-puma-track1-task2-v1"]
    beats: list[RexPumaTrack1Task2Beat]


class RexPumaTrack2Task2Channels(TypedDict):
    helper: tuple[float, float]
    focus: tuple[float, float]
    metric: tuple[float, float]


class RexPumaTrack2Task2Beat(ExpansionBeat):
    channels: RexPumaTrack2Task2Channels
    scene: Literal["input", "helper", "operation", "submission", "scoring", "limits"]


class RexPumaTrack2Task2Plan(ExpansionPlan):
    recipe: Literal["rexmle-puma-track2-task2-v1"]
    beats: list[RexPumaTrack2Task2Beat]


class RexSegAChannels(TypedDict):
    slice: tuple[float, float]
    reference: tuple[float, float]


class RexSegABeat(ExpansionBeat):
    channels: RexSegAChannels
    scene: Literal["inputs", "geometry", "operation", "output", "helper", "limits"]


class RexSegAPlan(ExpansionPlan):
    recipe: Literal["rex-seg-a-v1"]
    beats: list[RexSegABeat]


class RexTopbrainCtChannels(TypedDict):
    slice: tuple[float, float]
    reference: tuple[float, float]


class RexTopbrainCtBeat(ExpansionBeat):
    channels: RexTopbrainCtChannels
    scene: Literal["inputs", "geometry", "operation", "output", "helper", "limits"]


class RexTopbrainCtPlan(ExpansionPlan):
    recipe: Literal["rex-topbrain-ct-v1"]
    beats: list[RexTopbrainCtBeat]


class RexTopbrainMrChannels(TypedDict):
    slice: tuple[float, float]
    reference: tuple[float, float]


class RexTopbrainMrBeat(ExpansionBeat):
    channels: RexTopbrainMrChannels
    scene: Literal["inputs", "geometry", "operation", "output", "helper", "limits"]


class RexTopbrainMrPlan(ExpansionPlan):
    recipe: Literal["rex-topbrain-mr-v1"]
    beats: list[RexTopbrainMrBeat]


class RexTopcowMrSegChannels(TypedDict):
    slice: tuple[float, float]
    reference: tuple[float, float]


class RexTopcowMrSegBeat(ExpansionBeat):
    channels: RexTopcowMrSegChannels
    scene: Literal["inputs", "geometry", "operation", "output", "reference", "limits"]


class RexTopcowMrSegPlan(ExpansionPlan):
    recipe: Literal["rex-topcow-mr-seg-v1"]
    beats: list[RexTopcowMrSegBeat]


class RexTopcowCtBoxChannels(TypedDict):
    slice: tuple[float, float]
    step: tuple[float, float]
    reference: tuple[float, float]


class RexTopcowCtBoxBeat(ExpansionBeat):
    channels: RexTopcowCtBoxChannels
    scene: Literal["inputs", "geometry", "operation", "output", "reference", "limits"]


class RexTopcowCtBoxPlan(ExpansionPlan):
    recipe: Literal["rex-topcow-ct-box-v1"]
    beats: list[RexTopcowCtBoxBeat]


class RexTopcowMrBoxChannels(TypedDict):
    slice: tuple[float, float]
    step: tuple[float, float]
    reference: tuple[float, float]


class RexTopcowMrBoxBeat(ExpansionBeat):
    channels: RexTopcowMrBoxChannels
    scene: Literal["inputs", "geometry", "operation", "output", "reference", "limits"]


class RexTopcowMrBoxPlan(ExpansionPlan):
    recipe: Literal["rex-topcow-mr-box-v1"]
    beats: list[RexTopcowMrBoxBeat]


class RexTopcowCtEdgesChannels(TypedDict):
    slice: tuple[float, float]
    step: tuple[float, float]
    reference: tuple[float, float]


class RexTopcowCtEdgesBeat(ExpansionBeat):
    channels: RexTopcowCtEdgesChannels
    scene: Literal["inputs", "geometry", "operation", "output", "reference", "limits"]


class RexTopcowCtEdgesPlan(ExpansionPlan):
    recipe: Literal["rex-topcow-ct-edges-v1"]
    beats: list[RexTopcowCtEdgesBeat]


class RexTopcowMrEdgesChannels(TypedDict):
    slice: tuple[float, float]
    step: tuple[float, float]
    reference: tuple[float, float]


class RexTopcowMrEdgesBeat(ExpansionBeat):
    channels: RexTopcowMrEdgesChannels
    scene: Literal["inputs", "geometry", "operation", "output", "reference", "limits"]


class RexTopcowMrEdgesPlan(ExpansionPlan):
    recipe: Literal["rex-topcow-mr-edges-v1"]
    beats: list[RexTopcowMrEdgesBeat]


class AutomedDetectionBccdChannels(TypedDict):
    scan: tuple[float, float]
    format: tuple[float, float]
    reference: tuple[float, float]


class AutomedDetectionBccdBeat(ExpansionBeat):
    channels: AutomedDetectionBccdChannels
    scene: Literal["input", "coordinate", "classes", "submission", "reference", "limits"]


class AutomedDetectionBccdPlan(ExpansionPlan):
    recipe: Literal["automed-full-bccd-detection-v1"]
    beats: list[AutomedDetectionBccdBeat]


class AutomedDetectionDentexChannels(TypedDict):
    scan: tuple[float, float]
    format: tuple[float, float]
    reference: tuple[float, float]


class AutomedDetectionDentexBeat(ExpansionBeat):
    channels: AutomedDetectionDentexChannels
    scene: Literal["input", "coordinate", "classes", "submission", "reference", "limits"]


class AutomedDetectionDentexPlan(ExpansionPlan):
    recipe: Literal["automed-full-dentex-detection-v1"]
    beats: list[AutomedDetectionDentexBeat]


class AutomedDetectionGrazpedwriChannels(TypedDict):
    scan: tuple[float, float]
    format: tuple[float, float]
    reference: tuple[float, float]


class AutomedDetectionGrazpedwriBeat(ExpansionBeat):
    channels: AutomedDetectionGrazpedwriChannels
    scene: Literal["input", "coordinate", "classes", "submission", "reference", "limits"]


class AutomedDetectionGrazpedwriPlan(ExpansionPlan):
    recipe: Literal["automed-full-grazpedwri-detection-v1"]
    beats: list[AutomedDetectionGrazpedwriBeat]


class AutomedDetectionVindrCxrChannels(TypedDict):
    scan: tuple[float, float]
    format: tuple[float, float]
    reference: tuple[float, float]


class AutomedDetectionVindrCxrBeat(ExpansionBeat):
    channels: AutomedDetectionVindrCxrChannels
    scene: Literal["input", "coordinate", "classes", "submission", "reference", "limits"]


class AutomedDetectionVindrCxrPlan(ExpansionPlan):
    recipe: Literal["automed-full-vindr-cxr-detection-v1"]
    beats: list[AutomedDetectionVindrCxrBeat]


class AutomedSegAAeropathChannels(TypedDict):
    slice: tuple[float, float]
    format: tuple[float, float]
    reference: tuple[float, float]


class AutomedSegAAeropathBeat(ExpansionBeat):
    channels: AutomedSegAAeropathChannels
    scene: Literal["input", "stack", "labels", "schema", "reference", "limits"]


class AutomedSegAAeropathPlan(ExpansionPlan):
    recipe: Literal["automed-full-aeropath-seg-v1"]
    beats: list[AutomedSegAAeropathBeat]


class AutomedSegAColonChannels(TypedDict):
    slice: tuple[float, float]
    format: tuple[float, float]
    reference: tuple[float, float]


class AutomedSegAColonBeat(ExpansionBeat):
    channels: AutomedSegAColonChannels
    scene: Literal["input", "stack", "labels", "schema", "reference", "limits"]


class AutomedSegAColonPlan(ExpansionPlan):
    recipe: Literal["automed-full-colon-seg-v1"]
    beats: list[AutomedSegAColonBeat]


class AutomedSegAFetaChannels(TypedDict):
    slice: tuple[float, float]
    format: tuple[float, float]
    reference: tuple[float, float]


class AutomedSegAFetaBeat(ExpansionBeat):
    channels: AutomedSegAFetaChannels
    scene: Literal["input", "stack", "labels", "schema", "reference", "limits"]


class AutomedSegAFetaPlan(ExpansionPlan):
    recipe: Literal["automed-full-feta-seg-v1"]
    beats: list[AutomedSegAFetaBeat]


class AutomedSegAHeartChannels(TypedDict):
    slice: tuple[float, float]
    format: tuple[float, float]
    reference: tuple[float, float]


class AutomedSegAHeartBeat(ExpansionBeat):
    channels: AutomedSegAHeartChannels
    scene: Literal["input", "stack", "labels", "schema", "reference", "limits"]


class AutomedSegAHeartPlan(ExpansionPlan):
    recipe: Literal["automed-full-heart-seg-v1"]
    beats: list[AutomedSegAHeartBeat]


AutomedSegBHepaticvesselChannels = TypedDict(
    "AutomedSegBHepaticvesselChannels",
    {
        "view": tuple[float, float],
        "class": tuple[float, float],
        "reference": tuple[float, float],
    },
)


class AutomedSegBHepaticvesselBeat(ExpansionBeat):
    channels: AutomedSegBHepaticvesselChannels
    scene: Literal["inputs", "mapping", "output", "reference", "scorer", "limits"]


class AutomedSegBHepaticvesselPlan(ExpansionPlan):
    recipe: Literal["automed-full-hepaticvessel-v1"]
    beats: list[AutomedSegBHepaticvesselBeat]


AutomedSegBKidneyChannels = TypedDict(
    "AutomedSegBKidneyChannels",
    {
        "view": tuple[float, float],
        "class": tuple[float, float],
        "reference": tuple[float, float],
    },
)


class AutomedSegBKidneyBeat(ExpansionBeat):
    channels: AutomedSegBKidneyChannels
    scene: Literal["inputs", "mapping", "output", "reference", "scorer", "limits"]


class AutomedSegBKidneyPlan(ExpansionPlan):
    recipe: Literal["automed-full-kidney-v1"]
    beats: list[AutomedSegBKidneyBeat]


AutomedSegBLiverChannels = TypedDict(
    "AutomedSegBLiverChannels",
    {
        "view": tuple[float, float],
        "class": tuple[float, float],
        "reference": tuple[float, float],
    },
)


class AutomedSegBLiverBeat(ExpansionBeat):
    channels: AutomedSegBLiverChannels
    scene: Literal["inputs", "mapping", "output", "reference", "scorer", "limits"]


class AutomedSegBLiverPlan(ExpansionPlan):
    recipe: Literal["automed-full-liver-v1"]
    beats: list[AutomedSegBLiverBeat]


AutomedSegBPancreasOarChannels = TypedDict(
    "AutomedSegBPancreasOarChannels",
    {
        "view": tuple[float, float],
        "class": tuple[float, float],
        "reference": tuple[float, float],
    },
)


class AutomedSegBPancreasOarBeat(ExpansionBeat):
    channels: AutomedSegBPancreasOarChannels
    scene: Literal["inputs", "mapping", "output", "reference", "scorer", "limits"]


class AutomedSegBPancreasOarPlan(ExpansionPlan):
    recipe: Literal["automed-full-pancreas-oar-v1"]
    beats: list[AutomedSegBPancreasOarBeat]


class AutomedSegCPancreasChannels(TypedDict):
    slice: tuple[float, float]
    helper: tuple[float, float]
    output: tuple[float, float]


class AutomedSegCPancreasBeat(ExpansionBeat):
    channels: AutomedSegCPancreasChannels
    scene: Literal["input", "channels", "mapping", "output", "helper", "limits"]


class AutomedSegCPancreasPlan(ExpansionPlan):
    recipe: Literal["automed-full-pancreas-seg-v1"]
    beats: list[AutomedSegCPancreasBeat]


class AutomedSegCPantherT1Channels(TypedDict):
    slice: tuple[float, float]
    helper: tuple[float, float]
    output: tuple[float, float]


class AutomedSegCPantherT1Beat(ExpansionBeat):
    channels: AutomedSegCPantherT1Channels
    scene: Literal["input", "channels", "mapping", "output", "helper", "limits"]


class AutomedSegCPantherT1Plan(ExpansionPlan):
    recipe: Literal["automed-full-panther-t1-seg-v1"]
    beats: list[AutomedSegCPantherT1Beat]


class AutomedSegCPantherT2Channels(TypedDict):
    slice: tuple[float, float]
    helper: tuple[float, float]
    output: tuple[float, float]


class AutomedSegCPantherT2Beat(ExpansionBeat):
    channels: AutomedSegCPantherT2Channels
    scene: Literal["input", "channels", "mapping", "output", "helper", "limits"]


class AutomedSegCPantherT2Plan(ExpansionPlan):
    recipe: Literal["automed-full-panther-t2-seg-v1"]
    beats: list[AutomedSegCPantherT2Beat]


class AutomedSegCProstateChannels(TypedDict):
    slice: tuple[float, float]
    helper: tuple[float, float]
    output: tuple[float, float]


class AutomedSegCProstateBeat(ExpansionBeat):
    channels: AutomedSegCProstateChannels
    scene: Literal["input", "channels", "mapping", "output", "helper", "limits"]


class AutomedSegCProstatePlan(ExpansionPlan):
    recipe: Literal["automed-full-prostate-seg-v1"]
    beats: list[AutomedSegCProstateBeat]


class AutomedSegDSpleenChannels(TypedDict):
    view: tuple[float, float]
    label: tuple[float, float]
    reference: tuple[float, float]


class AutomedSegDSpleenBeat(ExpansionBeat):
    channels: AutomedSegDSpleenChannels
    scene: Literal["inputs", "mapping", "output", "reference", "scorer", "limits"]


class AutomedSegDSpleenPlan(ExpansionPlan):
    recipe: Literal["automed-full-spleen-v1"]
    beats: list[AutomedSegDSpleenBeat]


class AutomedSegDTsgMultiorganChannels(TypedDict):
    view: tuple[float, float]
    label: tuple[float, float]
    reference: tuple[float, float]


class AutomedSegDTsgMultiorganBeat(ExpansionBeat):
    channels: AutomedSegDTsgMultiorganChannels
    scene: Literal["inputs", "mapping", "output", "reference", "scorer", "limits"]


class AutomedSegDTsgMultiorganPlan(ExpansionPlan):
    recipe: Literal["automed-full-tsg-multiorgan-v1"]
    beats: list[AutomedSegDTsgMultiorganBeat]


class InterpretationAHealthagentbenchChannels(TypedDict):
    cursor: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class InterpretationAHealthagentbenchBeat(ExpansionBeat):
    channels: InterpretationAHealthagentbenchChannels
    scene: Literal["input", "inspect", "operation", "schema", "reference", "limits"]


class InterpretationAHealthagentbenchPlan(ExpansionPlan):
    recipe: Literal["healthagentbench-ct-findings-v1"]
    beats: list[InterpretationAHealthagentbenchBeat]


class InterpretationARadagentChannels(TypedDict):
    cursor: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class InterpretationARadagentBeat(ExpansionBeat):
    channels: InterpretationARadagentChannels
    scene: Literal["input", "inspect", "operation", "schema", "reference", "limits"]


class InterpretationARadagentPlan(ExpansionPlan):
    recipe: Literal["radagent-report-v1"]
    beats: list[InterpretationARadagentBeat]


class InterpretationAHealthagentbenchTumorTilesChannels(TypedDict):
    cursor: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class InterpretationAHealthagentbenchTumorTilesBeat(ExpansionBeat):
    channels: InterpretationAHealthagentbenchTumorTilesChannels
    scene: Literal["input", "inspect", "operation", "schema", "reference", "limits"]


class InterpretationAHealthagentbenchTumorTilesPlan(ExpansionPlan):
    recipe: Literal["healthagentbench-tumor-tiles-v1"]
    beats: list[InterpretationAHealthagentbenchTumorTilesBeat]


class InterpretationAHealthagentbenchCxrCorrectionChannels(TypedDict):
    cursor: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class InterpretationAHealthagentbenchCxrCorrectionBeat(ExpansionBeat):
    channels: InterpretationAHealthagentbenchCxrCorrectionChannels
    scene: Literal["input", "inspect", "operation", "schema", "reference", "limits"]


class InterpretationAHealthagentbenchCxrCorrectionPlan(ExpansionPlan):
    recipe: Literal["healthagentbench-cxr-correction-v1"]
    beats: list[InterpretationAHealthagentbenchCxrCorrectionBeat]


class InterpretationBBcerMediumBrainGradeClassifyChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class InterpretationBBcerMediumBrainGradeClassifyBeat(ExpansionBeat):
    channels: InterpretationBBcerMediumBrainGradeClassifyChannels
    scene: Literal["input", "route", "operation", "output", "limits"]


class InterpretationBBcerMediumBrainGradeClassifyPlan(ExpansionPlan):
    recipe: Literal["bcer-brain-grade-v1"]
    beats: list[InterpretationBBcerMediumBrainGradeClassifyBeat]


class InterpretationBBcerLongCardiacFullChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class InterpretationBBcerLongCardiacFullBeat(ExpansionBeat):
    channels: InterpretationBBcerLongCardiacFullChannels
    scene: Literal["input", "route", "operation", "output", "limits"]


class InterpretationBBcerLongCardiacFullPlan(ExpansionPlan):
    recipe: Literal["bcer-cardiac-full-v1"]
    beats: list[InterpretationBBcerLongCardiacFullBeat]


class InterpretationBBcerLongBrainFullChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class InterpretationBBcerLongBrainFullBeat(ExpansionBeat):
    channels: InterpretationBBcerLongBrainFullChannels
    scene: Literal["input", "route", "operation", "output", "limits"]


class InterpretationBBcerLongBrainFullPlan(ExpansionPlan):
    recipe: Literal["bcer-brain-full-v1"]
    beats: list[InterpretationBBcerLongBrainFullBeat]


class ImagingSenseChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class ImagingSenseBeat(ExpansionBeat):
    channels: ImagingSenseChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class ImagingSensePlan(ExpansionPlan):
    recipe: Literal["imaging101-sense-v1"]
    beats: list[ImagingSenseBeat]


class ImagingPnpAdmmChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class ImagingPnpAdmmBeat(ExpansionBeat):
    channels: ImagingPnpAdmmChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class ImagingPnpAdmmPlan(ExpansionPlan):
    recipe: Literal["imaging101-pnp-admm-v1"]
    beats: list[ImagingPnpAdmmBeat]


class ImagingNoncartesianChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class ImagingNoncartesianBeat(ExpansionBeat):
    channels: ImagingNoncartesianChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class ImagingNoncartesianPlan(ExpansionPlan):
    recipe: Literal["imaging101-noncartesian-v1"]
    beats: list[ImagingNoncartesianBeat]


class ImagingWaveletChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class ImagingWaveletBeat(ExpansionBeat):
    channels: ImagingWaveletChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class ImagingWaveletPlan(ExpansionPlan):
    recipe: Literal["imaging101-wavelet-v1"]
    beats: list[ImagingWaveletBeat]


class ImagingGrappaChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class ImagingGrappaBeat(ExpansionBeat):
    channels: ImagingGrappaChannels
    scene: Literal["input", "helper", "operation", "output", "limits"]


class ImagingGrappaPlan(ExpansionPlan):
    recipe: Literal["imaging-grappa-v1"]
    beats: list[ImagingGrappaBeat]


class ImagingDynamicMriChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class ImagingDynamicMriBeat(ExpansionBeat):
    channels: ImagingDynamicMriChannels
    scene: Literal["input", "helper", "operation", "output", "limits"]


class ImagingDynamicMriPlan(ExpansionPlan):
    recipe: Literal["imaging-dynamic-mri-v1"]
    beats: list[ImagingDynamicMriBeat]


class ImagingEitChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class ImagingEitBeat(ExpansionBeat):
    channels: ImagingEitChannels
    scene: Literal["input", "helper", "operation", "output", "limits"]


class ImagingEitPlan(ExpansionPlan):
    recipe: Literal["imaging-eit-v1"]
    beats: list[ImagingEitBeat]


class ImagingPoissonChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class ImagingPoissonBeat(ExpansionBeat):
    channels: ImagingPoissonChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class ImagingPoissonPlan(ExpansionPlan):
    recipe: Literal["imaging101-poisson-v1"]
    beats: list[ImagingPoissonBeat]


class BcerGrappaChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class BcerGrappaBeat(ExpansionBeat):
    channels: BcerGrappaChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class BcerGrappaPlan(ExpansionPlan):
    recipe: Literal["bcer-grappa-v1"]
    beats: list[BcerGrappaBeat]


class BcerSuperresChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class BcerSuperresBeat(ExpansionBeat):
    channels: BcerSuperresChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class BcerSuperresPlan(ExpansionPlan):
    recipe: Literal["bcer-superres-v1"]
    beats: list[BcerSuperresBeat]


class BcerDenoiseChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class BcerDenoiseBeat(ExpansionBeat):
    channels: BcerDenoiseChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class BcerDenoisePlan(ExpansionPlan):
    recipe: Literal["bcer-denoise-v1"]
    beats: list[BcerDenoiseBeat]


class AutomedVqaRadChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AutomedVqaRadBeat(ExpansionBeat):
    channels: AutomedVqaRadChannels
    scene: Literal["input", "helper", "operation", "output", "limits"]


class AutomedVqaRadPlan(ExpansionPlan):
    recipe: Literal["automed-vqa-rad-v1"]
    beats: list[AutomedVqaRadBeat]


class AutomedOmniChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AutomedOmniBeat(ExpansionBeat):
    channels: AutomedOmniChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class AutomedOmniPlan(ExpansionPlan):
    recipe: Literal["automed-omni-v1"]
    beats: list[AutomedOmniBeat]


class AutomedKvasirChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AutomedKvasirBeat(ExpansionBeat):
    channels: AutomedKvasirChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class AutomedKvasirPlan(ExpansionPlan):
    recipe: Literal["automed-kvasir-v1"]
    beats: list[AutomedKvasirBeat]


class AutomedSlakeChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AutomedSlakeBeat(ExpansionBeat):
    channels: AutomedSlakeChannels
    scene: Literal["input", "helper", "operation", "output", "limits"]


class AutomedSlakePlan(ExpansionPlan):
    recipe: Literal["automed-slake-v1"]
    beats: list[AutomedSlakeBeat]


class AutomedPathvqaChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AutomedPathvqaBeat(ExpansionBeat):
    channels: AutomedPathvqaChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class AutomedPathvqaPlan(ExpansionPlan):
    recipe: Literal["automed-pathvqa-v1"]
    beats: list[AutomedPathvqaBeat]


class AutomedMedxpertChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AutomedMedxpertBeat(ExpansionBeat):
    channels: AutomedMedxpertChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class AutomedMedxpertPlan(ExpansionPlan):
    recipe: Literal["automed-medxpert-mm-v1"]
    beats: list[AutomedMedxpertBeat]


class AutomedMedframeqaChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AutomedMedframeqaBeat(ExpansionBeat):
    channels: AutomedMedframeqaChannels
    scene: Literal["input", "helper", "operation", "output", "limits"]


class AutomedMedframeqaPlan(ExpansionPlan):
    recipe: Literal["automed-medframeqa-v1"]
    beats: list[AutomedMedframeqaBeat]


class AutomedPathology100Channels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AutomedPathology100Beat(ExpansionBeat):
    channels: AutomedPathology100Channels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class AutomedPathology100Plan(ExpansionPlan):
    recipe: Literal["automed-pathology-caption-100-v1"]
    beats: list[AutomedPathology100Beat]


class AutomedPathology500Channels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AutomedPathology500Beat(ExpansionBeat):
    channels: AutomedPathology500Channels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class AutomedPathology500Plan(ExpansionPlan):
    recipe: Literal["automed-pathology-caption-500-v1"]
    beats: list[AutomedPathology500Beat]


class AutomedMimicReportChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AutomedMimicReportBeat(ExpansionBeat):
    channels: AutomedMimicReportChannels
    scene: Literal["input", "helper", "operation", "output", "limits"]


class AutomedMimicReportPlan(ExpansionPlan):
    recipe: Literal["automed-mimic-report-v1"]
    beats: list[AutomedMimicReportBeat]


class AutomedIuReportChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AutomedIuReportBeat(ExpansionBeat):
    channels: AutomedIuReportChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class AutomedIuReportPlan(ExpansionPlan):
    recipe: Literal["automed-iu-xray-report-v1"]
    beats: list[AutomedIuReportBeat]


class AutomedChexpertReportChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AutomedChexpertReportBeat(ExpansionBeat):
    channels: AutomedChexpertReportChannels
    scene: Literal["input", "helper", "operation", "output", "limits"]


class AutomedChexpertReportPlan(ExpansionPlan):
    recipe: Literal["automed-chexpert-report-v1"]
    beats: list[AutomedChexpertReportBeat]


class AutomedSkinLesionChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AutomedSkinLesionBeat(ExpansionBeat):
    channels: AutomedSkinLesionChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class AutomedSkinLesionPlan(ExpansionPlan):
    recipe: Literal["automed-skin-lesion-cls-v1"]
    beats: list[AutomedSkinLesionBeat]


class AutomedPcamClsChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AutomedPcamClsBeat(ExpansionBeat):
    channels: AutomedPcamClsChannels
    scene: Literal["input", "helper", "operation", "output", "limits"]


class AutomedPcamClsPlan(ExpansionPlan):
    recipe: Literal["automed-pcam-cls-v1"]
    beats: list[AutomedPcamClsBeat]


class AutomedCrcClsChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AutomedCrcClsBeat(ExpansionBeat):
    channels: AutomedCrcClsChannels
    scene: Literal["input", "helper", "operation", "output", "limits"]


class AutomedCrcClsPlan(ExpansionPlan):
    recipe: Literal["automed-crc-cls-v1"]
    beats: list[AutomedCrcClsBeat]


class AutomedPneumoniaChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AutomedPneumoniaBeat(ExpansionBeat):
    channels: AutomedPneumoniaChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class AutomedPneumoniaPlan(ExpansionPlan):
    recipe: Literal["automed-pneumonia-cls-v1"]
    beats: list[AutomedPneumoniaBeat]


class AutomedBrainClsChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AutomedBrainClsBeat(ExpansionBeat):
    channels: AutomedBrainClsChannels
    scene: Literal["input", "helper", "operation", "output", "limits"]


class AutomedBrainClsPlan(ExpansionPlan):
    recipe: Literal["automed-brain-cls-v1"]
    beats: list[AutomedBrainClsBeat]


class RexLdctIqaChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class RexLdctIqaBeat(ExpansionBeat):
    channels: RexLdctIqaChannels
    scene: Literal["input", "helper", "operation", "output", "limits"]


class RexLdctIqaPlan(ExpansionPlan):
    recipe: Literal["rex-ldct-iqa-v1"]
    beats: list[RexLdctIqaBeat]


class RadagentVqaChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class RadagentVqaBeat(ExpansionBeat):
    channels: RadagentVqaChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class RadagentVqaPlan(ExpansionPlan):
    recipe: Literal["radagent-vqa-v1"]
    beats: list[RadagentVqaBeat]


class AbraBiradsChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AbraBiradsBeat(ExpansionBeat):
    channels: AbraBiradsChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class AbraBiradsPlan(ExpansionPlan):
    recipe: Literal["abra-birads-v1"]
    beats: list[AbraBiradsBeat]


class AbraVisionProbeChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AbraVisionProbeBeat(ExpansionBeat):
    channels: AbraVisionProbeChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class AbraVisionProbePlan(ExpansionPlan):
    recipe: Literal["abra-vision-probe-v1"]
    beats: list[AbraVisionProbeBeat]


class AbraMetadataQaChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AbraMetadataQaBeat(ExpansionBeat):
    channels: AbraMetadataQaChannels
    scene: Literal["input", "reference", "operation", "output", "limits"]


class AbraMetadataQaPlan(ExpansionPlan):
    recipe: Literal["abra-metadata-qa-v1"]
    beats: list[AbraMetadataQaBeat]


class AbraViewerControlChannels(TypedDict):
    progress: tuple[float, float]
    detail: tuple[float, float]
    reference: tuple[float, float]


class AbraViewerControlBeat(ExpansionBeat):
    channels: AbraViewerControlChannels
    scene: Literal["input", "route", "operation", "output", "limits"]


class AbraViewerControlPlan(ExpansionPlan):
    recipe: Literal["abra-viewer-control-v1"]
    beats: list[AbraViewerControlBeat]


class CardiacMaterialChannels(TypedDict):
    phase: tuple[float, float]
    helper: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class CardiacMaterialBeat(ExpansionBeat):
    channels: CardiacMaterialChannels
    scene: Literal[
        "inputs", "initial", "tracking", "tetra", "strain", "comparison", "controls", "limits"
    ]


class CardiacMaterialPlan(ExpansionPlan):
    recipe: Literal["cardiac-material-v1"]
    beats: list[CardiacMaterialBeat]


class CardiacAnchorChannels(TypedDict):
    phase: tuple[float, float]
    helper: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class CardiacAnchorBeat(ExpansionBeat):
    channels: CardiacAnchorChannels
    scene: Literal[
        "inputs",
        "anchors",
        "tracking-one",
        "tracking-two",
        "surface",
        "reference",
        "comparison",
        "limits",
    ]


class CardiacAnchorPlan(ExpansionPlan):
    recipe: Literal["cardiac-anchor-v1"]
    beats: list[CardiacAnchorBeat]


class ClinicalCavityChannels(TypedDict):
    phase: tuple[float, float]
    helper: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class ClinicalCavityBeat(ExpansionBeat):
    channels: ClinicalCavityChannels
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


class ClinicalCavityPlan(ExpansionPlan):
    recipe: Literal["clinical-cavity-v1"]
    beats: list[ClinicalCavityBeat]


class RespiratoryChannels(TypedDict):
    depth: tuple[float, float]
    output: tuple[float, float]
    reference: tuple[float, float]


class RespiratoryBeat(ExpansionBeat):
    channels: RespiratoryChannels
    scene: Literal[
        "inputs", "frame", "depth", "output", "reference", "judgment", "conditions", "limits"
    ]


class RespiratoryPlan(ExpansionPlan):
    recipe: Literal["respiratory-v1"]
    beats: list[RespiratoryBeat]


class CurationChannels(TypedDict):
    reference: tuple[float, float]
    focus: tuple[float, float]


class CurationBeat(ExpansionBeat):
    channels: CurationChannels
    scene: Literal[
        "pair", "preservation", "overlap", "calibration", "reserve", "ambiguity", "admission"
    ]


class CurationPlan(ExpansionPlan):
    recipe: Literal["anatomy-curation-v1"]
    beats: list[CurationBeat]


class MaskScreenChannels(TypedDict):
    measure: tuple[float, float]
    prediction: tuple[float, float]
    reference: tuple[float, float]
    focus: tuple[float, float]


class MaskScreenBeat(ExpansionBeat):
    channels: MaskScreenChannels
    scene: Literal["context", "ribs-32", "ribs-74", "organs-32", "admission"]


class MaskScreenPlan(ExpansionPlan):
    recipe: Literal["mask-screen-v1"]
    beats: list[MaskScreenBeat]


class MixedTissueChannels(TypedDict):
    conditions: list[float]
    plane: list[float]
    overlay: list[float]
    reference: list[float]
    witness: list[float]


class MixedTissueBeat(ExpansionBeat):
    channels: MixedTissueChannels


class MixedTissuePlan(ExpansionPlan):
    recipe: Literal["mixed-tissue-v1"]
    beats: list[MixedTissueBeat]


StoryPlan = (
    RouteStoryPlan
    | TopologyPlan
    | CorrespondencePlan
    | MaterialPlan
    | LongitudinalPlan
    | MultiscalePlan
    | InversePlan
    | EditPlan
    | AnatomyPlan
    | IdentityPlan
    | PrototypeIdentityPlan
    | LongitudinalCtRevisedPlan
    | LongitudinalCtOriginalPlan
    | LongitudinalMriPlan
    | TigerContextPlan
    | HubmapInventoryPlan
    | TopbrainScreenPlan
    | AirwayRepairPlan
    | VesselSourcePlan
    | ResectPilotPlan
    | ResectPlan
    | RegistrationAnalysisPlan
    | Imaging101EhtOriginalPlan
    | Imaging101EhtFeaturesDynamicPlan
    | Imaging101EhtDynamicPlan
    | Imaging101EhtUqPlan
    | Imaging101DtiPlan
    | Imaging101DeflectometryPlan
    | Imaging101FanBeamPlan
    | Imaging101DualEnergyPlan
    | Imaging101PtychographyPlan
    | Imaging101NlosPlan
    | Imaging101CarsPlan
    | RexTopcowPlan
    | AutomedMultiorganPlan
    | BcerWorkflowPlan
    | AbraAnnotationPlan
    | CtContextPlan
    | HistorySourcingPlan
    | MriImporterPlan
    | LocalizedCtPlan
    | AneurysmPlan
    | SegmentationCalibrationPlan
    | DentalV3Plan
    | DentalV2Plan
    | DentalOriginalPlan
    | CtOrganPlan
    | NamedLandmarksPlan
    | CardiacContourPlan
    | CardiacRealEchoPlan
    | MaskMechanicsPlan
    | ReportReadingPlan
    | AutomedKidneyPlan
    | BcerBrainPlan
    | BcerProstatePlan
    | AbraLongitudinalPlan
    | RexDentexPlan
    | RexIslesPlan
    | RexCellsegPlan
    | RexPantherTask1Plan
    | RexPantherTask2Plan
    | RexPumaTrack1Task1Plan
    | RexPumaTrack1Task2Plan
    | RexPumaTrack2Task2Plan
    | RexSegAPlan
    | RexTopbrainCtPlan
    | RexTopbrainMrPlan
    | RexTopcowMrSegPlan
    | RexTopcowCtBoxPlan
    | RexTopcowMrBoxPlan
    | RexTopcowCtEdgesPlan
    | RexTopcowMrEdgesPlan
    | AutomedDetectionBccdPlan
    | AutomedDetectionDentexPlan
    | AutomedDetectionGrazpedwriPlan
    | AutomedDetectionVindrCxrPlan
    | AutomedSegAAeropathPlan
    | AutomedSegAColonPlan
    | AutomedSegAFetaPlan
    | AutomedSegAHeartPlan
    | AutomedSegBHepaticvesselPlan
    | AutomedSegBKidneyPlan
    | AutomedSegBLiverPlan
    | AutomedSegBPancreasOarPlan
    | AutomedSegCPancreasPlan
    | AutomedSegCPantherT1Plan
    | AutomedSegCPantherT2Plan
    | AutomedSegCProstatePlan
    | AutomedSegDSpleenPlan
    | AutomedSegDTsgMultiorganPlan
    | InterpretationAHealthagentbenchPlan
    | InterpretationARadagentPlan
    | InterpretationAHealthagentbenchTumorTilesPlan
    | InterpretationAHealthagentbenchCxrCorrectionPlan
    | InterpretationBBcerMediumBrainGradeClassifyPlan
    | InterpretationBBcerLongCardiacFullPlan
    | InterpretationBBcerLongBrainFullPlan
    | ImagingSensePlan
    | ImagingPnpAdmmPlan
    | ImagingNoncartesianPlan
    | ImagingWaveletPlan
    | ImagingGrappaPlan
    | ImagingDynamicMriPlan
    | ImagingEitPlan
    | ImagingPoissonPlan
    | BcerGrappaPlan
    | BcerSuperresPlan
    | BcerDenoisePlan
    | AutomedVqaRadPlan
    | AutomedOmniPlan
    | AutomedKvasirPlan
    | AutomedSlakePlan
    | AutomedPathvqaPlan
    | AutomedMedxpertPlan
    | AutomedMedframeqaPlan
    | AutomedPathology500Plan
    | AutomedPathology100Plan
    | AutomedMimicReportPlan
    | AutomedIuReportPlan
    | AutomedChexpertReportPlan
    | AutomedSkinLesionPlan
    | AutomedPcamClsPlan
    | AutomedCrcClsPlan
    | AutomedPneumoniaPlan
    | AutomedBrainClsPlan
    | RexLdctIqaPlan
    | RadagentVqaPlan
    | AbraBiradsPlan
    | AbraVisionProbePlan
    | AbraMetadataQaPlan
    | AbraViewerControlPlan
    | CardiacMaterialPlan
    | CardiacAnchorPlan
    | ClinicalCavityPlan
    | RespiratoryPlan
    | CurationPlan
    | MaskScreenPlan
    | MixedTissuePlan
)


class Illustration(TypedDict):
    story_id: NotRequired[str]
    kind: str
    input: str
    output: str
    caption: str
    subject: NotRequired[str]
    target: NotRequired[str]
    scene_variant: NotRequired[str]
    mask_mode: NotRequired[str]
    input_form: NotRequired[str]
    initial_candidate: NotRequired[bool]
    labels: NotRequired[list[str]]


class Study(TypedDict):
    id: str
    title: str
    scope: str
    tasks: list[str]
    protocol: str
    record_path: str


class Condition(TypedDict):
    name: str
    helper: str
    remaining: str


class Visuals(TypedDict):
    input: str
    helpers: str
    answer: str


class LocalizedBrief(TypedDict):
    title: str
    goal: str
    value: str
    raw: str
    helpers: str
    output: str
    challenge: str
    spec: str
    tools: str
    score: str
    reference: str
    families: str
    gap: str
    case_note: str
    variants: list[Condition]
    sources: list[tuple[str, str]]
    visuals: Visuals
    html: dict[BriefField, str]
    stages: list[str]
    missing_media: list[str]


class TaskEntry(TypedDict):
    id: str
    title: str
    repo: str
    repository_id: NotRequired[str]
    category: str
    role: NotRequired[str]
    agent_work: str
    modalities: list[str]
    owner_group: NotRequired[str]
    operations: NotRequired[list[str]]
    task_family: NotRequired[str]
    nav_group: NotRequired[str]
    nav_label: NotRequired[str]
    proposed: NotRequired[bool]
    goal: str
    value: str
    raw: str
    helpers: str
    output: str
    challenge: str
    spec: str
    tools: str
    score: str
    reference: str
    families: str
    gap: str
    case_note: str
    variants: list[Condition]
    sources: list[tuple[str, str]]
    visuals: Visuals
    html: NotRequired[dict[BriefField, str]]
    illustration: NotRequired[Illustration]
    missing_media: NotRequired[list[str]]
    example_case_id: NotRequired[str]
    studies: NotRequired[list[Study]]
    stages: NotRequired[list[str]]
    locales: NotRequired[dict[str, LocalizedBrief]]


class CaseFact(TypedDict):
    value: str | int | float
    label: str


class CaseContext(TypedDict):
    label: NotRequired[str]
    facts: NotRequired[list[CaseFact]]
    source: NotRequired[str]


class InventoryItem(TypedDict):
    id: str
    title: str
    brief_id: NotRequired[str]
    kind: str
    definition: str
    condition: str
    condition_index: NotRequired[int]
    family: NotRequired[str]
    url: str
    brief_scope_note: NotRequired[str]
    case_context: NotRequired[CaseContext]


class RepositoryInventory(TypedDict):
    id: str
    items: list[InventoryItem]
    coverage: str
    observed_on: str
    commit: str


class LocalSource(TypedDict, total=False):
    sha256: str
    bytes: int
    base64: str
    content: str
    unavailable: str


class SourceDigest(TypedDict):
    path: str
    sha256: str


class SnapshotPanel(TypedDict):
    role: Literal["input", "reference", "metadata"]
    caption: str
    image_url: NotRequired[str]
    text: NotRequired[str]
    path: NotRequired[str]


class DatasetSnapshot(TypedDict):
    sample_id: str
    status: Literal["paired", "input-only", "reference-only", "unavailable"]
    summary: str
    panels: list[SnapshotPanel]
    reference_note: str
    sources: list[SourceDigest]


class SampleReceipt(SourceDigest):
    pointer: NotRequired[str]


class SampleSet(TypedDict):
    label: str
    role: str
    sample_ids: list[str]
    note: str
    receipt: SampleReceipt


class DatasetExperiment(TypedDict):
    id: str
    title: str


class SourceLink(TypedDict):
    path: str
    label: str


class DatasetLocalized(TypedDict):
    title: str
    summary: str
    modality: str
    sample_unit: str
    image_description: str
    annotation_description: str
    reference_note: str
    version_note: str
    terms_note: str
    access_note: str
    documentation_gaps: list[str]
    sample_set_notes: list[str]
    snapshot_summary: str
    snapshot_reference_note: str
    snapshot_captions: list[str]


class DatasetRecord(TypedDict):
    id: str
    title: str
    modality: str
    summary: str
    image_description: str
    annotation_description: str
    sample_unit: str
    reference_note: str
    sample_sets: list[SampleSet]
    task_ids: list[str]
    experiments: list[DatasetExperiment]
    links: NotRequired[list[SourceLink]]
    version_note: str
    terms_note: str
    access_note: NotRequired[str]
    documentation_gaps: NotRequired[list[str]]
    record_path: str
    locales: NotRequired[dict[str, DatasetLocalized]]


class CategoryInfo(TypedDict):
    title: str
    description: str


class Taxonomy(TypedDict, total=False):
    categories: dict[str, CategoryInfo]
    roles: dict[str, str]
    agent_work: dict[str, str]
    modalities: dict[str, str]


class TaskFamily(TypedDict):
    title: str
    selector: str


class PresentationContext(TypedDict, total=False):
    home_url: str
    home_label: str
    story_urls: dict[str, str]


class DatasetCoverage(TypedDict, total=False):
    experiments: int
    scope: str


class DatasetCollection(TypedDict):
    records: list[DatasetRecord]
    previews: NotRequired[dict[str, DatasetSnapshot]]
    coverage: DatasetCoverage


class Inventory(TypedDict, total=False):
    repositories: list[RepositoryInventory]


class ExplorerData(TypedDict):
    explanation_stories: NotRequired[dict[str, StoryPlan]]
    schema_version: Literal[1]
    title: NotRequired[str]
    entries: list[TaskEntry]
    inventory: Inventory
    taxonomy: Taxonomy
    task_families: NotRequired[dict[str, TaskFamily]]
    repository_contexts: NotRequired[dict[str, str]]
    local_sources: dict[str, LocalSource]
    presentation_context: NotRequired[PresentationContext]
    datasets: NotRequired[DatasetCollection]


class VocabularyTerm(TypedDict):
    label: str
    definition: str


class VocabularyAxis(TypedDict):
    values: dict[str, VocabularyTerm]


class OverviewVocabulary(TypedDict):
    axes: dict[str, VocabularyAxis]
    context_badges: dict[str, VocabularyTerm]
    display_rules: dict[str, str | list[str]]


class ReviewFlag(TypedDict):
    experiment_id: str
    assessment: str
    reason: str


class RecordCurrent(TypedDict, total=False):
    review_flags: list[ReviewFlag]


class PortableLink(TypedDict):
    label: str
    url: NotRequired[str | None]


class ResearchRecord(TypedDict):
    id: str
    kind: str
    current: RecordCurrent
    portable_links: NotRequired[list[PortableLink]]
    experiment_ids: NotRequired[list[str]]


class OverviewData(TypedDict):
    schema_version: Literal[1]
    records: list[ResearchRecord]
    vocabulary: OverviewVocabulary
    task_explorer_url: NotRequired[str | None]
    local_media: bool


ALIASES = {
    name: globals()[name]
    for name in ("VisualRole", "TaskTab", "BrowseView", "ResearchLane", "BriefField", "StoryPlan")
}
MODELS = {name: model for name, model in list(globals().items()) if is_typeddict(model)}
EXTENSIBLE = {"ResearchRecord", "RecordCurrent", "DatasetRecord"}
GENERATED = Path("presentation/frontend/contracts.generated.ts")


def _fields(model: object) -> list[tuple[str, object, bool]]:
    fields = []
    for name, kind in get_type_hints(model, include_extras=True).items():
        optional = get_origin(kind) is NotRequired or not getattr(model, "__total__", True)
        fields.append(
            (name, get_args(kind)[0] if get_origin(kind) is NotRequired else kind, optional)
        )
    return fields


def _validate(value: object, kind: object, path: str) -> None:
    origin, args = get_origin(kind), get_args(kind)
    if is_typeddict(kind):
        if not isinstance(value, dict):
            raise MedicalError(f"{path}: expected object")
        for name, field_type, optional in _fields(kind):
            if name not in value:
                if optional:
                    continue
                raise MedicalError(f"{path}.{name}: required field is missing")
            _validate(value[name], field_type, path + "." + name)
    elif origin is Literal:
        if not any(type(value) is type(item) and value == item for item in args):
            raise MedicalError(f"{path}: unsupported value {value!r}")
    elif origin is types.UnionType:
        for candidate in args:
            try:
                _validate(value, candidate, path)
                return
            except MedicalError:
                pass
        raise MedicalError(f"{path}: incompatible value type")
    elif origin in (list, tuple):
        if not isinstance(value, (list, tuple)) or (origin is tuple and len(value) != len(args)):
            raise MedicalError(f"{path}: expected {'array' if origin is list else 'fixed tuple'}")
        for index, item in enumerate(value):
            _validate(item, args[0] if origin is list else args[index], f"{path}[{index}]")
    elif origin is dict:
        if not isinstance(value, dict):
            raise MedicalError(f"{path}: expected mapping")
        for key, item in value.items():
            _validate(key, args[0], path + ".<key>")
            _validate(item, args[1], path + "." + str(key))
    elif kind is not object and type(value) is not kind:
        raise MedicalError(f"{path}: expected {getattr(kind, '__name__', kind)}")


def validate_payload(data: Document, surface: Literal["explorer", "overview"]) -> Document:
    """Validate the emitted boundary, retaining additional scientific source fields."""
    _validate(data, ExplorerData if surface == "explorer" else OverviewData, surface)
    return data


def _ts(kind: object) -> str:
    origin, args = get_origin(kind), get_args(kind)
    if is_typeddict(kind):
        return cast(type, kind).__name__
    if origin is Literal:
        return " | ".join(json.dumps(item) for item in args)
    if origin is types.UnionType:
        return " | ".join(dict.fromkeys(_ts(item) for item in args))
    if origin is list:
        return f"Array<{_ts(args[0])}>"
    if origin is tuple:
        return "[" + ", ".join(_ts(item) for item in args) + "]"
    if origin is dict:
        key = _ts(args[0])
        # Authored HTML fields may be absent and fall back to escaped text.
        mapping = f"Record<{key}, {_ts(args[1])}>"
        return f"Partial<{mapping}>" if args[0] == BriefField else mapping
    return {
        str: "string",
        int: "number",
        float: "number",
        bool: "boolean",
        type(None): "null",
        object: "unknown",
    }[cast(type, kind)]


def typescript() -> str:
    lines = ["// Generated by python -m tb3_medical.presentation_contracts. Do not edit."]
    for name, kind in ALIASES.items():
        lines.append(f"export type {name} = {_ts(kind)};")
    for name, model in MODELS.items():
        lines.append(f"export interface {name} {{")
        for field, kind, optional in _fields(model):
            lines.append(f"  {field}{'?' if optional else ''}: {_ts(kind)};")
        if name in EXTENSIBLE:
            lines.append("  [key: string]: unknown;")
        lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = Path.cwd() / GENERATED
    expected = typescript()
    if args.check:
        if not target.is_file() or target.read_text() != expected:
            print("Frontend types are stale; run python -m tb3_medical.presentation_contracts")
            return 1
        print("Python and TypeScript presentation contracts match")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
