import { useCallback, useLayoutEffect, useRef, useState } from 'react';
import type { ReaderProps } from '../../explainer';
import type { NativeTraceView, NativeTracePlan } from '../../contracts.generated';
import { useFramePlayer } from '../player/use-frame-player';
import { CtTraceStage } from '../native/CtTraceStage';
import { MraTraceStage } from '../native/MraTraceStage';
import styles from './native-trace-reader.module.css';

const adapter = { planar: true, interactiveProjection: true };
const chapterLabels: Record<string, string> = {
  input: 'Inputs',
  search: 'Search',
  bounds: 'Volume bounds',
  coarse: 'Coarse match',
  threshold: 'Thresholds',
  contacts: 'Contacts',
  output: 'Saved answer',
  reference: 'Reference',
};

function ReferenceResult({ view }: { view: NativeTraceView }) {
  if (!view.payload) return null;
  if (view.adapter === 'ct-pose') {
    const score = view.payload.reference.frozen_metrics;
    return (
      <section className={styles.result} data-native-reference-result>
        <strong>Frozen geometric check</strong>
        <span>
          RMS {score.rms_mm.toFixed(6)} mm · maximum {score.max_mm.toFixed(6)} mm
        </span>
        <small>
          Engineering calibration, not clinical precision. Amber dashed outline: private pose.
        </small>
      </section>
    );
  }
  const score = view.payload.reference.frozen;
  const passed = Object.values(score.checks).filter(Boolean).length;
  return (
    <section className={styles.result} data-native-reference-result>
      <strong>
        {passed} / {Object.keys(score.checks).length} frozen checks pass
      </strong>
      <span>
        {view.payload.observed.added.length} of{' '}
        {view.payload.observed.added.length + view.payload.reference.residual.length} authored
        deletions restored · {score.outside_edit_changed_voxels} outside-domain edits
      </span>
      <small>
        Magenta: missed reference voxels. This is a synthetic defect on real MRA, not a
        natural-error repair benchmark.
      </small>
    </section>
  );
}

function TraceEvidence({
  view,
  plan,
  index,
}: {
  view: NativeTraceView;
  plan: NativeTracePlan;
  index: number;
}) {
  const steps = plan.beats[index].trace_steps;
  const trace = view.payload?.observed.trace.filter((item) => steps.includes(item.step)) ?? [];
  return (
    <details className={styles.evidence} id={`native-evidence-${plan.id}`}>
      <summary>
        Inspect the recorded tools & provenance{' '}
        <span>{steps.length} selected steps in this chapter</span>
      </summary>
      <p>
        These are retained calls and outputs, not a reconstruction of hidden reasoning. Reader
        controls do not rerun the agent.
      </p>
      {trace.map((item) => (
        <details key={item.step} data-native-trace-step={item.step}>
          <summary>
            Step {item.step} · {item.timestamp}
          </summary>
          <pre>{item.calls.join('\n\n')}</pre>
          <pre>{item.output}</pre>
        </details>
      ))}
      <details>
        <summary>Images actually delivered to the solver</summary>
        <p>
          Retained image deliveries have their own step numbers; they are separate from newly
          generated reader views.
        </p>
        <div className={styles.delivered}>
          {view.payload?.delivered_images.map((image) => (
            <figure key={image.path}>
              <img loading="lazy" src={image.src} alt={`Recorded delivery at step ${image.step}`} />
              <figcaption>
                Step {image.step} · {image.path.split('/').at(-1)}
              </figcaption>
            </figure>
          ))}
        </div>
      </details>
      <details>
        <summary>Selected source files, hashes and terms</summary>
        <p>{view.reference_boundary}</p>
        <p>
          Native coordinates: {view.coordinates} · attempt: <code>{view.attempt}</code>
        </p>
        <ul>
          {view.bundle.assets.map((asset) => (
            <li key={asset.path}>
              <code>{asset.path}</code>
              <span>
                {asset.role} · {asset.bytes.toLocaleString()} bytes
              </span>
              <code>{asset.sha256}</code>
            </li>
          ))}
        </ul>
        {view.payload?.licenses.map((license, i) => (
          <pre key={i}>{license}</pre>
        ))}
      </details>
    </details>
  );
}

/** One shared clock and evidence shell; adapters own only native image geometry. */
export function NativeTraceReader({ entry, plan, view, capture, captureReady }: ReaderProps) {
  if (!plan || plan.recipe !== 'native-trace-v1' || !view || view.family !== 'native-trace')
    throw new Error('Native trace requires its canonical plan and selected view');
  const player = useFramePlayer(entry, plan, adapter);
  const state = player.storyState!;
  if (state.recipe !== 'native-trace-v1') throw new Error('Native trace player mismatch');
  const beat = plan.beats[state.index];
  const stageKey = `${plan.id}:${beat.id}:${player.resetRevision}`;
  const [consent, setConsent] = useState<string | null>(null);
  const [stageReady, setStageReady] = useState(false);
  const lastFrame = useRef(state.frame);
  const captureMode = new URLSearchParams(location.search).has('capture');
  const referenceShown =
    beat.reference && (captureMode || (consent === stageKey && state.frame >= lastFrame.current));
  const onReady = useCallback((ready: boolean) => setStageReady(ready), []);
  useLayoutEffect(() => {
    if (state.frame < lastFrame.current) setConsent(null);
    lastFrame.current = state.frame;
    if (capture) capture.current = player.actions.current;
    if ((stageReady || !view.payload) && player.actions.current) captureReady?.(true);
    return () => {
      if (capture) capture.current = null;
    };
  });
  const hiddenReference = beat.reference && !referenceShown;
  return (
    <div
      className={`scene-player ${styles.reader}`}
      ref={player.root}
      data-family="native-trace"
      data-recipe={plan.recipe}
      data-native-adapter={view.adapter}
      data-beat={state.beatId}
      data-committed-frame={state.frame}
      data-playing={String(player.playing)}
      data-reference-shown={String(referenceShown)}
      lang="en"
    >
      <header className={styles.heading}>
        <p className={styles.eyebrow}>
          A retained solving trace <span>{view.coordinates} · native context</span>
        </p>
        <h3>{plan.title}</h3>
        <p className={styles.scope}>{plan.scope}</p>
      </header>
      <nav className={styles.chapters} aria-label="Trace chapters">
        {plan.beats.map((chapter, i) => (
          <button
            key={chapter.id}
            data-story-step={i}
            aria-pressed={state.index === i}
            onClick={() => player.actions.current?.selectBeat(i)}
          >
            <span>{String(i + 1).padStart(2, '0')}</span>
            {chapterLabels[chapter.id] ?? chapter.caption}
          </button>
        ))}
      </nav>
      <section className={styles.chapter}>
        <header className={styles.chapterHeading}>
          <span>
            {String(state.index + 1).padStart(2, '0')} / {plan.beats.length}
          </span>
          <div>
            <h4 data-scene-title>{beat.caption}</h4>
            <p>
              {hiddenReference
                ? 'The saved answer is still visible. Reveal the evaluator evidence to compare it with the private reference.'
                : beat.narration}
            </p>
          </div>
        </header>
        {beat.reference && (
          <div className={styles.reveal}>
            <button
              data-native-reference-reveal
              aria-expanded={referenceShown}
              onClick={() => setConsent(referenceShown ? null : stageKey)}
              disabled={captureMode || !view.payload}
            >
              {referenceShown ? 'Hide private reference' : 'Reveal private reference'}
            </button>
            <small>
              {captureMode
                ? 'Authored reference chapter · canonical capture'
                : 'Reader evidence, not supplied solver input. Hidden again on chapter change or reset.'}
            </small>
          </div>
        )}
        <div className={`scene-stage ${styles.stage}`}>
          {!view.payload ? (
            <div className={styles.missing} data-native-ready="true">
              <strong>Native assets are unavailable in this copy.</strong>
              <p>{view.source.notice.text}</p>
              <p>The recorded narrative remains available. No substitute scan or run is shown.</p>
              <details>
                <summary>{view.missing.length} missing local files</summary>
                <ul>
                  {view.missing.map((path) => (
                    <li key={path}>
                      <code>{path}</code>
                    </li>
                  ))}
                </ul>
              </details>
            </div>
          ) : view.adapter === 'ct-pose' ? (
            <CtTraceStage
              key={stageKey}
              payload={view.payload}
              stateId={beat.state}
              chapterId={beat.id}
              referenceShown={referenceShown}
              onReady={onReady}
            />
          ) : (
            <MraTraceStage
              key={stageKey}
              payload={view.payload}
              stateId={beat.state}
              chapterId={beat.id}
              referenceShown={referenceShown}
              onReady={onReady}
            />
          )}
        </div>
        {referenceShown && <ReferenceResult view={view} />}
        {!hiddenReference && <p className={styles.mechanism}>{beat.visual}</p>}
        <div className="scene-annotations" ref={player.annotations} aria-hidden="true" />
      </section>
      <footer className={styles.transport}>
        <button
          disabled={state.index === 0}
          onClick={() => player.actions.current?.selectBeat(state.index - 1)}
        >
          ← Previous
        </button>
        <button
          disabled={state.index === plan.beats.length - 1}
          onClick={() => player.actions.current?.selectBeat(state.index + 1)}
        >
          Next chapter →
        </button>
        <span className={styles.spacer} />
        <button className="scene-play" onClick={() => player.actions.current?.toggle()}>
          {player.playing ? 'Pause' : 'Play'}
        </button>
        <button className="scene-reset" onClick={() => player.actions.current?.reset()}>
          Reset
        </button>
        <small>
          {Math.floor(state.frame / plan.fps)} / {Math.round(plan.durationFrames / plan.fps)} s
        </small>
      </footer>
      <TraceEvidence key={stageKey} view={view} plan={plan} index={state.index} />
    </div>
  );
}
