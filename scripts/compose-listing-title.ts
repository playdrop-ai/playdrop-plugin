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
node scripts/compose-listing-title.ts \\
  --input assets/marketing/playdrop/hero-art.png \\
  --out assets/marketing/playdrop/hero-title.png \\
  --title "Game Name" --font assets/fonts/title.ttf \\
  --artwork-source playdrop-ai \\
  [--root . --width 1920 --height 1080 --manifest assets/marketing/asset-manifest.json]
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

function parseArtworkSource(raw) {
  const source = String(raw || "").trim();
  if (source !== "playdrop-ai") {
    throw new Error("Missing --artwork-source playdrop-ai. Listing hero art must start from PlayDrop AI-generated or AI-edited artwork.");
  }
  return source;
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
  manifest.assets = manifest.assets.filter((asset) => asset.id !== entry.id).concat(entry);
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
  const title = requireString(args, "title");
  const font = resolveFromRoot(projectRoot, requireString(args, "font"));
  const width = parseNumber(args, "width", 1920, 320, 7680);
  const height = parseNumber(args, "height", 1080, 320, 7680);
  const fontSize = parseNumber(args, "font-size", Math.round(height * 0.13), 24, 520);
  const y = args.y === undefined ? "(h-text_h)/2" : String(parseNumber(args, "y", 0, 0, height));
  const artworkSource = parseArtworkSource(args["artwork-source"]);

  ensureTool("ffmpeg");
  ensureFile(input, "Input artwork");
  ensureFile(font, "Font file");
  const relativeInput = path.relative(projectRoot, input).split(path.sep).join("/");
  if (/^assets\/marketing\/(captures|screenshots|thumbnails|social)\//.test(relativeInput)) {
    throw new Error(`Listing hero input must be AI artwork, not a capture, screenshot, thumbnail, or social asset: ${relativeInput}`);
  }

  fs.mkdirSync(path.dirname(out), { recursive: true });
  const titleFile = createTextFile(title, tempDirs);
  const filters = [
    `scale=${width}:${height}:force_original_aspect_ratio=increase`,
    `crop=${width}:${height}`,
    `drawbox=x=0:y=0:w=iw:h=ih:color=black@0.08:t=fill`,
    `drawtext=fontfile='${escapeDraw(font)}':textfile='${escapeDraw(titleFile)}':x=(w-text_w)/2:y=${y}:fontsize=${fontSize}:fontcolor=white:borderw=8:bordercolor=black@0.72:expansion=none`,
  ];

  const result = spawnSync("ffmpeg", [
    "-y",
    "-i",
    input,
    "-frames:v",
    "1",
    "-update",
    "1",
    "-vf",
    filters.join(","),
    out,
  ], { stdio: "inherit" });

  if (result.status !== 0) {
    throw new Error(`ffmpeg failed while composing listing title: ${out}`);
  }

  updateManifest(projectRoot, args.manifest, {
    id: args.id || path.basename(out, path.extname(out)),
    kind: "playdrop-hero",
    path: path.relative(projectRoot, out),
    source: path.relative(projectRoot, input),
    width,
    height,
    title,
    font: path.relative(projectRoot, font),
    artworkSource,
    aiGenerated: true,
  });
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
} finally {
  cleanupTempDirs(tempDirs);
}
