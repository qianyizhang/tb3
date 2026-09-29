import {
  detectionPacks,
  detectionReveal,
  type AutoMedDetectionState,
  type DetectionPack,
} from './automed-full-detection';
import shared from './task-visual.module.css';
import css from './automed-full-detection.module.css';

const SCENE_TITLES = {
  input: 'Inspect the source image',
  coordinate: 'Return to original pixels',
  classes: 'Choose the exact class string',
  submission: 'Save one JSON per case',
  reference: 'Reveal upstream labels',
  limits: 'What remains unverified',
} as const;
const CLASS_NOTES = {
  bccd: 'The Full task uses three blood-cell classes. The selected upstream field and its labels are separate from the Full private case set.',
  dentex:
    'Source annotations have quadrant, tooth position and disease fields. Full scoring compares disease class strings, not tooth IDs.',
  grazpedwri:
    'The Full task uses nine wrist-finding classes. Source annotation classes remain covered until reader reveal.',
  'vindr-cxr':
    'Fourteen thoracic categories are named in task guidance; no source image or label is available here.',
};
function SymbolicCoordinateGrid({ scan }: { scan: number }) {
  const u = 0.14 + 0.72 * Math.min(1, Math.max(0, scan)),
    x = 30 + 300 * u;
  return (
    <figure className={css.imageFrame} data-detection-source="symbolic-coordinate-grid">
      <div className={css.imageHead}>
        <b>Symbolic coordinate plane</b>
        <span>W and H unknown; no image or finding</span>
      </div>
      <svg
        viewBox="0 0 370 280"
        role="img"
        aria-label="Symbolic top-left coordinate plane with a moving cyan probe; no patient data"
      >
        <rect x="30" y="30" width="300" height="210" fill="#122233" stroke="#627c8e" />
        {Array.from({ length: 9 }, (_, i) => (
          <line key={'v' + i} x1={60 + i * 30} y1="30" x2={60 + i * 30} y2="240" stroke="#294457" />
        ))}
        {Array.from({ length: 6 }, (_, i) => (
          <line key={'h' + i} x1="30" y1={60 + i * 30} x2="330" y2={60 + i * 30} stroke="#294457" />
        ))}
        <g fill="#c5d9e5" fontSize="12">
          <text x="12" y="24">
            0
          </text>
          <text x="270" y="20">
            x → W px
          </text>
          <text x="35" y="261">
            y ↓ H px
          </text>
          <text x="130" y="261">
            u = x/W; v = y/H
          </text>
        </g>
        <g stroke="#18c6d4" strokeWidth="2">
          <line x1={x} y1="30" x2={x} y2="240" />
          <line x1="30" y1="135" x2="330" y2="135" />
        </g>
        <circle cx={x} cy="135" r="4" fill="#18c6d4" />
        <text x="45" y="225" fill="#a7edf3" fontSize="13">
          Illustrative probe: u={u.toFixed(2)}, v=0.50
        </text>
      </svg>
      <figcaption>
        Cyan solid = coordinate probe. Grid units are illustrative; no radiograph, box or diagnosis.
      </figcaption>
    </figure>
  );
}
function ImageFrame({
  pack,
  scan = 0,
  reference = false,
}: {
  pack: DetectionPack;
  scan?: number;
  reference?: boolean;
}) {
  const w = pack.source.width_px,
    h = pack.source.height_px;
  if ((!pack.image || !w || !h) && scan > 0) return <SymbolicCoordinateGrid scan={scan} />;
  if (!pack.image || !w || !h)
    return (
      <div className={css.missing} data-detection-source="unavailable">
        <b>Source image unavailable</b>
        <span>
          Credentialed VinDr-CXR data was not accessed. This empty image socket is a protocol
          diagram, not a radiograph.
        </span>
      </div>
    );
  const x = Math.round(w * (0.14 + 0.72 * Math.min(1, Math.max(0, scan))));
  return (
    <figure className={css.imageFrame} data-detection-source="upstream-image">
      <div className={css.imageHead}>
        <b>{pack.source.image}</b>
        <span>
          {w} × {h} px · upstream source, not a verified Full case
        </span>
      </div>
      <svg
        viewBox={`0 0 ${w} ${h}`}
        role="img"
        aria-label={
          reference
            ? 'Upstream image with source annotations revealed'
            : 'Unmarked upstream source image'
        }
      >
        <image href={pack.image} x="0" y="0" width={w} height={h} />
        {scan > 0 && !reference && (
          <g className={css.ruler} aria-hidden="true">
            <line x1={x} y1="0" x2={x} y2={h} />
            <line x1="0" y1={Math.round(h / 2)} x2={w} y2={Math.round(h / 2)} />
            <circle cx={x} cy={Math.round(h / 2)} r={Math.max(4, w * 0.009)} />
            <rect
              x={Math.max(0, Math.min(w - w * 0.25, x - w * 0.125))}
              y={h * 0.375}
              width={w * 0.25}
              height={h * 0.25}
            />
          </g>
        )}
        {reference && (
          <g className={css.sourceBoxes} data-detection-reference="upstream-source-label">
            {pack.reference.source_boxes.map((b, i) => (
              <g key={b.id}>
                <rect
                  x={b.xyxy[0]}
                  y={b.xyxy[1]}
                  width={b.xyxy[2] - b.xyxy[0]}
                  height={b.xyxy[3] - b.xyxy[1]}
                />
                <text x={b.xyxy[0]} y={Math.max(18, b.xyxy[1] - 4)}>
                  {i + 1}
                </text>
              </g>
            ))}
          </g>
        )}
      </svg>
      <figcaption>Official upstream image · native aspect ratio · origin at upper left</figcaption>
    </figure>
  );
}
function Input({ pack }: { pack: DetectionPack }) {
  return (
    <div className={css.inputScene} data-detection-input>
      <ImageFrame pack={pack} />
      <div className={css.note}>
        <b>Solver sees an image, not a box</b>
        <p>
          {pack.image
            ? 'The official upstream example shows the visual task; its membership in the Full Detection100 split has not been established.'
            : 'No native input can be shown under the official access conditions.'}
        </p>
        <small>Full harness expects `public/{'{case_id}'}/image.png`.</small>
      </div>
    </div>
  );
}
function ScanZoom({ pack, scan }: { pack: DetectionPack; scan: number }) {
  const w = pack.source.width_px,
    h = pack.source.height_px;
  if (!pack.image || !w || !h) return null;
  const x = w * (0.14 + 0.72 * Math.min(1, Math.max(0, scan)));
  const cw = w * 0.25,
    ch = h * 0.25;
  const sx = Math.max(0, Math.min(w - cw, x - cw / 2));
  return (
    <div className={css.zoom} data-detection-zoom>
      <b>Source crop · ¼ width and height</b>
      <svg
        viewBox={`${sx} ${h * 0.375} ${cw} ${ch}`}
        role="img"
        aria-label="Magnified unlabeled source-image inspection window"
      >
        <image href={pack.image} x="0" y="0" width={w} height={h} />
      </svg>
      <small>Unlabeled crop for inspection; not a detection or supplied location.</small>
    </div>
  );
}
function Coordinate({ pack, state }: { pack: DetectionPack; state: AutoMedDetectionState }) {
  const w = pack.source.width_px;
  const x = w ? Math.round(w * (0.14 + 0.72 * Math.min(1, Math.max(0, state.scan)))) : null;
  return (
    <div className={css.two} data-detection-operation>
      <ImageFrame pack={pack} scan={Math.max(0.001, state.scan)} />
      <div className={css.stack}>
        <b>Locate in source pixels</b>
        <ScanZoom pack={pack} scan={Math.max(0.001, state.scan)} />
        {pack.image && (
          <small>
            <i className={css.rulerKey} /> Cyan solid = coordinate probe;{' '}
            <i className={css.cropKey} /> cyan dashed = inspection crop. Neither marks a finding.
          </small>
        )}
        <p>
          Search the entire image. If inference resizes it, convert both corners back to the
          original width and height.
        </p>
        {w && (
          <div className={css.equation}>
            <span>Source x coordinate</span>
            <strong>{x} px</strong>
            <span>Hypothetical 0.5× inference x</span>
            <strong>{Math.round((x || 0) / 2)} px</strong>
            <small>
              General mapping: x<sub>source</sub> = x<sub>model</sub> × W<sub>source</sub>/W
              <sub>model</sub>; use the corresponding height ratio for y. The actual SVG display
              size is not the inference grid.
            </small>
          </div>
        )}
        <code>
          0 ≤ x1 &lt; x2 ≤ W<br />0 ≤ y1 &lt; y2 ≤ H
        </code>
        {!w && (
          <div className={css.equation}>
            <span>Return to original pixels</span>
            <strong>x = u × W</strong>
            <span>Keep the vertical scale separate</span>
            <strong>y = v × H</strong>
            <small>
              For an inference grid Wm × Hm: xsource = xmodel × W/Wm; ysource = ymodel × H/Hm.
              Actual W and H require the acquired source PNG.
            </small>
          </div>
        )}
        {pack.key === 'vindr-cxr' && (
          <p className={css.muted}>
            Original PNG geometry must be available before any numeric box can be claimed.
          </p>
        )}
      </div>
    </div>
  );
}
function Classes({ pack }: { pack: DetectionPack }) {
  return (
    <div className={css.classes} data-detection-classes>
      <div>
        <b>{pack.source.classes.length} exact task classes</b>
        <div className={css.chips}>
          {pack.source.classes.map((c) => (
            <span key={c}>{c}</span>
          ))}
        </div>
      </div>
      <div className={css.note}>
        <b>String equality, case-insensitive</b>
        <p>{CLASS_NOTES[pack.key]}</p>
        <p>
          The common package prompt accidentally says “14 VinDr-CXR disease names” for every task.
          Use this task’s config/model guidance and the class-aware scorer instead.
        </p>
      </div>
    </div>
  );
}
function Submission({ pack }: { pack: DetectionPack }) {
  return (
    <div className={css.two} data-detection-output-schema>
      <div className={css.schema}>
        <b>Required path</b>
        <code>agents_outputs/{'{case_id}'}/prediction.json</code>
        <b>Current illustrative content</b>
        <pre>{'{"boxes": []}'}</pre>
        <small>No saved prediction, confidence, mAP or patient result.</small>
      </div>
      <div className={css.stack}>
        <b>Each future box</b>
        <code>{'{"class":"…", "score":0..1, "x1":…, "y1":…, "x2":…, "y2":…}'}</code>
        <p>
          Coordinates use original image pixels. The formatter allows `score` to be omitted, but AP
          ranks missing scores as 1.0; a real prediction should supply it.
        </p>
        <p>
          One JSON is needed for every case. The package contains no images to populate those
          folders here.
        </p>
      </div>
    </div>
  );
}
function Reference({ pack, reveal }: { pack: DetectionPack; reveal: boolean }) {
  if (!pack.image)
    return (
      <div className={css.covered} data-detection-reference-state="unavailable">
        <b>No source or Full reference available</b>
        <p>PhysioNet access is credentialed. A reveal cannot show a label that was not acquired.</p>
      </div>
    );
  if (!reveal)
    return (
      <div className={css.covered} data-detection-reference-state="covered">
        <b>Upstream source labels covered</b>
        <p>
          Use the reader reference control to inspect the official source annotations. They were not
          supplied as this Full task’s private boxes.
        </p>
      </div>
    );
  return (
    <div className={css.two} data-detection-reference-state="revealed">
      <ImageFrame pack={pack} reference />
      <div className={css.stack}>
        <b>Official upstream annotations · {pack.reference.source_box_count} boxes</b>
        <small>
          <i className={css.lineKey} /> Amber dashed = upstream source label; no Full private GT or
          model prediction.
        </small>
        <div className={css.refList}>
          {pack.reference.source_boxes.map((b, i) => (
            <div key={b.id}>
              <b>
                #{i + 1} {b.class}
              </b>
              <code>{b.xyxy.join(', ')} px</code>
            </div>
          ))}
        </div>
        <p>Source labels only; Full private boxes remain absent.</p>
      </div>
    </div>
  );
}
function Limits({ pack }: { pack: DetectionPack }) {
  return (
    <div className={css.limits} data-detection-limits>
      <div>
        <b>What is real</b>
        <p>
          {pack.image
            ? 'Official upstream image and matching raw source annotation, verified by source hash.'
            : 'Pinned task contract and official credentialed-access response.'}
        </p>
      </div>
      <div>
        <b>What is absent</b>
        <p>
          Full Detection100 staged case, private `boxes.json`, saved prediction, model run, and mAP.
        </p>
      </div>
      <div>
        <b>How scoring would work</b>
        <p>
          Rank by `score`, match same-class boxes at IoU ≥ 0.5, compute 101-point AP per class and
          mean over classes with GT. This is a contract, not a result.
        </p>
      </div>
    </div>
  );
}
export function AutoMedDetectionScene({ state }: { state: AutoMedDetectionState }) {
  const pack = detectionPacks[state.recipe];
  const reveal = detectionReveal(state, pack);
  return (
    <section
      className={css.scene}
      data-detection-scene={state.scene}
      data-detection-task={pack.key}
      data-detection-basis={pack.image ? 'mixed' : 'symbolic'}
    >
      <h3>
        {!pack.image && state.scene === 'reference'
          ? 'Reference unavailable'
          : !pack.image && state.scene === 'input'
            ? 'Source image unavailable'
            : SCENE_TITLES[state.scene]}
      </h3>
      {state.scene === 'input' && <Input pack={pack} />}
      {state.scene === 'coordinate' && <Coordinate pack={pack} state={state} />}
      {state.scene === 'classes' && <Classes pack={pack} />}
      {state.scene === 'submission' && <Submission pack={pack} />}
      {state.scene === 'reference' && <Reference pack={pack} reveal={reveal} />}
      {state.scene === 'limits' && <Limits pack={pack} />}
    </section>
  );
}
export function AutoMedDetectionOutput({ state }: { state: AutoMedDetectionState }) {
  const pack = detectionPacks[state.recipe];
  const reveal = detectionReveal(state, pack);
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-detection-output>
      <b>{state.scene === 'input' ? 'Input role' : 'Output contract'}</b>
      {state.scene === 'input' ? (
        <p>
          {pack.image
            ? 'Official upstream image only. Full split membership unverified.'
            : 'No native VinDr-CXR image available under credentialed access.'}
        </p>
      ) : (
        <p>
          `prediction.json` needs source-pixel boxes with class string and `score`. Current pack
          contains an empty schema, not a detector result.
        </p>
      )}
      {state.scene !== 'input' && (
        <>
          <b>Reference boundary</b>
          <p>
            {reveal
              ? 'Upstream source labels shown to reader; Full private boxes remain absent.'
              : pack.image
                ? 'Upstream source labels covered; Full private boxes absent.'
                : 'No reference asset acquired.'}
          </p>
          <small>Full release harness · IoU 0.5 · no model or grader run</small>
        </>
      )}
    </aside>
  );
}
