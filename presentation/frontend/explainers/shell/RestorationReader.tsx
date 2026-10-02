import { useId, useLayoutEffect, useRef, useState } from 'react';
import type { ReaderProps } from '../../explainer';
import type { RestorationView, StoryPlan } from '../../contracts.generated';
import { useLocale } from '../../locale';
import { useFramePlayer } from '../player/use-frame-player';
import { operationFrame, operationIndex } from '../player/restoration-controls';
import styles from './restoration-reader.module.css';

type Variant = 'guided' | 'compare' | 'focus';
const variants: Variant[] = ['guided', 'compare', 'focus'];
const chapterNames = ['Input', 'Assistance', 'Operation', 'Output', 'Evaluation'];
const planar = { planar: true, interactiveProjection: true };
const defaultControls = {
  tier: 'lite' as 'lite' | 'standard',
  format: 'declared' as 'declared' | 'checked',
  rule: 'raw',
  shown: false,
};

function Geometry({ view }: { view: RestorationView }) {
  return (
    <div
      className={styles.geometry}
      aria-label="Symbolic input and output contracts; no image data"
    >
      <div className={styles.gridCard} data-asset-role="input-contract">
        <span>01 / REQUIRED INPUT</span>
        <div className={styles.grid} aria-hidden="true" />
        <strong>{view.geometry.input}</strong>
        <small>Exact input absent</small>
      </div>
      <div className={styles.mapping}>
        <span aria-hidden="true">→</span>
        <strong>{view.geometry.mapping}</strong>
      </div>
      <div className={styles.gridCard} data-asset-role="output-contract">
        <span>02 / REQUIRED OUTPUT</span>
        <div className={styles.grid} aria-hidden="true" />
        <strong>{view.geometry.output}</strong>
        <small>Prediction unset</small>
      </div>
      <p className={styles.geometryNote}>{view.geometry.caution}</p>
    </div>
  );
}

function Protocol({
  view,
  plan,
  scene,
  frame,
  beat,
  progress,
  seek,
}: {
  view: RestorationView;
  plan: StoryPlan;
  scene: string;
  frame: number;
  beat: string;
  progress: number;
  seek: (frame: number) => void;
}) {
  const [controls, setControls] = useState(defaultControls);
  const previous = useRef({ frame, beat });
  const id = useId();
  const stable = previous.current.beat === beat && frame >= previous.current.frame;
  const current = stable ? controls : defaultControls;
  useLayoutEffect(() => {
    if (previous.current.beat !== beat || frame < previous.current.frame)
      setControls(defaultControls);
    previous.current = { frame, beat };
  }, [frame, beat]);
  const index = operationIndex(progress, view.operation.steps.length);
  const select = (change: Partial<typeof controls>) => setControls({ ...current, ...change });
  return (
    <section
      className={styles.protocol}
      data-restoration-stage={scene}
      data-restoration-currentstep={scene === 'operation' ? index : undefined}
    >
      {scene === 'input' ? (
        <>
          <h4>Know what the grid means</h4>
          <p>{view.source.input}</p>
          <p>{view.source.units}</p>
        </>
      ) : scene === 'helper' ? (
        <>
          <h4>What assistance changes</h4>
          <div className={styles.choices} role="group" aria-label="Assistance tier">
            {(['lite', 'standard'] as const).map((tier) => (
              <button
                key={tier}
                aria-pressed={current.tier === tier}
                onClick={() => select({ tier })}
              >
                {tier === 'lite' ? 'Lite' : 'Standard'}
              </button>
            ))}
          </div>
          <p>{view.helper[current.tier]}</p>
          <p>{view.helper.window}</p>
        </>
      ) : scene === 'operation' ? (
        <>
          <h4>Follow the protocol</h4>
          <ol className={styles.operations}>
            {view.operation.steps.map((step, i) => (
              <li key={step}>
                <button
                  data-restoration-step={i}
                  aria-pressed={i === index}
                  onClick={() => seek(operationFrame(plan, i, view.operation.steps.length))}
                >
                  <span>{i + 1}</span>
                  {step}
                </button>
              </li>
            ))}
          </ol>
          <p>
            {
              [
                view.helper.window,
                view.helper.lite,
                view.geometry.operation_note,
                view.output.format,
              ][index]
            }
          </p>
          <p className={styles.small}>{view.operation.limitations}</p>
        </>
      ) : scene === 'output' ? (
        <>
          <h4>Define a valid submission</h4>
          <code>{view.output.path}</code>
          <button
            className={styles.reveal}
            aria-expanded={current.shown}
            aria-controls={id}
            onClick={() => select({ shown: !current.shown })}
          >
            Inspect format contract
          </button>
          {current.shown && (
            <div id={id}>
              <div className={styles.choices} role="group" aria-label="Format rules">
                {(['declared', 'checked'] as const).map((format) => (
                  <button
                    key={format}
                    aria-pressed={current.format === format}
                    onClick={() => select({ format })}
                  >
                    {format === 'declared' ? 'Requested' : 'Actually checked'}
                  </button>
                ))}
              </div>
              <p>{view.geometry[current.format]}</p>
              <p>{view.output.format}</p>
              <p>{view.output.coverage}</p>
            </div>
          )}
          <p className={styles.status}>Prediction unset · score unset</p>
        </>
      ) : (
        <>
          <h4>Read the scoring boundary</h4>
          <p>{view.output.boundary}</p>
          <button
            className={styles.reveal}
            aria-expanded={current.shown}
            aria-controls={id}
            onClick={() => select({ shown: !current.shown })}
          >
            Reveal source metric rules
          </button>
          {current.shown && (
            <div id={id}>
              <div className={styles.choices} role="group" aria-label="Metric rule">
                {Object.keys(view.output.rules).map((rule) => (
                  <button
                    key={rule}
                    aria-pressed={current.rule === rule}
                    onClick={() => select({ rule })}
                  >
                    {rule}
                  </button>
                ))}
              </div>
              <p>{view.output.rules[current.rule]}</p>
            </div>
          )}
          <p className={styles.small}>Public scoring rules only. Private targets remain absent.</p>
        </>
      )}
    </section>
  );
}

function Evidence({ view, plan }: { view: RestorationView; plan: StoryPlan }) {
  return (
    <details className={styles.evidence} data-reader-evidence>
      <summary>
        Evidence & methods <span>Sources, units, limitations and full transcript</span>
      </summary>
      <div className={styles.evidenceBody}>
        <section>
          <h4>Source boundary</h4>
          <p>{view.source.simulation}</p>
          <p>{view.source.excluded}</p>
          <p>{view.helper.source_claims}</p>
          <p>{view.output.boundary}</p>
          <a href={view.source.notice.url} target="_blank" rel="noopener noreferrer">
            {view.source.notice.link_label} ↗
          </a>
        </section>
        <section>
          <h4>Artifact provenance</h4>
          <dl>
            <dt>Evidence basis</dt>
            <dd>Symbolic protocol; no patient pixels</dd>
            <dt>Declared units</dt>
            <dd>{view.bundle.units}</dd>
            <dt>Coordinate claim</dt>
            <dd>{view.bundle.coordinates}</dd>
            <dt>License</dt>
            <dd>{view.bundle.license}</dd>
          </dl>
          <details>
            <summary>Selected files and SHA-256 hashes</summary>
            <p>{view.bundle.notice}</p>
            <p>{view.bundle.license_text}</p>
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
          </details>
        </section>
        <section className={styles.transcript}>
          <h4>Transcript · English source</h4>
          {plan.beats.map((beat, index) => (
            <section key={beat.id}>
              <h5>
                {String(index + 1).padStart(2, '0')} / {beat.caption}
              </h5>
              <p>{beat.narration}</p>
            </section>
          ))}
        </section>
      </div>
    </details>
  );
}

/** Three comparison layouts, one default shell and one canonical frame/player contract. */
export function RestorationReader({ entry, plan, view, capture, captureReady }: ReaderProps) {
  if (!plan || !view) throw new Error('Restoration requires a compiled plan and asset view');
  const player = useFramePlayer(entry, plan, planar);
  const { t, locale } = useLocale();
  const params = new URLSearchParams(location.search);
  const captureMode = params.has('capture');
  const requested = params.get('layout') as Variant;
  const [variant, setVariant] = useState<Variant>(
    !captureMode && variants.includes(requested) ? requested : 'guided',
  );
  const state = player.storyState!;
  if (!('progress' in state) || !('scene' in state)) throw new Error('Invalid restoration state');
  useLayoutEffect(() => {
    if (capture) capture.current = player.actions.current;
    if (player.root.current?.dataset.rendered === 'true') captureReady?.(!!player.actions.current);
    return () => {
      if (capture) capture.current = null;
    };
  });
  const seek = (frame: number) => player.actions.current?.seekFrame(frame);
  const chooseVariant = (next: Variant) => {
    setVariant(next);
    const url = new URL(location.href);
    url.searchParams.set('layout', next);
    history.replaceState(null, '', url);
  };
  return (
    <div
      className={`scene-player ${styles.reader}`}
      ref={player.root}
      data-reader-variant={variant}
      data-recipe={plan.recipe}
      data-scene={entry.illustration.kind}
      data-family={view.family}
      data-beat={state.beatId}
      data-committed-frame={state.frame}
      data-playing={String(player.playing)}
      lang="en"
    >
      {params.has('review') && !captureMode && (
        <nav className={styles.variants} aria-label="Reader design comparison">
          <strong>Reader designs</strong>
          {variants.map((name) => (
            <button key={name} aria-pressed={variant === name} onClick={() => chooseVariant(name)}>
              {name[0].toUpperCase() + name.slice(1)}
            </button>
          ))}
        </nav>
      )}
      <header className={styles.heading}>
        <div className={styles.eyebrow}>
          {view.label} <span>Restoration / Task walkthrough</span>
        </div>
        <h3>{plan.title}</h3>
        <p>{plan.scope}</p>
      </header>
      <aside className={styles.boundary} data-symbolic-source-warning>
        <span>Evidence boundary</span>
        <strong>{view.source.notice.label}</strong>
        <p>{view.source.notice.text}</p>
      </aside>
      {locale === 'zh-CN' && (
        <p className={`scene-language-note ${styles.small}`} lang="zh-CN">
          示意图细节保留英文原文。
        </p>
      )}
      <div className={styles.walkthrough}>
        <nav className={styles.chapters} aria-label={t('Illustration stage')}>
          {plan.beats.map((beat, index) => (
            <button
              key={beat.id}
              data-story-step={index}
              data-scene-step={index}
              aria-pressed={state.index === index}
              aria-label={`${index + 1}. ${beat.caption}`}
              onClick={() => player.actions.current?.selectBeat(index)}
            >
              <span>{String(index + 1).padStart(2, '0')}</span>
              <strong>{chapterNames[index]}</strong>
            </button>
          ))}
        </nav>
        <section className={styles.chapter}>
          <header className={styles.chapterHeading}>
            <span>
              {String(state.index + 1).padStart(2, '0')} /{' '}
              {String(plan.beats.length).padStart(2, '0')} · {chapterNames[state.index]}
            </span>
            <h4 data-scene-title>{state.caption}</h4>
            <p>{state.narration}</p>
          </header>
          <div className={`scene-stage ${styles.stage}`}>
            <Geometry view={view} />
            <Protocol
              key={player.resetRevision}
              view={view}
              plan={plan}
              scene={state.scene}
              frame={state.frame}
              beat={state.beatId}
              progress={state.progress}
              seek={seek}
            />
          </div>
          <div className="scene-annotations" ref={player.annotations} aria-hidden="true" />
        </section>
      </div>
      <footer className={styles.transport}>
        <div>
          <button
            disabled={state.index === 0}
            onClick={() => player.actions.current?.selectBeat(state.index - 1)}
          >
            ← Previous
          </button>
          <button
            className={styles.next}
            disabled={state.index === plan.beats.length - 1}
            onClick={() => player.actions.current?.selectBeat(state.index + 1)}
          >
            Next chapter →
          </button>
        </div>
        <div>
          <button
            className="scene-play"
            onClick={() => player.actions.current?.toggle()}
            aria-label={t(player.playing ? 'Pause animation' : 'Play animation')}
          >
            {t(player.playing ? 'Pause' : 'Play')}
          </button>
          <button
            className="scene-reset"
            aria-label={t('Reset illustration view')}
            onClick={() => player.actions.current?.reset()}
          >
            {t('Reset')}
          </button>
          <span>
            {Math.floor(state.frame / plan.fps)} / {Math.round(plan.durationFrames / plan.fps)} s
          </span>
        </div>
      </footer>
      <Evidence key={player.resetRevision} view={view} plan={plan} />
    </div>
  );
}
