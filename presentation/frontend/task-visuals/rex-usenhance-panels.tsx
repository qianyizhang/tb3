import { useLayoutEffect, useRef, useState } from 'react';
import {
  rexUsenhancePack as pack,
  type RexUsenhanceState as State,
  operationFrame,
  operationIndex,
  canonicalRule,
  resetOnBackward,
} from './rex-usenhance';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './rex-usenhance.module.css';
const titles = {
  input: 'Missing native low/high pair · symbolic sockets',
  helper: 'Training helpers versus private high-quality test',
  operation: 'Pair, develop, infer and submit · no execution',
  output: 'Enhanced PNGs and CSV remain unset',
  limits: 'Image metrics and rank mechanics',
} as const;
function useReset(state: State, reset: () => void) {
  const prev = useRef(state.frame);
  useLayoutEffect(() => {
    if (resetOnBackward(prev.current, state.frame)) reset();
    prev.current = state.frame;
  }, [state.frame, reset]);
}
function Socket({
  title,
  kind = 'input',
}: {
  title: string;
  kind?: 'input' | 'output' | 'private';
}) {
  return (
    <div
      className={css.socket}
      style={{
        borderColor: kind === 'input' ? '#91a6ae' : kind === 'output' ? '#18c6d4' : '#7ba4b8',
      }}
    >
      <b>{title}</b>
      <span>Empty schematic socket · no ultrasound pixels or anatomy</span>
    </div>
  );
}
function Input() {
  return (
    <div className={css.columns} data-usenhance-input>
      <Socket title="Required low-quality source PNG" />
      <div className={css.card}>
        <b>Filename pairing is a protocol, not registered anatomy</b>
        <p>{pack.source.pairing}</p>
        <p>{pack.source.units}</p>
        <small>No native shape, spacing, patient join or frame correspondence acquired.</small>
      </div>
    </div>
  );
}
function Helper({ state }: { state: State }) {
  const [show, setShow] = useState(false);
  useReset(state, () => setShow(false));
  return (
    <div className={css.columns} data-usenhance-helper>
      <div className={css.card}>
        <b>Public training high-quality helper role</b>
        <p>No public training pair is acquired, so this reveal contains source roles only.</p>
        <button
          type="button"
          aria-expanded={show}
          aria-controls="usenhance-public-training-role"
          onClick={() => setShow(!show)}
        >
          {show ? 'Hide training role' : 'Reveal public training role'}
        </button>
        {show && (
          <div
            id="usenhance-public-training-role"
            className={css.card}
            data-usenhance-training-role
          >
            <p>{pack.helper.public_train}</p>
            <p>{pack.helper.rule}</p>
          </div>
        )}
        <small>
          Initially covered. Backward replay and chapter exit reset before paint. No private or
          native high-quality pixels.
        </small>
      </div>
      <div className={css.card}>
        <b>Private test reference stays outside teaching</b>
        <p>{pack.helper.public_test}</p>
        <p>{pack.helper.private_test}</p>
        <p>{pack.source.partition}</p>
      </div>
    </div>
  );
}
function Operation({
  state,
  plan,
  onSeekFrame,
}: {
  state: State;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  const [detail, setDetail] = useState(false);
  useReset(state, () => setDetail(false));
  return (
    <div data-usenhance-operation>
      <div className={css.buttons} role="group" aria-label="Canonical USEnhance workflow">
        {['Audit pairs / split', 'Develop method', 'Infer test lows', 'Submit PNG / CSV'].map(
          (s, i) => (
            <button
              key={s}
              type="button"
              data-usenhance-step={i}
              aria-pressed={operationIndex(state.progress) === i}
              onClick={() => onSeekFrame?.(operationFrame(plan, i))}
            >
              {i + 1}. {s}
            </button>
          ),
        )}
      </div>
      <div className={css.columns}>
        <div className={css.card}>
          <strong data-usenhance-currentstage>
            {pack.operation.steps[operationIndex(state.progress)]}
          </strong>
          <p>{pack.operation.limitations}</p>
          <button type="button" aria-expanded={detail} onClick={() => setDetail(!detail)}>
            Inspect method/runtime boundary
          </button>
          {detail && <p data-usenhance-method>{pack.helper.model}</p>}
        </div>
        <Socket kind="output" title="Participant enhanced image remains unsubmitted" />
      </div>
    </div>
  );
}
function Output({ state }: { state: State }) {
  const [detail, setDetail] = useState(false);
  useReset(state, () => setDetail(false));
  return (
    <div className={css.columns} data-usenhance-output-schema>
      <div className={css.card}>
        <b>{pack.output.path}</b>
        <code className={css.path}>{pack.output.columns.join(',')}</code>
        <div className={css.empty}>No case row · no enhanced PNG</div>
        <button type="button" aria-expanded={detail} onClick={() => setDetail(!detail)}>
          Inspect submission and geometry
        </button>
        {detail && (
          <div data-usenhance-format>
            <p>{pack.output.format}</p>
            <p>{pack.output.geometry}</p>
          </div>
        )}
        <small>Schema placeholders have no patient/image IDs or inferred pixel dimensions.</small>
      </div>
      <Socket kind="private" title="Private high-quality reference absent" />
    </div>
  );
}
function Limits({ state }: { state: State }) {
  const [show, setShow] = useState(false);
  const [rule, setRule] = useState<'lncc' | 'ssim_psnr' | 'rank' | 'fallback'>('lncc');
  useReset(state, () => {
    setShow(false);
    setRule('lncc');
  });
  return (
    <div data-usenhance-limits>
      <div className={css.columns}>
        <div className={css.card}>
          <b>Later public grading-mechanics reveal</b>
          <button
            type="button"
            aria-expanded={show}
            aria-controls="usenhance-grading-rule"
            onClick={() => setShow(!show)}
          >
            {show ? 'Hide grading mechanics' : 'Reveal grading mechanics'}
          </button>
          {show && (
            <div id="usenhance-grading-rule">
              <div className={css.buttons} role="group" aria-label="USEnhance scoring rule">
                {(['lncc', 'ssim_psnr', 'rank', 'fallback'] as const).map((r) => (
                  <button
                    key={r}
                    type="button"
                    aria-pressed={rule === r}
                    onClick={() => {
                      const v = canonicalRule(r);
                      if (v) setRule(v);
                    }}
                  >
                    {r.replaceAll('_', ' / ')}
                  </button>
                ))}
              </div>
              <p data-usenhance-rule>{pack.output.rules[rule]}</p>
            </div>
          )}
          <small>
            Rule text only; no actual/private metric, reference image or leaderboard outcome.
          </small>
        </div>
        <div className={css.card}>
          <b>Denominator and clinical limits</b>
          <p>{pack.output.coverage}</p>
          <strong className={css.caution}>{pack.output.boundary}</strong>
        </div>
      </div>
    </div>
  );
}
export function RexUsenhanceScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: State;
  plan: StoryPlan;
  onSeekFrame?: (frame: number) => void;
}) {
  return (
    <div className={css.scene} data-usenhance-scene={state.scene}>
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'input' ? (
        <Input key={state.beatId} />
      ) : state.scene === 'helper' ? (
        <Helper key={state.beatId} state={state} />
      ) : state.scene === 'operation' ? (
        <Operation key={state.beatId} state={state} plan={plan} onSeekFrame={onSeekFrame} />
      ) : state.scene === 'output' ? (
        <Output key={state.beatId} state={state} />
      ) : (
        <Limits key={state.beatId} state={state} />
      )}
    </div>
  );
}
export function RexUsenhanceOutput({ state }: { state: State }) {
  return (
    <aside className={`${shared.storyOutput} ${css.sidebar}`} data-usenhance-output>
      <span className={shared.storyEyebrow}>Image enhancement · unsubmitted</span>
      <h3>PNG images and CSV schema</h3>
      <code className={css.path}>submission.csv</code>
      <p>image_id, enhanced_image_path</p>
      <div className={css.empty}>Enhanced image, reference and score unset</div>
      <p>
        No exact low/high native pair, patient-level split or physical display calibration
        recovered.
      </p>
      <small>
        {state.scene === 'limits'
          ? 'LNCC/SSIM unitless, PSNR dB, rank lower-better; no universal fraction scale.'
          : 'Symbolic source protocol; no clinical finding or model outcome.'}
      </small>
    </aside>
  );
}
