import type { ReactNode } from 'react';
import {
  tigerSource as source,
  tigerViews as views,
  tigerRef as ref,
  tigerReveal,
  slidePoint,
  selectedCells,
  type TigerState,
  type TigerCell,
  type Bounds,
} from './tiger-context';
import styles from './task-visual.module.css';
const fmt = (n: number, d = 2) => n.toLocaleString('en-US', { maximumFractionDigits: d });
const roi = views[1],
  truth = ref.rois[1],
  boundary = ref.boundary;
function Text({
  x = 24,
  y,
  children,
  size = 18,
  color,
}: {
  x?: number;
  y: number;
  children: ReactNode;
  size?: number;
  color?: string;
}) {
  return (
    <text x={x} y={y} style={{ fontSize: size, ...(color ? { fill: color } : {}) }}>
      {children}
    </text>
  );
}
function View({
  image,
  bounds,
  x,
  y,
  width,
  height,
  children,
}: {
  image: string;
  bounds: Bounds;
  x: number;
  y: number;
  width: number;
  height: number;
  children?: ReactNode;
}) {
  const scale = Math.min(width / bounds[2], height / bounds[3]);
  return (
    <svg
      x={x}
      y={y}
      width={bounds[2] * scale}
      height={bounds[3] * scale}
      viewBox={`0 0 ${bounds[2]} ${bounds[3]}`}
    >
      <image data-tiger-input href={image} width={bounds[2]} height={bounds[3]} />
      {children}
    </svg>
  );
}
function Cells({
  cells,
  bounds = [0, 0, roi.bounds_level0[2], roi.bounds_level0[3]],
  boxes = false,
}: {
  cells: TigerCell[];
  bounds?: Bounds;
  boxes?: boolean;
}) {
  return (
    <g data-tiger-reference>
      {cells.map((c) => (
        <g key={c.id} transform={`translate(${-bounds[0]} ${-bounds[1]})`}>
          {boxes ? (
            <rect
              x={c.bbox[0]}
              y={c.bbox[1]}
              width={c.bbox[2]}
              height={c.bbox[3]}
              fill="none"
              stroke="#ffde35"
              strokeDasharray="3 2"
              strokeWidth="1.4"
              vectorEffect="non-scaling-stroke"
            />
          ) : (
            <path
              d={`M${c.center[0] - 5} ${c.center[1]}h10M${c.center[0]} ${c.center[1] - 5}v10`}
              stroke="#ffde35"
              strokeWidth="1.3"
              vectorEffect="non-scaling-stroke"
            />
          )}
        </g>
      ))}
    </g>
  );
}
function Mask() {
  return (
    <image
      data-tiger-mask
      data-tiger-reference
      href={truth.mask_overlay}
      width={roi.bounds_level0[2]}
      height={roi.bounds_level0[3]}
    />
  );
}
function Lines({ items }: { items: string[] }) {
  return (
    <>
      {items.map((s, i) => (
        <g key={s}>
          <rect x="24" y={55 + i * 76} width="552" height="65" rx="6" fill="#e5ebe2" />
          <Text x={40} y={94 + i * 76}>
            {s}
          </Text>
        </g>
      ))}
    </>
  );
}
export function TigerScene({ state }: { state: TigerState }) {
  const reveal = tigerReveal(state),
    b = source.detail.bounds_roi,
    point = selectedCells(b)[0] ?? truth.cells[0];
  const whole = slidePoint(point.center, roi.bounds_level0);
  return (
    <svg
      className={styles.operationCanvas}
      viewBox="0 0 600 420"
      role="img"
      aria-label="Source TIGER ROIs, reference tissue and cell points, and calibrated density arithmetic"
      data-tiger-scene={state.scene}
    >
      <g>
        {state.scene === 'inputs' ? (
          <>
            <Text y={31}>114S · three source-defined H&amp;E regions</Text>
            {views.map((v, i) => (
              <g key={v.pilot_id}>
                <View
                  image={v.image}
                  bounds={v.bounds_level0}
                  x={20 + i * 195}
                  y={70}
                  width={180}
                  height={220}
                />
                <Text x={20 + i * 195} y={283} size={16}>
                  {v.pilot_id} · COCO {v.coco_id}
                </Text>
                <Text x={20 + i * 195} y={309} size={15}>
                  {v.bounds_level0[2]} × {v.bounds_level0[3]} px
                </Text>
              </g>
            ))}
            <Text y={357}>0.456694 µm / pixel · local x right, y down</Text>
            <Text y={388} size={16}>
              Locations supplied; no autonomous slide search.
            </Text>
          </>
        ) : state.scene === 'conditions' ? (
          <>
            <Text y={31}>Declare what the solver receives</Text>
            <Lines
              items={[
                'Joint proposal: ROI + scale → tissue and cell inventory',
                'Tissue supplied: ROI + scale + integer tissue mask',
                'Pilot output: local cell points + compartment code',
                'Proposed output also needs regions, area and density',
              ]}
            />
          </>
        ) : ['tissue', 'area', 'density'].includes(state.scene) ? (
          <>
            <Text y={31}>COCO 940 · pilot roi2</Text>
            <View
              image={roi.image}
              bounds={roi.bounds_level0}
              x={24}
              y={62}
              width={310}
              height={300}
            >
              {reveal && (
                <>
                  <Mask />
                  {state.scene === 'density' && <Cells cells={truth.cells} />}
                </>
              )}
            </View>
            {state.scene === 'tissue' ? (
              <>
                {[0, 1, 2, 4, 6, 7].map((k, i) => (
                  <g key={k}>
                    <rect
                      x="349"
                      y={75 + i * 41}
                      width="16"
                      height="16"
                      fill={ref.palette[k].color}
                    />
                    <Text x={374} y={89 + i * 41} size={16}>
                      {k} ·{' '}
                      {
                        [
                          'unknown',
                          'invasive tumor',
                          'stroma',
                          '',
                          'healthy glands',
                          '',
                          'inflamed stroma',
                          'rest',
                        ][k]
                      }
                    </Text>
                  </g>
                ))}
                <Text y={387} size={16}>
                  {reveal
                    ? 'Reader tissue reference · codes 3 and 5 absent here'
                    : 'Tissue reference withheld until reveal'}
                </Text>
              </>
            ) : reveal ? (
              <g data-tiger-measurement>
                <Text x={349} y={97} size={18}>
                  {state.scene === 'area' ? 'Code 2 · stroma' : 'Codes 2 + 6 · stroma'}
                </Text>
                <Text x={349} y={148} size={23}>
                  {fmt(
                    state.scene === 'area' ? truth.rows[2].pixels : truth.merged_stroma.cells,
                    0,
                  )}{' '}
                  {state.scene === 'area' ? 'px²' : 'cells'}
                </Text>
                <Text x={349} y={197} size={16}>
                  {state.scene === 'area' ? '× (0.456694 / 1000)²' : '÷ 0.0849115 mm²'}
                </Text>
                <Text x={349} y={247} size={23}>
                  {state.view > 0.35
                    ? state.scene === 'area'
                      ? '0.0676069 mm²'
                      : '2,049.19 cells/mm²'
                    : '…'}
                </Text>
                <Text x={349} y={308} size={15}>
                  {state.scene === 'area' ? '0 = excluded domain' : 'Sum counts AND areas'}
                </Text>
                <Text y={387} size={16}>
                  {state.scene === 'area'
                    ? 'Source mask pixels define this worked denominator.'
                    : 'Weighted pooled density; not an average of densities.'}
                </Text>
              </g>
            ) : (
              <Text x={349} y={180}>
                Reference hidden
              </Text>
            )}
          </>
        ) : ['cells', 'coordinates'].includes(state.scene) ? (
          <>
            <Text y={31}>Reference-selected crop · COCO 940 / roi2</Text>
            <View image={source.detail.image} bounds={b} x={24} y={58} width={320} height={320}>
              {reveal && (
                <>
                  <Cells cells={selectedCells(b)} bounds={b} boxes={state.scene === 'cells'} />
                  {state.scene === 'coordinates' && (
                    <circle
                      data-tiger-worked-point
                      data-tiger-reference
                      cx={point.center[0] - b[0]}
                      cy={point.center[1] - b[1]}
                      r={8}
                      fill="none"
                      stroke="white"
                      strokeWidth="2"
                      vectorEffect="non-scaling-stroke"
                    />
                  )}
                </>
              )}
            </View>
            {state.scene === 'cells' ? (
              <>
                <Text x={362} y={102} size={17}>
                  Merged immune cells
                </Text>
                <Text x={362} y={148} size={16}>
                  Yellow dashed boxes
                </Text>
                <Text x={362} y={180} size={16}>
                  are point markers.
                </Text>
                <Text x={362} y={243} size={16}>
                  8 × 8 µm convention
                </Text>
                <Text x={362} y={282} size={16}>
                  No nuclear contours
                </Text>
                <Text x={362} y={331} size={16}>
                  No class split
                </Text>
              </>
            ) : reveal ? (
              <g data-tiger-coordinate>
                <Text x={360} y={94} size={16}>
                  White ring · crop point
                </Text>
                <Text x={360} y={127} size={18}>
                  {point.center[0] - b[0]}, {point.center[1] - b[1]}
                </Text>
                <Text x={360} y={173} size={16}>
                  + (640,420) → ROI
                </Text>
                <Text x={360} y={206} size={18}>
                  {point.center.join(', ')}
                </Text>
                <Text x={360} y={254} size={16}>
                  + (33188,13944)
                </Text>
                <Text x={360} y={289} size={16}>
                  = slide level 0
                </Text>
                <Text x={360} y={332} size={18}>
                  {state.view > 0.35 ? whole.join(', ') : '…'}
                </Text>
              </g>
            ) : (
              <Text x={360} y={180}>
                Reference hidden
              </Text>
            )}
            <Text y={405} size={15}>
              Teaching crop origin within roi2: (640,420) · 480 × 480 px
            </Text>
          </>
        ) : state.scene === 'assign' ? (
          <>
            <Text y={31}>A small displacement can cross a tissue boundary</Text>
            <View
              image={source.boundary.image}
              bounds={source.boundary.bounds_roi}
              x={24}
              y={64}
              width={304}
              height={304}
            >
              {reveal && (
                <g data-tiger-boundary data-tiger-reference>
                  <image
                    href={ref.rois[2].mask_overlay}
                    x={-405}
                    y={-810}
                    width={1144}
                    height={1137}
                  />
                  <circle
                    cx={60}
                    cy={60}
                    r="2"
                    fill="none"
                    stroke="white"
                    strokeWidth="1.5"
                    vectorEffect="non-scaling-stroke"
                  />
                  <circle
                    cx={60 + 2 * state.view}
                    cy={60 + 3 * state.view}
                    r="2"
                    fill="none"
                    stroke="black"
                    strokeWidth="1.5"
                    vectorEffect="non-scaling-stroke"
                  />
                </g>
              )}
            </View>
            <Text x={351} y={98} size={16}>
              COCO 941 / roi3
            </Text>
            {reveal ? (
              <>
                <Text x={351} y={151} size={16}>
                  White: source (465,870)
                </Text>
                <Text x={351} y={185} size={16}>
                  Code 1 · invasive tumor
                </Text>
                <Text x={351} y={247} size={16}>
                  Black target: (+2,+3) px
                </Text>
                <Text x={351} y={282} size={16}>
                  Target code 2 · stroma
                </Text>
                <Text x={351} y={331} size={16}>
                  Target offset: 3.61 px
                </Text>
              </>
            ) : (
              <Text x={351} y={180}>
                Reference hidden
              </Text>
            )}
            <Text y={398} size={15}>
              Constructed displacement · declare which center reads the mask.
            </Text>
          </>
        ) : state.scene === 'output' ? (
          <>
            <Text y={31}>Three linked deliverables in the proposed task</Text>
            <Lines
              items={[
                'cells.csv · local center, merged class, compartment',
                'regions.geojson · compartment geometry in level-0 px',
                'summary.csv · counts, area_mm2, density_per_mm2',
                'ROI origin links local points to full-slide geometry',
              ]}
            />
          </>
        ) : (
          <>
            <Text y={31}>The evaluation boundary remains explicit</Text>
            <Lines
              items={[
                'Retained pilots: points.json; no contour/density score',
                'Revised matcher: 20 px, one-to-one, two label reads',
                'Three selected training ROIs; outside is not negative',
                'No nuclear area or clinical stromal TIL percentage',
              ]}
            />
          </>
        )}
      </g>
    </svg>
  );
}
export function TigerOutput({ state }: { state: TigerState }) {
  const reveal = tigerReveal(state);
  return (
    <div className={styles.storyOutput} data-tiger-output={state.scene}>
      <strong>
        {state.scene === 'density'
          ? 'Count / annotated tissue area'
          : state.scene === 'assign'
            ? 'Source center versus submitted center'
            : state.scene === 'limits'
              ? 'What remains untested'
              : 'TIGER · inspect the operation'}
      </strong>
      {state.scene === 'inputs' ? (
        <>
          <p>One public training slide. Three supplied ROIs remove whole-slide search.</p>
          <p>Reference cell points, tissue labels and derived counts start hidden.</p>
        </>
      ) : state.scene === 'conditions' ? (
        <>
          <p>
            The joint proposal asks for tissue regions and an immune-cell inventory. Giving tissue
            labels changes the assistance condition.
          </p>
          <p>
            Frozen image-only and tissue-supplied pilots both submitted <code>points.json</code>.
          </p>
        </>
      ) : state.scene === 'tissue' ? (
        <>
          <p>
            Colored tissue is reader reference. Code 6 is inflamed tumor-associated stroma with high
            lymphocyte density.
          </p>
          <p>
            Code 0 is unknown and excluded. Classes 3 and 5 exist in the source schema but are
            absent in these ROIs.
          </p>
        </>
      ) : state.scene === 'cells' ? (
        <>
          <p>
            Source annotations merge lymphocytes and plasma cells. Box centers define points; box
            area is not nuclear area.
          </p>
          <p>
            The dense crop was selected using references. This is no record of agent search or
            detection.
          </p>
        </>
      ) : state.scene === 'assign' ? (
        <>
          <p>
            The worked shift crosses from code 1 to 2. It is constructed from a source center, not a
            model prediction.
          </p>
          <p>
            Revised pilots report mask labels at both the matched source center and the submitted
            center. Original scores remain unchanged.
          </p>
        </>
      ) : state.scene === 'coordinates' ? (
        <>
          <p>
            A crop-local point first adds (640,420) to reach ROI coordinates, then (33188,13944) to
            reach level 0.
          </p>
          <p>
            The CSV must name its frame and ROI; the same local numbers in a different ROI name a
            different location.
          </p>
        </>
      ) : state.scene === 'area' ? (
        <>
          <p>Area = mask pixels × (µm/pixel ÷ 1000)². Use the squared scale and exclude code 0.</p>
          <p>Zero annotated area means unavailable density, not zero density.</p>
        </>
      ) : state.scene === 'density' && reveal ? (
        <div data-tiger-density>
          <table>
            <thead>
              <tr>
                <th>Code</th>
                <th>Cells</th>
                <th>mm²</th>
                <th>/mm²</th>
              </tr>
            </thead>
            <tbody>
              {[truth.rows[2], truth.rows[6], { ...truth.merged_stroma, code: '2+6' }].map((r) => (
                <tr key={r.code}>
                  <td>{r.code}</td>
                  <td>{r.cells}</td>
                  <td>{fmt(r.area_mm2, 5)}</td>
                  <td>{fmt(r.density_per_mm2 ?? 0, 1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p>
            Reference-derived COCO 940 arithmetic. Pool counts and areas; never take the simple mean
            of the two densities.
          </p>
        </div>
      ) : state.scene === 'output' ? (
        <>
          <p>
            The output schema is a proposal. Actual tissue masks demonstrate the regional domain; no
            submitted contour file is shown.
          </p>
          <p>
            Cell rows, region geometry and summary denominators must use the same compartment policy
            and coordinates.
          </p>
        </>
      ) : state.scene === 'limits' ? (
        <>
          <p>
            Freeze a joint-task evaluator, boundary convention, inclusion rule and class 2/6 policy
            before a new trial.
          </p>
          <p>
            Point pilots do not establish tissue contour or density performance. Selected ROI counts
            cannot establish full-slide or population estimates.
          </p>
        </>
      ) : (
        <p>Reveal references to inspect source-derived arithmetic.</p>
      )}
      <small>Source-derived teaching · CC BY-NC 4.0 · no new trial</small>
    </div>
  );
}
