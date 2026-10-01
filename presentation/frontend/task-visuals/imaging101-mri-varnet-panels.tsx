import { useLayoutEffect, useRef, useState } from 'react';
import {
  source,
  reference,
  fixture,
  coilImages,
  steps,
  branches,
  operationIndex,
  branchIndex,
  operationFrame,
  referenceVisible,
  type ImagingVarNetState,
} from './imaging101-mri-varnet';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './imaging101-mri-varnet.module.css';
function Coil({ m }: { m: number }) {
  return (
    <figure className={css.native}>
      <img
        src={coilImages[m]}
        alt={`Native k-space magnitude samples, ${branches[m]}; no spatial reconstruction`}
      />
      <figcaption>
        Gray: log-display |k|, fixed .006 ceiling; phase lost. Every fourth row/column, 160 × 92
        cells.
      </figcaption>
    </figure>
  );
}
function Mask() {
  return (
    <figure className={css.mask}>
      <svg
        viewBox="0 0 368 8"
        role="img"
        aria-label="Saved source equispaced mask; 113 of 368 columns with 29 central lines"
      >
        {source.native_mask.map((v, j) => (
          <rect key={j} x={j} y="0" width="1" height="8" fill={v ? '#57d1cc' : '#122939'} />
        ))}
      </svg>
      <figcaption>Teal: saved sampled columns; dark: missing. 113 / 368; ACS 29.</figcaption>
    </figure>
  );
}
export function ImagingVarNetScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingVarNetState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const [showRules, setShowRules] = useState(false);
  const previous = useRef(state.frame);
  useLayoutEffect(() => {
    if (state.scene !== 'reference' || state.frame < previous.current) setShowRules(false);
    previous.current = state.frame;
  }, [state.frame, state.scene]);
  const i = operationIndex(state),
    m = branchIndex(state);
  return (
    <section
      className={css.scene}
      data-imaging-varnet-scene={state.scene}
      data-imaging-varnet-operation-step={state.scene === 'operation' ? i : undefined}
    >
      {state.scene === 'input' && (
        <>
          <h3>Actual k-space preview; model result absent</h3>
          <div className={css.two}>
            <Coil m={0} />
            <div>
              <b>1 slice · 15 coils · 640 × 368 complex grid</b>
              <p>
                fastMRI-derived source, CORPD_FBK. Frequency-array indices, no anatomical or
                clinical image.
              </p>
              <small>
                Promised checkpoint absent; local research only. No FFT, model forward or
                reconstruction.
              </small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Keep the input and learned output separate</h3>
          <nav className={css.controls} aria-label="VarNet contract steps">
            {steps.map((s, j) => (
              <button
                key={s}
                type="button"
                aria-pressed={i === j}
                disabled={!onSeekFrame}
                onClick={() => onSeekFrame?.(operationFrame(plan, j, m))}
              >
                {s}
              </button>
            ))}
          </nav>
          <div className={css.socket}>
            {i === 0 ? (
              <>
                <b>y_c=M F(S_c x); centered orthonormal FFT</b>
                <p>
                  Complex-pair model input: 1 × 15 × 640 × 368 × 2. Sensitivity maps estimated by
                  external model, not supplied or computed here.
                </p>
                <small>
                  Authored hard-consistency example [3,4]→[{fixture.toy_consistent.join(',')}];
                  teaching arithmetic, not VarNet's learned/soft update.
                </small>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Select native k-space display coil">
                  {branches.map((s, j) => (
                    <button
                      key={s}
                      type="button"
                      aria-pressed={m === j}
                      disabled={!onSeekFrame}
                      onClick={() => onSeekFrame?.(operationFrame(plan, 1, j))}
                    >
                      {s}
                    </button>
                  ))}
                </nav>
                <div className={css.two}>
                  <Coil m={m} />
                  <div>
                    <b>Equispaced columns with random offset</b>
                    <Mask />
                    <small>
                      Saved offset 2; nominal R4 plus 29 ACS lines, effective 368 / 113≈3.257. This
                      is not a Bernoulli mask or a fresh model tensor.
                    </small>
                  </div>
                </div>
              </>
            ) : (
              <>
                <b>12-cascade constructor; checkpoint absent</b>
                <p>
                  Regularizer pools 4 / channels 18; sensitivity pools 4 / channels 8. External
                  fastMRI lower bound does not pin exact blocks or calibration schedule.
                </p>
                <small>
                  CPU / eval / no_grad declared; no forward. Intended output crop 320 × 320, starts
                  (160,24); no resize or image computed.
                </small>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Actual reconstruction.npy absent</h3>
          <code>output/reconstruction.npy ·320 × 320 magnitude</code>
          <p>
            Participant image / score empty. Saved source VarNet output has no recovered checkpoint
            or new execution lineage.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Later source RSS and evaluator rules</h3>
          <button
            type="button"
            aria-expanded={referenceVisible(state, showRules)}
            aria-controls="varnet-reader-rules"
            disabled={state.reference <= 0.5}
            onClick={() => setShowRules(!showRules)}
          >
            {showRules ? 'Hide source rules' : 'Reveal source rules'}
          </button>
          {referenceVisible(state, showRules) ? (
            <div
              id="varnet-reader-rules"
              className={css.socket}
              data-imaging-varnet-reference-revealed
            >
              <b>{reference.role}</b>
              <p>
                Source RSS image is solver-visible, no private clinical truth. No source or
                participant image shown.
              </p>
              <p>
                Generic magnitude comparison: 102,400 pixels; no scale normalization. Phase
                information is lost; NCC differs from range error.
              </p>
              <small>
                Source windowed SSIM differs from generic global SSIM; source averages lack pass
                boundary fields. Saved metrics are not current model evidence.
              </small>
            </div>
          ) : (
            <p>Reader rules covered; reference/output images absent.</p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Resolve checkpoint and rights before replay or sharing</h3>
          <p>{source.actual_data_gap}</p>
          <small>
            Native k-space previews are input evidence only. No reconstructed finding, learned
            outcome, performance or clinical inference.
          </small>
        </>
      )}
    </section>
  );
}
export function ImagingVarNetOutput({ state }: { state: ImagingVarNetState }) {
  return (
    <aside
      data-imaging-varnet-output={state.scene}
      className={`${shared.storyOutput} ${css.output}`}
    >
      <b>VarNet input contract</b>
      <p>Native frequency samples; symbolic model rules.</p>
      <p>Checkpoint absent. Participant reconstruction / score empty. Local research use only.</p>
      <small>
        Reader rules require an explicit late reveal; backward / exit / reset covers them.
      </small>
    </aside>
  );
}
