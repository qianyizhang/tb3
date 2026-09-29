import { pumaPacks, type PumaPack, type PumaPoint, type RexPumaState } from './rexmle-puma';
import shared from './task-visual.module.css';
import css from './rexmle-puma.module.css';

const CLASS_COLOR: Record<string, string> = {
  tumor: '#0dc9d3',
  TILs: '#f4bc49',
  other: '#dd82b2',
  lymphocytes: '#f4bc49',
  apoptotic_cells: '#dd82b2',
  endothelium: '#86d879',
  plasma_cells: '#ef9a35',
  histiocytes: '#ad92e2',
  melanophages: '#b88a62',
  neutrophils: '#70b9ed',
  stromal_cells: '#a8c59a',
  epithelium: '#ef7798',
};
function Markers({
  points,
  x = 0,
  y = 0,
  crop = false,
}: {
  points: PumaPoint[];
  x?: number;
  y?: number;
  crop?: boolean;
}) {
  const visible = crop
    ? points.filter((p) => p.x_px >= x && p.x_px < x + 256 && p.y_px >= y && p.y_px < y + 256)
    : points;
  return (
    <g data-puma-training-annotation>
      {visible.map((p) => (
        <circle
          key={p.source_index}
          cx={p.x_px - x}
          cy={p.y_px - y}
          r={crop ? 3.2 : 4.2}
          fill={CLASS_COLOR[p.class] || '#fff'}
          stroke="#152733"
          strokeWidth={crop ? 1 : 1.4}
        />
      ))}
    </g>
  );
}
function Slide({
  pack,
  helper = false,
  crop = false,
  markCrop = false,
}: {
  pack: PumaPack;
  helper?: boolean;
  crop?: boolean;
  markCrop?: boolean;
}) {
  const side = crop ? 256 : 1024;
  const points = pack.helper.points || [];
  return (
    <figure className={css.slide} data-puma-real-training-input>
      <div className={css.slideHead}>
        <b>
          {pack.source.case_id}
          {crop ? ' · label-guided view' : ''}
        </b>
        <span>
          {side} × {side} px
        </span>
      </div>
      <div className={css.slideImage}>
        <img
          src={crop ? pack.zoom : pack.image}
          width={side}
          height={side}
          alt={`${crop ? 'Post-hoc crop of' : 'Full'} actual PUMA H&E public-training ROI; no model output`}
        />
        {helper && pack.task === 'tissue' && !crop && (
          <img
            className={css.overlay}
            src={pack.overlay}
            width="1024"
            height="1024"
            alt="Source training tissue polygon overlay"
            data-puma-training-annotation
          />
        )}
        {helper && pack.task !== 'tissue' && (
          <svg
            className={css.markers}
            viewBox={`0 0 ${side} ${side}`}
            aria-label="Source training nuclei centroids, not predictions"
          >
            <Markers points={points} x={crop ? 512 : 0} y={crop ? 512 : 0} crop={crop} />
          </svg>
        )}
        {!crop && markCrop && helper && pack.task !== 'tissue' && (
          <div className={css.roiSquare} aria-hidden="true" />
        )}
      </div>
      <figcaption>
        {crop
          ? 'Post-hoc 256 × 256 source crop, selected for annotation inspection; original search is the full ROI.'
          : 'Original 1024 × 1024 source ROI; annotations are public-training help only.'}
      </figcaption>
    </figure>
  );
}
function Input({ pack }: { pack: PumaPack }) {
  return (
    <div className={css.two}>
      <Slide pack={pack} />
      <div className={css.card} data-puma-split>
        <b>Same real ROI, three different tasks</b>
        <p>
          This source case is reconstructed as public train for all three pinned adapters. Tissue
          polygons and nucleus polygons are different supplied labels on the same H&E image.
        </p>
        <div className={css.split}>
          <strong>205</strong>
          <span>image IDs matched to both annotation sets</span>
          <strong>164 / 41</strong>
          <span>expected train / private-label test, seed 42</span>
        </div>
        <p>No ReX preparer was run; there is no retained held-out input, prediction, or score.</p>
      </div>
    </div>
  );
}
function Helper({ pack, reveal }: { pack: PumaPack; reveal: boolean }) {
  return (
    <div className={css.two}>
      <Slide pack={pack} helper={reveal} />
      <div className={css.card}>
        <b>{pack.task === 'tissue' ? 'Supplied tissue polygons' : 'Supplied nucleus polygons'}</b>
        <p>
          {reveal
            ? 'Colored source annotations are now visible. They are training labels, not a model result or private held-out truth.'
            : 'Open the training-helper channel to overlay the matching official annotation.'}
        </p>
        {pack.task === 'tissue' ? (
          <div className={css.legend}>
            <span>
              <i style={{ background: '#14c6d4' }} /> 3 · tumor
            </span>
            <span>
              <i style={{ background: '#f4bc49' }} /> 5 · necrosis
            </span>
            <small>
              The pinned converter maps five foreground tissue IDs; only these two occur in this
              ROI.
            </small>
          </div>
        ) : (
          <>
            <div className={css.legend}>
              {Object.entries(pack.helper.class_counts || {}).map(([name, n]) => (
                <span key={name}>
                  <i style={{ background: CLASS_COLOR[name] || '#fff' }} />
                  {name} · {n}
                </span>
              ))}
            </div>
            <small>
              633 original nucleus features; the pinned Polygon-only conversion keeps 628 and skips
              five MultiPolygons.
            </small>
          </>
        )}
      </div>
    </div>
  );
}
function Operation({ pack, focus }: { pack: PumaPack; focus: number }) {
  const tissueClass = focus < 0.5 ? 3 : 5;
  if (pack.task === 'tissue')
    return (
      <div className={css.two} data-puma-tissue-operation>
        <Slide pack={pack} helper />
        <div className={css.card}>
          <b>Polygon → semantic pixel mask</b>
          <p>
            The pinned converter paints the exterior of each source GeoJSON polygon into a 1024 ×
            1024 integer grid. Class 3 marks tumor; class 5 marks necrosis in this training ROI.
          </p>
          <div className={css.pixelMap}>
            <span>GeoJSON tissue_tumor</span>
            <strong data-puma-active={tissueClass === 3}>→ pixel 3</strong>
            <span>GeoJSON tissue_necrosis</span>
            <strong data-puma-active={tissueClass === 5}>→ pixel 5</strong>
          </div>
          <p>
            Pixels of the same tissue class share one ID. This is semantic segmentation, not
            individual cell detection. Source-derived mask counts are{' '}
            {pack.helper.pixels_by_id?.['3']?.toLocaleString()} tumor and{' '}
            {pack.helper.pixels_by_id?.['5']?.toLocaleString()} necrosis pixels. No prediction is
            shown.
          </p>
        </div>
      </div>
    );
  const counts = pack.helper.class_counts || {};
  const activeClass =
    Object.keys(counts)[
      Math.min(Object.keys(counts).length - 1, Math.floor(focus * Object.keys(counts).length))
    ];
  return (
    <div className={css.operation} data-puma-nuclei-operation>
      <div className={css.operationImages}>
        <Slide pack={pack} helper markCrop />
        <Slide pack={pack} helper crop />
      </div>
      <div className={css.card}>
        <b>
          {pack.task === 'coarse-nuclei'
            ? '628 polygons → 3 grouped classes'
            : '628 polygons → 10-class vocabulary'}
        </b>
        <p>
          Each accepted training polygon contributes a centroid by arithmetic mean of exterior path
          points. The source full image remains the search field; the 256-pixel crop is a labeled
          post-hoc inspection view.
        </p>
        <small>
          <i className={css.cropKey} /> Pale dashed box: the displayed post-hoc crop.
        </small>
        <div className={css.classList}>
          {Object.entries(counts).map(([name, n]) => (
            <span key={name} data-puma-active={name === activeClass}>
              <i style={{ background: CLASS_COLOR[name] || '#fff' }} />
              {name}
              <strong>{n}</strong>
            </span>
          ))}
        </div>
        <p>
          {pack.task === 'coarse-nuclei'
            ? 'Lymphocytes and plasma cells map to TILs; remaining non-tumor types map to other.'
            : 'Fine labels remain distinct. This source ROI has four of the ten target classes; absent classes are not inferred as negatives for the full dataset.'}
        </p>
      </div>
    </div>
  );
}
function Submission({ pack }: { pack: PumaPack }) {
  const o = pack.output;
  return (
    <div className={css.submission} data-puma-empty-output>
      <div className={css.empty}>
        <b>Held-out ROI</b>
        <span>Exact test image unavailable in this pack</span>
      </div>
      <span className={css.arrow}>→</span>
      <div className={css.card}>
        <b>submission/submission.csv</b>
        <div className={css.csv}>
          <strong>{o.csv_columns[0]}</strong>
          <strong>{o.csv_columns[1]}</strong>
          <span>{o.row_template[o.csv_columns[0]]}</span>
          <span>{o.row_template[o.csv_columns[1]]}</span>
        </div>
        <div className={css.empty}>
          <b>{pack.task === 'tissue' ? 'TIF semantic mask 0–5' : 'Per-case nuclei JSON'}</b>
          <span>Empty answer-owned artifact; no prediction retained</span>
        </div>
        <p>
          {pack.task === 'tissue'
            ? 'Background is 0; five tissue IDs are 1–5. The source training mask is never copied into this output.'
            : 'Polygon path_points or simplified centroids with class names are accepted; confidence is optional.'}
        </p>
      </div>
    </div>
  );
}
function Scoring({ pack, metric }: { pack: PumaPack; metric: number }) {
  return (
    <div
      className={css.score}
      data-puma-scoring-operation
      data-puma-metric-step={Math.min(3, Math.floor(metric * 4))}
    >
      {pack.task === 'tissue' ? (
        <>
          <div className={css.flow}>
            <div>Private semantic reference</div>
            <span>×</span>
            <div>Submitted 0–5 mask</div>
            <span>→</span>
            <div>Per-class overlap</div>
            <span>→</span>
            <div>Mean micro Dice</div>
          </div>
          <div className={css.card}>
            <b>Five foreground classes, background excluded</b>
            <p>
              The pinned grader concatenates cases by class, computes Dice for each of IDs 1–5, then
              averages those five class Dice values. Its separate macro Dice averages per-case
              scores. An absent class in both masks contributes 0 in its per-class case check. Shape
              mismatch is resized nearest-neighbor; no score is available here.
            </p>
          </div>
        </>
      ) : (
        <>
          <div className={css.flow}>
            <div>Private nuclei centroids</div>
            <span>×</span>
            <div>Submitted centroids + class</div>
            <span>→</span>
            <div>Same-class distance gate</div>
            <span>→</span>
            <div>Macro F1</div>
          </div>
          <div className={css.distance}>
            <span>0 px</span>
            <div className={css.distanceTrack}>
              <i />
            </div>
            <strong>{pack.metric.distance_rule} 15 px</strong>
          </div>
          <div className={css.card}>
            <b>
              {pack.task === 'coarse-nuclei' ? '3-class' : '10-class'} greedy one-to-one matching
            </b>
            <p>
              For each private GT nucleus, eligible same-class predictions are sorted by descending
              confidence, then ascending centroid distance. A chosen prediction is consumed once.
              The Track 1 gate is strictly under 15 pixels; Track 2 includes exactly 15 pixels.
              {pack.task === 'coarse-nuclei'
                ? 'Each class F1 averages every case (both-empty is 0), then the three class means are averaged.'
                : 'Each class F1 averages only cases where GT or predictions contain it. A never-present class contributes 0 to the ten-class mean.'}{' '}
              No prediction or F1 was computed.
            </p>
          </div>
        </>
      )}
    </div>
  );
}
function Limits({ pack }: { pack: PumaPack }) {
  return (
    <div className={css.limits}>
      <div>
        <b>Actual source</b>
        <p>
          One CRC-verified PUMA 1024² H&E ROI and matching official{' '}
          {pack.task === 'tissue' ? 'tissue' : 'nucleus'} GeoJSON annotation, CC0-1.0.
        </p>
      </div>
      <div>
        <b>Static reconstruction</b>
        <p>
          205 matched images; seed-42 164/41 split. This case falls in public train, but pinned
          preparation was not executed.
        </p>
      </div>
      <div>
        <b>Absent</b>
        <p>
          No materialized held-out case, prediction, private reference, scorer run or task score.
        </p>
      </div>
      <div>
        <b>Scope</b>
        <p>
          {pack.task === 'tissue'
            ? 'Only tumor and necrosis are annotated in this selected ROI; the five-class contract is broader.'
            : pack.task === 'coarse-nuclei'
              ? 'All three grouped classes occur here. Five MultiPolygon source features are skipped by the pinned Polygon-only conversion.'
              : 'Five MultiPolygon source features are skipped by pinned Polygon-only conversion; only four of ten target classes occur here.'}
        </p>
      </div>
    </div>
  );
}
const TITLES: Record<RexPumaState['scene'], string> = {
  input: 'One actual melanoma H&E ROI',
  helper: 'Open its supplied training annotation',
  operation: 'Trace the task-specific label operation',
  submission: 'Specify an empty held-out output',
  scoring: 'How the pinned grader would compare',
  limits: 'Evidence and scope limits',
};
export function RexPumaScene({ state }: { state: RexPumaState }) {
  const pack = pumaPacks[state.recipe];
  return (
    <section className={css.scene} data-puma-scene={state.scene} data-puma-task={pack.task}>
      <h3>{TITLES[state.scene]}</h3>
      {state.scene === 'input' && <Input pack={pack} />}
      {state.scene === 'helper' && <Helper pack={pack} reveal={state.helper > 0.5} />}
      {state.scene === 'operation' && <Operation pack={pack} focus={state.focus} />}
      {state.scene === 'submission' && <Submission pack={pack} />}
      {state.scene === 'scoring' && <Scoring pack={pack} metric={state.metric} />}
      {state.scene === 'limits' && <Limits pack={pack} />}
    </section>
  );
}
export function RexPumaOutput({ state }: { state: RexPumaState }) {
  const pack = pumaPacks[state.recipe];
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-puma-output>
      <b>Example role</b>
      <p>
        Official source ROI reconstructed as public train. Matching annotation is supplied learning
        help.
      </p>
      {state.scene !== 'input' && (
        <>
          <b>Answer-owned output</b>
          <p>
            Empty schema only: {pack.output.csv_columns.join(', ')}. No model artifact or score.
          </p>
        </>
      )}
      <b>Evidence boundary</b>
      <p>
        Private held-out labels are absent. The ReX split is static reconstruction; preparer and
        grader were not run.
      </p>
      <small>PUMA 14869398 · CC0-1.0 · local source-derived teaching</small>
    </aside>
  );
}
