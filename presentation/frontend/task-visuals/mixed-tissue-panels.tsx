import { mixedTissue, mixedTissueView, type MixedTissueState } from './mixed-tissue';
import axial from '../../task-explorer/mixed-tissue/axial.png?inline';
import coronal from '../../task-explorer/mixed-tissue/coronal.png?inline';
import sagittal from '../../task-explorer/mixed-tissue/sagittal.png?inline';
import styles from './task-visual.module.css';

const images: Record<string, string> = { axial, coronal, sagittal };
export function MixedTissueScene({ state }: { state: MixedTissueState }) {
  const { slice, referenceVisible, witnessVisible } = mixedTissueView(state);
  const [x, y] = slice.witness_pixel;
  return (
    <>
      <p className={styles.mixedMobileMeta} data-mixed-orientation>
        {slice.plane.toUpperCase()} · right {slice.right} · down {slice.down}
        <br />
        LPS mm · 1.5 mm pixels · 223.5 mm field
        <br />
        CT level 50 / width 400 HU
      </p>
      <svg
        className={styles.operationCanvas}
        viewBox="0 0 600 420"
        role="img"
        aria-label={`${slice.plane} CT with supplied mask outlines${referenceVisible ? ' and explicit injected-region reference reveal' : '; private reference hidden'}`}
        data-mixed-plane={slice.plane}
      >
        <text x="24" y="25" fontSize="16">
          {slice.plane.toUpperCase()} · LPS mm · CT level 50 / width 400 HU
        </text>
        <svg x="125" y="40" width="340" height="340" viewBox={`0 0 ${slice.size} ${slice.size}`}>
          <image href={images[slice.plane]} width={slice.size} height={slice.size} />
          <g opacity={state.overlay} fill="none" strokeWidth="0.7">
            <path d={slice.paths.host} stroke="#57cabb" />
            <path d={slice.paths.donor} stroke="#6cafff" />
          </g>
          {referenceVisible && (
            <g data-mixed-reference opacity={state.reference}>
              <path d={slice.region_cells} fill="#f5b344" fillOpacity="0.45" />
              <path d={slice.paths.region} fill="none" stroke="#f5b344" strokeWidth="0.8" />
            </g>
          )}
          {witnessVisible && (
            <g
              data-mixed-witness
              opacity={state.witness}
              fill="none"
              stroke="#fff"
              strokeWidth="0.8"
            >
              <circle cx={x} cy={y} r="3.2" />
              <path d={`M${x - 5},${y}h10M${x},${y - 5}v10`} />
            </g>
          )}
        </svg>
        <text x="478" y="208" fontSize="19">
          {slice.right} →
        </text>
        <text x="278" y="403" fontSize="17">
          ↓ {slice.down}
        </text>
        <text x="24" y="70" fontSize="13">
          1.5 mm
        </text>
        <text x="24" y="89" fontSize="13">
          per pixel
        </text>
        <text x="24" y="343" fontSize="13">
          223.5 mm
        </text>
        <text x="24" y="362" fontSize="13">
          field
        </text>
      </svg>
    </>
  );
}

export function MixedTissueOutput({ state }: { state: MixedTissueState }) {
  const { referenceVisible, witnessVisible } = mixedTissueView(state);
  return (
    <aside className={styles.storyOutput} data-mixed-output>
      <strong>
        {referenceVisible
          ? 'Reference reveal · author-only key'
          : 'Audit the contents, not just the names'}
      </strong>
      {state.conditions > 0 ? (
        <table data-mixed-conditions>
          <tbody>
            <tr>
              <td>M01</td>
              <td>Whole organ; name absent</td>
            </tr>
            <tr>
              <td>M02</td>
              <td>Partial; all names present</td>
            </tr>
            <tr>
              <td>N01</td>
              <td>Unchanged; empty findings</td>
            </tr>
            <tr>
              <td>F01</td>
              <td>M02 data; pair-focused audit</td>
            </tr>
          </tbody>
        </table>
      ) : (
        <p>
          Teal: o327 / proposed duodenum.
          <br />
          Blue: o589 / remaining pancreas.
        </p>
      )}
      {state.conditions === 0 && (
        <p>
          {referenceVisible
            ? `Gold: ${mixedTissue.reference_volume_ml.toFixed(2)} mL reassigned from source pancreas. CT is unchanged.`
            : 'Both labels remain present in M02. The number of findings is unspecified; zero is allowed.'}
        </p>
      )}
      {witnessVisible ? (
        <div data-mixed-answer>
          <b>Example from the private key</b>
          <p>Host: o327 · included: pancreas</p>
          <code>LPS ({mixedTissue.witness_lps_mm.map((v) => v.toFixed(2)).join(', ')}) mm</code>
        </div>
      ) : (
        <p data-mixed-pending>
          Return host ID, included class and one physical LPS point. Reference answer hidden.
        </p>
      )}
      <p>
        Within 3 mm of an injected voxel centre.
        <br />
        No contour reconstruction or diagnosis.
      </p>
      <small>
        Three reference-centred crops, not blind search or a full audit. TotalSegmentator s1233 · CC
        BY 4.0; taxonomy Apache 2.0.
      </small>
    </aside>
  );
}
