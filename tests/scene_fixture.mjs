// Bundle the production ES modules through the same Vite transforms as the UI.
// Nothing is copied, import-stripped, substituted or exposed on window.
export { AnatomyAssets as anatomy } from '../presentation/task-explorer/scene-anatomy.js';
export { TaskSceneModels as models } from '../presentation/task-explorer/scene-models.js';
export { SceneSurfaces as surfaces } from '../presentation/task-explorer/scene-surfaces.js';
export { TaskScenes as scenes } from '../presentation/task-explorer/scenes.js';
export { TaskTeachingArt as teachingArt } from '../presentation/assets/teaching/task-art.js';
export { TaskTeachingStory as teachingStory } from '../presentation/assets/teaching/task-story.js';
