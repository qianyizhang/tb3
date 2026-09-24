import { routeSampler, sampledImage } from './route-prefab';
import type { StoryState } from './story-timeline';
import styles from './task-visual.module.css';
export function StoryOutput({ state }: { state: StoryState }) {
  const sample = routeSampler.atDistanceFraction(state.cursor);
  const visible = state.index >= 2;
  const reveal =
    state.output >= 1 ? 1 : state.output > 0 ? (sample.column + 1) / routeSampler.columns : 0;
  const points = sample.profile
    .map(
      (v, i) =>
        `${(i / (sample.profile.length - 1)) * 300},${70 - Math.max(0, Math.min(1, v)) * 65}`,
    )
    .join(' ');
  return (
    <aside className={styles.storyOutput} lang="en" data-column={sample.column}>
      <strong>Route-conditioned image</strong>
      <p>One column per transverse sample line</p>
      <div className={styles.sampledImage}>
        <img
          src={sampledImage}
          alt="Scalar samples from the synthetic branching volume"
          style={{ clipPath: `inset(0 ${(1 - reveal) * 100}% 0 0)` }}
        />
        {state.output > 0 && <i style={{ left: `${sample.displayUV[0] * 100}%` }} />}
        {state.output === 0 && <span>Required output</span>}
      </div>
      <div className={styles.profile} style={{ visibility: visible ? 'visible' : 'hidden' }}>
        <div>
          Column {sample.column + 1} / {routeSampler.columns} · s = {sample.distanceM.toFixed(3)} m
        </div>
        <svg
          viewBox="0 0 300 76"
          role="img"
          aria-label="Same scalar profile as the selected image column"
        >
          <polyline points={points} fill="none" stroke="#557e93" strokeWidth="2.5" />
        </svg>
        <span>Transverse offset → · synthetic scalar (not HU)</span>
      </div>
      <p className={styles.equation}>I(s,u) = V(C(s) + u N(s))</p>
      <small>Gold: route · blue: source line and image column.</small>
    </aside>
  );
}
