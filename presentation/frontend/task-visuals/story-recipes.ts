import type { StoryPlan } from '../types';
import { createRoutePrefab } from './route-prefab';
import {
  createTopologyPrefab,
  createCorrespondencePrefab,
  createMaterialPrefab,
  createAnatomyPrefab,
  createIdentityPrefab,
  createPrototypeIdentityPrefab,
  createMaskScreenPrefab,
  createCurationPrefab,
  createRespiratoryPrefab,
  createAirwayRepairPrefab,
} from './operation-prefabs';
export function isPlanarStory(plan: StoryPlan): boolean {
  return [
    'multiscale-v1',
    'local-edit-v1',
    'longitudinal-v1',
    'inverse-v1',
    'mixed-tissue-v1',
    'registration-analysis-v1',
    'vessel-source-v1',
    'resect-pilot-v1',
    'resect-correspondence-v1',
  ].includes(plan.recipe);
}
export function hasInteractiveProjection(plan: StoryPlan): boolean {
  // Identity names must stay hidden at the start even without a GPU.
  return [
    'anatomy-identity-v1',
    'prototype-identity-v1',
    'mask-screen-v1',
    'anatomy-curation-v1',
    'airway-repair-v1',
    'respiratory-v1',
  ].includes(plan.recipe);
}
export function nativeFactory(plan: StoryPlan) {
  switch (plan.recipe) {
    case 'airway-repair-v1':
      return createAirwayRepairPrefab;
    case 'respiratory-v1':
      return createRespiratoryPrefab;
    case 'anatomy-curation-v1':
      return createCurationPrefab;
    case 'mask-screen-v1':
      return createMaskScreenPrefab;
    case 'route-unfold-v1':
      return createRoutePrefab;
    case 'topology-v1':
      return createTopologyPrefab;
    case 'correspondence-v1':
      return createCorrespondencePrefab;
    case 'shape-material-v1':
      return createMaterialPrefab;
    case 'anatomy-audit-v1':
      return createAnatomyPrefab;
    case 'anatomy-identity-v1':
      return createIdentityPrefab;
    case 'prototype-identity-v1':
      return createPrototypeIdentityPrefab;
    default:
      throw new Error('No native factory for ' + plan.recipe);
  }
}
export function storyPresentation(plan: StoryPlan): {
  heading: string;
  corner: string;
  legend: [string, string, boolean?][];
} {
  switch (plan.recipe) {
    case 'airway-repair-v1':
      return {
        heading: 'Airway repair · one local route and two preservation controls',
        corner: 'AeroPath · RAS+ mm · fixed display poses · actual saved outputs',
        legend: [
          ['#7197a9', 'Input mask'],
          ['#efa933', 'Public anchors / edit region'],
          ['#2bbba0', 'Saved addition / route'],
          ['#e880ad', 'Private core'],
          ['#e880ad', 'Private path', true],
        ],
      };
    case 'vessel-source-v1':
      return {
        heading: 'TopCoW · source curation for local vessel repair',
        corner: 'Four public MRA cases · author study · separate reference reveal',
        legend: [
          ['#f49c30', 'Right Pcom · reference'],
          ['#27c4bc', 'Left Pcom · reference'],
          ['#5773df', 'Other vessels · reference'],
          ['#f5e4a7', 'Graph nodes · circles'],
        ],
      };
    case 'resect-pilot-v1':
      return {
        heading: 'RESECT pilot · two queries and a supplied cue',
        corner: 'One retained attempt · RAS+ mm · explicit reference reveal',
        legend: [
          ['#efa933', 'Initial / MRI query'],
          ['#697be8', 'Prompt cue'],
          ['#41c5b6', 'Returned'],
          ['#e880ad', 'Manual reference', true],
        ],
      };
    case 'resect-correspondence-v1':
      return {
        heading: 'RESECT · MRI to ultrasound point correspondence',
        corner: 'Three-case proposal · NIfTI RAS+ mm · selected reader example',
        legend: [
          ['#efa933', 'MRI query'],
          ['#41c5b6', 'Initial US candidate'],
          ['#e880ad', 'Manual US target · reveal', true],
        ],
      };
    case 'registration-analysis-v1':
      return {
        heading: 'Registration postmortem · retained BR-022 evidence',
        corner: 'Case 1 · dataset-world mm · author diagnostics, not new trials',
        legend: [
          ['#b77128', 'Public query / search box'],
          ['#307f74', 'Submitted point / outcome'],
          ['#a34575', 'Manual target / bound', true],
        ],
      };
    case 'respiratory-v1':
      return {
        heading: 'Respiratory correspondence · real CT and retained output',
        corner: 'Dataset-world mm · display poses only · HU −1000 to 200',
        legend: [
          ['#efa933', 'Public source query'],
          ['#41c5b6', 'Retained target output'],
          ['#e880ad', 'Manual target · reveal'],
          ['#e880ad', '5 mm radius · reveal', true],
        ],
      };
    case 'anatomy-curation-v1':
      return {
        heading: 'Anatomy curation · source evidence before task admission',
        corner: 'VerSe · LPS points · independent scan fitting · no CT',
        legend: [
          ['#8c9589', 'Source name hidden'],
          ['#537d9b', 'Cervical · reveal'],
          ['#b77128', 'Thoracic · reveal'],
          ['#307f74', 'Lumbar · reveal'],
          ['#a34555', 'Selected object'],
        ],
      };
    case 'mask-screen-v1':
      return {
        heading: 'Geometric shortcut screen · retained author study',
        corner: 'Source LPS points · per-scene fit · no CT',
        legend: [
          ['#8c9589', 'Other source objects'],
          ['#307f74', 'Selected object'],
          ['#b77128', 'Centroid ordering guide', true],
          ['#a34555', 'Baseline / source disagreement'],
        ],
      };
    case 'prototype-identity-v1':
      return {
        heading: 'Anonymous object identity · retained BR-011 I2 prototype',
        corner: 'Case 32 · shared LPS frame · sampled surface points',
        legend: [
          ['#8c9589', 'Other supplied objects'],
          ['#307f74', 'Selected object'],
        ],
      };
    case 'mixed-tissue-v1':
      return {
        heading: 'Mixed tissue inside a proposed label · retained BR-017 M02 slices',
        corner: 'Reference-centred teaching crops · LPS mm',
        legend: [
          ['#57cabb', 'Supplied duodenum host'],
          ['#6cafff', 'Remaining pancreas'],
          ['#f5b344', 'Injected region · reveal only'],
          ['#ffffff', 'Witness ring · reveal only'],
        ],
      };
    case 'route-unfold-v1':
      return {
        heading: 'How route-conditioned resampling works — synthetic teaching example',
        corner: 'Synthetic branching volume · teaching frame',
        legend: [
          ['#b77128', 'Connected route'],
          ['#557e93', 'Linked sample'],
        ],
      };
    case 'topology-v1':
      return {
        heading: 'Connected geometry · synthetic operation explanation',
        corner: 'Teaching graph · translucent context · metres',
        legend: [
          ['#aaa99b', 'Graph context'],
          ['#b77128', 'Selected path'],
          ['#307f74', 'Enumerated edge'],
          ['#557e93', 'Cursor on path'],
        ],
      };
    case 'correspondence-v1':
      return {
        heading: 'Rigid coordinate transfer · synthetic operation explanation',
        corner: 'One shared right-handed frame · metres',
        legend: [
          ['#b77128', 'Moving / fit points'],
          ['#307f74', 'Fixed target / held-out check'],
          ['#9b5863', 'Deformed target · scope chapter'],
        ],
      };
    case 'multiscale-v1':
      return {
        heading: 'Coordinates and coverage · abstract planar explanation',
        corner: 'Abstract level-0 canvas · not histology',
        legend:
          plan.operation === 'annotation-coverage'
            ? [
                ['#307f74', 'Synthetic evaluated ROI'],
                ['#a0a099', 'Unannotated / unknown', true],
              ]
            : plan.operation === 'coordinate-navigation'
              ? [
                  ['#b77128', 'Selected local point'],
                  ['#557e93', 'Viewport'],
                ]
              : [
                  ['#b77128', 'Supplied target slot'],
                  ['#557e93', 'Context window'],
                ],
      };
    case 'local-edit-v1':
      return {
        heading: 'Bounded edits · binary-grid teaching fixture',
        corner: 'Grid cells · no source-image support',
        legend: [
          ['#b77128', 'Editable domain'],
          ['#555555', 'Supplied mask / unchanged control'],
        ],
      };
    case 'longitudinal-v1':
      return {
        heading: 'Visit-local candidates · identity and observation',
        corner: 'Unit-square teaching frame',
        legend: [
          ['#307f74', 'Matched identity'],
          ['#557e93', 'Declared link'],
          ['#a2a99c', 'Unmatched candidate'],
        ],
      };
    case 'shape-material-v1':
      return {
        heading: 'Analytic shape / material ambiguity',
        corner: 'Two constructed material maps · metres',
        legend: [
          ['#b8b5a6', 'Identical shell'],
          ['#307f74', 'Point A / trajectory'],
          ['#b77128', 'Point B / trajectory'],
          ['#557e93', 'Point C / trajectory'],
        ],
      };
    case 'anatomy-identity-v1':
      return {
        heading: 'Supplied objects → anatomical identities',
        corner: 's1233 subset · teaching IDs · shared source frame',
        legend: [
          ['#b8b5a6', 'Supplied neighbouring objects'],
          ['#307f74', 'Object being inspected'],
        ],
      };
    case 'anatomy-audit-v1':
      return {
        heading: 'Source-derived assembly · label audit',
        corner: 's1233 · shared source frame · display anchors only',
        legend: [
          ['#b8b5a6', 'Retained neighbouring objects'],
          ['#307f74', 'Source object under inspection'],
        ],
      };
    case 'inverse-v1':
      return {
        heading:
          plan.acquisition === 'ct-parallel'
            ? 'Parallel-beam CT · mathematical fixture'
            : 'Cartesian MRI · mathematical fixture',
        corner: 'Unitless 128 × 128 fixture',
        legend: [['#555555', 'Derived numerical arrays; shared scalar display']],
      };
    default:
      return { heading: 'Synthetic operation explanation', corner: 'Teaching fixture', legend: [] };
  }
}
