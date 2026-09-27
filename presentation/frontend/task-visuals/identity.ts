import { AnatomyAssets } from './anatomy';
import type { StoryState } from './story-timeline';

export type IdentityState = Extract<StoryState, { recipe: 'anatomy-identity-v1' }>;

// Teaching identifiers deliberately differ from the frozen task's object IDs.
// Preserve the shared source assembly; names come from retained source metadata.
export const identityObjects = () =>
  AnatomyAssets.get('abdomen')!.map((part, index) => ({
    part,
    objectId: `T${String(index + 1).padStart(2, '0')}`,
  }));

export function identityRows(state: IdentityState) {
  const objects = identityObjects();
  const selected = Math.min(objects.length - 1, Math.floor(state.focus * objects.length));
  const revealed = Math.floor(state.reveal * objects.length + 1e-8);
  return objects.map(({ part, objectId }, index) => ({
    objectId,
    selected: index === selected,
    label: index < revealed ? part.id : null,
  }));
}
