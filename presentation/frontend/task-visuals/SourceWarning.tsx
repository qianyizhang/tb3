import styles from './source-warning.module.css';

export type SourceWarningData = {
  label: string;
  text: string;
  url: string;
  link_label: string;
};

/** A source gap remains visible before the task and throughout its illustration. */
export function SourceWarning({ warning }: { warning?: SourceWarningData }) {
  if (!warning) return null;
  return (
    <aside className={styles.warning} data-symbolic-source-warning lang="en">
      <strong>{warning.label}</strong> {warning.text}{' '}
      <a href={warning.url} target="_blank" rel="noopener noreferrer">
        {warning.link_label}
      </a>
      .
    </aside>
  );
}
