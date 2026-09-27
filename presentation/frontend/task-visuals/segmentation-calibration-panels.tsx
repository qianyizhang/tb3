import {
  calibrationSource as src,
  calibrationOutput as outputs,
  calibrationReference as refs,
  calibrationLabels as labels,
  calibrationColors as colors,
  calibrationSelection,
  calibrationPath,
  calibrationMetric,
  calibrationOrgans,
  type CalibrationState,
  type BoxCondition,
} from './segmentation-calibration';
import styles from './task-visual.module.css';
const f = (n: number, places = 3) => n.toFixed(places);
function Plane({
  sample,
  tag,
  condition = 'tight',
  reveal = false,
  box = false,
  full = false,
  filled = false,
}: {
  sample: string;
  tag?: string;
  condition?: BoxCondition;
  reveal?: boolean;
  box?: boolean;
  full?: boolean;
  filled?: boolean;
}) {
  const view = src.views[sample],
    [x0, y0, x1, y1] = full ? [0, 0, 265, 265] : view.detail_bounds_xyxy;
  const [bx, by, bx1, by1] = view.boxes[condition];
  const mask = tag ? outputs.views[sample][tag][condition] : undefined;
  return (
    <>
      <svg
        className={styles.calibrationImage}
        viewBox={`${x0} ${y0} ${x1 - x0} ${y1 - y0}`}
        role="img"
        aria-label={`${labels[view.organ]} native k ${view.slice_k}, ${tag ? labels[tag] : 'CT'}, ${condition} box${reveal ? ', reference revealed' : ''}`}
        data-calibration-view={sample}
        data-calibration-panel={tag ?? (filled ? 'rectangle' : 'ct')}
      >
        <image href={view.png} x="0" y="0" width="265" height="265" />
        {box && (
          <rect
            data-calibration-layer="box"
            x={bx}
            y={by}
            width={bx1 - bx}
            height={by1 - by}
            fill={filled ? colors.box : 'none'}
            fillOpacity={filled ? 0.25 : 0}
            stroke={colors.box}
            strokeWidth="1.3"
            strokeDasharray="2 2"
            vectorEffect="non-scaling-stroke"
          />
        )}
        {mask && (
          <path
            data-calibration-layer={tag}
            d={calibrationPath(mask)}
            fill="none"
            stroke={colors[tag!]}
            strokeWidth="1.4"
            vectorEffect="non-scaling-stroke"
          />
        )}
        {reveal && (
          <path
            data-calibration-layer="reference"
            d={calibrationPath(refs.views[sample])}
            fill="none"
            stroke={colors.reference}
            strokeWidth="1.4"
            strokeDasharray="4 3"
            vectorEffect="non-scaling-stroke"
          />
        )}
      </svg>
      <small>
        k={view.slice_k} · i [{x0},{x1}) · j [{y0},{y1}) · j↓
      </small>
    </>
  );
}
function Pair({
  sample,
  condition,
  reveal,
  output,
  box,
  backend = false,
}: {
  sample: string;
  condition: BoxCondition;
  reveal: boolean;
  output: boolean;
  box: boolean;
  backend?: boolean;
}) {
  return (
    <div className={styles.calibrationCards}>
      {(backend ? ['sam2-mps', 'sam2-cpu'] : ['sam2-mps', 'lite-mps']).map((tag) => (
        <article key={tag}>
          <b>{labels[tag]}</b>
          <Plane
            sample={sample}
            tag={output ? tag : undefined}
            condition={condition}
            reveal={reveal}
            box={box}
          />
          {output && reveal && (
            <small data-calibration-private>
              Dice {f(calibrationMetric(tag, sample, condition).dice)} · HD95{' '}
              {f(calibrationMetric(tag, sample, condition).hd95_mm, 1)} mm
            </small>
          )}
        </article>
      ))}
    </div>
  );
}
function MeanTable({ organ }: { organ?: string }) {
  const row = organ ? refs.per_organ.find((r) => r.organ === organ)! : undefined;
  const values = row
    ? [
        [row.sam2_tight, row.sam2_loose],
        [row.lite_tight, row.lite_loose],
      ]
    : ['sam2-mps', 'lite-mps'].map((tag) => [
        refs.aggregates[tag].tight.mean_dice,
        refs.aggregates[tag].loose.mean_dice,
      ]);
  return (
    <table className={styles.calibrationTable} data-calibration-private>
      <thead>
        <tr>
          <th>Mean 2D Dice</th>
          <th>Tight · +3 mm</th>
          <th>Loose · +15 mm</th>
        </tr>
      </thead>
      <tbody>
        {['sam2-mps', 'lite-mps'].map((tag, i) => (
          <tr key={tag}>
            <th>{labels[tag]}</th>
            <td>{f(values[i][0])}</td>
            <td>{f(values[i][1])}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
export function CalibrationScene({ state: s }: { state: CalibrationState }) {
  const v = calibrationSelection(s),
    view = src.views[v.sample];
  const parity = refs.backend_pairs.find(
    (r) => r.model === 'sam2' && r.id === v.sample && r.condition === v.condition,
  );
  return (
    <section
      className={styles.calibrationScene}
      data-calibration-scene={s.scene}
      data-calibration-reference={v.reveal ? 'visible' : 'hidden'}
      data-calibration-condition={v.condition}
    >
      {s.scene === 'inputs' ? (
        <>
          <h4>Full slices enter the tool</h4>
          <div className={styles.calibrationInput}>
            <article>
              <b>s1233 · native axial section</b>
              <Plane sample={v.sample} full />
            </article>
            <div className={styles.calibrationFacts}>
              <p>
                <strong>1 CT</strong>known public development case
              </p>
              <p>
                <strong>265 × 265</strong>full image per prompt · 1.5 mm pixels
              </p>
              <p>
                <strong>−160 to 240 HU</strong>uint8 grayscale in three RGB channels
              </p>
            </div>
          </div>
          <p>
            No output or dense reference is displayed. The protocol supplies reference-derived
            localization.
          </p>
        </>
      ) : s.scene === 'sampling' ? (
        <>
          <h4>Fixed slice selection comes from reference masks</h4>
          <div className={styles.calibrationInput}>
            <article>
              <b>Pancreas · q{view.q * 100}</b>
              <Plane sample={v.sample} full reveal={v.reveal} />
            </article>
            <table className={styles.calibrationTable}>
              <thead>
                <tr>
                  <th>Native k</th>
                  <th>q25</th>
                  <th>q50</th>
                  <th>q75</th>
                </tr>
              </thead>
              <tbody>
                {calibrationOrgans.map((o) => (
                  <tr key={o}>
                    <th>{labels[o]}</th>
                    {[25, 50, 75].map((q) => (
                      <td key={q}>{src.views[o + '_q' + q].slice_k}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p>
            Quantiles of each nonempty slice-index list; nearest-even rounding. Eighteen correlated
            organ/slice pairs ≠ eighteen patients.
          </p>
        </>
      ) : s.scene === 'boxes' ? (
        <>
          <h4>The same reference-derived rectangles go to both tools</h4>
          <div className={styles.calibrationCards}>
            {(['tight', 'loose'] as const).map((c) => (
              <article key={c}>
                <b>{c === 'tight' ? 'Tight · +2 px / 3 mm' : 'Loose · +10 px / 15 mm'}</b>
                <Plane sample={v.sample} condition={c} box={v.box} reveal={v.reveal} />
                <small>xyxy [{view.boxes[c].join(', ')}]</small>
              </article>
            ))}
          </div>
          <p>
            Half-open native coordinates; expansion is on every side. Dense reference and organ name
            are withheld from each model.
          </p>
        </>
      ) : s.scene === 'preprocess' ? (
        <>
          <h4>Shared native prompt; different internal transforms</h4>
          <div className={styles.calibrationFlow}>
            <article>
              <b>SAM 2.1 Small</b>
              <strong>265² → 1024²</strong>
              <p>Tensor resize and fixed channel normalization</p>
              <code>[{view.sam2_boxes_1024[v.condition].map((x) => f(x, 1)).join(', ')}]</code>
              <small>Box scales in floating point</small>
            </article>
            <article>
              <b>LiteMedSAM</b>
              <strong>265² → 256²</strong>
              <p>Area resize and per-image intensity normalization</p>
              <code>[{view.lite_boxes_256[v.condition].join(', ')}]</code>
              <small>Scaled box truncates to integers</small>
            </article>
          </div>
          <p>
            Native pancreas {v.condition} box: [{view.boxes[v.condition].join(', ')}]. One image
            embedding → two box decodes → native 265² Boolean masks. No extra component cleanup.
          </p>
        </>
      ) : ['outputs', 'reference', 'sensitivity', 'duodenum', 'backend'].includes(s.scene) ? (
        <>
          <h4>
            {s.scene === 'backend' ? 'SAM2 backend disagreement' : labels[view.organ]} ·{' '}
            {v.condition === 'tight' ? 'tight +3 mm' : 'loose +15 mm'} box · k={view.slice_k}
          </h4>
          <Pair
            sample={v.sample}
            condition={v.condition}
            reveal={v.reveal}
            output={v.output}
            box={v.box}
            backend={s.scene === 'backend'}
          />
          {s.scene === 'outputs' || s.scene === 'reference' ? (
            <p>
              {v.reveal ? (
                <span data-calibration-private>
                  Pancreas q50: reference agreement measures the mask after localization is
                  supplied. The same native pixels underlie both panels.
                </span>
              ) : (
                'Original saved MPS masks. Reference contours and accuracy measurements remain hidden.'
              )}
            </p>
          ) : s.scene === 'backend' ? (
            <p data-calibration-private={v.reveal ? true : undefined}>
              {v.reveal && parity ? (
                <>
                  CPU/MPS mask Dice <strong>{f(parity.cpu_mps_mask_dice, 4)}</strong> ·{' '}
                  {parity.differing_pixels.toLocaleString('en-US')} differing pixels.{' '}
                  {v.sample === 'liver_q25'
                    ? 'Worst pair selected after results; full CPU expansion was diagnostic.'
                    : 'Prespecified middle-adrenal check exposed the discrepancy.'}
                </>
              ) : (
                'Backend measurements hidden.'
              )}
            </p>
          ) : v.reveal ? (
            <>
              <p data-calibration-private>
                {s.scene === 'duodenum'
                  ? 'Separated reference regions; both wider-box masks include intervening tissue. No correction prompt was tried.'
                  : 'Table: all 3 fixed slices for this organ. Images: prespecified middle slice only.'}
              </p>
            </>
          ) : (
            <p>Reference measurements hidden.</p>
          )}
          <small>
            Reader crop includes all saved masks and both boxes. Inference used the full 265² slice;
            no interpolated masks.
          </small>
        </>
      ) : s.scene === 'controls' ? (
        <>
          <h4>How much overlap does the supplied rectangle provide?</h4>
          <div className={styles.calibrationCards}>
            {(['tight', 'loose'] as const).map((c) => (
              <article key={c}>
                <b>{c === 'tight' ? 'Tight rectangle' : 'Loose rectangle'}</b>
                <Plane sample={v.sample} condition={c} box={v.box} reveal={v.reveal} filled />
                <small>
                  {v.reveal && (
                    <span data-calibration-private>
                      18-sample mean Dice {f(refs.controls.filled_box_mean_dice[c])}
                    </span>
                  )}
                </small>
              </article>
            ))}
          </div>
          <p>
            {v.reveal && (
              <span data-calibration-private>
                Exact-reference Dice 1; empty-mask Dice 0 on all 18 nonempty references. Images
                illustrate one pancreas slice; means cover all samples.
              </span>
            )}
          </p>
        </>
      ) : s.scene === 'metrics' ? (
        <>
          <h4>Overlap and boundary distance answer different questions</h4>
          {v.reveal ? (
            <>
              <MeanTable />
              <table className={styles.calibrationTable} data-calibration-private>
                <thead>
                  <tr>
                    <th>Mean 2D HD95 · mm</th>
                    <th>Tight</th>
                    <th>Loose</th>
                  </tr>
                </thead>
                <tbody>
                  {['sam2-mps', 'lite-mps'].map((tag) => (
                    <tr key={tag}>
                      <th>{labels[tag]}</th>
                      <td>{f(refs.aggregates[tag].tight.mean_hd95_mm, 2)}</td>
                      <td>{f(refs.aggregates[tag].loose.mean_hd95_mm, 2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p data-calibration-private>
                LiteMedSAM loose boxes improve mean Dice while mean HD95 increases. Both columns use
                18 correlated slices, one CT.
              </p>
            </>
          ) : (
            <p>Reference measurements hidden.</p>
          )}
          <p>
            HD95: 95th percentile of pooled bidirectional 2D boundary distances, 4-connected
            erosion, 1.5 mm pixels. Not a 3D score.
          </p>
        </>
      ) : s.scene === 'latency' ? (
        <>
          <h4>Encode once; decode two cached box prompts</h4>
          <table className={styles.calibrationTable}>
            <thead>
              <tr>
                <th>Retained medians</th>
                <th>Image encode</th>
                <th>Box decode</th>
              </tr>
            </thead>
            <tbody>
              {['sam2-mps', 'lite-mps', 'sam2-cpu'].map((tag) => (
                <tr key={tag}>
                  <th>{labels[tag]}</th>
                  <td>{f(outputs.timing[tag].encode_median_ms, 1)} ms</td>
                  <td>{f(outputs.timing[tag].prompt_median_ms, 1)} ms</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className={styles.calibrationFacts}>
            <p>
              <strong>18 encodes</strong>unique images per complete run
            </p>
            <p>
              <strong>36 decodes</strong>two boxes reuse each embedding
            </p>
            <p>
              <strong>786 ms</strong>first SAM2 MPS encode; median 134.5 ms
            </p>
          </div>
          <p>
            FP32 · 4 threads · device synchronization. Encode includes transform; decode includes
            CPU mask return. Disk input, model load and warmup excluded.
          </p>
        </>
      ) : (
        <>
          <h4>What this retained calibration can support</h4>
          <div className={styles.calibrationFlow}>
            <article>
              <b>Supported locally</b>
              <p>Conditional mask agreement with fixed supplied boxes</p>
              <p>Measured encode/decode latency</p>
              <p>Specific backend discrepancies</p>
            </article>
            <article>
              <b>Still untested</b>
              <p>Agent-selected prompts and correction</p>
              <p>Whole-volume segmentation and semantic naming</p>
              <p>Population accuracy, training non-overlap and clinical reference intent</p>
            </article>
          </div>
          <p>
            72 primary MPS masks + 8 planned CPU checks + 36 later SAM2 CPU diagnostic masks. No
            revised prompts or new inference; original scores remain unchanged.
          </p>
        </>
      )}
    </section>
  );
}
export function CalibrationOutput({ state: s }: { state: CalibrationState }) {
  const v = calibrationSelection(s),
    view = src.views[v.sample];
  return (
    <div className={styles.calibrationAside} data-calibration-output>
      <b>
        {s.scene === 'latency'
          ? 'Runtime boundaries'
          : s.scene === 'backend'
            ? 'Backend evidence'
            : s.scene === 'sampling'
              ? 'Author selection'
              : 'One-case tool calibration'}
      </b>
      {['outputs', 'reference', 'sensitivity', 'duodenum', 'boxes', 'controls', 'backend'].includes(
        s.scene,
      ) && (
        <>
          <Plane sample={v.sample} full box={v.box} condition={v.condition} />
          <small>
            Full supplied field · {labels[view.organ]} · q{view.q * 100}
          </small>
        </>
      )}
      <p>
        Known public s1233. Reference masks provide slice and box selection; models receive image +
        box.
      </p>
      {['sensitivity', 'duodenum'].includes(s.scene) ? (
        v.reveal && <MeanTable organ={view.organ} />
      ) : s.scene === 'backend' ? (
        <>
          <p>
            Four planned LiteMedSAM CPU/MPS masks are pixel-identical. Four SAM2 CPU
            subset/full-repeat masks also match.
          </p>
          {v.reveal && (
            <p data-calibration-private>
              36 SAM2 CPU/MPS pairs: median mask Dice {f(refs.sam2_backend.median_mask_dice, 4)};{' '}
              {refs.sam2_backend.below_095} below 0.95. Cause unresolved.
            </p>
          )}
        </>
      ) : s.scene === 'latency' ? (
        <>
          <p>Setup + warmup: SAM2 11.6 + 16.8 s; LiteMedSAM 4.6 + 5.3 s.</p>
          <p>
            Observed driver allocation: 2,822 vs 1,140 MiB. RSS: 828 vs 537 MiB. Different counters;
            do not add them or infer total unified-memory peak.
          </p>
        </>
      ) : (
        <p>
          18 correlated organ/slice pairs from one CT. These 2D scores are not comparable to
          whole-volume CT-only agent scores.
        </p>
      )}
      <p>
        {v.reveal
          ? 'Dense reference is revealed for readers; it was not a model input.'
          : 'Dense reference and accuracy measurements are hidden.'}
      </p>
    </div>
  );
}
