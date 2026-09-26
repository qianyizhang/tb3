/** Browser and FFmpeg operations for retained tours; planning is pure. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import type { Page } from 'playwright';
import { serveDirectory, withBrowser } from '../browser.mts';
import { runPipedEncoder } from './encoder.mts';
import {
  captions,
  resolveConfig,
  resolveStories,
  type TourFlags,
  type TourConfig,
  type Stories,
  type Locale,
} from './tour-plan.mts';

declare global {
  var tourApp: {
    ready: Promise<void>;
    configure(config: {
      locale: string;
      stories: Stories;
      labels: Record<string, string>;
    }): Promise<void>;
    select(id: string): Promise<void>;
    renderFrame(time: number, width: number, height: number): Promise<string>;
    renderStill(
      time: number,
      width: number,
      height: number,
      type: string,
      quality: number,
    ): Promise<string>;
  };
}
interface Provenance {
  renderer_sha256: string;
  storyboard_sha256: string;
  data_provenance_sha256: string;
  locale_sha256: string | null;
  settings: TourConfig;
  music: { file: string; sha256: string } | null;
}
interface Video {
  file: string;
  width: number;
  height: number;
  seconds: number;
  fps: number;
  frames: number;
  bytes: number;
  sha256: string;
  codec: string;
  audio: boolean;
  provenance?: Provenance;
}
interface Manifest extends Provenance {
  schema: number;
  renderer: string;
  videos: Video[];
}
const read = <T,>(file: string): T => JSON.parse(fs.readFileSync(file, 'utf8'));

export async function exportTours(
  repo: string,
  flags: TourFlags,
  stillsOnly: boolean,
): Promise<void> {
  const root = path.join(repo, 'presentation/tours');
  const sha = (file: string) =>
    crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
  const custom = flags.config ? read<Record<string, unknown>>(path.resolve(flags.config)) : {};
  const preset = flags.preset || custom.extends || 'compact';
  if (typeof preset !== 'string' || !['compact', 'master', 'web-av1'].includes(preset))
    throw Error('Unknown preset');
  const cfg = resolveConfig(
    read<Record<string, unknown>>(path.join(root, 'presets', preset + '.json')),
    custom,
    flags,
  );
  const base = read<Stories>(path.join(root, 'storyboards.json'));
  const localeFile = path.join(root, 'locales', cfg.locale + '.json');
  const loc = read<Locale>(localeFile);
  loc.labels = { ...loc.labels, ...cfg.labels };
  const stories = resolveStories(base, loc, cfg);
  const out = path.resolve(
    repo,
    cfg.output ||
      `presentation/tours/exports${cfg.locale === 'en' ? '' : '/' + cfg.locale}${preset === 'web-av1' ? '/web-av1' : preset === 'master' ? '/master' : ''}`,
  );
  fs.mkdirSync(out, { recursive: true });
  const music = cfg.music ? path.resolve(repo, cfg.music) : null;
  if (music && !fs.existsSync(music)) throw Error('Music file does not exist');
  async function encode(
    page: Page,
    id: string,
    format: string,
    w: number,
    h: number,
    duration: number,
  ): Promise<Video> {
    const file = `${id}-${format}.${cfg.codec === 'av1' ? 'webm' : 'mp4'}`,
      dest = path.join(out, file),
      frames = Math.round(duration * cfg.fps),
      args = [
        '-hide_banner',
        '-loglevel',
        'error',
        '-y',
        '-f',
        'image2pipe',
        '-vcodec',
        'png',
        '-framerate',
        String(cfg.fps),
        '-i',
        'pipe:0',
      ];
    if (music) args.push('-stream_loop', '-1', '-i', music);
    args.push('-map', '0:v:0');
    if (music) {
      const fade = Math.min(cfg.fadeSeconds, duration / 2);
      args.push(
        '-map',
        '1:a:0',
        '-af',
        `volume=${cfg.musicVolume},afade=t=in:st=0:d=${fade},afade=t=out:st=${duration - fade}:d=${fade}`,
        '-c:a',
        cfg.codec === 'av1' ? 'libopus' : 'aac',
        '-b:a',
        '96k',
        '-t',
        String(duration),
      );
    } else args.push('-an');
    args.push(
      '-c:v',
      cfg.codec === 'av1' ? 'libsvtav1' : 'libx264',
      '-preset',
      String(cfg.encoderPreset),
      '-crf',
      String(cfg.crf),
      '-pix_fmt',
      'yuv420p',
    );
    if (cfg.codec !== 'av1') args.push('-movflags', '+faststart');
    await runPipedEncoder({
      command: process.env.FFMPEG || 'ffmpeg',
      args,
      destination: dest,
      renderFrames: async (writeFrame) => {
        for (let frame = 0; frame < frames; frame++) {
          const png = await page.evaluate(
            ([time, width, height]) => tourApp.renderFrame(time, width, height),
            [frame / cfg.fps, w, h],
          );
          await writeFrame(Buffer.from(png.split(',')[1], 'base64'));
          if (frame % (cfg.fps * 8) === 0)
            console.log(`${id} ${format}: ${frame / cfg.fps}/${duration}s`);
        }
      },
    });
    return {
      file,
      width: w,
      height: h,
      seconds: frames / cfg.fps,
      fps: cfg.fps,
      frames,
      bytes: fs.statSync(dest).size,
      sha256: sha(dest),
      codec: cfg.codec,
      audio: !!music,
    };
  }
  await withBrowser(
    async (browser) => {
      let server;
      try {
        server = await serveDirectory(root);
        const page = await browser.newPage();
        const errors: string[] = [];
        page.on('pageerror', (e) => errors.push(e.message));
        await page.goto(server.url);
        await page.waitForFunction(() => window.tourApp);
        await page.evaluate(() => tourApp.ready);
        await page.evaluate((o) => tourApp.configure(o), {
          locale: cfg.locale,
          stories,
          labels: loc.labels,
        });
        await page.evaluate(() => document.fonts.ready);
        const manifest: Manifest = {
          schema: 2,
          renderer: 'presentation/tours/tour.js',
          renderer_sha256: sha(path.join(root, 'tour.js')),
          storyboard_sha256: sha(path.join(root, 'storyboards.json')),
          data_provenance_sha256: sha(path.join(root, 'data/provenance.json')),
          locale_sha256: localeFile ? sha(localeFile) : null,
          settings: cfg,
          music: music ? { file: path.basename(music), sha256: sha(music) } : null,
          videos: [],
        };
        const previous = path.join(out, 'manifest.json');
        if (cfg.only && fs.existsSync(previous)) {
          const old = read<Manifest>(previous);
          manifest.videos = old.videos.filter((v) => !v.file.startsWith(cfg.only + '-'));
        }
        for (const [id, s] of Object.entries(stories)) {
          if (cfg.only && cfg.only !== id) continue;
          await page.evaluate((id) => tourApp.select(id), id);
          const duration = Math.min(s.duration, cfg.previewSeconds ?? s.duration);
          for (const ext of ['vtt', 'srt'] as const)
            fs.writeFileSync(path.join(out, id + '.' + ext), captions(s, duration, ext));
          for (const format of cfg.formats) {
            const [w, h] = format === 'landscape' ? [1280, 720] : [720, 1280];
            for (let i = 0; i < s.steps.length; i++) {
              const st = s.steps[i],
                end = s.steps[i + 1]?.at ?? s.duration,
                t = st.at + (end - st.at) * 0.28125,
                type = 'image/' + cfg.stills,
                url = await page.evaluate(
                  ([t, w, h, type, q]) => tourApp.renderStill(t, w, h, type, q),
                  [t, w, h, type, Number(cfg.stillQuality || 90) / 100] as const,
                );
              fs.writeFileSync(
                path.join(
                  out,
                  `${id}-${format}-step${i + 1}.${cfg.stills === 'jpeg' ? 'jpg' : cfg.stills}`,
                ),
                Buffer.from(url.split(',')[1], 'base64'),
              );
            }
            if (!stillsOnly) {
              const video = await encode(page, id, format, w, h, duration);
              video.provenance = {
                renderer_sha256: manifest.renderer_sha256,
                storyboard_sha256: manifest.storyboard_sha256,
                data_provenance_sha256: manifest.data_provenance_sha256,
                locale_sha256: manifest.locale_sha256,
                settings: cfg,
                music: manifest.music,
              };
              manifest.videos.push(video);
              console.log(`Saved ${id} ${format}`);
            }
          }
        }
        if (errors.length) throw Error(errors.join('\n'));
        if (!stillsOnly) fs.writeFileSync(previous, JSON.stringify(manifest, null, 2) + '\n');
        fs.writeFileSync(
          path.join(out, 'resolved-storyboards.json'),
          JSON.stringify(stories, null, 2) + '\n',
        );
        console.log('Done. Browser errors: 0.');
      } finally {
        if (server) await server.close();
      }
    },
    { channel: undefined, executablePath: process.env.TOUR_BROWSER || undefined },
  );
}
