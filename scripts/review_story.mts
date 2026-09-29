import { collectStoryReview } from '../presentation/tooling/story-review.mts';

function option(name: string): string | undefined {
  const matches = process.argv.slice(2).filter((argument) => argument.startsWith(`--${name}=`));
  if (matches.length > 1) throw Error(`Repeated --${name}`);
  return matches[0]?.slice(name.length + 3);
}

try {
  const exportDir = option('export');
  const outputDir = option('output');
  const playback = process.argv.includes('--playback');
  const frames = option('frames');
  const known = new Set(['--playback']);
  for (const argument of process.argv.slice(2)) {
    if (!known.has(argument) && !/^--(export|output|frames)=/.test(argument))
      throw Error(`Unknown option: ${argument}`);
  }
  if (!exportDir || !outputDir)
    throw Error(
      'Usage: node scripts/review_story.mts --export=DIR --output=FRESH_DIR [--playback] [--frames=0,42]',
    );
  const manifest = await collectStoryReview(exportDir, outputDir, { playback, frames });
  process.stdout.write(
    `${JSON.stringify({ status: manifest.status, output: outputDir, storyId: manifest.storyId })}\n`,
  );
} catch (error) {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
  process.exitCode = 1;
}
