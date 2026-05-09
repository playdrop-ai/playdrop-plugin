#!/usr/bin/env node
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { spawnSync } = require("node:child_process");

const MIN_SOURCE_CAPTURE_FPS = 60;
const MIN_SOURCE_CAPTURE_SECONDS = 12;
const MIN_FINAL_VIDEO_SECONDS = 8;
const MAX_FINAL_VIDEO_SECONDS = 15;
const MIN_FINAL_VIDEO_FPS = 30;
const MIN_INTEGRATED_LUFS = -28;
const MIN_PEAK_DB = -12;
const REQUIRED_VIDEO_FAMILIES = [
  { id: "vertical short", width: 1080, height: 1920 },
  { id: "landscape short", width: 1920, height: 1080 },
  { id: "feed portrait", width: 1080, height: 1350 },
  { id: "square feed", width: 1080, height: 1080 },
  { id: "pinterest pin", width: 1000, height: 1500 },
];

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
  --report assets/marketing/marketing-report.json \\
  --marketing MARKETING.md
`;
}

function readJson(file) {
  if (!fs.existsSync(file)) {
    throw new Error(`Required JSON file not found: ${file}`);
  }
  return JSON.parse(fs.readFileSync(file, "utf8"));
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

function ensureTool(name) {
  const result = spawnSync(name, ["-version"], { encoding: "utf8" });
  if (result.status !== 0) {
    throw new Error(`Missing required tool: ${name}`);
  }
}

function parseFps(raw) {
  if (typeof raw !== "string" || !raw.includes("/")) return Number(raw);
  const [num, den] = raw.split("/").map(Number);
  if (!Number.isFinite(num) || !Number.isFinite(den) || den === 0) return Number.NaN;
  return num / den;
}

function probeVideo(file) {
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
    ? probe.streams.find(stream => stream.codec_type === "video")
    : null;
  if (!video) {
    throw new Error(`Video stream missing: ${file}`);
  }
  return {
    width: Number(video.width),
    height: Number(video.height),
    fps: parseFps(video.avg_frame_rate || video.r_frame_rate),
    durationSeconds: Number.parseFloat(probe.format?.duration || "0"),
    audioTracks: Array.isArray(probe.streams)
      ? probe.streams.filter(stream => stream.codec_type === "audio").length
      : 0,
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
    throw new Error(`Unable to measure audio loudness: ${file}`);
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
    throw new Error(`Unable to measure audio peak: ${file}`);
  }
  const volumeText = `${volume.stdout || ""}\n${volume.stderr || ""}`;
  const peakMatch = volumeText.match(/max_volume:\s*(-?\d+(?:\.\d+)?) dB/);
  const peakDb = peakMatch ? Number(peakMatch[1]) : Number.NaN;
  if (!Number.isFinite(integratedLufs) || !Number.isFinite(peakDb)) {
    throw new Error(`Unable to parse audio metrics: ${file}`);
  }
  return { integratedLufs, peakDb };
}

function fileSha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
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

function resolveExistingMarketingPath(projectRoot, relativePath, label) {
  assertUnderMarketing(projectRoot, relativePath, label);
  return path.resolve(projectRoot, relativePath);
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
  if (manifest.captureSource !== "playdrop-cli-local-screen") {
    throw new Error("capture-manifest.json must come from playdrop project marketing capture with captureSource=playdrop-cli-local-screen");
  }
  if (typeof manifest.captureMethod === "string") {
    throw new Error("capture-manifest.json must not use ad hoc captureMethod text; use the public CLI captureSource contract");
  }
  if (Array.isArray(manifest.rejectedCaptures) && manifest.rejectedCaptures.length > 0) {
    throw new Error("Accepted marketing packs cannot contain rejected captures. Rerun CLI capture cleanly before rendering assets.");
  }
  if (!Array.isArray(manifest.captures) || manifest.captures.length === 0) {
    throw new Error("capture-manifest.json must include at least one capture");
  }
  for (const capture of manifest.captures) {
    const capturePath = resolveExistingMarketingPath(projectRoot, capture.path, `capture ${capture.surface || "unknown"}`);
    if (!["desktop", "mobile-landscape", "mobile-portrait"].includes(capture.surface)) {
      throw new Error(`Invalid capture surface: ${capture.surface}`);
    }
    if (!Number.isFinite(capture.width) || !Number.isFinite(capture.height)) {
      throw new Error(`Capture dimensions missing for ${capture.surface}`);
    }
    if (capture.audio?.policy !== "silent" && capture.hasAudio !== true) {
      throw new Error(`Capture ${capture.surface} requires audio for policy ${capture.audio?.policy}`);
    }
    if (!Number.isFinite(capture.fps) || capture.fps < MIN_SOURCE_CAPTURE_FPS) {
      throw new Error(`Capture ${capture.surface} must be at least ${MIN_SOURCE_CAPTURE_FPS} fps`);
    }
    if (!Number.isFinite(capture.durationSeconds) || capture.durationSeconds < MIN_SOURCE_CAPTURE_SECONDS) {
      throw new Error(`Capture ${capture.surface} must be at least ${MIN_SOURCE_CAPTURE_SECONDS} seconds`);
    }
    const probe = probeVideo(capturePath);
    if (probe.width !== capture.width || probe.height !== capture.height) {
      throw new Error(`Capture ${capture.surface} file dimensions do not match manifest`);
    }
    if (Math.round(probe.fps) < MIN_SOURCE_CAPTURE_FPS) {
      throw new Error(`Capture ${capture.surface} file is ${probe.fps} fps; expected at least ${MIN_SOURCE_CAPTURE_FPS}`);
    }
    if (capture.audio?.policy !== "silent") {
      if (!Number.isFinite(capture.audio?.integratedLufs) || !Number.isFinite(capture.audio?.peakDb)) {
        throw new Error(`Capture ${capture.surface} must include integratedLufs and peakDb audio metrics`);
      }
      if (capture.audio.integratedLufs < MIN_INTEGRATED_LUFS || capture.audio.peakDb < MIN_PEAK_DB) {
        throw new Error(`Capture ${capture.surface} audio is too quiet: ${capture.audio.integratedLufs} LUFS, peak ${capture.audio.peakDb} dB`);
      }
      if (manifest.audioPolicy === "music-and-sfx" && capture.audio.backgroundMusic !== true) {
        throw new Error(`Capture ${capture.surface} must include background music for music-and-sfx`);
      }
    }
  }
  return { count: manifest.captures.length, audioPolicy: manifest.audioPolicy || "music-and-sfx" };
}

function validateAssetManifest(projectRoot, file, audioPolicy) {
  const manifest = readJson(file);
  if (!Array.isArray(manifest.assets)) {
    throw new Error("asset-manifest.json must include assets[]");
  }
  const finalVideos = [];
  const playdropListingAssets = [];
  const hashes = new Map();
  for (const asset of manifest.assets) {
    const assetPath = resolveExistingMarketingPath(projectRoot, asset.path, `asset ${asset.id || "unknown"}`);
    const kind = String(asset.kind || "");
    const hash = asset.sha256 || fileSha256(assetPath);
    if (!hashes.has(hash)) hashes.set(hash, []);
    hashes.get(hash).push({ ...asset, hash });
    if (kind === "video") {
      finalVideos.push(asset);
      const probe = probeVideo(assetPath);
      if (probe.width !== asset.width || probe.height !== asset.height) {
        throw new Error(`Video ${asset.id || asset.path} dimensions do not match manifest`);
      }
      if (probe.durationSeconds < MIN_FINAL_VIDEO_SECONDS || probe.durationSeconds > MAX_FINAL_VIDEO_SECONDS + 0.5) {
        throw new Error(`Video ${asset.id || asset.path} must be ${MIN_FINAL_VIDEO_SECONDS}-${MAX_FINAL_VIDEO_SECONDS} seconds`);
      }
      if (Math.round(probe.fps) < MIN_FINAL_VIDEO_FPS) {
        throw new Error(`Video ${asset.id || asset.path} must be at least ${MIN_FINAL_VIDEO_FPS} fps`);
      }
      if (asset.firstSecondAction !== true || typeof asset.hookDescription !== "string" || !asset.hookDescription.trim()) {
        throw new Error(`Video ${asset.id || asset.path} must declare firstSecondAction and hookDescription`);
      }
      if (audioPolicy !== "silent") {
        if (probe.audioTracks === 0) {
          throw new Error(`Video ${asset.id || asset.path} must include audio`);
        }
        const audio = measureAudio(assetPath);
        if (audio.integratedLufs < MIN_INTEGRATED_LUFS || audio.peakDb < MIN_PEAK_DB) {
          throw new Error(`Video ${asset.id || asset.path} audio is too quiet: ${audio.integratedLufs} LUFS, peak ${audio.peakDb} dB`);
        }
      }
    }
    if (kind.startsWith("playdrop-")) {
      playdropListingAssets.push(asset);
    }
    if (kind === "playdrop-hero" || kind === "playdrop-icon") {
      if (asset.artworkSource !== "playdrop-ai" || asset.aiGenerated !== true) {
        throw new Error(`${kind} ${asset.id || asset.path} must declare artworkSource=playdrop-ai and aiGenerated=true`);
      }
    }
  }
  for (const family of REQUIRED_VIDEO_FAMILIES) {
    const found = finalVideos.some(asset => asset.width === family.width && asset.height === family.height);
    if (!found) {
      throw new Error(`Missing final social video family: ${family.id} (${family.width}x${family.height})`);
    }
  }
  const iconCount = playdropListingAssets.filter(asset => asset.kind === "playdrop-icon").length;
  const heroCount = playdropListingAssets.filter(asset => asset.kind === "playdrop-hero").length;
  if (iconCount < 1 || heroCount < 2) {
    throw new Error("PlayDrop listing assets must include at least one icon and two hero assets");
  }
  for (const duplicates of hashes.values()) {
    if (duplicates.length < 2) continue;
    const hasPlaydrop = duplicates.some(asset => String(asset.kind || "").startsWith("playdrop-"));
    const hasNonPlaydrop = duplicates.some(asset => !String(asset.kind || "").startsWith("playdrop-"));
    if (hasPlaydrop && hasNonPlaydrop) {
      const labels = duplicates.map(asset => `${asset.id || asset.path} (${asset.kind || "unknown"})`).join(", ");
      throw new Error(`Do not reuse social/capture assets as PlayDrop listing assets: ${labels}`);
    }
  }
  return manifest.assets.length;
}

function validateReport(file) {
  const report = readJson(file);
  if (!["passed", "failed"].includes(report.status)) {
    throw new Error("marketing-report.json status must be passed or failed");
  }
  if (report.status !== "passed") {
    throw new Error("marketing-report.json must be passed for an accepted marketing pack");
  }
  if (!Array.isArray(report.gates)) {
    throw new Error("marketing-report.json must include gates[]");
  }
  for (const gate of report.gates) {
    if (gate.status !== "passed") {
      throw new Error(`Marketing gate ${gate.id || "unknown"} is not passed`);
    }
    if (/\bwarning\b|\bcaveat\b|could not|unable|rejected/i.test(String(gate.summary || ""))) {
      throw new Error(`Marketing gate ${gate.id || "unknown"} contains caveat language`);
    }
  }
  if (Array.isArray(report.warnings) && report.warnings.length > 0) {
    throw new Error("Accepted marketing-report.json must not contain warnings");
  }
  if (report.captureValidation?.excitingMomentValidated !== true) {
    throw new Error("marketing-report.json must validate an exciting moment");
  }
  if (report.captureValidation?.audioValidated !== true) {
    throw new Error("marketing-report.json must validate audio");
  }
  return report.gates.length;
}

function validateMarketingMarkdown(projectRoot, markdownPath) {
  const file = path.resolve(projectRoot, markdownPath);
  if (!fs.existsSync(file)) return;
  const text = fs.readFileSync(file, "utf8");
  const blocked = [
    /PASS with caveat/i,
    /Listing art:\s*WARNING/i,
    /Marketing capture:\s*PASS with caveat/i,
    /no callable PlayDrop AI/i,
    /browser-frame capture/i,
    /manual capture/i,
    /recorded an unrelated/i,
  ];
  for (const pattern of blocked) {
    if (pattern.test(text)) {
      throw new Error(`MARKETING.md contains blocked caveat language: ${pattern}`);
    }
  }
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
  const marketingPath = args.marketing || "MARKETING.md";

  ensureTool("ffmpeg");
  ensureTool("ffprobe");
  const captureValidation = validateCaptureManifest(projectRoot, capturePath);
  const assetCount = validateAssetManifest(projectRoot, assetPath, captureValidation.audioPolicy);
  const gateCount = validateReport(reportPath);
  validateMarketingMarkdown(projectRoot, marketingPath);

  console.log(`Marketing manifests valid: ${captureValidation.count} captures, ${assetCount} assets, ${gateCount} gates`);
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
