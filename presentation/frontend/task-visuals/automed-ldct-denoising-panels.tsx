import { useLayoutEffect, useRef, useState } from 'react';
import type { StoryPlan } from '../contracts.generated';
import {
  automedLdctDenoisingPack as pack,
  operationIndex,
  operationFrame,
  resetOnBackward,
  formatRequirement,
  type AutomedLdctDenoisingState,
} from './automed-ldct-denoising';
import styles from './automed-ldct-denoising.module.css';
export function AutomedLdctDenoisingScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedLdctDenoisingState;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  const [tier, setTier] = useState<'lite' | 'standard'>('lite');
  const [shown, setShown] = useState(false);
  const [format, setFormat] = useState<'declared' | 'checked'>('declared');
  const [rule, setRule] = useState<keyof typeof pack.output.rules>('raw');
  const previous = useRef({ frame: state.frame, beat: state.beatId });
  useLayoutEffect(() => {
    if (
      previous.current.beat !== state.beatId ||
      resetOnBackward(previous.current.frame, state.frame)
    ) {
      setShown(false);
      setTier('lite');
      setFormat('declared');
      setRule('raw');
    }
    previous.current = { frame: state.frame, beat: state.beatId };
  }, [state.frame, state.beatId]);
  const stable =
    previous.current.beat === state.beatId && !resetOnBackward(previous.current.frame, state.frame);
  const visible = shown && stable;
  const activeTier = stable ? tier : 'lite';
  const activeFormat = stable ? format : 'declared';
  const activeRule = stable ? rule : 'raw';
  const index = operationIndex(state.progress);
  return (
    <div
      className={styles.scene}
      data-ldct-stage={state.scene}
      data-ldct-currentstep={state.scene === 'operation' ? index : undefined}
    >
      <h3>
        {state.scene === 'input'
          ? 'HU input without patient pixels'
          : state.scene === 'helper'
            ? 'Inference-only method guidance'
            : state.scene === 'operation'
              ? pack.operation.steps[index]
              : state.scene === 'output'
                ? 'Required artifact, still unsubmitted'
                : 'Inspect scoring rules; references absent'}
      </h3>
      <div className={styles.columns}>
        <div className={styles.socket}>
          <strong>512 × 512 CT array socket</strong>
          <span>No anatomy, noise realization or enhanced pixels</span>
          <code>input.npy → enhanced.npy</code>
        </div>
        <div className={styles.card}>
          {state.scene === 'input' ? (
            <>
              <p>{pack.source.input}</p>
              <p>{pack.source.units}</p>
              <p>{pack.source.simulation}</p>
            </>
          ) : state.scene === 'helper' ? (
            <>
              <div className={styles.buttons}>
                {(['lite', 'standard'] as const).map((t) => (
                  <button key={t} aria-pressed={activeTier === t} onClick={() => setTier(t)}>
                    {t}
                  </button>
                ))}
              </div>
              <p>{pack.helper[activeTier]}</p>
              <p>{pack.helper.window}</p>
            </>
          ) : state.scene === 'operation' ? (
            <>
              <div className={styles.buttons}>
                {pack.operation.steps.map((s, i) => (
                  <button
                    key={s}
                    data-ldct-step={i}
                    aria-pressed={i === index}
                    disabled={!onSeekFrame}
                    onClick={() => onSeekFrame?.(operationFrame(plan, i))}
                  >
                    {i + 1}. {s}
                  </button>
                ))}
              </div>
              <p>
                {index === 0
                  ? pack.helper.window
                  : index === 1
                    ? pack.helper.lite
                    : index === 2
                      ? 'Invert the chosen mapping into HU; clipping and model output are unverified.'
                      : pack.output.format}
              </p>
              <p>{pack.operation.limitations}</p>
            </>
          ) : state.scene === 'output' ? (
            <>
              <code className={styles.path}>{pack.output.path}</code>
              <button
                aria-expanded={visible}
                aria-controls="ldct-format-rules"
                onClick={() => setShown(!shown)}
              >
                Inspect format contract
              </button>
              {visible && (
                <div id="ldct-format-rules">
                  <div className={styles.buttons}>
                    {(['declared', 'checked'] as const).map((f) => (
                      <button
                        key={f}
                        aria-pressed={activeFormat === f}
                        onClick={() => setFormat(f)}
                      >
                        {f}
                      </button>
                    ))}
                  </div>
                  <p>{formatRequirement(activeFormat)}</p>
                  <p>{pack.output.coverage}</p>
                </div>
              )}
              <div className={styles.empty}>Prediction = unset · score = unset</div>
            </>
          ) : (
            <>
              <button
                aria-expanded={visible}
                aria-controls="ldct-metric-rules"
                onClick={() => setShown(!shown)}
              >
                Reveal source metric rules
              </button>
              {visible && (
                <div id="ldct-metric-rules">
                  <div className={styles.buttons}>
                    {(['raw', 'lpips', 'rating', 'normalization', 'pass'] as const).map((r) => (
                      <button key={r} aria-pressed={activeRule === r} onClick={() => setRule(r)}>
                        {r}
                      </button>
                    ))}
                  </div>
                  <p>{pack.output.rules[activeRule]}</p>
                </div>
              )}
              <p>{pack.output.boundary}</p>
            </>
          )}
        </div>
      </div>
      <p className={styles.caution}>
        {pack.source.excluded} Reader controls expose mechanics only; private targets never appear.
      </p>
    </div>
  );
}
export function AutomedLdctDenoisingOutput({ state }: { state: AutomedLdctDenoisingState }) {
  return (
    <aside className={styles.sidebar} data-ldct-output="absent">
      <h3>Unsubmitted CT artifact</h3>
      <code className={styles.path}>{pack.output.path}</code>
      <p>HU declared · no actual data range, case count or output.</p>
      <p>
        {state.scene === 'input'
          ? 'No staged noisy-clean selection or upstream equivalence.'
          : state.scene === 'helper'
            ? pack.helper.source_claims
            : 'Format, metric agreement and 0–1 normalized fields do not establish clinical accuracy.'}
      </p>
      <p className={styles.caution}>No private reference or measured denoising performance.</p>
    </aside>
  );
}
