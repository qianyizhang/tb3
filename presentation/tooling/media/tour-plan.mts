/** Resolve tour copy and timing without browser, encoder or filesystem effects. */
export interface Step {
  at: number;
  title: string;
  caption: string;
}
export interface Story {
  title: string;
  subtitle: string;
  source: string;
  duration: number;
  steps: Step[];
}
export type Stories = Record<string, Story>;
export type StoryOverride = Partial<Pick<Story, 'title' | 'subtitle' | 'source'>> & {
  steps?: Partial<Omit<Step, 'at'>>[];
};
export interface Locale {
  labels: Record<string, string>;
  stories: Record<string, StoryOverride>;
}
export type TourFlags = Partial<
  Record<
    | 'preset'
    | 'config'
    | 'locale'
    | 'only'
    | 'formats'
    | 'fps'
    | 'crf'
    | 'duration-scale'
    | 'music'
    | 'music-volume'
    | 'output'
    | 'preview-seconds',
    string
  >
>;
export interface TourConfig {
  locale: string;
  only?: string;
  output?: string;
  fps: number;
  crf: number;
  music: string | null;
  musicVolume: number;
  fadeSeconds: number;
  durationScale: number;
  previewSeconds: number | null;
  codec: 'av1' | 'h264';
  encoderPreset: string;
  formats: ('landscape' | 'portrait')[];
  stills: 'png' | 'jpeg' | 'webp';
  stillQuality?: number;
  labels?: Record<string, string>;
  durations?: Record<string, number[]>;
  overrides?: Record<string, StoryOverride>;
}

export function resolveConfig(
  preset: Record<string, unknown>,
  custom: Record<string, unknown>,
  flags: TourFlags,
): TourConfig {
  const raw = { ...preset, ...custom };
  for (const [arg, key] of Object.entries({
    locale: 'locale',
    only: 'only',
    fps: 'fps',
    crf: 'crf',
    music: 'music',
    'music-volume': 'musicVolume',
    output: 'output',
    'duration-scale': 'durationScale',
    'preview-seconds': 'previewSeconds',
  }) as [keyof TourFlags, string][])
    if (flags[arg] !== undefined) raw[key] = flags[arg];
  if (flags.formats) raw.formats = flags.formats.split(',');
  if (!Array.isArray(raw.formats) || !raw.formats.length) throw Error('Invalid formats');
  const cfg: TourConfig = {
    ...raw,
    locale: text(raw.locale || 'en', 'locale'),
    only: optionalText(raw.only, 'only'),
    output: optionalText(raw.output, 'output'),
    fps: Number(raw.fps),
    crf: Number(raw.crf),
    music: optionalText(raw.music, 'music') ?? null,
    musicVolume: Number(raw.musicVolume),
    fadeSeconds: Number(raw.fadeSeconds),
    durationScale: Number(raw.durationScale ?? 1),
    previewSeconds: raw.previewSeconds == null ? null : Number(raw.previewSeconds),
    codec: choice(raw.codec, ['av1', 'h264'], 'codec'),
    encoderPreset: text(raw.encoderPreset, 'encoder preset'),
    formats: raw.formats.map((format: unknown) =>
      choice(format, ['landscape', 'portrait'], 'format'),
    ),
    stills: choice(raw.stills, ['png', 'jpeg', 'webp'], 'still format'),
    stillQuality: raw.stillQuality === undefined ? undefined : Number(raw.stillQuality),
    labels:
      raw.labels === undefined
        ? undefined
        : Object.fromEntries(
            Object.entries(object(raw.labels)).map(([key, value]) => [key, text(value, key)]),
          ),
    durations: parseDurations(raw.durations),
    overrides: parseOverrides(raw.overrides),
  };
  if (!Number.isInteger(cfg.fps) || cfg.fps < 12 || cfg.fps > 60) throw Error('fps must be 12–60');
  if (!Number.isFinite(cfg.crf) || cfg.crf < 0 || cfg.crf > 51) throw Error('crf must be 0–51');
  if (!(cfg.musicVolume >= 0 && cfg.musicVolume <= 1) || !(cfg.fadeSeconds >= 0))
    throw Error('Invalid music volume or fade');
  if (!(cfg.durationScale > 0 && cfg.durationScale <= 10))
    throw Error('duration scale must be >0 and <=10');
  if (
    cfg.previewSeconds !== null &&
    !(Number.isFinite(cfg.previewSeconds) && cfg.previewSeconds > 0)
  )
    throw Error('Invalid preview duration');
  if (
    cfg.stillQuality !== undefined &&
    !(Number.isFinite(cfg.stillQuality) && cfg.stillQuality >= 0 && cfg.stillQuality <= 100)
  )
    throw Error('Invalid still quality');
  return cfg;
}

function choice<T extends string>(value: unknown, choices: T[], name: string): T {
  const match = choices.find((choice) => choice === value);
  if (match === undefined) throw Error(`Invalid ${name}`);
  return match;
}
function text(value: unknown, name: string): string {
  if (typeof value !== 'string') throw Error(`Invalid ${name}`);
  return value;
}
function optionalText(value: unknown, name: string): string | undefined {
  return value == null ? undefined : text(value, name);
}
function object(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value))
    throw Error('Expected a settings object');
  return value as Record<string, unknown>;
}
function parseDurations(value: unknown): TourConfig['durations'] {
  if (value === undefined) return undefined;
  return Object.fromEntries(
    Object.entries(object(value)).map(([key, durations]) => {
      if (
        !Array.isArray(durations) ||
        durations.some((item) => typeof item !== 'number' || !Number.isFinite(item) || item <= 0)
      )
        throw Error(`Invalid scene durations: ${key}`);
      return [key, durations];
    }),
  );
}
function parseOverrides(value: unknown): TourConfig['overrides'] {
  if (value === undefined) return undefined;
  return Object.fromEntries(
    Object.entries(object(value)).map(([key, raw]) => {
      const row = object(raw);
      const result: StoryOverride = {};
      for (const field of ['title', 'subtitle', 'source'] as const)
        if (row[field] !== undefined)
          result[field] = text(row[field], `story copy: ${key}.${field}`);
      if (row.steps !== undefined) {
        if (!Array.isArray(row.steps)) throw Error(`Invalid scene copy: ${key}`);
        result.steps = row.steps.map((raw: unknown) => {
          const step = object(raw),
            copy: Partial<Step> = {};
          for (const field of ['title', 'caption'] as const)
            if (step[field] !== undefined)
              copy[field] = text(step[field], `scene copy: ${key}.${field}`);
          return copy;
        });
      }
      return [key, result];
    }),
  );
}

export function resolveStories(base: Stories, locale: Locale, cfg: TourConfig): Stories {
  if (cfg.only && !Object.hasOwn(base, cfg.only)) throw Error('Unknown tour');
  const stories: Stories = {};
  for (const [id, story] of Object.entries(base)) {
    const translation = locale.stories[id] || {},
      override = cfg.overrides?.[id] || {};
    const durations =
      cfg.durations?.[id] ||
      story.steps.map((step, i) => (story.steps[i + 1]?.at ?? story.duration) - step.at);
    if (
      !Array.isArray(durations) ||
      durations.length !== story.steps.length ||
      durations.some((value) => !Number.isFinite(value) || value <= 0)
    )
      throw Error(`Invalid scene durations: ${id}`);
    let at = 0;
    const steps = story.steps.map((step, i) => {
      const resolved = { ...step, ...translation.steps?.[i], ...override.steps?.[i], at };
      if (typeof resolved.title !== 'string' || typeof resolved.caption !== 'string')
        throw Error(`Invalid scene copy: ${id}`);
      at += durations[i] * cfg.durationScale;
      return resolved;
    });
    stories[id] = { ...story, ...translation, ...override, steps, duration: at };
  }
  return stories;
}

export function captions(story: Story, duration: number, format: 'vtt' | 'srt'): string {
  const stamp = (seconds: number) => {
    const ms = Math.round(seconds * 1000);
    return (
      [Math.floor(ms / 3600000), Math.floor(ms / 60000) % 60, Math.floor(ms / 1000) % 60]
        .map((v) => String(v).padStart(2, '0'))
        .join(':') +
      (format === 'vtt' ? '.' : ',') +
      String(ms % 1000).padStart(3, '0')
    );
  };
  return (
    (format === 'vtt' ? 'WEBVTT\n\n' : '') +
    story.steps
      .filter((step) => step.at < duration)
      .map(
        (step, i) =>
          `${i + 1}\n${stamp(step.at)} --> ${stamp(Math.min(story.steps[i + 1]?.at ?? story.duration, duration))}\n${step.title}\n${step.caption}\n`,
      )
      .join('\n')
  );
}
