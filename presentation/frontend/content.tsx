import { useEffect, useRef, type ReactNode } from 'react';
import type { BriefField, TaskEntry } from './types';
import { TaskScenes } from '../task-explorer/scenes.js';
import { useLocale } from './locale';
export const taskSceneMode = (entry: TaskEntry): '3d' | 'static' => TaskScenes.mode(entry);
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
/** The scene renderer owns only its subtree and disposes observers/GPU resources on exit. */
export function TaskScene({ entry }: { entry: TaskEntry }) {
  const { locale } = useLocale();
  const host = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const root = host.current;
    if (!root) return;
    root.innerHTML = TaskScenes.figure(entry, locale);
    const dispose = TaskScenes.mount(root, entry, locale);
    return () => {
      dispose();
      root.replaceChildren();
    };
  }, [entry, locale]);
  return <div ref={host} className="task-scene-host" />;
}
