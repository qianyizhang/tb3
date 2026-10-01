import { useLayoutEffect, useRef, useState } from 'react';
import {
  upstreamSourceImage,
  source,
  reference,
  fixture,
  steps,
  branches,
  operationIndex,
  branchIndex,
  operationFrame,
  referenceVisible,
  resetReader,
  type AutomedLidcDenoiseState,
} from './automedbench-full-lidc-idri-denoising-task';
import type { StoryPlan } from '../contracts.generated';
import shared from './task-visual.module.css';
import css from './automedbench-full-lidc-idri-denoising-task.module.css';
function Grid() {
  return (
    <figure className={css.native}>
      <svg
        viewBox="0 0 330 100"
        role="img"
        aria-label="Authored normalized noisy two by two cells beside two by two unknown clean or denoised values; same geometry, not CT or a Gaussian realization"
      >
        {fixture.observed_grid.flat().map((v, i) => (
          <g key={`observed-${i}`}>
            <rect
              x={10 + (i % 2) * 40}
              y={8 + Math.floor(i / 2) * 40}
              width="38"
              height="38"
              fill={`rgb(20,${80 + Math.round(v * 120)},${110 + Math.round(v * 100)})`}
            />
            <text
              x={29 + (i % 2) * 40}
              y={32 + Math.floor(i / 2) * 40}
              fill="#fff"
              textAnchor="middle"
              fontSize="13"
            >
              {v}
            </text>
          </g>
        ))}
        <text x="120" y="53" fill="#e9f4f7" fontSize="13">
          unknown D
        </text>
        {Array.from({ length: 4 }, (_, i) => (
          <g key={`unknown-${i}`}>
            <rect
              x={230 + (i % 2) * 40}
              y={8 + Math.floor(i / 2) * 40}
              width="38"
              height="38"
              fill="none"
              stroke="#b1bccc"
            />
            <text
              x={249 + (i % 2) * 40}
              y={32 + Math.floor(i / 2) * 40}
              fill="#d8e4ee"
              textAnchor="middle"
              fontSize="14"
            >
              ?
            </text>
          </g>
        ))}
      </svg>
      <figcaption>
        Teal: authored noisy values; outline: unknown clean/output values. Same geometry. Not CT,
        random noise, private target or denoised result.
      </figcaption>
    </figure>
  );
}
export function AutomedLidcDenoiseScene({
  state,
  plan,
  onSeekFrame,
}: {
  state: AutomedLidcDenoiseState;
  plan: StoryPlan;
  onSeekFrame?: (f: number) => void;
}) {
  const [show, setShow] = useState(false);
  const previous = useRef({ frame: state.frame, beat: state.beatId });
  const stable = state.frame >= previous.current.frame && state.beatId === previous.current.beat;
  useLayoutEffect(() => {
    if (
      resetReader(previous.current.frame, state.frame, state.scene) ||
      state.beatId !== previous.current.beat
    )
      setShow(false);
    previous.current = { frame: state.frame, beat: state.beatId };
  }, [state.frame, state.scene]);
  const i = operationIndex(state),
    m = branchIndex(state);
  return (
    <section
      className={css.scene}
      data-automed-lidc-denoise-scene={state.scene}
      data-automed-lidc-denoise-operation-step={state.scene === 'operation' ? i : undefined}
    >
      {state.scene === 'input' && (
        <>
          <h3>Matching Full noisy CT / private clean target absent</h3>
          <div className={css.two}>
            <Grid />
            <div>
              <b>Declared 512 × 512 normalized CT</b>
              <p>
                262,144 pixels in and out; no Full native cases or split mapping recovered. Symbolic
                values only.
              </p>
              <small>
                σ = 0.05 normalized intensity, not HU, photon noise, dose fraction or real low-dose
                acquisition.
              </small>
            </div>
          </div>
        </>
      )}
      {state.scene === 'operation' && (
        <>
          <h3>Separate normalized noise from a denoising outcome</h3>
          <nav className={css.controls} aria-label="LIDC-IDRI steps">
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
                <b>Declared additive Gaussian σ = 0.05; variance = 0.0025</b>
                <p>
                  Normalization, seed, clipping, spatial correlation and exact mean specification
                  unavailable. No native noise draw.
                </p>
                <small>
                  Authored 0.98 + 0.05 = 1.03 illustrates range ambiguity; [0,1] requirement does
                  not establish a clipping rule or calibrated CT noise.
                </small>
              </>
            ) : i === 1 ? (
              <>
                <nav className={css.controls} aria-label="Select assistance or format rule">
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
                {m === 0 ? (
                  <>
                    <b>Full Lite: prescribed public pretrained DRUNet</b>
                    <p>
                      Document checkpoint, normalized preprocessing and σ = 0.05 mapping; validate
                      public input pilot, inference only.
                    </p>
                    <small>
                      No checkpoint loaded; exact model noise-conditioning convention and
                      lesion-detail preservation unverified.
                    </small>
                  </>
                ) : m === 1 ? (
                  <>
                    <b>Full Standard: ≥ 3 denoisers, ≥ 2 pretrained neural</b>
                    <p>
                      BM3D may be one classical baseline; DnCNN / Restormer / SwinIR candidates.
                      Choose from public evidence and pilot.
                    </p>
                    <small>
                      No private target access, training or benchmark performance. Related
                      Lite/gallery equivalence unresolved.
                    </small>
                  </>
                ) : (
                  <>
                    <b>Required float32, finite normalized 512 × 512</b>
                    <p>
                      Checker accepts any finite floating 2D private-reference shape, including
                      float64, copy, constant or out-of-range values.
                    </p>
                    <small>
                      Protocol validation is stricter; plural agents_outputs vs singular tier
                      wording retained. No checker or metric executed.
                    </small>
                  </>
                )}
              </>
            ) : (
              <>
                <Grid />
                <small>
                  Authored y = {fixture.toy_y} = 0.40 + 0.05 = 0.50 − 0.05. Clean value and D(y)
                  unknown; no denoised CT.
                </small>
              </>
            )}
          </div>
        </>
      )}
      {state.scene === 'output' && (
        <>
          <h3>Actual enhanced.npy absent</h3>
          <code>agents_outputs/&lt;case_id&gt;/enhanced.npy · 512 × 512</code>
          <p>
            Intended normalized float32. No submitted array, clean CT, inferred lesion boundaries,
            metric or rating.
          </p>
        </>
      )}
      {state.scene === 'reference' && (
        <>
          <h3>Later upstream helper; Full clean target absent</h3>
          <button
            type="button"
            className={css.revealButton}
            aria-expanded={show && stable}
            aria-controls="lidc-reader-source-example"
            onClick={() => setShow(!show)}
          >
            {show && stable ? 'Hide upstream helper' : 'Reveal upstream helper / rules'}
          </button>
          {referenceVisible(state, show && stable) ? (
            <div
              id="lidc-reader-source-example"
              className={css.socket}
              data-automed-lidc-denoise-reference-revealed
            >
              <div className={css.two}>
                <figure className={css.native}>
                  <img
                    data-automed-lidc-denoise-native
                    src={upstreamSourceImage}
                    alt="Upstream LIDC-IDRI source-example native CT slice with display window, not Full noisy or clean pair or denoised output"
                  />
                  <figcaption>
                    LIDC-IDRI-0003 · member 00000001 / Instance 80. Stride 4, C 40 / W 400
                    source-rescaled units grayscale; CC BY 3.0 / TCIA. No Full matching or clinical
                    noise claim.
                  </figcaption>
                </figure>
                <div>
                  <b>{reference.role}</b>
                  <small>
                    Native 512², signed-int16; rescaled = stored -1024, pixel spacing 0.820312 mm.
                    PNG 128² is a display sampling only, not Full normalized input or private clean
                    target. No noise draw or denoising.
                  </small>
                </div>
              </div>
              <p>
                Runner needs PSNR / SSIM / LPIPS; means drop NaNs independently. Format validity and
                scoring counts differ; case count unknown.
              </p>
              <small>
                LIDC-IDRI task absent named rating/normalization maps; do not borrow LDCT bands.
                Missing bands omit pass rate. “Clinical” code composite is not medical validation.
                Backward / exit / reset covers.
              </small>
            </div>
          ) : (
            <p>Reader-only evaluator rules covered; private clean image and output absent.</p>
          )}
        </>
      )}
      {state.scene === 'limits' && (
        <>
          <h3>Resolve matching data, noise lineage and evaluator assets</h3>
          <p>{source.actual_data_gap}</p>
          <small>
            No Full noise realization, model denoising, preserved lesion detail, clinical outcome or
            measured metric.
          </small>
        </>
      )}
    </section>
  );
}
export function AutomedLidcDenoiseOutput({ state }: { state: AutomedLidcDenoiseState }) {
  return (
    <aside
      data-automed-lidc-denoise-output={state.scene}
      className={`${shared.storyOutput} ${css.output}`}
    >
      <b>Symbolic noise; enhanced.npy empty</b>
      <p>Matching noisy input / private clean target absent.</p>
      <small>
        Reader-only helper requires explicit late reveal; backward / exit / reset covers. No private
        answer assets.
      </small>
    </aside>
  );
}
