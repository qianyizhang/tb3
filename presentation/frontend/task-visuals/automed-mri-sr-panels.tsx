import { useLayoutEffect, useRef, useState } from 'react';
import type { StoryPlan } from '../contracts.generated';
import {
  automedMriSrPack as pack,
  operationIndex,
  operationFrame,
  resetOnBackward,
  formatRequirement,
  type AutomedMriSrState,
} from './automed-mri-sr';
import styles from './automed-mri-sr.module.css';
export function AutomedMriSrScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedMriSrState;
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
      data-mrisr-stage={state.scene}
      data-mrisr-currentstep={state.scene === 'operation' ? index : undefined}
    >
      <h3>
        {state.scene === 'input'
          ? 'Normalized MRI without native pixels'
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
          <div className={styles.empty}>
            <strong>360 × 256 LR</strong>
            <span>Required input · absent</span>
          </div>
          <span>↓ x2 per axis · symbolic grids</span>
          <div className={styles.empty}>
            <strong>720 × 512 HR</strong>
            <span>Required output · unset</span>
          </div>
          <span>Two grid sizes · no anatomy or reconstructed pixels</span>
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
                    data-mrisr-step={i}
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
                      ? 'Resolve 720×512 target; generic same-shape guidance conflicts. No resampling or model output produced.'
                      : pack.output.format}
              </p>
              <p>{pack.operation.limitations}</p>
            </>
          ) : state.scene === 'output' ? (
            <>
              <code className={styles.path}>{pack.output.path}</code>
              <button
                aria-expanded={visible}
                aria-controls="mrisr-format-rules"
                onClick={() => setShown(!shown)}
              >
                Inspect format contract
              </button>
              {visible && (
                <div id="mrisr-format-rules">
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
                aria-controls="mrisr-metric-rules"
                onClick={() => setShown(!shown)}
              >
                Reveal source metric rules
              </button>
              {visible && (
                <div id="mrisr-metric-rules">
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
export function AutomedMriSrOutput({ state }: { state: AutomedMriSrState }) {
  return (
    <aside className={styles.sidebar} data-mrisr-output="absent">
      <h3>Unsubmitted MRI SR artifact</h3>
      <code className={styles.path}>{pack.output.path}</code>
      <p>Normalized scale declared · no actual LR/HR or output.</p>
      <p>
        {state.scene === 'input'
          ? 'No selected fastMRI slice, degradation or upstream equivalence.'
          : state.scene === 'helper'
            ? pack.helper.source_claims
            : 'Format, metric agreement and 0–1 normalized fields do not establish clinical accuracy.'}
      </p>
      <p className={styles.caution}>No private HR or measured super-resolution performance.</p>
    </aside>
  );
}
