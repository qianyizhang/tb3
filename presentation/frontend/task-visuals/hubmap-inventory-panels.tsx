import type { ReactNode } from 'react';
import {
  hubmapSource as source,
  hubmapDetail as detail,
  hubmapTiles as tiles,
  hubmapRef as ref,
  hubmapHelpers as helpers,
  hubmapReveal,
  slideFit,
  toLocal,
  ringPath,
  hubmapRows,
  profileArea,
  type SlideView,
  type HubmapState,
} from './hubmap-inventory';
import styles from './task-visual.module.css';

const teal = '#187d74',
  amber = '#be791f';
const first = ref.objects[0];
const number = (n: number) => n.toLocaleString('en-US', { maximumFractionDigits: 2 });
function Slide({
  p,
  x,
  y,
  width,
  height,
  children,
}: {
  p: SlideView;
  x: number;
  y: number;
  width: number;
  height: number;
  children?: ReactNode;
}) {
  const fit = slideFit(p, width, height);
  return (
    <g transform={`translate(${x + (width - fit.width) / 2} ${y})`}>
      <image
        data-hubmap-input
        href={p.image}
        width={fit.width}
        height={fit.height}
        preserveAspectRatio="none"
      />
      <svg
        width={fit.width}
        height={fit.height}
        viewBox={`0 0 ${p.bounds_level0[2]} ${p.bounds_level0[3]}`}
      >
        {children}
      </svg>
    </g>
  );
}
function Outline({ p, all = false, fill = 0 }: { p: SlideView; all?: boolean; fill?: number }) {
  return (
    <g data-hubmap-reference>
      {(all ? ref.objects : [first]).map((obj) => (
        <path
          key={obj.id}
          d={ringPath([obj.ring], p.bounds_level0)}
          stroke={teal}
          strokeWidth="2"
          strokeDasharray="6 4"
          vectorEffect="non-scaling-stroke"
          fill={teal}
          fillOpacity={fill}
        />
      ))}
    </g>
  );
}
function Center({ p }: { p: SlideView }) {
  const point = toLocal(first.center_level0, p.bounds_level0);
  return (
    <g data-hubmap-centroid transform={`translate(${point.join(' ')})`}>
      <path
        d="M-25 0H25M0 -25V25"
        stroke={amber}
        strokeWidth="2"
        vectorEffect="non-scaling-stroke"
      />
    </g>
  );
}
function Rows({ items }: { items: string[][] }) {
  return (
    <g>
      {items.map(([a, b], i) => (
        <g key={a}>
          <rect x="24" y={65 + i * 78} width="552" height="68" rx="7" fill="#e5ebe2" />
          <text x="40" y={91 + i * 78} style={{ fontSize: 18 }}>
            {a}
          </text>
          <text x="40" y={117 + i * 78} style={{ fontSize: 17 }} fontWeight="600">
            {b}
          </text>
        </g>
      ))}
    </g>
  );
}
export function HubmapScene({ state }: { state: HubmapState }) {
  const reveal = hubmapReveal(state),
    local = toLocal(first.center_level0, detail.bounds_level0);
  const detailScene = ['outline', 'coordinates', 'area'].includes(state.scene);
  return (
    <svg
      className={styles.operationCanvas}
      viewBox="0 0 600 420"
      role="img"
      aria-label="Actual PAS slide and separately revealed source polygons for a proposed object inventory"
      data-hubmap-scene={state.scene}
    >
      {['inputs', 'helpers', 'inventory'].includes(state.scene) ? (
        <g>
          <text style={{ fontSize: 17 }} x="24" y="32">
            aaa6a05cc · PAS kidney training slide
          </text>
          <Slide p={source.overview} x={24} y={53} width={280} height={309}>
            {state.scene === 'helpers' &&
              helpers.features.map((f, i) => {
                const polygons =
                  f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;
                const color = f.properties.classification.name === 'Cortex' ? '#426ebc' : '#8854ad';
                return (
                  <g key={i} data-hubmap-helper>
                    {polygons.map((rings, j) => (
                      <path
                        key={j}
                        d={ringPath(rings, source.overview.bounds_level0)}
                        fill={color}
                        fillOpacity={0.22 * state.view}
                        fillRule="evenodd"
                        stroke={color}
                        strokeWidth="2"
                        vectorEffect="non-scaling-stroke"
                      />
                    ))}
                  </g>
                );
              })}
            {state.scene === 'inventory' && reveal && <Outline p={source.overview} all />}
          </Slide>
          {state.scene === 'inputs' ? (
            <g>
              <text x="324" y="105" style={{ fontSize: 22 }}>
                13,013 × 18,484 px
              </text>
              <text x="324" y="142" style={{ fontSize: 19 }}>
                0.65 µm / pixel
              </text>
              <text x="324" y="203" style={{ fontSize: 17 }}>
                Level 0 · x right, y down
              </text>
              <text x="324" y="237" style={{ fontSize: 17 }}>
                Proposed work:
              </text>
              <text x="324" y="268" style={{ fontSize: 18 }}>
                find → outline → measure
              </text>
              <text x="324" y="309" style={{ fontSize: 17 }}>
                Reference remains hidden.
              </text>
            </g>
          ) : state.scene === 'helpers' ? (
            <g>
              <text style={{ fill: '#426ebc', fontSize: 17 }} x="324" y="105">
                Cortex
              </text>
              <text style={{ fill: '#8854ad', fontSize: 17 }} x="324" y="145">
                Medulla
              </text>
              <text x="324" y="205" style={{ fontSize: 17 }}>
                Rough source regions
              </text>
              <text x="324" y="240" style={{ fontSize: 17 }}>
                Optional helper condition
              </text>
              <text x="324" y="287" style={{ fontSize: 17 }}>
                No object contours
              </text>
              <text x="324" y="319" style={{ fontSize: 17 }}>
                No negative-domain proof
              </text>
            </g>
          ) : reveal ? (
            <g data-hubmap-inventory>
              <text x="324" y="100" style={{ fontSize: 27 }}>
                {ref.source_object_count} source polygons
              </text>
              <text x="324" y="138" style={{ fontSize: 16 }}>
                Reference count in this member
              </text>
              <text x="324" y="206" style={{ fontSize: 18 }}>
                One geometry ↔ one row
              </text>
              <text x="324" y="245" style={{ fontSize: 17 }}>
                Stable IDs · level-0 centers
              </text>
              <text x="324" y="280" style={{ fontSize: 17 }}>
                Areas in µm²
              </text>
              <text x="324" y="321" style={{ fontSize: 17 }}>
                Worked format, not a result
              </text>
            </g>
          ) : (
            <text x="324" y="146" style={{ fontSize: 18 }}>
              Inventory reference hidden
            </text>
          )}
          <text x="24" y="402" style={{ fontSize: 16 }}>
            {state.scene === 'inputs'
              ? 'Actual full image · reduced display · no stain normalization'
              : state.scene === 'helpers'
                ? 'These helper regions were absent from retained point pilots.'
                : 'Source polygons are not an adjudicated exhaustive object count.'}
          </text>
        </g>
      ) : state.scene === 'detail' ? (
        <g>
          <text style={{ fontSize: 17 }} x="24" y="32">
            Locate the teaching crop on the full slide
          </text>
          <Slide p={source.overview} x={24} y={63} width={164} height={269}>
            <rect
              data-hubmap-viewport
              x={detail.bounds_level0[0] * state.view}
              y={detail.bounds_level0[1] * state.view}
              width={source.size_level0[0] * (1 - state.view) + 1600 * state.view}
              height={source.size_level0[1] * (1 - state.view) + 1600 * state.view}
              fill="none"
              stroke={amber}
              strokeWidth="3"
              vectorEffect="non-scaling-stroke"
            />
          </Slide>
          <Slide p={detail} x={245} y={63} width={276} height={276} />
          <text x="24" y="373" style={{ fontSize: 17 }}>
            Crop origin (2016, 6706) · 1600 × 1600 native pixels
          </text>
          <text x="24" y="403" style={{ fontSize: 16 }}>
            Reference-selected view · this removes the slide-search problem.
          </text>
        </g>
      ) : detailScene ? (
        <g>
          <text style={{ fontSize: 17 }} x="24" y="32">
            {state.scene === 'outline'
              ? 'Reveal a source contour; do not call it a prediction'
              : state.scene === 'coordinates'
                ? 'A local center must return to level-0 coordinates'
                : 'Measure the profile inside the original polygon'}
          </text>
          <Slide p={detail} x={24} y={56} width={280} height={280}>
            {reveal && <Outline p={detail} fill={state.scene === 'area' ? state.view * 0.24 : 0} />}
            {reveal && state.scene !== 'outline' && <Center p={detail} />}
          </Slide>
          {reveal ? (
            <g data-hubmap-measurement>
              <text x="328" y="98" style={{ fontSize: 22 }}>
                ref-001
              </text>
              {state.scene === 'outline' ? (
                <g>
                  <text x="328" y="151" style={{ fontSize: 18 }}>
                    Source-array object 1
                  </text>
                  <text x="328" y="200" style={{ fontSize: 17 }}>
                    Teal dashed: reference
                  </text>
                  <text x="328" y="235" style={{ fontSize: 17 }}>
                    No inferred outline
                  </text>
                  <text x="328" y="285" style={{ fontSize: 17 }}>
                    Partial neighbours remain.
                  </text>
                </g>
              ) : state.scene === 'coordinates' ? (
                <g>
                  <text x="328" y="149" style={{ fontSize: 16 }}>
                    Local ({number(local[0])}, {number(local[1])})
                  </text>
                  <text x="328" y="193" style={{ fontSize: 18 }}>
                    + origin (2016, 6706)
                  </text>
                  {state.view > 0.5 && (
                    <g data-hubmap-level0>
                      <text x="328" y="244" style={{ fontSize: 18 }}>
                        = ({number(first.center_level0[0])},
                      </text>
                      <text x="347" y="276" style={{ fontSize: 18 }}>
                        {number(first.center_level0[1])}) px
                      </text>
                    </g>
                  )}
                </g>
              ) : (
                <g>
                  <text x="328" y="153" style={{ fontSize: 23 }}>
                    {number(first.area_px2)} px²
                  </text>
                  <text x="328" y="198" style={{ fontSize: 20 }}>
                    × (0.65 µm/px)²
                  </text>
                  {state.view > 0.5 && (
                    <text data-hubmap-area x="328" y="254" style={{ fontSize: 24 }}>
                      = {number(profileArea(first.area_px2))} µm²
                    </text>
                  )}
                  <text x="328" y="304" style={{ fontSize: 16 }}>
                    2D section profile only
                  </text>
                </g>
              )}
            </g>
          ) : (
            <text x="328" y="141" style={{ fontSize: 19 }}>
              Source reference hidden
            </text>
          )}
          <text x="24" y="370" style={{ fontSize: 17 }}>
            {state.scene === 'outline'
              ? 'This crop was chosen using the first reference polygon.'
              : state.scene === 'coordinates'
                ? 'Amber: polygon area centroid · not an annotated center point'
                : 'Shoelace area from original coordinates; no JPEG thresholding'}
          </text>
          <text x="24" y="402" style={{ fontSize: 16 }}>
            {state.scene === 'area'
              ? 'A section area does not estimate 3D volume or whole-kidney count.'
              : 'Source IDs repeat; ref-NNN uses source order for this worked example.'}
          </text>
        </g>
      ) : state.scene === 'duplicate' ? (
        <g>
          <text style={{ fontSize: 17 }} x="24" y="32">
            Two overlapping views can describe one object
          </text>
          {tiles.map((p, i) => (
            <g key={i}>
              <text x={24 + i * 298} y="65" style={{ fontSize: 17 }}>
                Tile {i + 1} · origin {p.bounds_level0.slice(0, 2).join(', ')}
              </text>
              <Slide p={p} x={24 + i * 298} y={82} width={254} height={254}>
                {reveal && (
                  <>
                    <Outline p={p} />
                    <Center p={p} />
                  </>
                )}
              </Slide>
            </g>
          ))}
          <text data-hubmap-duplicate-count x="24" y="370" style={{ fontSize: 21 }}>
            {reveal
              ? state.view > 0.5
                ? 'Same level-0 center → 1 unique source object'
                : '2 view records → compare global coordinates'
              : 'Reference comparison hidden'}
          </text>
          <text x="24" y="403" style={{ fontSize: 16 }}>
            Constructed duplicate teaching example · no observed agent error
          </text>
        </g>
      ) : state.scene === 'conditions' ? (
        <g>
          <text style={{ fontSize: 17 }} x="24" y="32">
            Keep the proposed and executed contracts separate
          </text>
          <Rows
            items={[
              ['Proposed contour inventory', 'glomeruli.geojson + inventory.csv'],
              ['Retained diagnostic pilots', 'points.json · level-0 centers only'],
              ['Point reference matching', 'Inside polygon or within 50 µm · one-to-one'],
              ['Unmatched point candidates', 'Review queue; not established false positives'],
            ]}
          />
          <text x="24" y="403" style={{ fontSize: 16 }}>
            No evaluated contour/area output is established by point pilots.
          </text>
        </g>
      ) : (
        <g>
          <text style={{ fontSize: 17 }} x="24" y="32">
            What remains unresolved before a contour trial?
          </text>
          <Rows
            items={[
              ['Reference inclusion', 'Partial / altered profiles and missing annotations'],
              ['Proposed evaluator', 'Matching, contour quality and count/area rules'],
              ['Sample scope', 'One public training slide · exposure possible'],
              ['Meaning of the measurement', '2D profiles; no population or clinical claim'],
            ]}
          />
          <text x="24" y="403" style={{ fontSize: 16 }}>
            No new medical run, clinical adjudication or publication.
          </text>
        </g>
      )}
    </svg>
  );
}
const titles = {
  inputs: 'An object inventory is more than a count',
  helpers: 'Declare regional assistance',
  detail: 'A teaching zoom removes search',
  outline: 'Reference reveal is not inference',
  coordinates: 'Keep one slide coordinate frame',
  duplicate: 'Reconcile overlapping views',
  area: 'Square the pixel spacing',
  inventory: 'Tie every row to its geometry',
  conditions: 'Point pilots cover a narrower task',
  limits: 'Retain the unresolved boundaries',
};
export function HubmapOutput({ state }: { state: HubmapState }) {
  const reveal = hubmapReveal(state);
  return (
    <aside className={styles.storyOutput} data-hubmap-output={state.scene}>
      <h4>{titles[state.scene]}</h4>
      {state.scene === 'inputs' ? (
        <>
          <p>
            The proposed task asks a solver to find glomerular profiles in native PAS imagery, keep
            separate instance contours, and return an inventory with centers and calibrated areas.
          </p>
          <p>
            The reader references are withheld at the start. A contour set alone is not evidence of
            an exhaustive count.
          </p>
          <small>Public HuBMAP training example · CC BY 4.0 · no new model execution.</small>
        </>
      ) : state.scene === 'helpers' ? (
        <>
          <p>
            Source cortex and medulla regions supply optional anatomical context. They are rough
            expert estimates, not object-level answers or a complete annotation-validity mask.
          </p>
          <p>
            Retained point-only trials received the image, a GT-free overview and crop helper; these
            regional masks were not supplied.
          </p>
          <small>
            Declare this assistance as its own condition. Unannotated tissue is not an adjudicated
            negative.
          </small>
        </>
      ) : state.scene === 'detail' ? (
        <>
          <p>
            The full slide is roughly 13k × 18k pixels. The displayed 1600-pixel crop covers 1040 µm
            on each side.
          </p>
          <p>
            The first reference polygon chose this crop. The animation explains its location; it is
            not a logged agent search or a fair detection test.
          </p>
          <small>
            Native crop pixels are JPEG-encoded for display. Geometry uses unchanged source
            coordinates.
          </small>
        </>
      ) : state.scene === 'outline' ? (
        <>
          <p>
            Reveal an actual source polygon over the same PAS pixels. Annotation began with
            automated segmentation and expert correction; its clinical completeness is not
            independently adjudicated here.
          </p>
          <p>
            The dashed teal boundary is a reader reference. It is never a submitted contour or a
            simulated solver step.
          </p>
          <small>The reference-selected crop also contains neighbouring partial profiles.</small>
        </>
      ) : state.scene === 'coordinates' ? (
        <>
          <p>
            Compute a polygon area centroid in the local crop, then add the crop origin to return to
            the full-slide frame. The same transform applies to every contour vertex.
          </p>
          {reveal && (
            <p data-hubmap-coordinate-value>
              ref-001 → ({number(first.center_level0[0])}, {number(first.center_level0[1])}) level-0
              px.
            </p>
          )}
          <small>
            Origin at upper left, x right, y down. Area centroid is a derived convenience, not an
            independently annotated center.
          </small>
        </>
      ) : state.scene === 'duplicate' ? (
        <>
          <p>
            These two native crops deliberately contain the same reference object. Their different
            local centers become identical after adding their respective origins.
          </p>
          {reveal && (
            <table data-hubmap-local-centers>
              <thead>
                <tr>
                  <th>Tile</th>
                  <th>Local x, y (px)</th>
                </tr>
              </thead>
              <tbody>
                {ref.duplicate.local_centers.map((p, i) => (
                  <tr key={i}>
                    <td>{i + 1}</td>
                    <td>{p.map(number).join(', ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <small>
            This exact duplicate illustrates reconciliation. Real candidate matching needs a
            declared policy; no agent duplicate error is asserted.
          </small>
        </>
      ) : state.scene === 'area' ? (
        <>
          <p>
            Polygon area is measured in square pixels using the original ring. With equal x/y
            spacing, multiply by 0.65 × 0.65, not by 0.65 once.
          </p>
          {reveal && (
            <p data-hubmap-area-value>
              {number(first.area_px2)} px² → {number(first.area_um2)} µm².
            </p>
          )}
          <small>
            This is an area of a two-dimensional tissue section. It does not infer whole-object
            volume or a whole-kidney count.
          </small>
        </>
      ) : state.scene === 'inventory' ? (
        <>
          <p>
            Proposed files: <code>glomeruli.geojson</code> and <code>inventory.csv</code>. Join by a
            stable ID; store centers in level-0 pixels and areas in µm².
          </p>
          {reveal && (
            <table data-hubmap-worked-rows>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>x, y (px)</th>
                  <th>µm²</th>
                </tr>
              </thead>
              <tbody>
                {ref.objects.slice(0, hubmapRows(state.view)).map((o) => (
                  <tr key={o.id}>
                    <td>{o.id}</td>
                    <td>{o.center_level0.map((v) => Math.round(v)).join(', ')}</td>
                    <td>{Math.round(o.area_um2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          <small>
            Reference-derived worked rows, rounded for display. ref-NNN is source-array order
            because original IDs repeat. Full values and a GeoJSON feature are retained in the
            teaching pack.
          </small>
        </>
      ) : state.scene === 'conditions' ? (
        <>
          <p>
            The original and revised diagnostic tasks both asked for point centers. Their private
            references match these source polygons exactly; neither evaluated segmentation contours
            or area measurements.
          </p>
          <p>
            The revised protocol emphasizes reference recall. Its one-to-one matcher accepts points
            inside or within 50 µm of a polygon; unmatched candidates await review.
          </p>
          <small>
            Valid-file reward, point matching and clinical correctness are distinct. Existing trial
            outcomes remain unchanged.
          </small>
        </>
      ) : (
        <>
          <p>
            A contour trial still needs frozen instructions, instance-matching and area-quality
            rules, and a clear policy for partial or altered profiles. Optional helpers must be
            declared.
          </p>
          <p>
            Only three archive members were acquired and checked. The full 33.6 GB archive checksum
            was not verified.
          </p>
          <small>
            One public training slide; possible exposure, unresolved reference completeness.
            Portable teaching HTML contains reader references and is not a solver packet.
          </small>
        </>
      )}
    </aside>
  );
}
