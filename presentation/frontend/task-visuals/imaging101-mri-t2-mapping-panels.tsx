import { useLayoutEffect, useRef, useState } from 'react';
import {
  source,
  reference,
  fixture,
  echoImages,
  steps,
  branches,
  operationIndex,
  branchIndex,
  operationFrame,
  referenceVisible,
  type ImagingT2MappingState,
} from './imaging101-mri-t2-mapping';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './imaging101-mri-t2-mapping.module.css';
function Echo({ m }: { m: number }) {
  return (
    <figure className={css.native}>
      <img
        src={echoImages[m]}
        alt={`Actual synthetic magnitude image, ${branches[m]}; no fitted T2 map`}
      />
      <figcaption>
        Black→white: magnitude signal a.u., fixed 0–1 display; {branches[m]}. Native 256² cells; no
        fit.
      </figcaption>
    </figure>
  );
}
export function ImagingT2MappingScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingT2MappingState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const [showRules, setShowRules] = useState(false);
  const previous = useRef(state.frame);
  const previousBeat = useRef(state.beatId);
  const stable =
    state.scene === 'reference' &&
    previousBeat.current === state.beatId &&
    state.frame >= previous.current;
  useLayoutEffect(() => {
    if (!stable) setShowRules(false);
    previousBeat.current = state.beatId;
    previous.current = state.frame;
  }, [state.frame, state.scene, state.beatId, stable]);
  const i = operationIndex(state),
    m = branchIndex(state);
  return (
    <section
      className={css.scene}
      data-imaging-t2-mapping-scene={state.scene}
      data-imaging-t2-mapping-operation-step={state.scene === 'operation' ? i : undefined}
    >
      {state.scene === 'input' && (
        <>
          <h3>Actual synthetic echo; fitted map absent</h3>
          <div className={css.two}>
            <Echo m={0} />
            <div>
              <b>10 echoes · TE 10…100 ms ·256×256</b>
              <p>
                Magnitude signal a.u.; no complex/coil axis. Synthetic 220 mm FOV, no patient
                acquisition.
              </p>
              <small>
                Generic target ranking may choose M0 instead of T2. Truth mask solver-visible; no
                participant result.
              </small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Separate echo signal from a fitted parameter</h3>
          <nav className={css.controls} aria-label="T2 mapping steps">
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
                <b>S(TE)=M₀ exp(−TE/T₂), TE and T₂ in ms</b>
                <p>
                  Rician magnitude √((S+nᵣ)²+nᵢ²); σ=.02 per Gaussian channel. Positive
                  background/floor, not zero-mean magnitude noise.
                </p>
                <small>
                  Authored M₀=.8,T₂=80 ms, expected signal at 10/50/100 ms:{' '}
                  {fixture.toy_signal.map((v) => v.toFixed(3)).join(' / ')}; no native fit/noise
                  draw.
                </small>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Select native echo display">
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
                  <Echo m={m} />
                  <div>
                    <b>Same grayscale scale across echoes</b>
                    <p>
                      Indices 0/4/9 select TE 10/50/100 ms; no per-echo normalization, log or fitted
                      map.
                    </p>
                    <small>
                      Signal intensity is a.u.; T2 output is ms. Source background noise remains
                      visible; truth mask not applied to display.
                    </small>
                  </div>
                </div>
              </>
            ) : (
              <>
                <b>Log OLS versus signal-domain LM</b>
                <p>
                  log(max(S,1e−10)) unweighted OLS; T₂=−1/slope. Unweighted nonlinear LM 50 starts
                  from log fit, positivity/clipping and fallback on failure.
                </p>
                <small>
                  Doc weighted/unbiased claims not established by code. Source fits/metrics use
                  27,817 truth-mask pixels; outside stays 0. No fit/convergence/error measured.
                </small>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Actual T2 reconstruction.npy absent</h3>
          <code>output/reconstruction.npy ·256×256 ·intended ms</code>
          <p>
            Participant map/score empty. Saved source T2/M0 archives are separate; generic target
            ambiguity unresolved.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Later phantom and evaluator target rules</h3>
          <button
            type="button"
            aria-expanded={referenceVisible(state, stable && showRules)}
            aria-controls="t2-reader-rules"
            disabled={state.reference <= 0.5}
            onClick={() => setShowRules(!showRules)}
          >
            {stable && showRules ? 'Hide source rules' : 'Reveal source rules'}
          </button>
          {referenceVisible(state, stable && showRules) ? (
            <div
              id="t2-reader-rules"
              className={css.socket}
              data-imaging-t2-mapping-reference-revealed
            >
              <b>{reference.role}</b>
              <p>
                Source main T2: 27,817 masked pixels, 110 ms range. Generic: 65,536 pixels, no mask;
                alphabetical M0_map before T2_map.
              </p>
              <p>
                Source thresholds derive from masked T2 baseline; transferring them to unmasked M0
                is unresolved. No truth/fitted image or verdict.
              </p>
              <small>
                Source phantom parameters are solver-visible, never private or patient truth; reset
                covers rules.
              </small>
            </div>
          ) : (
            <p>Reader rules covered; truth/fit/output absent.</p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Resolve target, units and mask before scores</h3>
          <p>{source.actual_data_gap}</p>
          <small>
            Actual synthetic echo contrast is input evidence only. No fitted T2, statistical
            unbiasedness, model performance or clinical finding.
          </small>
        </>
      )}
    </section>
  );
}
export function ImagingT2MappingOutput({ state }: { state: ImagingT2MappingState }) {
  return (
    <aside
      data-imaging-t2-mapping-output={state.scene}
      className={`${shared.storyOutput} ${css.output}`}
    >
      <b>Synthetic magnitude echo contract</b>
      <p>Native echo previews; symbolic fit/noise rules.</p>
      <p>Generic M0/T2 target ambiguity. Participant map/score absent.</p>
      <small>Reader rules require an explicit late reveal; backward/exit/reset covers them.</small>
    </aside>
  );
}
