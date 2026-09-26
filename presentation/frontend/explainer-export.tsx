/** Dedicated composed export entry. The ordinary Explorer exposes no capture global. */
import { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { flushSync } from 'react-dom';
import { LocaleProvider } from './locale';
import { TaskVisual } from './task-visuals/TaskVisual';
import type { PlayerActions } from './task-visuals/use-scene-player';
import type { StoryPlan } from './types';
import type { VisualEntry } from './task-visuals/types';
import type {} from './capture';
const plan: StoryPlan = JSON.parse(document.querySelector('#story-plan')!.textContent!);
const entry: VisualEntry = {
  illustration: {
    kind: 'route_unfold',
    story_id: plan.id,
    input: plan.beats[0].caption,
    output: plan.beats.at(-1)!.caption,
    caption: plan.scope,
  },
};
function ExportView() {
  const capture = useRef<PlayerActions | null>(null);
  const [readiness] = useState(() => {
    let resolve!: () => void, reject!: (error: Error) => void;
    const promise = new Promise<void>((a, b) => {
      resolve = a;
      reject = b;
    });
    return { promise, resolve, reject };
  });
  useEffect(() => {
    const ready = readiness.promise;
    // Rejections are observed by the capture consumer; avoid an unhandled promise before it connects.
    void ready.catch(() => {});
    window.__tb3ExplainerCapture = {
      ready,
      async seekFrame({ frame, fps, width, height }) {
        if (!document.querySelector('[data-explainer-export-frame]'))
          throw new Error('Open the export entry with ?capture=1 before capturing');
        await ready;
        if (fps !== plan.fps || width !== 1280 || height !== 720)
          throw new Error('Pilot capture requires canonical 1280x720 at script fps');
        flushSync(() => capture.current!.seekFrame(frame, true));
        if (
          document.querySelector('.scene-player')?.getAttribute('data-committed-frame') !==
          String(frame)
        )
          throw new Error('React frame did not commit');
        await document.fonts.ready;
      },
    };
    return () => {
      delete window.__tb3ExplainerCapture;
    };
  }, [readiness]);
  return (
    <div
      data-explainer-export-frame={
        new URLSearchParams(location.search).has('capture') ? '' : undefined
      }
    >
      <TaskVisual
        entry={entry}
        plan={plan}
        capture={capture}
        captureReady={(available) =>
          available ? readiness.resolve() : readiness.reject(new Error('WebGL export unavailable'))
        }
      />
    </div>
  );
}
createRoot(document.querySelector('#root')!).render(
  <LocaleProvider>
    <ExportView />
  </LocaleProvider>,
);
