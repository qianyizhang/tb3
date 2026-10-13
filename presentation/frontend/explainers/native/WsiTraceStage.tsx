import { useEffect, useId, useRef, useState } from 'react';
import type { WsiTracePayload, WsiTracePanel } from '../../contracts.generated';
import {
  fitBounds,
  intersect,
  level0ToPanel,
  paddedFraction,
  panelToLevel0,
  panBounds,
  zoomBounds,
  type Bounds,
  type XY,
} from './wsi-geometry';
import styles from './wsi-trace.module.css';

interface Props {
  payload: WsiTracePayload;
  stateId: string | null;
  chapterId: string;
  referenceShown: boolean;
  onReady: (ready: boolean) => void;
}
const bounds = (values: number[]): Bounds => [values[0], values[1], values[2], values[3]];
const number = (value: number) => Math.round(value).toLocaleString('en-US');
const rectText = (value: Bounds) =>
  `${number(value[0])}, ${number(value[1])} · ${number(value[2])} × ${number(value[3])} px`;
const pointer = (svg: SVGSVGElement, x: number, y: number): XY => {
  const point = svg.createSVGPoint();
  point.x = x;
  point.y = y;
  const mapped = point.matrixTransform(svg.getScreenCTM()!.inverse());
  return [mapped.x, mapped.y];
};

/** Retained RGB deliveries in level-0 geometry; no slide server or inference access. */
export function WsiTraceStage({ payload, stateId, chapterId, referenceShown, onReady }: Props) {
  const { input, observed } = payload;
  const defaultState = observed.states.find((state) => state.id === stateId) ?? observed.states[0];
  const [selectedState, setSelectedState] = useState(defaultState.id);
  const state = observed.states.find((item) => item.id === selectedState)!;
  const panels = observed.panels.filter((panel) => state.panel_ids.includes(panel.id));
  const [selectedId, setSelectedId] = useState(panels[0]?.id ?? '');
  const selected = panels.find((panel) => panel.id === selectedId) ?? panels[0];
  const full: Bounds = [0, 0, input.size_level0[0], input.size_level0[1]];
  const [viewport, setViewport] = useState<Bounds>(() => fitBounds(full, 1.5));
  const [point, setPoint] = useState<XY | null>(null);
  const [ready, setReady] = useState(false);
  const [imageSize, setImageSize] = useState<XY>([1, 1]);
  const [imageError, setImageError] = useState('');
  const delivery = payload.delivered_images.find(
    (image) => image.sha256 === selected?.delivery_sha256,
  );
  const drag = useRef<{ at: XY; view: Bounds; moved: boolean } | null>(null);
  const prefix = useId().replace(/:/g, '');
  const nativeBounds = selected ? bounds(selected.bounds_level0) : null;
  const rasterBounds = selected ? bounds(selected.raster_bounds) : null;
  const saved = chapterId === 'output' || chapterId === 'reference';
  useEffect(() => {
    let active = true;
    setReady(false);
    setImageError('');
    onReady(false);
    const decode = async (src: string) => {
      const image = new Image();
      image.src = src;
      await image.decode();
      return image;
    };
    void Promise.all([
      decode(input.overview),
      delivery ? decode(delivery.src) : Promise.resolve(null),
    ])
      .then(([, image]) => {
        if (!active) return;
        if (image) setImageSize([image.naturalWidth, image.naturalHeight]);
        setReady(true);
        onReady(true);
      })
      .catch((error: unknown) => {
        if (active)
          setImageError(error instanceof Error ? error.message : 'Retained image unavailable');
      });
    return () => {
      active = false;
    };
  }, [input.overview, delivery?.src, onReady]);
  const reset = () => {
    setViewport(fitBounds(full, 1.5));
    setPoint(null);
  };
  const selectPanel = (panel: WsiTracePanel) => {
    setSelectedId(panel.id);
    setPoint(null);
  };
  const selectState = (id: string) => {
    setSelectedState(id);
    setSelectedId(observed.states.find((item) => item.id === id)?.panel_ids[0] ?? '');
    reset();
  };
  const zoom = (factor: number) =>
    setViewport((view) => {
      const next = zoomBounds(view, factor);
      return next[2] >= 32 && next[2] <= full[2] * 8 ? next : view;
    });
  const imageRect = (panel: WsiTracePanel) => {
    const value = bounds(panel.raster_bounds);
    return { x: value[0], y: value[1], width: value[2], height: value[3] };
  };
  const validNative = nativeBounds ? intersect(nativeBounds, full) : null;
  const validRaster =
    validNative && rasterBounds && nativeBounds
      ? (() => {
          const p = level0ToPanel([validNative[0], validNative[1]], rasterBounds, nativeBounds);
          return [
            p[0],
            p[1],
            (validNative[2] * rasterBounds[2]) / nativeBounds[2],
            (validNative[3] * rasterBounds[3]) / nativeBounds[3],
          ] as Bounds;
        })()
      : null;
  const padding = nativeBounds ? paddedFraction(nativeBounds, [full[2], full[3]]) : 0;
  return (
    <div
      className={styles.stage}
      data-native-ready={String(ready)}
      data-native-state={state.id}
      data-native-renderer="planar"
      data-reference-visible={String(referenceShown)}
      data-native-reference-count={referenceShown ? payload.reference.polygons.length : 0}
      data-native-selected-panel={selected?.id ?? ''}
      data-native-selected-delivery={delivery?.sha256 ?? ''}
      data-native-footprint={nativeBounds?.join(',') ?? ''}
      data-native-selected-level0={point?.join(',') ?? ''}
      data-native-submitted-points={observed.points.length}
      data-native-viewport={viewport.join(',')}
    >
      <div className={styles.inventory}>
        <strong>Whole-slide search · retained views</strong>
        <span>
          {number(full[2])} × {number(full[3])} level-0 px · {observed.reads.length} logged reads
        </span>
      </div>
      <div className={styles.controls}>
        <label>
          Recorded inspection{' '}
          <select
            aria-label="WSI recorded inspection"
            value={state.id}
            onChange={(event) => selectState(event.target.value)}
          >
            {observed.states.map((item) => (
              <option key={item.id} value={item.id}>
                {item.label}
              </option>
            ))}
          </select>
        </label>
        {panels.length > 0 && (
          <label>
            Panel{' '}
            <select
              aria-label="WSI delivered panel"
              value={selected?.id ?? ''}
              onChange={(event) => {
                const panel = panels.find((item) => item.id === event.target.value)!;
                selectPanel(panel);
              }}
            >
              {panels.map((panel) => (
                <option key={panel.id} value={panel.id}>
                  {panel.label}
                </option>
              ))}
            </select>
          </label>
        )}
      </div>
      <div className={styles.grid}>
        <section className={styles.card} data-native-card>
          <header className={styles.heading}>
            <strong>01 / Supplied whole slide</strong>
            <span>Level-0 frame</span>
          </header>
          <svg
            className={styles.overview}
            viewBox={viewport.join(' ')}
            role="img"
            aria-label="Whole supplied slide in native level-0 pixels"
            tabIndex={0}
            onKeyDown={(event) => {
              const directions: Record<string, XY> = {
                ArrowLeft: [-1, 0],
                ArrowRight: [1, 0],
                ArrowUp: [0, -1],
                ArrowDown: [0, 1],
              };
              if (event.key in directions) {
                event.preventDefault();
                const direction = directions[event.key];
                setViewport((view) =>
                  panBounds(view, direction[0] * view[2] * 0.1, direction[1] * view[3] * 0.1),
                );
              } else if (event.key === '+' || event.key === '=') {
                event.preventDefault();
                zoom(1.5);
              } else if (event.key === '-') {
                event.preventDefault();
                zoom(1 / 1.5);
              } else if (event.key === 'Home') {
                event.preventDefault();
                reset();
              }
            }}
            onPointerDown={(event) => {
              event.currentTarget.setPointerCapture(event.pointerId);
              drag.current = {
                at: [event.clientX, event.clientY],
                view: viewport,
                moved: false,
              };
            }}
            onPointerMove={(event) => {
              if (!drag.current) return;
              const origin = drag.current;
              const transform = event.currentTarget.getScreenCTM()!;
              const dx = (origin.at[0] - event.clientX) / transform.a;
              const dy = (origin.at[1] - event.clientY) / transform.d;
              if (
                Math.abs(origin.at[0] - event.clientX) + Math.abs(origin.at[1] - event.clientY) >
                3
              )
                origin.moved = true;
              setViewport(panBounds(origin.view, dx, dy));
            }}
            onPointerUp={(event) => {
              if (drag.current && !drag.current.moved)
                setPoint(pointer(event.currentTarget, event.clientX, event.clientY));
              drag.current = null;
            }}
            onPointerCancel={() => {
              drag.current = null;
            }}
          >
            <defs>
              <clipPath id={`${prefix}-slide`}>
                <rect width={full[2]} height={full[3]} />
              </clipPath>
              <pattern
                id={`${prefix}-pad`}
                width={viewport[2] * 0.02}
                height={viewport[2] * 0.02}
                patternUnits="userSpaceOnUse"
              >
                <path
                  d={`M0 ${viewport[2] * 0.02}L${viewport[2] * 0.02} 0`}
                  stroke="#a08866"
                  strokeWidth={viewport[2] * 0.003}
                />
              </pattern>
              {selected && (
                <mask id={`${prefix}-outside`}>
                  <rect
                    x={nativeBounds![0]}
                    y={nativeBounds![1]}
                    width={nativeBounds![2]}
                    height={nativeBounds![3]}
                    fill="white"
                  />
                  <rect width={full[2]} height={full[3]} fill="black" />
                </mask>
              )}
            </defs>
            <rect width={full[2]} height={full[3]} fill="#eee9dc" />
            <image
              href={input.overview}
              width={input.overview_size[0] * input.overview_downsample}
              height={input.overview_size[1] * input.overview_downsample}
              preserveAspectRatio="none"
              clipPath={`url(#${prefix}-slide)`}
            />
            {selected && padding > 0 && (
              <rect
                x={nativeBounds![0]}
                y={nativeBounds![1]}
                width={nativeBounds![2]}
                height={nativeBounds![3]}
                fill={`url(#${prefix}-pad)`}
                mask={`url(#${prefix}-outside)`}
              />
            )}
            {referenceShown &&
              payload.reference.polygons.map((polygon) => (
                <polygon
                  key={polygon.id}
                  points={polygon.points.map((p) => p.join(',')).join(' ')}
                  fill={polygon.kind === 'tumor' ? '#c43f3433' : '#7864a033'}
                  stroke={polygon.kind === 'tumor' ? '#c43f34' : '#7864a0'}
                  strokeWidth={2}
                  vectorEffect="non-scaling-stroke"
                  strokeDasharray={polygon.kind === 'tumor' ? undefined : '6 4'}
                />
              ))}
            {panels.map((panel) => (
              <rect
                key={panel.id}
                x={panel.bounds_level0[0]}
                y={panel.bounds_level0[1]}
                width={panel.bounds_level0[2]}
                height={panel.bounds_level0[3]}
                fill={panel.id === selected?.id ? '#087e8b22' : 'transparent'}
                stroke={panel.id === selected?.id ? '#087e8b' : '#385951'}
                strokeWidth={panel.id === selected?.id ? 3 : 1}
                vectorEffect="non-scaling-stroke"
                onClick={() => selectPanel(panel)}
                style={{ cursor: 'pointer' }}
              />
            ))}
            {(saved ? observed.points : []).map((p, index) => (
              <circle key={index} cx={p.x} cy={p.y} r={viewport[2] * 0.006} fill="#087e8b" />
            ))}
            {point && (
              <g stroke="#24343b" strokeWidth={1.5} vectorEffect="non-scaling-stroke">
                <path
                  d={`M${point[0] - viewport[2] * 0.012} ${point[1]}h${viewport[2] * 0.024}M${point[0]} ${point[1] - viewport[3] * 0.018}v${viewport[3] * 0.036}`}
                />
              </g>
            )}
          </svg>
          <div className={styles.tools}>
            <button aria-label="WSI zoom in" onClick={() => zoom(1.5)}>
              ＋
            </button>
            <button aria-label="WSI zoom out" onClick={() => zoom(1 / 1.5)}>
              −
            </button>
            <button
              onClick={() => nativeBounds && setViewport(fitBounds(nativeBounds, 1.5))}
              disabled={!selected}
            >
              Fit panel
            </button>
            <button aria-label="Reset WSI view" onClick={reset}>
              Whole slide
            </button>
          </div>
          <p className={styles.note}>
            Drag to pan · arrows pan · + / − zoom · Home resets. Outline = selected recorded panel;
            this is not a search-coverage map.
          </p>
        </section>
        <section className={styles.card} data-native-card>
          <header className={styles.heading}>
            <strong>02 / Exact delivered montage</strong>
            <span>{delivery ? `Step ${delivery.step}` : 'No image delivery'}</span>
          </header>
          {delivery ? (
            <svg
              className={styles.montage}
              viewBox={`0 0 ${imageSize[0]} ${imageSize[1]}`}
              role="img"
              aria-label={`Exact delivered WSI image at step ${delivery.step}`}
            >
              <image href={delivery.src} width={imageSize[0]} height={imageSize[1]} />
              {panels
                .filter((panel) => panel.delivery_sha256 === delivery.sha256)
                .map((panel) => (
                  <rect
                    key={panel.id}
                    {...imageRect(panel)}
                    fill="transparent"
                    stroke={panel.id === selected?.id ? '#087e8b' : '#eee9dc'}
                    strokeWidth={panel.id === selected?.id ? 3 : 1}
                    vectorEffect="non-scaling-stroke"
                    onClick={() => selectPanel(panel)}
                    style={{ cursor: 'pointer' }}
                  />
                ))}
            </svg>
          ) : (
            <div className={styles.empty}>This recorded state has no delivered panel.</div>
          )}
          <p className={styles.note}>
            Original image bytes · panel outlines are reader controls. Labels and borders in the
            delivery are not tissue pixels.
          </p>
        </section>
        <section className={styles.card} data-native-card>
          <header className={styles.heading}>
            <strong>03 / Selected panel detail</strong>
            <span>{selected ? `Pyramid level ${selected.level}` : 'Saved output'}</span>
          </header>
          {delivery && selected && rasterBounds && validRaster ? (
            <svg
              className={styles.detail}
              viewBox={rasterBounds.join(' ')}
              role="img"
              aria-label="Exact selected WSI panel pixels"
              onClick={(event) =>
                setPoint(
                  panelToLevel0(
                    pointer(event.currentTarget, event.clientX, event.clientY),
                    rasterBounds,
                    nativeBounds!,
                  ),
                )
              }
            >
              <defs>
                <mask id={`${prefix}-padding`}>
                  <rect {...imageRect(selected)} fill="white" />
                  <rect
                    x={validRaster[0]}
                    y={validRaster[1]}
                    width={validRaster[2]}
                    height={validRaster[3]}
                    fill="black"
                  />
                </mask>
                <pattern
                  id={`${prefix}-detail-pad`}
                  width={12}
                  height={12}
                  patternUnits="userSpaceOnUse"
                >
                  <path d="M0 12L12 0" stroke="#a08866" strokeWidth={3} />
                </pattern>
              </defs>
              <image href={delivery.src} width={imageSize[0]} height={imageSize[1]} />
              {padding > 0 && (
                <rect
                  {...imageRect(selected)}
                  fill={`url(#${prefix}-detail-pad)`}
                  opacity={0.7}
                  mask={`url(#${prefix}-padding)`}
                />
              )}
            </svg>
          ) : (
            <div className={styles.empty}>
              {saved
                ? `${observed.points.length} points submitted`
                : 'This recorded state has no delivered panel.'}
            </div>
          )}
          <div className={styles.readout}>
            <strong>{selected?.label ?? state.label}</strong>
            {nativeBounds && <code>{rectText(nativeBounds)}</code>}
            {point && (
              <code data-native-point-readout>
                Reader cursor ({point.map(number).join(', ')}) level-0 px
                {point[0] < 0 || point[1] < 0 || point[0] >= full[2] || point[1] >= full[3]
                  ? ' · outside native extent'
                  : ''}
              </code>
            )}
            {padding > 0 && (
              <span className={styles.padding}>
                Hatched: outside native slide · {(padding * 100).toFixed(1)}% of this requested
                footprint. Pyramid padding is retained.
              </span>
            )}
            <span>{selected?.description ?? state.description}</span>
          </div>
        </section>
      </div>
      <div className={styles.legend}>
        <span className={styles.recordedKey}>Recorded footprint / solver points</span>
        {referenceShown && (
          <>
            <span className={styles.tumorKey}>Source tumor reference · red solid</span>
            <span className={styles.exclusionKey}>Source exclusion reference · purple dashed</span>
          </>
        )}
      </div>
      {saved && (
        <div className={styles.saved} data-native-saved-output>
          <strong>
            {observed.points.length === 0
              ? 'Saved answer: no points submitted.'
              : `Saved answer: ${observed.points.length} points submitted.`}
          </strong>
          <code>{observed.answer_text}</code>
        </div>
      )}
      {imageError && <p role="alert">Retained image decode failed: {imageError}</p>}
      <p className={styles.boundary}>
        Detail enlarges exact delivered pixels; it does not fetch full-resolution slide data. Logged
        helper and pyramid reads remain distinct; these views do not establish complete search
        coverage.
      </p>
    </div>
  );
}
