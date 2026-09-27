import type { StoryPlan } from '../types';
import { createRoutePrefab } from './route-prefab';
import {
  createTopologyPrefab,
  createCorrespondencePrefab,
  createMaterialPrefab,
  createAnatomyPrefab,
  createIdentityPrefab,
  createPrototypeIdentityPrefab,
} from './operation-prefabs';
export function isPlanarStory(plan: StoryPlan): boolean {
  return [
    'multiscale-v1',
    'local-edit-v1',
    'longitudinal-v1',
    'inverse-v1',
    'mixed-tissue-v1',
  ].includes(plan.recipe);
}
export function hasInteractiveProjection(plan: StoryPlan): boolean {
  // Identity names must stay hidden at the start even without a GPU.
  return ['anatomy-identity-v1', 'prototype-identity-v1'].includes(plan.recipe);
}
export function nativeFactory(plan: StoryPlan) {
  switch (plan.recipe) {
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
