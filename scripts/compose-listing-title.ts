#!/usr/bin/env node
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const { tmpdir } = require("node:os");
const path = require("node:path");

const MAX_HERO_BYTES = 2 * 1024 * 1024;
const TARGET_HERO_BYTES = Math.floor(MAX_HERO_BYTES * 0.92);

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

function createTempFile(prefix, suffix, tempDirs) {
  const dir = fs.mkdtempSync(path.join(tmpdir(), prefix));
  tempDirs.push(dir);
  return path.join(dir, `output${suffix}`);
}

function normalizeTitle(value) {
  return String(value).replace(/\s+/g, " ").trim();
}

function visualUnits(text) {
  let units = 0;
  for (const char of Array.from(text)) {
    if (char === " ") {
      units += 0.45;
    } else if (/[ilI1!.,'|]/.test(char)) {
      units += 0.45;
    } else if (/[mwMW@#%&]/.test(char)) {
      units += 1.15;
    } else if (/[A-Z0-9]/.test(char)) {
      units += 0.9;
    } else {
      units += 0.78;
    }
  }
  return Math.max(units, 1);
}

function buildBalancedLines(words, lineCount) {
  if (lineCount <= 1 || words.length <= 1) return [words.join(" ")];
  if (words.length <= lineCount) return words.slice();

  const totalUnits = visualUnits(words.join(" "));
  const targetUnits = totalUnits / lineCount;
  const lines = [];
  let current = [];

  for (let index = 0; index < words.length; index += 1) {
    const word = words[index];
    const candidate = current.concat(word).join(" ");
    const remainingWords = words.length - index - 1;
    const remainingSlots = lineCount - lines.length - 1;
    if (
      current.length > 0 &&
      lines.length < lineCount - 1 &&
      visualUnits(candidate) > targetUnits &&
      remainingWords >= remainingSlots
    ) {
      lines.push(current.join(" "));
      current = [word];
    } else {
      current.push(word);
    }
  }

  if (current.length) lines.push(current.join(" "));
  return lines;
}

function fitTitleLayout(title, width, height, maxFontSize) {
  const normalizedTitle = normalizeTitle(title);
  const words = normalizedTitle.split(" ").filter(Boolean);
  if (!words.length) {
    throw new Error("Title is empty after whitespace normalization.");
  }

  const maxLines = Math.min(4, words.length);
  const safeWidth = Math.floor(width * 0.55);
  const safeHeight = Math.floor(height * 0.24);
  const minFontSize = Math.max(32, Math.floor(Math.min(width, height) * 0.035));
  let best = null;

  for (let lineCount = 1; lineCount <= maxLines; lineCount += 1) {
    const lines = buildBalancedLines(words, lineCount);
    const maxLineUnits = Math.max(...lines.map(visualUnits));
    const widthFontSize = Math.floor(safeWidth / (maxLineUnits * 0.62));
    const heightFontSize = Math.floor(safeHeight / (lines.length + Math.max(0, lines.length - 1) * 0.12));
    const fontSize = Math.min(maxFontSize, widthFontSize, heightFontSize);
    const score = fontSize * 100 - lines.length;
    if (!best || score > best.score) {
      best = { lines, fontSize, score };
    }
  }

  if (!best || best.fontSize < minFontSize) {
    throw new Error(`Listing title is too long to compose readably: ${normalizedTitle}`);
  }

  const lineSpacing = Math.max(4, Math.round(best.fontSize * 0.12));
  const borderWidth = Math.max(3, Math.round(best.fontSize * 0.045));
  const blockHeight = best.lines.length * best.fontSize + Math.max(0, best.lines.length - 1) * lineSpacing;

  return {
    title: normalizedTitle,
    lines: best.lines,
    fontSize: best.fontSize,
    lineSpacing,
    borderWidth,
    blockHeight,
  };
}

function cleanupTempDirs(tempDirs) {
  for (const dir of tempDirs) {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

function runFfmpeg(args, label) {
  const result = spawnSync("ffmpeg", args, { stdio: "inherit" });
  if (result.status !== 0) {
    throw new Error(`ffmpeg failed while ${label}`);
  }
}

function fileSize(file) {
  return fs.statSync(file).size;
}

function shrinkPngToHeroLimit(file, tempDirs) {
  if (fileSize(file) <= TARGET_HERO_BYTES) return;
  const source = createTempFile("playdrop-hero-source-", ".png", tempDirs);
  fs.copyFileSync(file, source);

  for (const colors of [224, 192, 160, 128, 96, 64]) {
    const palette = createTempFile(`playdrop-hero-palette-${colors}-`, ".png", tempDirs);
    const candidate = createTempFile(`playdrop-hero-candidate-${colors}-`, ".png", tempDirs);
    runFfmpeg([
      "-y",
      "-i",
      source,
      "-frames:v",
      "1",
      "-update",
      "1",
      "-vf",
      `palettegen=max_colors=${colors}:reserve_transparent=0`,
      palette,
    ], `creating listing hero palette (${colors} colors)`);
    runFfmpeg([
      "-y",
      "-i",
      source,
      "-i",
      palette,
      "-lavfi",
      "paletteuse=dither=bayer:bayer_scale=3",
      "-compression_level",
      "9",
      "-frames:v",
      "1",
      "-update",
      "1",
      candidate,
    ], `compressing listing hero (${colors} colors)`);
    if (fileSize(candidate) < fileSize(file)) {
      fs.copyFileSync(candidate, file);
    }
    if (fileSize(file) <= TARGET_HERO_BYTES) return;
  }

  throw new Error(`Listing hero remains too large after compression: ${file} is ${fileSize(file)} bytes, limit is ${MAX_HERO_BYTES} bytes.`);
}

function pngCrc32(buffer) {
  const table = pngCrc32.table || (pngCrc32.table = (() => {
    const built = [];
    for (let n = 0; n < 256; n += 1) {
      let c = n;
      for (let k = 0; k < 8; k += 1) {
        c = (c & 1) ? (0xedb88320 ^ (c >>> 1)) : (c >>> 1);
      }
      built[n] = c >>> 0;
    }
    return built;
  })());
  let crc = 0xffffffff;
  for (let index = 0; index < buffer.length; index += 1) {
    crc = table[(crc ^ buffer[index]) & 0xff] ^ (crc >>> 8);
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function pngTextChunk(keyword, value) {
  const key = String(keyword).trim().slice(0, 79);
  if (!/^[\x20-\x7e]+$/.test(key) || key.includes("\0")) {
    throw new Error(`Invalid PNG metadata keyword: ${keyword}`);
  }
  const text = String(value).replace(/[^\x20-\xff]/g, " ").slice(0, 4096);
  const data = Buffer.concat([
    Buffer.from(key, "latin1"),
    Buffer.from([0]),
    Buffer.from(text, "latin1"),
  ]);
  const type = Buffer.from("tEXt", "ascii");
  const length = Buffer.alloc(4);
  length.writeUInt32BE(data.length, 0);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(pngCrc32(Buffer.concat([type, data])), 0);
  return Buffer.concat([length, type, data, crc]);
}

function embedTitleMetadata(file, entries) {
  const input = fs.readFileSync(file);
  if (
    input.length < 12 ||
    input[0] !== 0x89 ||
    input[1] !== 0x50 ||
    input[2] !== 0x4e ||
    input[3] !== 0x47
  ) {
    throw new Error(`Title composition output is not a PNG: ${file}`);
  }
  const chunks = Object.entries(entries).map(([key, value]) => pngTextChunk(key, value));
  const parts = [input.subarray(0, 8)];
  let offset = 8;
  let inserted = false;
  while (offset + 12 <= input.length) {
    const length = input.readUInt32BE(offset);
    const chunkEnd = offset + 12 + length;
    if (chunkEnd > input.length) {
      throw new Error(`Invalid PNG output: ${file}`);
    }
    const type = input.toString("ascii", offset + 4, offset + 8);
    if (type === "IEND" && !inserted) {
      parts.push(...chunks);
      inserted = true;
    }
    parts.push(input.subarray(offset, chunkEnd));
    offset = chunkEnd;
    if (type === "IEND") break;
  }
  if (!inserted) {
    throw new Error(`PNG output is missing IEND: ${file}`);
  }
  fs.writeFileSync(file, Buffer.concat(parts));
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
  const title = normalizeTitle(requireString(args, "title"));
  const font = typeof args.font === "string" && args.font.trim() ? resolveFromRoot(projectRoot, args.font.trim()) : null;
  const width = parseNumber(args, "width", 1920, 320, 7680);
  const height = parseNumber(args, "height", 1080, 320, 7680);
  const maxFontSize = parseNumber(args, "font-size", Math.round(height * 0.13), 24, 520);
  const layout = fitTitleLayout(title, width, height, maxFontSize);
  const yBase = args.y === undefined
    ? Math.round((height - layout.blockHeight) / 2)
    : parseNumber(args, "y", 0, 0, height);
  if (yBase + layout.blockHeight > height) {
    throw new Error(`Listing title block does not fit vertically at y=${yBase}.`);
  }
  const artworkSource = parseArtworkSource(args["artwork-source"]);

  ensureTool("ffmpeg");
  ensureFile(input, "Input artwork");
  if (font) {
    ensureFile(font, "Font file");
  }
  const relativeInput = path.relative(projectRoot, input).split(path.sep).join("/");
  if (/^assets\/marketing\/(captures|screenshots|thumbnails|social)\//.test(relativeInput)) {
    throw new Error(`Listing hero input must be AI artwork, not a capture, screenshot, thumbnail, or social asset: ${relativeInput}`);
  }

  fs.mkdirSync(path.dirname(out), { recursive: true });
  const filters = [
    `scale=${width}:${height}:force_original_aspect_ratio=increase`,
    `crop=${width}:${height}`,
    `drawbox=x=0:y=0:w=iw:h=ih:color=black@0.08:t=fill`,
  ];
  layout.lines.forEach((line, index) => {
    const lineFile = createTextFile(line, tempDirs);
    const lineY = yBase + index * (layout.fontSize + layout.lineSpacing);
    const drawTextParts = [
      font ? `fontfile='${escapeDraw(font)}'` : null,
      `textfile='${escapeDraw(lineFile)}'`,
      "x=(w-text_w)/2",
      `y=${lineY}`,
      `fontsize=${layout.fontSize}`,
      "fontcolor=white",
      `borderw=${layout.borderWidth}`,
      "bordercolor=black@0.72",
      "expansion=none",
    ].filter(Boolean);
    filters.push(`drawtext=${drawTextParts.join(":")}`);
  });

  runFfmpeg([
    "-y",
    "-i",
    input,
    "-frames:v",
    "1",
    "-update",
    "1",
    "-compression_level",
    "9",
    "-vf",
    filters.join(","),
    out,
  ], `composing listing title: ${out}`);

  shrinkPngToHeroLimit(out, tempDirs);

  embedTitleMetadata(out, {
    "playdrop:listingTitleTool": "playdrop compose-listing-title",
    "playdrop:listingTitle": title,
    "playdrop:listingTitleSource": relativeInput,
    "playdrop:listingTitleArtworkSource": artworkSource,
  });

  updateManifest(projectRoot, args.manifest, {
    id: args.id || path.basename(out, path.extname(out)),
    kind: "playdrop-hero",
    path: path.relative(projectRoot, out),
    source: path.relative(projectRoot, input),
    width,
    height,
    title,
    font: font ? path.relative(projectRoot, font) : null,
    artworkSource,
    aiGenerated: true,
  });
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
} finally {
  cleanupTempDirs(tempDirs);
}
