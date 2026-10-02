import { useLayoutEffect, useRef, useState } from 'react';
import type { StoryPlan } from '../contracts.generated';
import {
  automedTotalsegmentatorCtsrPack as pack,
  operationIndex,
  operationFrame,
  resetOnBackward,
  formatRequirement,
  type AutomedTotalsegmentatorCtsrState,
} from './automed-totalsegmentator-ctsr';
import styles from './automed-totalsegmentator-ctsr.module.css';
export function AutomedTotalsegmentatorCtsrScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedTotalsegmentatorCtsrState;
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
      data-totalseg-stage={state.scene}
      data-totalseg-currentstep={state.scene === 'operation' ? index : undefined}
    >
      <h3>
        {state.scene === 'input'
          ? 'Same-grid TotalSegmentator without native pixels'
          : state.scene === 'helper'
            ? 'Prescribed pretrained CT-SR guidance'
            : state.scene === 'operation'
              ? pack.operation.steps[index]
              : state.scene === 'output'
                ? 'Required artifact, still unsubmitted'
                : 'Inspect scoring rules; references absent'}
      </h3>
      <div className={styles.columns}>
        <div className={styles.socket}>
          <div className={styles.empty}>
            <strong>Degraded CT grid</strong>
            <span>Required input · absent</span>
          </div>
          <span>↓ restore detail · grid size retained</span>
          <div className={styles.empty}>
            <strong>Restored same grid</strong>
            <span>Required output · unset</span>
          </div>
          <span>Same-grid sockets · no anatomy or restored voxels</span>
          <code>ct.nii.gz → sct.nii.gz</code>
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
                    data-totalseg-step={i}
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
                      ? 'Restore the same public/target grid. x4 through-plane degradation does not require fourfold output expansion. Preserve HU/affine/header; none verified here.'
                      : pack.output.format}
              </p>
              <p>{pack.operation.limitations}</p>
            </>
          ) : state.scene === 'output' ? (
            <>
              <code className={styles.path}>{pack.output.path}</code>
              <button
                aria-expanded={visible}
                aria-controls="totalseg-format-rules"
                onClick={() => setShown(!shown)}
              >
                Inspect format contract
              </button>
              {visible && (
                <div id="totalseg-format-rules">
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
                aria-controls="totalseg-metric-rules"
                onClick={() => setShown(!shown)}
              >
                Reveal source metric rules
              </button>
              {visible && (
                <div id="totalseg-metric-rules">
                  <div className={styles.buttons}>
                    {(['raw', 'ssim', 'rating', 'completion', 'workflow'] as const).map((r) => (
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
export function AutomedTotalsegmentatorCtsrOutput({
  state,
}: {
  state: AutomedTotalsegmentatorCtsrState;
}) {
  return (
    <aside className={styles.sidebar} data-totalseg-output="absent">
      <h3>Unsubmitted TotalSegmentator artifact</h3>
      <code className={styles.path}>{pack.output.path}</code>
      <p>HU declared · no actual volume, target or output.</p>
      <p>
        {state.scene === 'input'
          ? 'No selected TotalSegmentator case, executed degradation or upstream equivalence.'
          : state.scene === 'helper'
            ? pack.helper.source_claims
            : 'Format, metric agreement and 0–1 proxy fields do not establish clinical accuracy.'}
      </p>
      <p className={styles.caution}>No private CT target or measured restoration performance.</p>
    </aside>
  );
}
