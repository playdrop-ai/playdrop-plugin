#!/usr/bin/env node
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const { tmpdir } = require("node:os");
const path = require("node:path");

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 1) {
    const raw = argv[i];
    if (!raw.startsWith("--")) continue;
    const eq = raw.indexOf("=");
    if (eq !== -1) {
      args[raw.slice(2, eq)] = raw.slice(eq + 1);
      continue;
    }
    const key = raw.slice(2);
    const next = argv[i + 1];
    if (next && !next.startsWith("--")) {
      args[key] = next;
      i += 1;
    } else {
      args[key] = true;
    }
  }
  return args;
}

function usage() {
  return `Usage:
node scripts/render-marketing-video.ts \\
  --input assets/marketing/captures/mobile-portrait.mp4 \\
  --out assets/marketing/social/tiktok.mp4 \\
  --width 1080 --height 1920 --duration 12 --fps 60 \\
  --first-second-action --hook-description "Boss attack lands in frame 1" \\
  --audio-policy music-and-sfx \\
  --text "Beat the boss" --font assets/fonts/title.ttf \\
  --thumbnail-out assets/marketing/thumbnails/tiktok-cover.png \\
  [--root . --manifest assets/marketing/asset-manifest.json]
`;
}

function requireString(args, name) {
  const value = args[name];
  if (typeof value !== "string" || value.trim() === "") {
    throw new Error(`Missing --${name}`);
  }
  return value;
}

function parseNumber(args, name, defaultValue, min, max) {
  const raw = args[name] === undefined ? defaultValue : Number(args[name]);
  if (!Number.isFinite(raw) || raw < min || raw > max) {
    throw new Error(`Invalid --${name}: expected ${min} to ${max}`);
  }
  return raw;
}

function ensureFile(file, label) {
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
    throw new Error(`${label} not found: ${file}`);
  }
}

function ensureNonEmptyFile(file, label) {
  ensureFile(file, label);
  if (fs.statSync(file).size <= 0) {
    throw new Error(`${label} is empty: ${file}`);
  }
}

function ensureTool(name) {
  const result = spawnSync(name, ["-version"], { encoding: "utf8" });
  if (result.status !== 0) {
    throw new Error(`Missing required tool: ${name}`);
  }
}

function runTool(command, args, label) {
  const result = spawnSync(command, args, {
    encoding: "utf8",
    maxBuffer: 20 * 1024 * 1024,
  });
  if (result.status !== 0) {
    const combined = [result.stdout, result.stderr].filter(Boolean).join("\n").trim();
    throw new Error(`${label} failed${combined ? `: ${combined}` : ""}`);
  }
  return {
    stdout: result.stdout || "",
    stderr: result.stderr || "",
  };
}

function parseFps(raw) {
  if (typeof raw !== "string" || !raw.includes("/")) return Number(raw);
  const [num, den] = raw.split("/").map(Number);
  if (!Number.isFinite(num) || !Number.isFinite(den) || den === 0) return Number.NaN;
  return num / den;
}

function probeMedia(file) {
  const { stdout } = runTool("ffprobe", [
    "-v",
    "error",
    "-show_streams",
    "-show_format",
    "-of",
    "json",
    file,
  ], "ffprobe");
  const probe = JSON.parse(stdout);
  const video = Array.isArray(probe.streams)
    ? probe.streams.find((stream) => stream.codec_type === "video")
    : null;
  if (!video) throw new Error(`Video stream not found: ${file}`);
  const audioTracks = Array.isArray(probe.streams)
    ? probe.streams.filter((stream) => stream.codec_type === "audio").length
    : 0;
  return {
    width: Number(video.width),
    height: Number(video.height),
    fps: parseFps(video.avg_frame_rate || video.r_frame_rate),
    durationSeconds: Number.parseFloat(probe.format?.duration || "0"),
    audioTracks,
  };
}

function measureAudio(file) {
  const ebur = spawnSync("ffmpeg", [
    "-hide_banner",
    "-nostats",
    "-i",
    file,
    "-filter_complex",
    "ebur128",
    "-f",
    "null",
    "-",
  ], { encoding: "utf8", maxBuffer: 20 * 1024 * 1024 });
  if (ebur.status !== 0) {
    throw new Error(`Unable to measure loudness: ${file}`);
  }
  const eburText = `${ebur.stdout || ""}\n${ebur.stderr || ""}`;
  const integratedMatches = [...eburText.matchAll(/I:\s*(-?\d+(?:\.\d+)?) LUFS/g)];
  const integratedLufs = integratedMatches.length
    ? Number(integratedMatches[integratedMatches.length - 1][1])
    : Number.NaN;

  const volume = spawnSync("ffmpeg", [
    "-hide_banner",
    "-nostats",
    "-i",
    file,
    "-af",
    "volumedetect",
    "-f",
    "null",
    "-",
  ], { encoding: "utf8", maxBuffer: 20 * 1024 * 1024 });
  if (volume.status !== 0) {
    throw new Error(`Unable to measure peak volume: ${file}`);
  }
  const volumeText = `${volume.stdout || ""}\n${volume.stderr || ""}`;
  const peakMatch = volumeText.match(/max_volume:\s*(-?\d+(?:\.\d+)?) dB/);
  const peakDb = peakMatch ? Number(peakMatch[1]) : Number.NaN;
  if (!Number.isFinite(integratedLufs) || !Number.isFinite(peakDb)) {
    throw new Error(`Unable to parse audio metrics for ${file}`);
  }
  return { integratedLufs, peakDb };
}

function parseAudioPolicy(raw) {
  const policy = String(raw || "music-and-sfx");
  if (!["music-and-sfx", "sfx-only", "silent"].includes(policy)) {
    throw new Error(`Invalid --audio-policy: ${policy}`);
  }
  return policy;
}

function resolveFromRoot(projectRoot, file) {
  return path.resolve(projectRoot, file);
}

function ensureMarketingOut(projectRoot, file) {
  const resolved = resolveFromRoot(projectRoot, file);
  const marketingRoot = path.resolve(projectRoot, "assets", "marketing");
  const relativeToMarketing = path.relative(marketingRoot, resolved);
  if (
    relativeToMarketing === ".." ||
    relativeToMarketing.startsWith(`..${path.sep}`) ||
    path.isAbsolute(relativeToMarketing)
  ) {
    throw new Error(`Output must live under assets/marketing/: ${file}`);
  }
  return resolved;
}

function escapeDraw(value) {
  return String(value)
    .replace(/\\/g, "\\\\")
    .replace(/:/g, "\\:")
    .replace(/'/g, "\\'")
    .replace(/%/g, "\\%");
}

function createTextFile(text, tempDirs) {
  const dir = fs.mkdtempSync(path.join(tmpdir(), "playdrop-marketing-text-"));
  const file = path.join(dir, "text.txt");
  fs.writeFileSync(file, text);
  tempDirs.push(dir);
  return file;
}

function cleanupTempDirs(tempDirs) {
  for (const dir of tempDirs) {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

function updateManifest(projectRoot, manifestPath, entries) {
  if (!manifestPath) return;
  const resolved = ensureMarketingOut(projectRoot, manifestPath);
  let manifest = { version: 1, assets: [] };
  if (fs.existsSync(resolved)) {
    manifest = JSON.parse(fs.readFileSync(resolved, "utf8"));
    if (!Array.isArray(manifest.assets)) manifest.assets = [];
  }
  const ids = new Set(entries.map((entry) => entry.id));
  manifest.assets = manifest.assets.filter((asset) => !ids.has(asset.id)).concat(entries);
  fs.mkdirSync(path.dirname(resolved), { recursive: true });
  fs.writeFileSync(resolved, `${JSON.stringify(manifest, null, 2)}\n`);
}

function runFfmpeg(args, label) {
  const result = spawnSync("ffmpeg", args, { stdio: "inherit" });
  if (result.status !== 0) {
    throw new Error(`ffmpeg failed while ${label}`);
  }
}

const tempDirs = [];

try {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
    process.exit(0);
  }
  const projectRoot = path.resolve(args.root || process.cwd());
  const input = resolveFromRoot(projectRoot, requireString(args, "input"));
  const out = ensureMarketingOut(projectRoot, requireString(args, "out"));
  const width = parseNumber(args, "width", 1080, 320, 7680);
  const height = parseNumber(args, "height", 1920, 320, 7680);
  const start = parseNumber(args, "start", 0, 0, 300);
  const duration = parseNumber(args, "duration", 12, 1, 300);
  const fps = parseNumber(args, "fps", 60, 1, 120);
  const text = args.text === undefined ? "" : String(args.text);
  const font = args.font === undefined ? "" : resolveFromRoot(projectRoot, String(args.font));
  const fontSize = parseNumber(args, "font-size", Math.round(height * 0.052), 12, 360);
  const bannerHeight = parseNumber(args, "banner-height", Math.round(height * 0.16), 0, height);
  const thumbnailOut = args["thumbnail-out"] ? ensureMarketingOut(projectRoot, String(args["thumbnail-out"])) : null;
  const thumbnailAt = parseNumber(args, "thumbnail-at", Math.min(1, duration / 2), 0, duration);
  const audioPolicy = parseAudioPolicy(args["audio-policy"]);
  const hookDescription = args["hook-description"] === undefined ? "" : String(args["hook-description"]).trim();

  ensureTool("ffmpeg");
  ensureTool("ffprobe");
  ensureFile(input, "Input video");
  if (!args["first-second-action"]) {
    throw new Error("Missing --first-second-action. Marketing videos must start with visible gameplay action, not a static title card.");
  }
  if (!hookDescription) {
    throw new Error("Missing --hook-description explaining the visible gameplay action in the first second.");
  }
  if (text) {
    if (!font) throw new Error("Missing --font for text overlay");
    ensureFile(font, "Font file");
  }
  const inputProbe = probeMedia(input);
  if (audioPolicy !== "silent" && inputProbe.audioTracks === 0) {
    throw new Error(`Input video has no audio but --audio-policy is ${audioPolicy}: ${input}`);
  }

  const filters = [
    `scale=${width}:${height}:force_original_aspect_ratio=increase`,
    `crop=${width}:${height}`,
    `fps=${fps}`,
  ];
  if (text) {
    const y = Math.round(Math.max(24, bannerHeight * 0.28));
    const textFile = createTextFile(text, tempDirs);
    filters.push(`drawbox=x=0:y=0:w=iw:h=${bannerHeight}:color=black@0.55:t=fill`);
    filters.push(
      `drawtext=fontfile='${escapeDraw(font)}':textfile='${escapeDraw(textFile)}':x=(w-text_w)/2:y=${y}:fontsize=${fontSize}:fontcolor=white:borderw=5:bordercolor=black@0.65:expansion=none`
    );
  }

  fs.mkdirSync(path.dirname(out), { recursive: true });
  const ffmpegArgs = [
    "-y",
    "-ss",
    String(start),
    "-t",
    String(duration),
    "-i",
    input,
    "-vf",
    filters.join(","),
    "-c:v",
    "libx264",
    "-preset",
    "slow",
    "-crf",
    "18",
    "-pix_fmt",
    "yuv420p",
  ];
  if (audioPolicy === "silent") {
    ffmpegArgs.push("-an");
  } else {
    ffmpegArgs.push(
      "-af",
      "loudnorm=I=-16:TP=-1.5:LRA=11",
      "-c:a",
      "aac",
      "-b:a",
      "192k",
    );
  }
  ffmpegArgs.push("-movflags", "+faststart", out);
  runFfmpeg(ffmpegArgs, `rendering video: ${out}`);

  const outputProbe = probeMedia(out);
  if (outputProbe.width !== width || outputProbe.height !== height) {
    throw new Error(`Rendered video has wrong dimensions: ${outputProbe.width}x${outputProbe.height}, expected ${width}x${height}`);
  }
  if (Math.round(outputProbe.fps) !== Math.round(fps)) {
    throw new Error(`Rendered video has wrong fps: ${outputProbe.fps}, expected ${fps}`);
  }
  let audioMetrics = null;
  if (audioPolicy !== "silent") {
    if (outputProbe.audioTracks === 0) {
      throw new Error(`Rendered video has no audio: ${out}`);
    }
    audioMetrics = measureAudio(out);
    if (audioMetrics.integratedLufs < -28 || audioMetrics.peakDb < -12) {
      throw new Error(`Rendered video audio is too quiet: ${audioMetrics.integratedLufs} LUFS, peak ${audioMetrics.peakDb} dB`);
    }
  }

  const entries = [{
    id: args.id || path.basename(out, path.extname(out)),
    kind: "video",
    platform: args.platform || null,
    path: path.relative(projectRoot, out),
    source: path.relative(projectRoot, input),
    width,
    height,
    fps,
    durationSeconds: duration,
    text: text || null,
    firstSecondAction: true,
    hookDescription,
    audioPolicy,
    integratedLufs: audioMetrics?.integratedLufs ?? null,
    peakDb: audioMetrics?.peakDb ?? null,
  }];

  if (thumbnailOut) {
    fs.mkdirSync(path.dirname(thumbnailOut), { recursive: true });
    runFfmpeg([
      "-y",
      "-ss",
      String(thumbnailAt),
      "-i",
      out,
      "-frames:v",
      "1",
      "-update",
      "1",
      thumbnailOut,
    ], `rendering thumbnail: ${thumbnailOut}`);
    ensureNonEmptyFile(thumbnailOut, "Thumbnail output");
    entries.push({
      id: `${args.id || path.basename(out, path.extname(out))}-thumbnail`,
      kind: "thumbnail",
      platform: args.platform || null,
      path: path.relative(projectRoot, thumbnailOut),
      source: path.relative(projectRoot, out),
      width,
      height,
    });
  }

  updateManifest(projectRoot, args.manifest, entries);
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
} finally {
  cleanupTempDirs(tempDirs);
}
