import { createClinicalCavityPrefab } from './clinical-cavity-prefab';
import type { StoryPlan } from '../types';
import type { StoryState } from './story-timeline';
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
export function showInlineNarration(state: StoryState): boolean {
  // The identity chapter reveals its reference midway through playback.
  return !(
    (state.recipe === 'automed-multiorgan-v1' &&
      state.scene === 'reference' &&
      state.reference <= 0.5) ||
    (state.recipe === 'abra-annotation-v1' &&
      state.scene === 'reference' &&
      state.reference <= 0.5) ||
    (state.recipe === 'ct-context-v1' && state.scene === 'reference' && state.reference <= 0.5) ||
    (state.recipe === 'history-sourcing-v1' &&
      state.scene === 'reference' &&
      state.reference <= 0.5) ||
    (state.recipe === 'mri-importer-v1' && state.scene === 'reference' && state.reference <= 0.5) ||
    (state.recipe === 'localized-ct-v1' && state.scene === 'reference' && state.reference <= 0.5) ||
    (state.recipe === 'aneurysm-localization-v1' &&
      state.scene === 'reference' &&
      state.reference <= 0.5) ||
    (state.recipe === 'segmentation-calibration-v1' &&
      state.scene === 'reference' &&
      state.reference <= 0.5) ||
    (state.recipe === 'dental-v2-v1' && state.scene === 'identity' && state.reference <= 0.5) ||
    (state.recipe === 'dental-v3-v1' && state.scene === 'shape' && state.reference <= 0.5)
  );
}
export function isPlanarStory(plan: StoryPlan): boolean {
  return [
    'automed-multiorgan-v1',
    'bcer-workflow-v1',
    'abra-annotation-v1',
    'ct-context-v1',
    'history-sourcing-v1',
    'mri-importer-v1',
    'localized-ct-v1',
    'aneurysm-localization-v1',
    'segmentation-calibration-v1',
    'dental-v3-v1',
    'dental-v2-v1',
    'dental-original-v1',
    'ct-organ-v1',
    'named-landmarks-v1',
    'multiscale-v1',
    'local-edit-v1',
    'longitudinal-v1',
    'inverse-v1',
    'mixed-tissue-v1',
    'registration-analysis-v1',
    'vessel-source-v1',
    'topbrain-screen-v1',
    'hubmap-inventory-v1',
    'tiger-context-v1',
    'longitudinal-ct-revised-v1',
    'longitudinal-ct-original-v1',
    'longitudinal-mri-v1',
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
    'clinical-cavity-v1',
    'respiratory-v1',
  ].includes(plan.recipe);
}
export function nativeFactory(plan: StoryPlan) {
  switch (plan.recipe) {
    case 'clinical-cavity-v1':
      return createClinicalCavityPrefab;
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
  legend: [string, string, (boolean | 'dotted')?][];
} {
  switch (plan.recipe) {
    case 'automed-multiorgan-v1':
      return {
        heading: 'Map CT anatomy into the benchmark labels',
        corner: 'Native CT · partial reference reveal · nonclinical scoring',
        legend: [
          ['#49cfac', 'Left kidney · reference fill'],
          ['#69aaff', 'Right kidney · reference fill'],
          ['#ffd26b', 'Liver · reference fill'],
          ['#ee8dbd', 'Spleen · reference fill'],
          ['#c2a0ff', 'Aorta · reference fill'],
        ],
      };
    case 'bcer-workflow-v1':
      return {
        heading: 'Complete a prostate MRI workflow',
        corner: 'Native MRI · public contract · nonclinical validator replay',
        legend: [
          ['#ffffff', 'Header-coordinate witness · cross'],
          ['#267f72', 'Selected public dependency'],
        ],
      };
    case 'abra-annotation-v1':
      return {
        heading: 'Outline a nodule in native image coordinates',
        corner: 'Actual CT and source contour · ordinary and oracle conditions',
        legend: [
          ['#37c9bc', 'Reader reference · solid'],
          ['#ffc35b', 'Reference-copy example · dashed', true],
          ['#78afff', 'Oracle contour · dotted', 'dotted'],
        ],
      };
    case 'ct-context-v1':
      return {
        heading: 'What context can these CTs support?',
        corner: 'Native CT pair · qualified output · separate metadata reveal',
        legend: [
          ['#ffc35b', 'Agent evidence point · cross'],
          ['#ffc35b', 'Agent evidence region · dashed', true],
        ],
      };
    case 'history-sourcing-v1':
      return {
        heading: 'From history to bounded task evidence',
        corner: 'Eight retained excerpts · five candidate contracts · original outcomes',
        legend: [
          ['#c97b18', 'Selected record'],
          ['#267f72', 'Verified provenance'],
          ['#c97b18', 'Untested branch', true],
        ],
      };
    case 'mri-importer-v1':
      return {
        heading: 'Reconstruct MRI frame associations',
        corner: 'Actual synthetic samples · native metadata · private result reveal',
        legend: [
          ['#c97b18', 'Selected frame or corner'],
          ['#267f72', 'Canonical slot or corner'],
        ],
      };
    case 'localized-ct-v1':
      return {
        heading: 'Judge a supplied CT candidate',
        corner: 'Full CT pair + two points · saved decisions · private reference reveal',
        legend: [
          ['#ff626b', 'Supplied point · cross'],
          ['#36dcdd', 'Private reference · solid'],
        ],
      };
    case 'aneurysm-localization-v1':
      return {
        heading: 'Aneurysm search and localization',
        corner: 'Native MRA · three retained cases · separate reference reveal',
        legend: [
          ['#32d8e2', 'Submitted point · cross'],
          ['#9beb72', 'Weak region · dashed', true],
          ['#f5d76e', '+1 mm acceptance · dotted', 'dotted'],
        ],
      };
    case 'segmentation-calibration-v1':
      return {
        heading: 'Box-to-mask calibration',
        corner: 'One CT · reference-derived boxes · retained tool outputs',
        legend: [
          ['#32d8e2', 'SAM2 MPS · solid'],
          ['#fb923c', 'LiteMedSAM MPS · solid'],
          ['#d197ff', 'SAM2 CPU · solid'],
          ['#9beb72', 'Reference · dashed', true],
          ['#f5d76e', 'Supplied box · dotted', 'dotted'],
        ],
      };
    case 'dental-v3-v1':
      return {
        heading: 'Dental v3 · how far refinement can reach',
        corner: 'One F018 pair · native indices · saved operations',
        legend: [
          ['#fb923c', 'No example · solid'],
          ['#32d8e2', 'Assisted / example · solid'],
          ['#9beb72', 'Private target reference · dashed', true],
          ['#d197ff', 'Transferred prior · solid'],
          ['#f5d76e', 'Eligible region / search box · dotted', 'dotted'],
        ],
      };
    case 'dental-v2-v1':
      return {
        heading: 'Dental v2 · what transfers, what fails',
        corner: 'One F002 pair · native indices · unchanged answers',
        legend: [
          ['#fb923c', 'No example · solid'],
          ['#32d8e2', 'Assisted / supplied example · solid'],
          ['#9beb72', 'Private target reference · dashed', true],
          ['#d197ff', 'Transferred prior · solid'],
          ['#f472b6', 'Deleted pulp · solid'],
        ],
      };
    case 'dental-original-v1':
      return {
        heading: 'Dental anatomy · geometry, identity and reference conventions',
        corner: 'Native indices · selected reader views · unchanged submitted arrays',
        legend: [
          ['#fb923c', 'F018 medium · solid'],
          ['#32d8e2', 'Xhigh / F002 output · solid'],
          ['#9beb72', 'Private reference · dashed', true],
          ['#d197ff', 'Reconstructed pulp gate · solid'],
        ],
      };
    case 'ct-organ-v1':
      return {
        heading: 'CT organs · construct, name and compare',
        corner: 'Native CT · reader-selected sections · independent masks',
        legend: [
          ['#fb923c', 'Astra/medium · solid'],
          ['#32d8e2', '+ LiteMedSAM · solid'],
          ['#9beb72', 'Private reference · dashed', true],
          ['#d197ff', 'Method polygon / box · dashed', true],
        ],
      };
    case 'named-landmarks-v1':
      return {
        heading: 'Named targets · location and availability',
        corner: 'Native CT / MRI · reader-selected diagnostic views · physical 3D scoring',
        legend: [
          ['#fb923c', 'Terra/high · saved cross'],
          ['#cf94ff', 'Sol/xhigh · saved circle'],
          ['#54deaa', 'Private source point · plus'],
        ],
      };
    case 'clinical-cavity-v1':
      return {
        heading: 'Clinical cavity · track, measure and test',
        corner: 'EchoXFlow · local mm axes · discrete acquired frames · slowed playback',
        legend: [
          ['#8398ad', 'Supplied initial surface'],
          ['#18c6d4', 'Saved output · solid section'],
          ['#f4bc49', 'Private reference · dashed section', true],
        ],
      };
    case 'longitudinal-ct-revised-v1':
      return {
        heading: 'Revised CT · inclusion, partition and context',
        corner: 'Two selected cases · three revised conditions · original scores retained',
        legend: [
          ['#36dcdd', 'Reference mask · cyan solid'],
          ['#e583ea', 'Revised / image-only mask · purple solid'],
          ['#ffb636', 'Original / context mask · amber solid'],
        ],
      };
    case 'longitudinal-ct-original-v1':
      return {
        heading: 'Original CT · find, partition and link',
        corner: 'Native CT · reader-only reference reveals · convention under review',
        legend: [
          ['#ffb636', 'Saved Astra mask · solid'],
          ['#36dcdd', 'Reference palette · cyan solid'],
          ['#ef81e4', 'Reference palette · pink solid'],
          ['#a8ed70', 'Reference palette · green solid'],
          ['#72a9ff', 'Reference palette · blue solid'],
        ],
      };
    case 'longitudinal-mri-v1':
      return {
        heading: 'Longitudinal MRI · locate, measure, qualify',
        corner: 'BR037 · native MRI · saved outputs and reader references',
        legend: [
          ['#cb8523', 'Saved output / projected method box'],
          ['#187d74', 'Source reference', true],
          ['#697582', 'Unregistered native visits'],
        ],
      };
    case 'tiger-context-v1':
      return {
        heading: 'TIGER · cells, tissue and a calibrated denominator',
        corner: '114S · supplied ROIs · source-reference teaching',
        legend: [
          ['#ffde35', 'Cell marker reference', true],
          ['#d54579', '1 · invasive tumor'],
          ['#20a49a', '2 · stroma'],
          ['#3476c9', '6 · inflamed stroma'],
          ['#8970c6', '4 · healthy glands'],
          ['#aaa54a', '7 · rest'],
          ['#697582', '0 · excluded'],
        ],
      };
    case 'hubmap-inventory-v1':
      return {
        heading: 'HuBMAP · one contour, one inventory row',
        corner: 'PAS kidney · level-0 pixels · reference-derived teaching',
        legend: [
          ['#187d74', 'Source reference', true],
          ['#be791f', 'Teaching viewport / centroid'],
          ['#426ebc', 'Optional cortex'],
          ['#8854ad', 'Optional medulla'],
        ],
      };
    case 'topbrain-screen-v1':
      return {
        heading: 'TopBrain · prediction screening before task admission',
        corner: 'Five development scans · selected native views · no agent trial',
        legend: [
          ['#5b77d8', 'Prediction / reference context'],
          ['#f4aa3d', 'First named class'],
          ['#27c4bc', 'Second named class'],
          ['#e7519f', 'Saved addition / detached reference'],
        ],
      };
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
