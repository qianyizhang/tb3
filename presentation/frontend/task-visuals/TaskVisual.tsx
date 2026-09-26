import { useId, useLayoutEffect, type CSSProperties, type RefObject } from 'react';
import type { StoryPlan } from '../types';
import type { PlayerActions } from './use-scene-player';
import { StoryOutput } from './story-output';
import { fixturePoster } from './route-prefab';
import { isPlanarStory, storyPresentation } from './story-recipes';
import { OperationScene, OperationOutput } from './operation-view';
export interface VisualProps {
  entry: VisualEntry;
  plan?: StoryPlan;
  capture?: RefObject<PlayerActions | null>;
  captureReady?: (available: boolean) => void;
}
import { TaskTeachingArt } from '../../assets/teaching/task-art.js';
import { TaskTeachingStory } from '../../assets/teaching/task-story.js';
import { useLocale } from '../locale';
import { AnatomyAssets } from './anatomy';
import { TaskSceneModels } from './recipes';
import { taskSceneMode } from './mode';
import { useScenePlayer } from './use-scene-player';
import type { Stage, VisualEntry } from './types';
import styles from './task-visual.module.css';

/** Only the retained SVG teaching library crosses this markup boundary. */
function TeachingArt({ entry, output = false }: { entry: VisualEntry; output?: boolean }) {
  return <div dangerouslySetInnerHTML={{ __html: TaskTeachingArt.render(entry, output) }} />;
}
function PicturePair({ entry }: { entry: VisualEntry }) {
  const { t } = useLocale();
  return (
    <div className="picture-pair">
      <section>
        <h4>{t('Input')}</h4>
        <TeachingArt entry={entry} />
        <p lang="en">{entry.illustration.input}</p>
      </section>
      <div className="picture-arrow" aria-hidden="true">
        →
      </div>
      <section>
        <h4>{t(entry.role && entry.role !== 'task' ? 'Study output' : 'Expected output')}</h4>
        <TeachingArt entry={entry} output />
        <p lang="en">{entry.illustration.output}</p>
      </section>
    </div>
  );
}
function LanguageNote() {
  const { locale } = useLocale();
  return locale === 'zh-CN' ? (
    <p className="scene-language-note" lang="zh-CN">
      示意图细节保留英文原文。
    </p>
  ) : null;
}
function VisualNotes({ entry }: { entry: VisualEntry }) {
  const { t } = useLocale();
  return (
    <details className="scene-notes">
      <summary>{t('About this illustration')}</summary>
      <p lang="en">{entry.illustration.caption}</p>
      {!!entry.illustration.labels?.length && (
        <details className="scene-label-space">
          <summary>
            {t('Possible class labels')} ({entry.illustration.labels.length})
          </summary>
          <div>
            {entry.illustration.labels.map((name) => (
              <span key={name}>{name}</span>
            ))}
          </div>
        </details>
      )}
      {TaskSceneModels.usesAnatomy(entry) && (
        <details className="scene-asset-notice">
          <summary>{t('About the anatomy models')}</summary>
          <p lang="en">
            Shared teaching anatomy, not a reconstruction or scored output for the selected case.
            Markers and motion are illustrative.
          </p>
          <p lang="en">
            Organ surfaces: Wasserthal and the TotalSegmentator contributors, University Hospital
            Basel.{' '}
            <a href="https://zenodo.org/records/10047263" target="_blank" rel="noopener noreferrer">
              TotalSegmentator v2.0.1
            </a>
            . Brain and dental shapes are authored schematics.
          </p>
          <details>
            <summary>{t('Derivation and licenses')}</summary>
            <pre>{AnatomyAssets.notice}</pre>
          </details>
        </details>
      )}
    </details>
  );
}
function StaticVisual({ entry }: { entry: VisualEntry }) {
  const story = TaskTeachingStory.describe(entry);
  return (
    <div
      className={`scene-static ${styles.staticVisual}`}
      data-scene={entry.illustration.kind}
      data-scene-mode="static"
    >
      <LanguageNote />
      <div className="scene-static-heading">
        <strong lang="en">{story.action}</strong>
        <p lang="en">{story.cue}</p>
      </div>
      <PicturePair entry={entry} />
      <VisualNotes entry={entry} />
    </div>
  );
}
function SpatialVisual({ entry, plan, capture, captureReady }: VisualProps) {
  const { t } = useLocale();
  const description = useId();
  const story = TaskTeachingStory.describe(entry),
    d = entry.illustration;
  const player = useScenePlayer(entry, plan);
  const planar = !!plan && isPlanarStory(plan);
  const presentation = plan ? storyPresentation(plan) : undefined;
  useLayoutEffect(() => {
    if (capture) capture.current = player.actions.current;
    if (player.root.current?.dataset.rendered === 'true')
      captureReady?.(!player.fallback && !!player.actions.current);
    return () => {
      if (capture) capture.current = null;
    };
  });
  const { stage, playing, fallback, actions, pointer } = player;
  const steps = plan
    ? plan.beats.map((beat) => beat.id)
    : [t('Input'), t('Action'), t(entry.role && entry.role !== 'task' ? 'Study output' : 'Output')];
  const copy = plan ? plan.beats.map((beat) => beat.caption) : [d.input, story.action, d.output];
  const selected = player.storyState?.index ?? stage;
  const atEnd = plan ? player.storyState?.frame === plan.durationFrames - 1 : stage === 2;
  const stopDrag = () => {
    pointer.current = null;
    actions.current?.drag(false);
    player.canvas.current?.classList.remove('dragging');
  };
  return (
    <div
      className={`scene-player ${styles.player} ${plan ? styles.scripted : ''}`}
      ref={player.root}
      data-recipe={plan?.recipe}
      data-scene={d.kind}
      data-stage={stage}
      data-beat={player.storyState?.beatId}
      data-committed-frame={player.storyState?.frame}
      data-playing={String(playing)}
    >
      <LanguageNote />
      {plan && (
        <header className={styles.storyHeading} lang="en">
          <span>{presentation!.heading}</span>
          <h3>{plan.title}</h3>
          <p>{plan.scope}</p>
        </header>
      )}
      <div className="scene-walkthrough-heading">
        <strong lang="en">{story.action}</strong>
        <p lang="en">{story.cue}</p>
      </div>
      <div className="scene-controls" hidden={fallback}>
        <div
          className="scene-steps scene-storyboard"
          role="group"
          aria-label={t('Illustration stage')}
        >
          {steps.map((label, i) => (
            <button
              key={i}
              data-scene-step={i}
              data-story-step={i}
              aria-pressed={selected === i}
              onClick={() =>
                plan ? actions.current?.selectBeat(i) : actions.current?.select(i as Stage)
              }
            >
              <span className="scene-step-index" aria-hidden="true">
                0{i + 1}
              </span>
              <span>
                <strong>{label}</strong>
                <span className="scene-step-copy" lang="en">
                  {copy[i]}
                </span>
              </span>
            </button>
          ))}
        </div>
      </div>
      <div className={plan ? styles.storyLayout : undefined}>
        <div className="scene-stage" hidden={fallback}>
          {planar && plan && player.storyState && (
            <>
              <OperationScene plan={plan} state={player.storyState} />
              <p className={styles.mobileNarration}>{player.storyState.narration}</p>
            </>
          )}
          <canvas
            hidden={planar}
            className="scene-canvas"
            ref={player.canvas}
            tabIndex={0}
            role="img"
            aria-label={`${d.input} → ${d.output}. ${t('Drag or use arrow keys to rotate. Space to play or pause.')}`}
            aria-describedby={description}
            onPointerDown={(event) => {
              if (event.button !== 0) return;
              pointer.current = [event.clientX, event.clientY];
              actions.current?.drag(true);
              event.currentTarget.setPointerCapture(event.pointerId);
              event.currentTarget.classList.add('dragging');
            }}
            onPointerMove={(event) => {
              if (!pointer.current) return;
              actions.current?.rotate(
                (event.clientX - pointer.current[0]) * 0.008,
                (event.clientY - pointer.current[1]) * 0.007,
              );
              pointer.current = [event.clientX, event.clientY];
            }}
            onPointerUp={stopDrag}
            onPointerCancel={stopDrag}
            onLostPointerCapture={stopDrag}
            onKeyDown={(event) => {
              if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', ' '].includes(event.key))
                return;
              event.preventDefault();
              if (event.key === ' ') actions.current?.toggle();
              else
                actions.current?.rotate(
                  event.key === 'ArrowLeft' ? -0.15 : event.key === 'ArrowRight' ? 0.15 : 0,
                  event.key === 'ArrowUp' ? -0.12 : event.key === 'ArrowDown' ? 0.12 : 0,
                );
            }}
          >
            {d.caption}
          </canvas>
          <div className="scene-annotations" ref={player.annotations} aria-hidden="true" />
          <span className="scene-corner" lang="en" hidden={planar}>
            {plan
              ? presentation!.corner
              : [
                    'dynamic_mesh',
                    'cardiac_material',
                    'cardiac_contours',
                    'cardiac_anchors',
                  ].includes(d.kind)
                ? 'Schematic ventricular cavity'
                : story.context}
          </span>
        </div>
        {plan &&
          player.storyState &&
          (player.storyState.recipe === 'route-unfold-v1' ? (
            <StoryOutput state={player.storyState} />
          ) : (
            <OperationOutput plan={plan} state={player.storyState} />
          ))}
      </div>
      <div className="scene-transport" hidden={fallback}>
        <button
          className="scene-play"
          onClick={() => actions.current?.toggle()}
          aria-label={t(
            playing ? 'Pause animation' : atEnd ? 'Replay illustration' : 'Play animation',
          )}
        >
          <span className={playing ? styles.pauseIcon : styles.playIcon} aria-hidden="true" />
          {t(playing ? 'Pause' : atEnd ? 'Replay' : 'Play')}
        </button>
        <button
          className="scene-reset"
          onClick={() => actions.current?.reset()}
          aria-label={t('Reset illustration view')}
        >
          {t('Reset')}
        </button>
        <span className="scene-gesture" aria-hidden="true" hidden={planar}>
          {t('Drag to explore in 3D')}
        </span>
      </div>
      <div className="scene-fallback" hidden={!fallback}>
        {fallback && (
          <>
            <p lang={plan?.schema === 2 ? 'en' : undefined}>
              {plan?.schema === 2
                ? `3D is unavailable. This is a data-derived ending-frame projection${plan.recipe === 'anatomy-audit-v1' ? ' of the retained source assembly' : ' of the teaching fixture'}; the transcript retains every step.`
                : t(
                    plan
                      ? '3D is unavailable. The synthetic fixture poster and transcript remain available.'
                      : '3D is unavailable. The task diagram is shown below.',
                  )}
            </p>
            {plan && plan.recipe !== 'route-unfold-v1' && player.storyState ? (
              <OperationScene plan={plan} state={player.storyState} />
            ) : plan ? (
              <figure>
                <img
                  src={fixturePoster}
                  alt="Derived fixed-view poster of this synthetic fixture"
                />
                <figcaption>{plan.beats[selected].caption}</figcaption>
              </figure>
            ) : (
              <PicturePair entry={entry} />
            )}
          </>
        )}
      </div>
      <div className="scene-explanation" id={description}>
        <span className="scene-current-step">{steps[selected]}</span>
        <strong data-scene-title lang="en">
          {copy[selected]}
        </strong>
      </div>
      <div className="scene-legend" lang="en">
        {(plan ? presentation!.legend : TaskSceneModels.legend(entry)).map(
          ([color, label, dashed]) => (
            <span key={label}>
              <i
                style={
                  { '--key': color, borderTopStyle: dashed ? 'dashed' : 'solid' } as CSSProperties
                }
              />
              {label}
            </span>
          ),
        )}
      </div>
      {plan ? (
        <details className="scene-notes" lang="en">
          <summary>Transcript · English source</summary>
          {plan.beats.map((beat) => (
            <section key={beat.id}>
              <strong>{beat.caption}</strong>
              <p>{beat.narration}</p>
            </section>
          ))}
        </details>
      ) : (
        <VisualNotes entry={entry} />
      )}
    </div>
  );
}
export function TaskVisual({ entry, plan, capture, captureReady }: VisualProps) {
  if (entry.illustration.story_id && !plan) throw new Error('Unresolved explanation story');
  return !plan && taskSceneMode(entry) === 'static' ? (
    <StaticVisual entry={entry} />
  ) : (
    <SpatialVisual entry={entry} plan={plan} capture={capture} captureReady={captureReady} />
  );
}
