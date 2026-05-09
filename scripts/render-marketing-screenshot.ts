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
node scripts/render-marketing-screenshot.ts \\
  --input assets/marketing/captures/mobile-portrait.mp4 \\
  --out assets/marketing/screenshots/tiktok-cover.png \\
  --width 1080 --height 1920 --at 2 \\
  --text "Beat the boss" --font assets/fonts/title.ttf \\
  [--root . --manifest assets/marketing/asset-manifest.json --id tiktok-cover --platform tiktok]
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

function ensureTool(name) {
  const result = spawnSync(name, ["-version"], { encoding: "utf8" });
  if (result.status !== 0) {
    throw new Error(`Missing required tool: ${name}`);
  }
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

function updateManifest(projectRoot, manifestPath, entry) {
  if (!manifestPath) return;
  const resolved = ensureMarketingOut(projectRoot, manifestPath);
  let manifest = { version: 1, assets: [] };
  if (fs.existsSync(resolved)) {
    manifest = JSON.parse(fs.readFileSync(resolved, "utf8"));
    if (!Array.isArray(manifest.assets)) manifest.assets = [];
  }
  const next = manifest.assets.filter((asset) => asset.id !== entry.id);
  next.push(entry);
  manifest.assets = next;
  fs.mkdirSync(path.dirname(resolved), { recursive: true });
  fs.writeFileSync(resolved, `${JSON.stringify(manifest, null, 2)}\n`);
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
  const at = parseNumber(args, "at", 2, 0, 300);
  const text = args.text === undefined ? "" : String(args.text);
  const font = args.font === undefined ? "" : resolveFromRoot(projectRoot, String(args.font));
  const fontSize = parseNumber(args, "font-size", Math.round(height * 0.052), 12, 360);
  const bannerHeight = parseNumber(args, "banner-height", Math.round(height * 0.16), 0, height);

  ensureTool("ffmpeg");
  ensureFile(input, "Input video");
  if (text) {
    if (!font) throw new Error("Missing --font for text overlay");
    ensureFile(font, "Font file");
  }

  const filters = [
    `scale=${width}:${height}:force_original_aspect_ratio=increase`,
    `crop=${width}:${height}`,
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
    String(at),
    "-i",
    input,
    "-frames:v",
    "1",
    "-update",
    "1",
    "-vf",
    filters.join(","),
    out,
  ];

  const result = spawnSync("ffmpeg", ffmpegArgs, { stdio: "inherit" });
  if (result.status !== 0) {
    throw new Error(`ffmpeg failed while rendering screenshot: ${out}`);
  }

  updateManifest(projectRoot, args.manifest, {
    id: args.id || path.basename(out, path.extname(out)),
    kind: "screenshot",
    platform: args.platform || null,
    path: path.relative(projectRoot, out),
    source: path.relative(projectRoot, input),
    width,
    height,
    text: text || null,
  });
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
} finally {
  cleanupTempDirs(tempDirs);
}
