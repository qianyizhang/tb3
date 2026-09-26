/** Parse and dispatch media requests without executing work on import. */
import { parseArgs } from 'node:util';
import { exportStory, type StoryOptions } from './stories.mts';
import { exportTours } from './tours.mts';
import type { TourFlags } from './tour-plan.mts';

const help = `Medical media tool — npm run media -- [options]
  --preset=compact|master|web-av1   Encoding and still-image preset (default compact)
  --config=FILE                    Editable JSON settings, durations and copy overrides
  --locale=en|zh-CN               Story and in-frame label language
  --story=ID --output=DIR         Canonical explainer source; fixed composed pilot format
  --only=TOUR                     segmentation, vessels, cardiac, registration, landmarks, aneurysm
  --formats=landscape,portrait    Recompose each aspect ratio (not a crop)
  --fps=24 --crf=26               Override preset encoding settings
  --duration-scale=1.25           Lengthen every scene without changing its visual sequence
  --music=FILE --music-volume=.12 Loop a local track, trim to duration, fade in/out
  --output=DIR                    Separate output for each variant
  --stills-only                   Export caption files and one still per scene
  --preview-seconds=2             Short render for audio/encoding checks
Configuration: {extends, locale, only, formats, durations:{tour:[seconds,...]},
  overrides:{tour:{title,subtitle,steps:[{title,caption},...]}}, music, musicVolume,
  fadeSeconds, output}. Copy and labels live in storyboards.json and locales/*.json.
No model calls, dependency installs or publishing. See presentation/tours/TOOL.md.`;
type Request =
  | { kind: 'help' }
  | ({ kind: 'story' } & StoryOptions)
  | { kind: 'tour'; flags: TourFlags; stillsOnly: boolean };
export function parseMediaArgs(args: string[]): Request {
  const { values } = parseArgs({
    args,
    options: {
      help: { type: 'boolean' },
      story: { type: 'string' },
      output: { type: 'string' },
      'stills-only': { type: 'boolean' },
      preset: { type: 'string' },
      config: { type: 'string' },
      locale: { type: 'string' },
      only: { type: 'string' },
      formats: { type: 'string' },
      fps: { type: 'string' },
      crf: { type: 'string' },
      'duration-scale': { type: 'string' },
      music: { type: 'string' },
      'music-volume': { type: 'string' },
      'preview-seconds': { type: 'string' },
    },
  });
  if (values.help) return { kind: 'help' };
  const { story, 'stills-only': stillsOnly = false, help: _help, ...flags } = values;
  if (story !== undefined) {
    for (const key of Object.keys(flags))
      if (key !== 'output')
        throw Error(
          `Story source does not accept --${key}; edit canonical copy/timing in the group story`,
        );
    if (!story || !values.output) throw Error('--story=ID requires --output=DIR');
    return { kind: 'story', story, output: values.output, stillsOnly };
  }
  return { kind: 'tour', flags, stillsOnly };
}

export async function runMedia(root: string, args: string[]): Promise<void> {
  const request = parseMediaArgs(args);
  if (request.kind === 'help') console.log(help);
  else if (request.kind === 'story') await exportStory(root, request);
  else await exportTours(root, request.flags, request.stillsOnly);
}
