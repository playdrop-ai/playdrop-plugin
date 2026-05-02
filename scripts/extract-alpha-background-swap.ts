#!/usr/bin/env node
const fs = require("node:fs");
const path = require("node:path");

function loadPng() {
  const candidates = [
    "pngjs",
    process.env.PLAYDROP_NODE_MODULES
      ? path.join(process.env.PLAYDROP_NODE_MODULES, "pngjs")
      : "",
    process.env.CODEX_NODE_MODULES
      ? path.join(process.env.CODEX_NODE_MODULES, "pngjs")
      : "",
    process.env.HOME
      ? path.join(
          process.env.HOME,
          ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/pngjs"
        )
      : "",
  ].filter(Boolean);

  for (const candidate of candidates) {
    try {
      return require(candidate).PNG;
    } catch {
      // Try the next known location.
    }
  }

  throw new Error(
    "Missing pngjs. Set PLAYDROP_NODE_MODULES or NODE_PATH to a node_modules directory containing pngjs."
  );
}

const PNG = loadPng();

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
  throw new Error(`Usage:
node scripts/extract-alpha-background-swap.ts \\
  --base matte-a.png --swap matte-b.png --out element.png \\
  --base-bg '#000000' --swap-bg '#00ff00' \\
  [--preview-bg '#ff00ff' --preview-out preview.png] \\
  [--contact-sheet-out contact-sheet.png] [--report report.json]

Both input images must be the same element on flat, different background colors.
`);
}

function parseColor(value) {
  if (typeof value !== "string") usage();
  const named = {
    black: "#000000",
    white: "#ffffff",
    green: "#00ff00",
    purple: "#ff00ff",
    red: "#ff0000",
    cyan: "#00ffff",
    yellow: "#ffff00",
  };
  const raw = (named[value.toLowerCase()] ?? value).trim();
  const short = /^#?([0-9a-f]{3})$/i.exec(raw);
  if (short) {
    const [r, g, b] = short[1].split("").map((c) => parseInt(c + c, 16));
    return { r, g, b };
  }
  const full = /^#?([0-9a-f]{6})$/i.exec(raw);
  if (!full) throw new Error(`Invalid color: ${value}`);
  const hex = full[1];
  return {
    r: parseInt(hex.slice(0, 2), 16),
    g: parseInt(hex.slice(2, 4), 16),
    b: parseInt(hex.slice(4, 6), 16),
  };
}

function readPng(file) {
  return PNG.sync.read(fs.readFileSync(file));
}

function writePng(file, png) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, PNG.sync.write(png));
}

function clamp(value, min = 0, max = 255) {
  return Math.max(min, Math.min(max, value));
}

function dist(a, b) {
  const dr = a.r - b.r;
  const dg = a.g - b.g;
  const db = a.b - b.b;
  return Math.sqrt(dr * dr + dg * dg + db * db);
}

function rgbAt(data, index) {
  return { r: data[index], g: data[index + 1], b: data[index + 2] };
}

function median(values) {
  const sorted = values.slice().sort((a, b) => a - b);
  return sorted[Math.floor(sorted.length / 2)];
}

function estimateAlpha(first, second, firstBg, secondBg) {
  const ratios = [];
  const channels = ["r", "g", "b"];
  for (const channel of channels) {
    const denom = firstBg[channel] - secondBg[channel];
    if (Math.abs(denom) < 24) continue;
    const transparency = (first[channel] - second[channel]) / denom;
    if (Number.isFinite(transparency)) {
      ratios.push(clamp(transparency, -0.2, 1.2));
    }
  }

  if (!ratios.length) return 1;
  return clamp(1 - median(ratios), 0, 1);
}

function unmatte(first, second, firstBg, secondBg, alpha) {
  if (alpha <= 0.001) return { r: 0, g: 0, b: 0 };
  const transparency = 1 - alpha;
  return {
    r: Math.round(
      clamp(
        ((first.r - transparency * firstBg.r) + (second.r - transparency * secondBg.r)) /
          (2 * alpha)
      )
    ),
    g: Math.round(
      clamp(
        ((first.g - transparency * firstBg.g) + (second.g - transparency * secondBg.g)) /
          (2 * alpha)
      )
    ),
    b: Math.round(
      clamp(
        ((first.b - transparency * firstBg.b) + (second.b - transparency * secondBg.b)) /
          (2 * alpha)
      )
    ),
  };
}

function compositeOver(pixel, bg) {
  const alpha = pixel.a / 255;
  return {
    r: Math.round(pixel.r * alpha + bg.r * (1 - alpha)),
    g: Math.round(pixel.g * alpha + bg.g * (1 - alpha)),
    b: Math.round(pixel.b * alpha + bg.b * (1 - alpha)),
    a: 255,
  };
}

function colorToHex(color) {
  return `#${[color.r, color.g, color.b]
    .map((value) => value.toString(16).padStart(2, "0"))
    .join("")}`;
}

function parseContactSheetColors(value) {
  const raw = typeof value === "string" ? value : "red,purple,cyan,yellow,black,white";
  return raw.split(",").map((item) => parseColor(item.trim()));
}

function readNumberArg(
  value,
  fallback,
  name,
  min,
  max
) {
  const parsed = value === undefined ? fallback : Number(value);
  if (!Number.isFinite(parsed) || parsed < min || parsed > max) {
    throw new Error(`Invalid --${name}: expected a number from ${min} to ${max}`);
  }
  return parsed;
}

function createContactSheet(source, colors) {
  const sheet = new PNG({ width: source.width * colors.length, height: source.height });
  for (let panel = 0; panel < colors.length; panel += 1) {
    const bg = colors[panel];
    for (let y = 0; y < source.height; y += 1) {
      for (let x = 0; x < source.width; x += 1) {
        const sourceIndex = (source.width * y + x) * 4;
        const sheetIndex = (sheet.width * y + panel * source.width + x) * 4;
        const mixed = compositeOver(
          {
            r: source.data[sourceIndex],
            g: source.data[sourceIndex + 1],
            b: source.data[sourceIndex + 2],
            a: source.data[sourceIndex + 3],
          },
          bg
        );
        sheet.data[sheetIndex] = mixed.r;
        sheet.data[sheetIndex + 1] = mixed.g;
        sheet.data[sheetIndex + 2] = mixed.b;
        sheet.data[sheetIndex + 3] = 255;
      }
    }
  }
  return sheet;
}

const args = parseArgs(process.argv.slice(2));
const baseFile = args.base;
const swapFile = args.swap;
const outFile = args.out;
if (typeof baseFile !== "string" || typeof swapFile !== "string" || typeof outFile !== "string") {
  usage();
}

const firstBg = parseColor(args["base-bg"]);
const secondBg = parseColor(args["swap-bg"]);
if (dist(firstBg, secondBg) < 32) {
  throw new Error("--base-bg and --swap-bg must be visibly different colors");
}
const previewBg = args["preview-bg"] ? parseColor(args["preview-bg"]) : undefined;
const contactSheetColors =
  typeof args["contact-sheet-out"] === "string"
    ? parseContactSheetColors(args["contact-sheet-colors"])
    : undefined;
const bgThreshold = readNumberArg(
  args["background-threshold"],
  12,
  "background-threshold",
  0,
  441
);
const sameThreshold = readNumberArg(args["same-threshold"], 8, "same-threshold", 0, 441);
const alphaFloor = readNumberArg(args["alpha-floor"], 2, "alpha-floor", 0, 255);
const residueThreshold = readNumberArg(
  args["residue-threshold"],
  bgThreshold,
  "residue-threshold",
  0,
  441
);

const base = readPng(baseFile);
const swap = readPng(swapFile);
if (base.width !== swap.width || base.height !== swap.height) {
  throw new Error(`Image sizes differ: ${base.width}x${base.height} vs ${swap.width}x${swap.height}`);
}

const out = new PNG({ width: base.width, height: base.height });
const preview = previewBg ? new PNG({ width: base.width, height: base.height }) : undefined;
let transparent = 0;
let matte = 0;
let opaque = 0;
let visible = 0;
let semiTransparent = 0;
let pairDrift = 0;
let potentialBaseResidue = 0;
let potentialSwapResidue = 0;

for (let y = 0; y < base.height; y += 1) {
  for (let x = 0; x < base.width; x += 1) {
    const index = (base.width * y + x) * 4;
    const first = rgbAt(base.data, index);
    const second = rgbAt(swap.data, index);
    const firstDistance = dist(first, firstBg);
    const secondDistance = dist(second, secondBg);
    const pairDistance = dist(first, second);

    let pixel;
    const isFlatBackground = firstDistance <= bgThreshold && secondDistance <= bgThreshold;
    if (isFlatBackground) {
      pixel = { r: 0, g: 0, b: 0, a: 0 };
      transparent += 1;
    } else if (pairDistance <= sameThreshold) {
      pixel = {
        r: Math.round((first.r + second.r) / 2),
        g: Math.round((first.g + second.g) / 2),
        b: Math.round((first.b + second.b) / 2),
        a: 255,
      };
      opaque += 1;
    } else {
      const alpha = estimateAlpha(first, second, firstBg, secondBg);
      if (alpha * 255 <= alphaFloor) {
        pixel = { r: 0, g: 0, b: 0, a: 0 };
        transparent += 1;
      } else if (alpha >= 0.985) {
        pixel = {
          r: Math.round((first.r + second.r) / 2),
          g: Math.round((first.g + second.g) / 2),
          b: Math.round((first.b + second.b) / 2),
          a: 255,
        };
        opaque += 1;
      } else {
        const color = unmatte(first, second, firstBg, secondBg, alpha);
        pixel = { ...color, a: Math.round(alpha * 255) };
        matte += 1;
      }
    }

    if (!isFlatBackground && pairDistance > sameThreshold) {
      pairDrift += 1;
    }
    if (pixel.a > alphaFloor) {
      visible += 1;
      if (pixel.a < 255) semiTransparent += 1;
      const pixelRgb = { r: pixel.r, g: pixel.g, b: pixel.b };
      if (dist(pixelRgb, firstBg) <= residueThreshold) potentialBaseResidue += 1;
      if (dist(pixelRgb, secondBg) <= residueThreshold) potentialSwapResidue += 1;
    }

    out.data[index] = pixel.r;
    out.data[index + 1] = pixel.g;
    out.data[index + 2] = pixel.b;
    out.data[index + 3] = pixel.a;

    if (preview && previewBg) {
      const mixed = compositeOver(pixel, previewBg);
      preview.data[index] = mixed.r;
      preview.data[index + 1] = mixed.g;
      preview.data[index + 2] = mixed.b;
      preview.data[index + 3] = mixed.a;
    }
  }
}

writePng(outFile, out);
if (preview && typeof args["preview-out"] === "string") {
  writePng(args["preview-out"], preview);
}
if (contactSheetColors && typeof args["contact-sheet-out"] === "string") {
  writePng(args["contact-sheet-out"], createContactSheet(out, contactSheetColors));
}

const warnings = [];
const visiblePixels = Math.max(visible, 1);
const pairDriftRatio = pairDrift / (base.width * base.height);
const baseResidueRatio = potentialBaseResidue / visiblePixels;
const swapResidueRatio = potentialSwapResidue / visiblePixels;
if (pairDriftRatio > 0.05) {
  warnings.push(
    "Matte pair drift detected. This is common with AI-generated matte pairs and is not a failure by itself; inspect visual previews."
  );
}
if (baseResidueRatio > 0.01 || swapResidueRatio > 0.01) {
  warnings.push(
    "Potential matte-color residue detected in visible pixels. Inspect the contact sheet for halos, holes, or background blocks."
  );
}

const report = {
  width: base.width,
  height: base.height,
  pixels: base.width * base.height,
  transparent,
  matte,
  opaque,
  diagnostics: {
    visible,
    semiTransparent,
    pairDriftPixels: pairDrift,
    pairDriftRatio,
    potentialMatteResidue: {
      baseBgPixels: potentialBaseResidue,
      baseBgRatio: baseResidueRatio,
      swapBgPixels: potentialSwapResidue,
      swapBgRatio: swapResidueRatio,
      threshold: residueThreshold,
    },
    warnings,
    acceptance: {
      automaticResult: warnings.length ? "visual-review-required" : "no-obvious-script-detected-residue",
      rule: "Do not reject only because matte/semiTransparent counts are high. Accept or retry based on visual contact-sheet inspection.",
    },
  },
  colors: { firstBg, secondBg, previewBg },
  contactSheet: contactSheetColors
    ? {
        out: typeof args["contact-sheet-out"] === "string" ? args["contact-sheet-out"] : undefined,
        colors: contactSheetColors.map(colorToHex),
      }
    : undefined,
  thresholds: { bgThreshold, sameThreshold, alphaFloor, residueThreshold },
};

if (typeof args.report === "string") {
  fs.mkdirSync(path.dirname(args.report), { recursive: true });
  fs.writeFileSync(args.report, `${JSON.stringify(report, null, 2)}\n`);
} else {
  process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
}
