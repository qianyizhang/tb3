// Bundle the production ES modules through the same Vite transforms as the UI.
// Nothing is copied, import-stripped, substituted or exposed on window.
export { AnatomyAssets as anatomy } from '../presentation/frontend/task-visuals/anatomy.ts';
export { TaskSceneModels as models } from '../presentation/frontend/task-visuals/recipes.ts';
export { SceneStage as stage } from '../presentation/frontend/task-visuals/stage.ts';
export { taskSceneMode as mode } from '../presentation/frontend/task-visuals/mode.ts';
export { TaskTeachingArt as teachingArt } from '../presentation/assets/teaching/task-art.js';
export { TaskTeachingStory as teachingStory } from '../presentation/assets/teaching/task-story.js';
