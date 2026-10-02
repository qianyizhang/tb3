import { Component, lazy, Suspense, type ReactNode } from 'react';
import type { VisualProps } from './task-visuals/TaskVisual';
import type { RestorationView } from './contracts.generated';
import { views } from './explainers/registry';
import { SourceWarning } from './task-visuals/SourceWarning';

export interface ReaderProps extends VisualProps {
  view?: RestorationView;
}
const LegacyView = lazy(() =>
  import('./task-visuals/TaskVisual').then((m) => ({ default: m.TaskVisual })),
);
const LegacyWarning = lazy(() => import('./explainers/LegacyWarning'));

class LoadBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? (
      <p role="alert">
        The visual could not load. The task and its sources remain available.{' '}
        <button onClick={() => location.reload()}>Reload visual</button>
      </p>
    ) : (
      this.props.children
    );
  }
}
export function Explainer(props: ReaderProps) {
  if (props.view) {
    const View = views[props.view.family];
    return <View {...props} />;
  }
  return (
    <LoadBoundary key={props.plan?.id ?? props.entry.illustration.kind}>
      <Suspense fallback={<p role="status">Loading task visual…</p>}>
        <LegacyView {...props} />
      </Suspense>
    </LoadBoundary>
  );
}
export function ExplainerWarning({ plan, view }: Pick<ReaderProps, 'plan' | 'view'>) {
  if (view) return <SourceWarning warning={view.source.notice} />;
  if (!plan) return null;
  return (
    <LoadBoundary key={plan.id}>
      <Suspense fallback={null}>
        <LegacyWarning plan={plan} />
      </Suspense>
    </LoadBoundary>
  );
}
