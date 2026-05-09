#!/usr/bin/env node
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
node scripts/validate-marketing-manifest.ts \\
  --root . \\
  --capture assets/marketing/capture-manifest.json \\
  --assets assets/marketing/asset-manifest.json \\
  --report assets/marketing/marketing-report.json
`;
}

function readJson(file) {
  if (!fs.existsSync(file)) {
    throw new Error(`Required JSON file not found: ${file}`);
  }
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function assertUnderMarketing(projectRoot, relativePath, label) {
  if (typeof relativePath !== "string" || relativePath.trim() === "") {
    throw new Error(`${label} path is missing`);
  }
  const resolved = path.resolve(projectRoot, relativePath);
  const marketingRoot = path.resolve(projectRoot, "assets", "marketing");
  const rel = path.relative(marketingRoot, resolved);
  if (rel === ".." || rel.startsWith(`..${path.sep}`) || path.isAbsolute(rel)) {
    throw new Error(`${label} must live under assets/marketing/: ${relativePath}`);
  }
  if (!fs.existsSync(resolved)) {
    throw new Error(`${label} file not found: ${relativePath}`);
  }
}

function resolveMarketingFile(projectRoot, file, label) {
  const resolved = path.resolve(projectRoot, file);
  const marketingRoot = path.resolve(projectRoot, "assets", "marketing");
  const rel = path.relative(marketingRoot, resolved);
  if (rel === ".." || rel.startsWith(`..${path.sep}`) || path.isAbsolute(rel)) {
    throw new Error(`${label} must live under assets/marketing/: ${file}`);
  }
  return resolved;
}

function validateCaptureManifest(projectRoot, file) {
  const manifest = readJson(file);
  if (!Array.isArray(manifest.captures) || manifest.captures.length === 0) {
    throw new Error("capture-manifest.json must include at least one capture");
  }
  for (const capture of manifest.captures) {
    assertUnderMarketing(projectRoot, capture.path, `capture ${capture.surface || "unknown"}`);
    if (!["desktop", "mobile-landscape", "mobile-portrait"].includes(capture.surface)) {
      throw new Error(`Invalid capture surface: ${capture.surface}`);
    }
    if (!Number.isFinite(capture.width) || !Number.isFinite(capture.height)) {
      throw new Error(`Capture dimensions missing for ${capture.surface}`);
    }
    if (capture.audio?.policy !== "silent" && capture.hasAudio !== true) {
      throw new Error(`Capture ${capture.surface} requires audio for policy ${capture.audio?.policy}`);
    }
  }
  return manifest.captures.length;
}

function validateAssetManifest(projectRoot, file) {
  const manifest = readJson(file);
  if (!Array.isArray(manifest.assets)) {
    throw new Error("asset-manifest.json must include assets[]");
  }
  for (const asset of manifest.assets) {
    assertUnderMarketing(projectRoot, asset.path, `asset ${asset.id || "unknown"}`);
  }
  return manifest.assets.length;
}

function validateReport(file) {
  const report = readJson(file);
  if (!["passed", "failed"].includes(report.status)) {
    throw new Error("marketing-report.json status must be passed or failed");
  }
  if (!Array.isArray(report.gates)) {
    throw new Error("marketing-report.json must include gates[]");
  }
  return report.gates.length;
}

try {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
    process.exit(0);
  }
  const projectRoot = path.resolve(args.root || ".");
  const capturePath = resolveMarketingFile(projectRoot, args.capture || "assets/marketing/capture-manifest.json", "capture manifest");
  const assetPath = resolveMarketingFile(projectRoot, args.assets || "assets/marketing/asset-manifest.json", "asset manifest");
  const reportPath = resolveMarketingFile(projectRoot, args.report || "assets/marketing/marketing-report.json", "marketing report");

  const captureCount = validateCaptureManifest(projectRoot, capturePath);
  const assetCount = validateAssetManifest(projectRoot, assetPath);
  const gateCount = validateReport(reportPath);

  console.log(`Marketing manifests valid: ${captureCount} captures, ${assetCount} assets, ${gateCount} gates`);
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
