#!/usr/bin/env node
/** Reusable deterministic media CLI: copy, translations, scene timing, codecs and music. */
const fs = require('node:fs'),
  path = require('node:path'),
  crypto = require('node:crypto');
const { serveDirectory, withBrowser } = require('./browser.cjs');
const { normalizeTiming, runPipedEncoder } = require('./media_export_support.cjs');
const repo = path.resolve(__dirname, '..'),
  root = path.join(repo, 'presentation/tours');
const argv = process.argv.slice(2),
  flags = {};
for (const a of argv) {
  if (!a.startsWith('--')) throw Error(`Use --name=value: ${a}`);
  const n = a.indexOf('=');
  flags[n < 0 ? a.slice(2) : a.slice(2, n)] = n < 0 ? true : a.slice(n + 1);
}
if (flags.help) {
  console.log(`Medical media tool — npm run media -- [options]
  --preset=compact|master|web-av1   Encoding and still-image preset (default compact)
  --config=FILE                    Editable JSON settings, durations and copy overrides
  --locale=en|zh-CN               Story and in-frame label language
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
No model calls, dependency installs or publishing. See presentation/tours/TOOL.md.`);
  process.exit(0);
}
const allowed = new Set([
  'preset',
  'config',
  'locale',
  'only',
  'formats',
  'fps',
  'crf',
  'duration-scale',
  'music',
  'music-volume',
  'output',
  'stills-only',
  'preview-seconds',
]);
for (const k of Object.keys(flags)) if (!allowed.has(k)) throw Error(`Unknown option --${k}`);
const read = (p) => JSON.parse(fs.readFileSync(p, 'utf8')),
  sha = (p) => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const custom = flags.config ? read(path.resolve(flags.config)) : {};
const preset = flags.preset || custom.extends || 'compact';
if (!['compact', 'master', 'web-av1'].includes(preset)) throw Error('Unknown preset');
const cfg = { ...read(path.join(root, 'presets', preset + '.json')), ...custom };
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
}))
  if (flags[arg] !== undefined) cfg[key] = flags[arg];
if (flags.formats) cfg.formats = String(flags.formats).split(',');
cfg.locale ||= 'en';
cfg.fps = Number(cfg.fps);
cfg.crf = Number(cfg.crf);
cfg.musicVolume = Number(cfg.musicVolume);
cfg.fadeSeconds = Number(cfg.fadeSeconds);
const timing = normalizeTiming(cfg);
cfg.durationScale = timing.durationScale;
if (!Number.isInteger(cfg.fps) || cfg.fps < 12 || cfg.fps > 60) throw Error('fps must be 12–60');
if (!Number.isFinite(cfg.crf) || cfg.crf < 0 || cfg.crf > 51) throw Error('crf must be 0–51');
if (!(cfg.musicVolume >= 0 && cfg.musicVolume <= 1) || !(cfg.fadeSeconds >= 0))
  throw Error('Invalid music volume or fade');
if (
  !Array.isArray(cfg.formats) ||
  !cfg.formats.length ||
  cfg.formats.some((f) => !['landscape', 'portrait'].includes(f))
)
  throw Error('Invalid formats');
const base = read(path.join(root, 'storyboards.json'));
if (cfg.only && !base[cfg.only]) throw Error('Unknown tour');
const localeFile = path.join(root, 'locales', cfg.locale + '.json');
const loc = read(localeFile);
loc.labels = { ...loc.labels, ...cfg.labels };
const stories = structuredClone(base);
for (const [id, s] of Object.entries(stories)) {
  const translation = loc.stories[id] || {},
    override = cfg.overrides?.[id] || {};
  Object.assign(s, translation, { ...override, steps: s.steps });
  s.steps = base[id].steps.map((step, i) => ({
    ...step,
    ...translation.steps?.[i],
    ...override.steps?.[i],
  }));
  const durations =
    cfg.durations?.[id] ||
    base[id].steps.map((st, i) => (base[id].steps[i + 1]?.at ?? base[id].duration) - st.at);
  if (durations.length !== s.steps.length || durations.some((v) => !Number.isFinite(v) || v <= 0))
    throw Error(`Invalid scene durations: ${id}`);
  let at = 0;
  s.steps.forEach((st, i) => {
    st.at = at;
    at += durations[i] * cfg.durationScale;
  });
  s.duration = at;
}
const out = path.resolve(
  repo,
  cfg.output ||
    `presentation/tours/exports${cfg.locale === 'en' ? '' : '/' + cfg.locale}${preset === 'web-av1' ? '/web-av1' : preset === 'master' ? '/master' : ''}`,
);
fs.mkdirSync(out, { recursive: true });
const music = cfg.music ? path.resolve(repo, cfg.music) : null;
if (music && !fs.existsSync(music)) throw Error('Music file does not exist');
function stamp(n, sep = '.') {
  const ms = Math.round(n * 1000);
  return (
    [Math.floor(ms / 3600000), Math.floor(ms / 60000) % 60, Math.floor(ms / 1000) % 60]
      .map((v) => String(v).padStart(2, '0'))
      .join(':') +
    sep +
    String(ms % 1000).padStart(3, '0')
  );
}
async function encode(page, id, format, w, h, duration) {
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
withBrowser(
  async (browser) => {
    let server;
    try {
      server = await serveDirectory(root);
      const page = await browser.newPage();
      const errors = [];
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
      const manifest = {
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
        const old = read(previous);
        manifest.videos = old.videos.filter((v) => !v.file.startsWith(cfg.only + '-'));
      }
      for (const [id, s] of Object.entries(stories)) {
        if (cfg.only && cfg.only !== id) continue;
        await page.evaluate((id) => tourApp.select(id), id);
        const duration = Math.min(s.duration, timing.previewSeconds ?? s.duration),
          captions = s.steps
            .filter((st) => st.at < duration)
            .map((st, i) => ({
              start: st.at,
              end: Math.min(s.steps[i + 1]?.at ?? s.duration, duration),
              text: st.title + '\n' + st.caption,
            }));
        for (const ext of ['vtt', 'srt'])
          fs.writeFileSync(
            path.join(out, id + '.' + ext),
            (ext === 'vtt' ? 'WEBVTT\n\n' : '') +
              captions
                .map(
                  (c, i) =>
                    `${i + 1}\n${stamp(c.start, ext === 'vtt' ? '.' : ',')} --> ${stamp(c.end, ext === 'vtt' ? '.' : ',')}\n${c.text}\n`,
                )
                .join('\n'),
          );
        for (const format of cfg.formats) {
          const [w, h] = format === 'landscape' ? [1280, 720] : [720, 1280];
          for (let i = 0; i < s.steps.length; i++) {
            const st = s.steps[i],
              end = s.steps[i + 1]?.at ?? s.duration,
              t = st.at + (end - st.at) * 0.28125,
              type = 'image/' + cfg.stills,
              url = await page.evaluate(
                ([t, w, h, type, q]) => tourApp.renderStill(t, w, h, type, q),
                [t, w, h, type, Number(cfg.stillQuality || 90) / 100],
              );
            fs.writeFileSync(
              path.join(
                out,
                `${id}-${format}-step${i + 1}.${cfg.stills === 'jpeg' ? 'jpg' : cfg.stills}`,
              ),
              Buffer.from(url.split(',')[1], 'base64'),
            );
          }
          if (!flags['stills-only']) {
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
      if (!flags['stills-only'])
        fs.writeFileSync(previous, JSON.stringify(manifest, null, 2) + '\n');
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
).catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
