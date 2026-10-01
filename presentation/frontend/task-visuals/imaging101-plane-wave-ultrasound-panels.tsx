import { useLayoutEffect, useRef, useState } from 'react';
import {
  source,
  reference,
  fixture,
  fibersImage,
  cystsImage,
  steps,
  branches,
  operationIndex,
  branchIndex,
  operationFrame,
  referenceVisible,
  type ImagingPlaneWaveState,
} from './imaging101-plane-wave-ultrasound';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './imaging101-plane-wave-ultrasound.module.css';
function Trace({ m }: { m: number }) {
  const p = source.native_profiles.profiles[m],
    n = p.values.length,
    last = (p.t0_seconds + (n - 1) * source.native_profiles.dt_seconds) * 1e6;
  return (
    <figure className={css.native}>
      <svg
        viewBox="0 0 270 165"
        role="img"
        aria-label={`Native raw ADC trace ${branches[m]}; no envelope or B-mode`}
      >
        <path d="M14 8V148H258" stroke="#657984" fill="none" />
        <line
          x1="14"
          x2="258"
          y1={148 - (p.global_mean * 140) / 255}
          y2={148 - (p.global_mean * 140) / 255}
          stroke="#b2c2ce"
        />
        <polyline
          points={p.values
            .map((v, j) => `${14 + (j * 244) / (n - 1)},${148 - (v * 140) / 255}`)
            .join(' ')}
          stroke="#57d1cc"
          strokeWidth="1"
          fill="none"
        />
        <text x="17" y="17" fill="#dfeef3" fontSize="10">
          ADC 0–255
        </text>
        <text x="152" y="161" fill="#dfeef3" fontSize="10">
          {(p.t0_seconds * 1e6).toFixed(0)}–{last.toFixed(2)} µs →
        </text>
      </svg>
      <figcaption>
        Teal: {n.toLocaleString('en-US')} untouched samples, element 63, {branches[m]}. Gray: global
        mean {p.global_mean.toFixed(3)}.
      </figcaption>
    </figure>
  );
}
export function ImagingPlaneWaveScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: ImagingPlaneWaveState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const [showRules, setShowRules] = useState(false);
  const previousFrame = useRef(state.frame);
  const previousBeat = useRef(state.beatId);
  const stable =
    state.scene === 'reference' &&
    previousBeat.current === state.beatId &&
    state.frame >= previousFrame.current;
  useLayoutEffect(() => {
    if (!stable) setShowRules(false);
    previousFrame.current = state.frame;
    previousBeat.current = state.beatId;
  }, [state.frame, state.scene, state.beatId, stable]);
  const i = operationIndex(state),
    m = branchIndex(state);
  return (
    <section
      className={css.scene}
      data-imaging-plane-wave-scene={state.scene}
      data-imaging-plane-wave-operation-step={state.scene === 'operation' ? i : undefined}
    >
      {state.scene === 'input' && (
        <>
          <h3>Physical phantom RF; focused image absent</h3>
          <div className={css.two}>
            {[
              [fibersImage, 'Fibers: 336 time rows, t₀ = 0 µs'],
              [cystsImage, 'Cysts: 192 time rows, t₀ = 50 µs'],
            ].map(([src, label]) => (
              <figure className={css.native} key={label}>
                <img src={src} alt={`${label}; raw ADC time/element sheet, not B-mode`} />
                <figcaption>
                  {label}. 128 element columns, 0°; every eighth native time sample. Black 0 → white
                  255: raw ADC code.
                </figcaption>
              </figure>
            ))}
          </div>
          <p>
            128 elements · 7 angles · 20 MHz. Display stride only; no DC subtraction, envelope or
            beamforming.
          </p>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Separate RF phase from focused display intensity</h3>
          <nav className={css.controls} aria-label="Plane-wave steps">
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
                <b>Real ADC → global DC removal → per-angle migration</b>
                <p>
                  c = 1,540 m/s; 298 µm pitch; angles −1.5°…+1.5°. Fibers t₀ = 0; cysts t₀ = 50 µs.
                  Raw RF is not IQ.
                </p>
                <small>
                  Source depth grid uses c / (2fs), 38.5 µm steps, relative to acquisition start. t₀
                  compensation does not add an absolute depth label.
                </small>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Select native RF trace">
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
                <Trace m={m} />
              </>
            ) : (
              <>
                <b>mean(complex migrated angles) → envelope → power gamma</b>
                <p>
                  ERM at 0° uses c/√2, while README says c/2. Signed steering and linear Stolt
                  interpolation precede compounding. Hilbert(real(compound)); gamma 0.7 fibers / 0.5
                  cysts.
                </p>
                <small>
                  Authored +1 and −1 average to 0; mean magnitudes = {fixture.toy_mean_envelopes}.
                  Phase fixture only. No FFT, Hilbert, migration or result computed.
                </small>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Actual reconstruction.npy absent</h3>
          <code>output/reconstruction.npy · one phantom shape</code>
          <p>
            Fibers 2,688 × 128 or cysts 1,536 × 128. No participant B-mode, aggregate verdict, FWHM
            or CNR.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Later baseline and generic binding rules</h3>
          <button
            type="button"
            aria-expanded={stable && showRules}
            aria-controls="plane-wave-reader-rules"
            disabled={state.reference <= 0.5}
            onClick={() => setShowRules(!showRules)}
          >
            {stable && showRules ? 'Hide source rules' : 'Reveal source rules'}
          </button>
          {referenceVisible(state, stable && showRules) ? (
            <div
              id="plane-wave-reader-rules"
              className={css.socket}
              data-imaging-plane-wave-reference-revealed
            >
              <b>{reference.role}</b>
              <p>
                Baselines are solver-visible source arrays, differ from saved B-mode, and are not
                anatomical truth. Pixel denominators: 344,064 fibers / 196,608 cysts.
              </p>
              <small>
                Source centered NCC differs from generic cosine; per-phantom threshold names do not
                bind generic keys. Baseline / output images and scores absent. Exit / backward /
                reset covers rules.
              </small>
            </div>
          ) : (
            <p>Reader rules covered; baseline/output images absent.</p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Resolve selected condition and original-data rights</h3>
          <p>{source.actual_data_gap}</p>
          <small>
            Physical phantoms are not patients; no focused tissue finding or numerical performance.
          </small>
        </>
      )}
    </section>
  );
}
export function ImagingPlaneWaveOutput({ state }: { state: ImagingPlaneWaveState }) {
  return (
    <aside
      data-imaging-plane-wave-output={state.scene}
      className={`${shared.storyOutput} ${css.output}`}
    >
      <b>Actual RF; B-mode absent</b>
      <p>Native phantom ADC subsets and full traces.</p>
      <p>
        Participant image / score empty; selected reference and original-data rights unresolved.
      </p>
      <small>
        Reader rules require an explicit late reveal; backward / exit / reset covers them.
      </small>
    </aside>
  );
}
