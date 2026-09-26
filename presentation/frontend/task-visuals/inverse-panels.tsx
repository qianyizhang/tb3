import type { StoryPlan } from '../types';
import type { StoryState } from './story-timeline';
import styles from './task-visual.module.css';
import objectImage from '../../assets/teaching-fixtures/inverse-problems-v1/object.png?inline';
import sinogram from '../../assets/teaching-fixtures/inverse-problems-v1/ct-sinogram.png?inline';
import reconstructed from '../../assets/teaching-fixtures/inverse-problems-v1/ct-reconstruction.png?inline';
import kspace from '../../assets/teaching-fixtures/inverse-problems-v1/mri-kspace.png?inline';
import sampled from '../../assets/teaching-fixtures/inverse-problems-v1/mri-sampled.png?inline';
import zerofill from '../../assets/teaching-fixtures/inverse-problems-v1/mri-zero-filled.png?inline';
import raw from '../../assets/teaching-fixtures/inverse-problems-v1/fixture.json?raw';
const fixture = JSON.parse(raw) as {
  ct: { relative_reprojection_l2: number };
  mri: { sampled_complex_coefficient_max_error: number };
};
export function InverseScene({ plan, state }: { plan: StoryPlan; state: StoryState }) {
  if (plan.recipe !== 'inverse-v1' || state.recipe !== 'inverse-v1') return null;
  const ct = plan.acquisition === 'ct-parallel';
  return (
    <>
      <div className={styles.mobileInverse}>
        {[
          ['Constructed object', objectImage, 1],
          [
            ct ? 'Line integrals' : 'log |k-space|',
            ct ? sinogram : state.observations > 0.5 ? sampled : kspace,
            1,
          ],
          [
            ct ? 'FBP image' : 'Zero-filled magnitude',
            ct ? reconstructed : zerofill,
            state.reconstruction,
          ],
        ].map(([label, src, opacity]) => (
          <figure key={String(label)}>
            <img src={String(src)} alt={String(label)} style={{ opacity: Number(opacity) }} />
            <figcaption>{label}</figcaption>
          </figure>
        ))}
        <p>{ct ? 'y = R x; compare R x̂ with y' : 'y = M F x; x̂ = F⁻¹ y'}</p>
      </div>
      <svg
        className={`${styles.operationCanvas} ${styles.inverseCanvas}`}
        viewBox="0 0 600 420"
        role="img"
        aria-label={
          ct
            ? 'Parallel-beam measurements and reconstructed image'
            : 'Complex Fourier sampling and zero-filled magnitude image'
        }
      >
        <text x="24" y="32">
          {ct ? 'Parallel-beam CT · 90-angle fixture' : 'Cartesian MRI · single-channel fixture'}
        </text>
        <image href={objectImage} x="25" y="65" width="125" height="125" />
        <text x="25" y="214" fontSize="14">
          Constructed object
        </text>
        <text x="160" y="135" fontSize="25">
          →
        </text>
        <image
          href={ct ? sinogram : state.observations > 0.5 ? sampled : kspace}
          x="205"
          y="65"
          width="160"
          height="155"
          preserveAspectRatio="xMidYMid meet"
        />
        <text x="205" y="245" fontSize="14">
          {ct ? 'Line integrals' : 'log |k-space| display'}
        </text>
        <text x="380" y="135" fontSize="25">
          →
        </text>
        <image
          href={ct ? reconstructed : zerofill}
          x="425"
          y="65"
          width="150"
          height="150"
          opacity={state.reconstruction}
        />
        <text x="425" y="245" fontSize="14">
          {ct ? 'FBP image' : 'Zero-filled |image|'}
        </text>
        <text x="25" y="307" fontSize="20">
          {ct
            ? 'y = R x; reconstruct x̂, then compare R x̂ to y'
            : 'y = M F x; zero-filled x̂ = F⁻¹ y'}
        </text>
        <text x="25" y="350" fontSize="16">
          {ct
            ? 'Residual is measured in projection space.'
            : 'Consistency is checked on complex sampled coefficients.'}
        </text>
        <text x="25" y="390" fontSize="16">
          Synthetic object and arrays · no patient anatomy or clinical result
        </text>
      </svg>
    </>
  );
}
export function InverseOutput({ plan, state }: { plan: StoryPlan; state: StoryState }) {
  if (plan.recipe !== 'inverse-v1' || state.recipe !== 'inverse-v1') return null;
  const ct = plan.acquisition === 'ct-parallel';
  return (
    <aside className={styles.storyOutput}>
      <strong>
        {ct ? 'Reconstruction and reprojection' : 'Sampling consistency is not missing information'}
      </strong>
      <p>
        {ct
          ? 'Fixture: 128² object, 90 parallel angles, ramp-filter FBP.'
          : 'Fixture: single-channel 128² array, every fourth row plus central eight rows. Zero-filled inverse FFT.'}
      </p>
      <p>
        {ct ? 'Relative projection residual:' : 'Sampled complex coefficient max error:'}{' '}
        <b>
          {state.residual > 0
            ? ct
              ? fixture.ct.relative_reprojection_l2.toFixed(6)
              : fixture.mri.sampled_complex_coefficient_max_error.toExponential(3)
            : 'check pending'}
        </b>
      </p>
      <p>
        {ct
          ? 'Actual sparse-CT task: 256² phantom, noisy 256 × 30 sinogram. Required output: reconstruction.npy.'
          : 'Actual knee-MRI task: accelerated multi-coil measurements, coil sensitivities and sampling mask; TV regularization. Single-channel zero fill is only a contrast example.'}
      </p>
      <p>L1 README / L2 approach / L3 software design are distinct assistance conditions.</p>
      <p>
        Upstream solver-visible reference staging remains unverified. No upstream reference arrays
        are embedded here.
      </p>
    </aside>
  );
}
