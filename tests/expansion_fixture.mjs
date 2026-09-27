export {
  cavityCases,
  cavityOutputs,
  cavityReferences,
  cavitySelection,
  cavitySectionPath,
  decodeCavity,
} from '../presentation/frontend/task-visuals/clinical-cavity';
export {
  revisedSource,
  revisedViews,
  revisedRef,
  revisedIndex,
  revisedReference,
  revisedOutput,
  ctNativePoint,
  recoveredIdentities,
  sizeSummary,
} from '../presentation/frontend/task-visuals/longitudinal-ct-revised';
export {
  ctSource,
  ctVisits,
  ctReference,
  ctFrameIndex,
  ctShowReference,
  ctShowOutput,
  ctEdges,
  ctEligibleGroups,
} from '../presentation/frontend/task-visuals/longitudinal-ct-original';
export {
  mriSource,
  mriP02,
  mriP03,
  mriRef,
  mriPhaseIndex,
  mriShowReference,
  mriShowOutput,
  percentChange,
  projectedMethodBox,
} from '../presentation/frontend/task-visuals/longitudinal-mri';
export {
  tigerSource,
  tigerViews,
  tigerRef,
  tigerReveal,
  tissueArea,
  pooledDensity,
  slidePoint,
} from '../presentation/frontend/task-visuals/tiger-context';
export {
  hubmapSource,
  hubmapDetail,
  hubmapTiles,
  hubmapRef,
  hubmapReveal,
  slideFit,
  toLocal,
  toLevel0,
  profileArea,
  hubmapRows,
} from '../presentation/frontend/task-visuals/hubmap-inventory';
export { Group } from 'three';
export { sampleStory } from '../presentation/frontend/task-visuals/story-timeline.ts';
export {
  brainCases,
  brainRefs,
  brainResult,
  brainReveal,
  brainOutput,
  brainSelection,
  brainPlaneFit,
  brainPixel,
} from '../presentation/frontend/task-visuals/topbrain-screen';
export {
  supportRows,
  objectiveSamples,
  analysisRevealed,
} from '../presentation/frontend/task-visuals/registration-analysis.ts';
export { identityRows } from '../presentation/frontend/task-visuals/identity.ts';
export { screenRows, screenReference } from '../presentation/frontend/task-visuals/mask-screen.ts';
export {
  prototypeRows,
  prototypeObjects,
  prototypeVocabulary,
  prototypeDisplay,
} from '../presentation/frontend/task-visuals/prototype-identity.ts';
export {
  mixedTissueView,
  mixedTissue,
} from '../presentation/frontend/task-visuals/mixed-tissue.ts';
export {
  nativeFactory,
  isPlanarStory,
  storyPresentation,
} from '../presentation/frontend/task-visuals/story-recipes.ts';
export {
  traceEdges,
  graph,
  rigid,
  transformedPoint,
  residualM,
  level0Point,
} from '../presentation/frontend/task-visuals/operation-fixtures.ts';

export {
  curationRows,
  curationReference,
} from '../presentation/frontend/task-visuals/anatomy-curation.ts';

export {
  respiratory,
  respiratoryRows,
  respiratoryReference,
  respiratoryOutput,
  q06Error,
  planePoint,
  planePixels,
} from '../presentation/frontend/task-visuals/respiratory.ts';

export {
  resectCase,
  resectReference,
  resectProjection,
  resectReveal,
  resectSweepIndex,
  resectTeachingOutput,
} from '../presentation/frontend/task-visuals/resect.ts';

export {
  pilotGeometry,
  pilotTrace,
  pilotReference,
  pilotOutput,
  pilotReveal,
  pilotSlabIndex,
} from '../presentation/frontend/task-visuals/resect-pilot';

export {
  vesselCases,
  vesselReference,
  vesselReveal,
  vesselOutput,
  vesselSliceIndex,
  vesselNodePixel,
  vesselVisibleNodes,
} from '../presentation/frontend/task-visuals/vessel-source';

export {
  airwayCases,
  airwayOutput,
  airwayReference,
  airwayReveal,
  airwayReturned,
  airwayCaseIndex,
  airwaySliceIndex,
  airwayAngleIndex,
  airwayRouteIndex,
  airwayDisplay,
  airwayBounds,
  airwayCPRRowEdges,
} from '../presentation/frontend/task-visuals/airway-repair';

export * from '../presentation/frontend/task-visuals/named-landmarks';

export * from '../presentation/frontend/task-visuals/ct-organ';
