import { type ReactNode } from 'react';
import type { BriefField, TaskEntry, StoryPlan } from './types';
import { TaskVisual } from './task-visuals/TaskVisual';
import type { VisualEntry } from './task-visuals/types';
import { useLocale } from './locale';
/** Only build-authored, escaped Markdown fragments enter this boundary. UI is React-owned. */
export function Markup({ html, className }: { html: string; className?: string }) {
  return <div className={className} dangerouslySetInnerHTML={{ __html: html }} />;
}
export function Field({ entry, name }: { entry: TaskEntry; name: BriefField }) {
  return entry.html?.[name] ? <Markup html={entry.html[name]!} /> : <p>{entry[name]}</p>;
}
export function Box({
  title,
  children,
  className = '',
}: {
  title: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={'box ' + className}>
      <h3>{title}</h3>
      {children}
    </section>
  );
}
export function SourceLink({ url, children }: { url: string; children: ReactNode }) {
  return (
    <a href={url} target="_blank" rel="noopener noreferrer">
      {children}
    </a>
  );
}
/** Keyed React ownership resets the player when task or language changes. */
export function TaskScene({ entry, plan }: { entry: TaskEntry; plan?: StoryPlan }) {
  const { locale } = useLocale();
  if (!entry.illustration) return null;
  return (
    <div className="task-scene-host">
      <TaskVisual key={entry.id + locale} entry={entry as VisualEntry} plan={plan} />
    </div>
  );
}
