import { useEffect, useState } from 'react';
import type { ExplorerData, StoryPlan, RestorationView } from '../types';

interface Resource {
  plan: StoryPlan;
  view?: RestorationView;
}
const pending = new Map<string, Promise<Resource>>();

/** The static packager owns these same-origin JSON projections. Share overlapping requests. */
export function useExplainerResource(id: string | undefined, data: ExplorerData) {
  const url = id ? data.explainer_resources?.[id] : undefined;
  const [loaded, setLoaded] = useState<{ url?: string; resource?: Resource; error?: string }>({});
  useEffect(() => {
    if (!url || !id) return;
    let active = true;
    if (!pending.has(url))
      pending.set(
        url,
        fetch(url)
          .then(async (response) => {
            if (!response.ok) throw new Error(`Walkthrough could not load (${response.status}).`);
            const resource: Resource = await response.json();
            if (resource.plan?.id !== id || !Array.isArray(resource.plan.beats))
              throw new Error('Walkthrough identity differs from the selected task.');
            return resource;
          })
          .catch((error) => {
            pending.delete(url);
            throw error;
          }),
      );
    pending.get(url)!.then(
      (resource) => {
        if (active) setLoaded({ url, resource });
      },
      (error: Error) => {
        if (active) setLoaded({ url, error: error.message });
      },
    );
    return () => {
      active = false;
    };
  }, [id, url]);
  const resource = loaded.url === url ? loaded.resource : undefined;
  return {
    plan: id ? (data.explanation_stories?.[id] ?? resource?.plan) : undefined,
    view: id ? (data.explainer_views?.[id] ?? resource?.view) : undefined,
    error: loaded.url === url ? loaded.error : undefined,
  };
}
