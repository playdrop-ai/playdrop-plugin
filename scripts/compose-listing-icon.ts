#!/usr/bin/env node
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
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
node scripts/compose-listing-icon.ts \\
  --input assets/marketing/playdrop/icon-art.png \\
  --out assets/marketing/playdrop/icon.png \\
  [--root . --size 1024 --manifest assets/marketing/asset-manifest.json]
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

function resolveFromRoot(projectRoot, file) {
  return path.resolve(projectRoot, file);
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

try {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
    process.exit(0);
  }
  const projectRoot = path.resolve(args.root || process.cwd());
  const input = resolveFromRoot(projectRoot, requireString(args, "input"));
  const out = ensureMarketingOut(projectRoot, requireString(args, "out"));
  const size = parseNumber(args, "size", 1024, 256, 4096);

  ensureTool("ffmpeg");
  ensureFile(input, "Input icon artwork");

  fs.mkdirSync(path.dirname(out), { recursive: true });
  const result = spawnSync("ffmpeg", [
    "-y",
    "-i",
    input,
    "-frames:v",
    "1",
    "-update",
    "1",
    "-vf",
    `scale=${size}:${size}:force_original_aspect_ratio=increase,crop=${size}:${size}`,
    out,
  ], { stdio: "inherit" });

  if (result.status !== 0) {
    throw new Error(`ffmpeg failed while composing listing icon: ${out}`);
  }

  updateManifest(projectRoot, args.manifest, {
    id: args.id || path.basename(out, path.extname(out)),
    kind: "playdrop-icon",
    path: path.relative(projectRoot, out),
    source: path.relative(projectRoot, input),
    width: size,
    height: size,
  });
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
}
