import {
  dentexImage,
  dentexOutput,
  dentexReference,
  dentexRevealed,
  dentexSource,
  type DentexBox,
  type RexDentexState,
} from './rexmle-dentex';
import shared from './task-visual.module.css';
import css from './rexmle-dentex.module.css';

const labels = dentexReference.category_names_by_source_id;

function Radiograph({
  reference = false,
  ruler = false,
}: {
  reference?: boolean;
  ruler?: boolean;
}) {
  return (
    <figure className={css.radiograph} data-dentex-input>
      <div className={css.imageHead}>
        <b>train_266.png</b>
        <span>1976 × 976 source pixels · top-left origin</span>
      </div>
      <svg
        viewBox="0 0 1976 976"
        role="img"
        aria-label={
          reference
            ? 'Source panoramic dental radiograph with five reader-only annotation boxes'
            : 'Source panoramic dental radiograph without reference boxes or prediction'
        }
      >
        <image href={dentexImage} x="0" y="0" width="1976" height="976" />
        {ruler && (
          <g className={css.ruler} aria-hidden="true">
            <line x1="0" y1="488" x2="1976" y2="488" />
            <line x1="988" y1="0" x2="988" y2="976" />
            <circle cx="988" cy="488" r="24" />
            <text x="1008" y="463">
              (988, 488) px · coordinate ruler
            </text>
          </g>
        )}
        {reference && (
          <g className={css.refBoxes} data-dentex-reference>
            {dentexReference.boxes.map((box, i) => (
              <g key={box.annotation_id}>
                <rect x={box.bbox[0]} y={box.bbox[1]} width={box.bbox[2]} height={box.bbox[3]} />
                <text x={box.bbox[0]} y={Math.max(34, box.bbox[1] - 10)}>
                  {i + 1}
                </text>
              </g>
            ))}
          </g>
        )}
      </svg>
      <figcaption>
        Official DENTEX source image · ReX public test input · original aspect ratio preserved
      </figcaption>
    </figure>
  );
}

function Split() {
  return (
    <div className={css.split} data-dentex-split>
      <div>
        <b>705</b>
        <span>fully labeled source images</span>
      </div>
      <span className={css.arrow}>seed 42 →</span>
      <div>
        <b>564</b>
        <span>ReX public train</span>
      </div>
      <div className={css.selected}>
        <b>141</b>
        <span>ReX private-label test · this image</span>
      </div>
    </div>
  );
}

function Localize(state: RexDentexState) {
  return (
    <div className={css.twoColumn} data-dentex-localize>
      <Radiograph ruler />
      <div className={css.operation}>
        <h4>Localize in the full panorama</h4>
        <p>
          Search the entire image; no lesion location is supplied. The crosshair is a coordinate
          ruler, not a tooth, disease label or detected point.
        </p>
        <div className={css.formula}>
          <b>Box geometry</b>
          <code>[x, y, width, height]</code>
          <span>Origin: upper left. Width and height extend right and down in source pixels.</span>
        </div>
        <div className={css.formula}>
          <b>For each proposed box</b>
          <span>
            Assign quadrant → tooth enumeration → diagnosis, then confidence. The three IDs describe
            one localized finding.
          </span>
        </div>
        <small>
          {state.box > 0.5
            ? 'Box encoding step selected; no coordinates saved.'
            : 'Coordinate operation visible; no candidate box drawn or saved.'}
        </small>
      </div>
    </div>
  );
}

function Encode(state: RexDentexState) {
  return (
    <div className={css.encode} data-dentex-output-schema>
      <div className={css.schema}>
        <b>Required submission path</b>
        <code>submission/submission.csv</code>
        <div className={css.csv}>
          <span>image_id</span>
          <span>predictions_json</span>
          <strong>train_266</strong>
          <strong>predictions/train_266.json</strong>
        </div>
        <b>Per-image JSON · presently empty</b>
        <pre>{'{"annotations": []}'}</pre>
        <small>No retained model prediction, box coordinates, confidence or AP.</small>
      </div>
      <div className={css.hierarchy}>
        <b>Each future annotation must combine</b>
        <div>
          <em>1</em>
          <span>Location</span>
          <code>bbox: [x,y,w,h]</code>
        </div>
        <div>
          <em>2</em>
          <span>Quadrant</span>
          <code>category_id_1</code>
        </div>
        <div>
          <em>3</em>
          <span>Tooth position</span>
          <code>category_id_2</code>
        </div>
        <div>
          <em>4</em>
          <span>Finding type</span>
          <code>category_id_3</code>
        </div>
        <div>
          <em>5</em>
          <span>Confidence</span>
          <code>score</code>
        </div>
        <p>
          {state.labels > 0.5
            ? 'The three category IDs belong to the same box. Source IDs must remain 0-based in the source reference.'
            : 'Select label encoding to inspect the three-level record.'}
        </p>
      </div>
    </div>
  );
}

function BoxRow({ box, index }: { box: DentexBox; index: number }) {
  return (
    <div className={css.boxRow}>
      <b>#{index + 1}</b>
      <code>{box.bbox.map((n) => Number(n.toFixed(1))).join(', ')}</code>
      <span>
        Q {box.category_id_1}→{labels.categories_1[String(box.category_id_1)]}
      </span>
      <span>
        Tooth {box.category_id_2}→{labels.categories_2[String(box.category_id_2)]}
      </span>
      <span>
        {box.category_id_3}→{labels.categories_3[String(box.category_id_3)]}
      </span>
    </div>
  );
}

function Reference({ reveal }: { reveal: boolean }) {
  if (!reveal)
    return (
      <div className={css.covered} data-dentex-reference-covered>
        <b>Private source boxes covered</b>
        <p>
          Use the reference reveal control to mount all five original annotations. They are
          reader-only, never an agent prediction.
        </p>
      </div>
    );
  return (
    <div className={css.referenceScene}>
      <Radiograph reference />
      <div className={css.referenceList} data-dentex-reference-list>
        <b>Five original source boxes</b>
        <small>
          <i className={css.legendLine} /> Amber dashed = private reference; image = public input
        </small>
        {dentexReference.boxes.map((box, i) => (
          <BoxRow key={box.annotation_id} box={box} index={i} />
        ))}
        <p>
          IDs on the left are original 0-based source category IDs; arrows give source category
          names. Coordinates are [x,y,w,h] in native pixels.
        </p>
      </div>
    </div>
  );
}

function Audit() {
  const c = dentexReference.scorer_caveat;
  return (
    <div className={css.audit} data-dentex-category-audit>
      <h4>Unresolved pinned scorer mapping</h4>
      <p>
        The original source uses zero-based category IDs. Pinned ReX `grade.py` passes those
        ground-truth IDs through unchanged, then declares categories starting at one. This makes AP
        interpretation unsafe without a dedicated scorer fixture.
      </p>
      <div className={css.auditGrid}>
        <b>Field</b>
        <b>Source annotation IDs</b>
        <b>Grader category IDs</b>
        {(['quadrant', 'enumeration', 'diagnosis'] as const).map((k) => (
          <div className={css.auditRow} key={k}>
            <strong>{k}</strong>
            <code>{c.source_ids[k].join(' · ')}</code>
            <code>{c.grader_declared_ids[k].join(' · ')}</code>
          </div>
        ))}
      </div>
      <p>
        <strong>Example:</strong> source diagnosis ID 0 means “Impacted”; the pinned grader declares
        diagnosis ID 1 as “caries.” This is a source/scorer contract discrepancy, not a measured
        model error.
      </p>
    </div>
  );
}

const titles: Record<RexDentexState['scene'], string> = {
  input: 'One actual panoramic radiograph',
  localize: 'Search → image-pixel box geometry',
  encode: 'One box, three label fields',
  reference: 'Reader-only source boxes',
  audit: 'Why AP remains unresolved',
};

export function RexDentexScene({ state }: { state: RexDentexState }) {
  const reveal = dentexRevealed(state);
  return (
    <section
      className={css.scene}
      data-dentex-scene={state.scene}
      data-dentex-reference-state={reveal ? 'revealed' : 'hidden'}
    >
      <h3>{titles[state.scene]}</h3>
      {state.scene === 'input' && (
        <div className={css.inputScene}>
          <Radiograph />
          <Split />
        </div>
      )}
      {state.scene === 'localize' && <Localize {...state} />}
      {state.scene === 'encode' && <Encode {...state} />}
      {state.scene === 'reference' && <Reference reveal={reveal} />}
      {state.scene === 'audit' && <Audit />}
    </section>
  );
}

export function RexDentexOutput({ state }: { state: RexDentexState }) {
  const reveal = dentexRevealed(state);
  return (
    <aside className={`${shared.storyOutput} ${css.output}`} data-dentex-output>
      <b>{state.scene === 'input' ? 'Input' : 'Task record'}</b>
      {state.scene === 'input' ? (
        <p>
          One native 1976 × 976 panoramic X-ray. ReX selected it for the 141-case private-label test
          partition.
        </p>
      ) : (
        <p>
          Locate a box, then assign quadrant, tooth enumeration, diagnosis and score in the
          per-image JSON.
        </p>
      )}
      {state.scene !== 'input' && (
        <>
          <b>Output status</b>
          <p>
            {dentexOutput.status === 'not-retained'
              ? 'Empty schema only. No saved prediction or AP.'
              : 'Unexpected status'}
          </p>
        </>
      )}
      <b>Reference boundary</b>
      <p>
        {reveal
          ? 'Five original source annotations shown to the reader only.'
          : 'Private source boxes remain covered.'}
      </p>
      <small>DENTEX 7812323 · CC-BY-4.0 · source-derived image, symbolic output contract</small>
    </aside>
  );
}
