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
node scripts/extract-template-background.ts \\
  --input tmp/constrained.png --out assets/iso/building.png \\
  --keys '#ff0000,#ff00ff' \\
  [--distance-threshold 90] [--hue-threshold 18] \\
  [--remove-guide-lines --line-hue-threshold 45 --line-min-run 256] \\
  [--keep-largest-component] \\
  [--preview-bg '#ff00ff' --preview-out preview.png] \\
  [--contact-sheet-out contact-sheet.png] [--report report.json]

Removes template background pixels that are connected to the image border.
Use this when a generated template extraction has known red/purple locked
background colors but AI matte-pair regeneration drifts too much.
`);
}

function parseColor(value) {
  const named = {
    black: "#000000",
    white: "#ffffff",
    green: "#00ff00",
    purple: "#ff00ff",
    red: "#ff0000",
    cyan: "#00ffff",
    yellow: "#ffff00",
  };
  if (typeof value !== "string") throw new Error(`Invalid color: ${value}`);
  const raw = (named[value.toLowerCase()] ?? value).trim();
  const full = /^#?([0-9a-f]{6})$/i.exec(raw);
  if (!full) throw new Error(`Invalid color: ${value}`);
  const hex = full[1];
  return {
    r: parseInt(hex.slice(0, 2), 16),
    g: parseInt(hex.slice(2, 4), 16),
    b: parseInt(hex.slice(4, 6), 16),
  };
}

function colorToHex(color) {
  return `#${[color.r, color.g, color.b]
    .map((value) => value.toString(16).padStart(2, "0"))
    .join("")}`;
}

function readNumberArg(args, name, fallback, min, max) {
  const parsed = args[name] === undefined ? fallback : Number(args[name]);
  if (!Number.isFinite(parsed) || parsed < min || parsed > max) {
    throw new Error(`Invalid --${name}: expected a number from ${min} to ${max}`);
  }
  return parsed;
}

function readPng(file) {
  return PNG.sync.read(fs.readFileSync(file));
}

function writePng(file, png) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, PNG.sync.write(png));
}

function channelDistance(a, b) {
  return Math.max(Math.abs(a.r - b.r), Math.abs(a.g - b.g), Math.abs(a.b - b.b));
}

function rgbToHsv(color) {
  const r = color.r / 255;
  const g = color.g / 255;
  const b = color.b / 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const delta = max - min;
  let h = 0;
  if (delta !== 0) {
    if (max === r) h = 60 * (((g - b) / delta) % 6);
    else if (max === g) h = 60 * ((b - r) / delta + 2);
    else h = 60 * ((r - g) / delta + 4);
  }
  if (h < 0) h += 360;
  return {
    h,
    s: max === 0 ? 0 : delta / max,
    v: max,
  };
}

function hueDistance(a, b) {
  const diff = Math.abs(a - b) % 360;
  return Math.min(diff, 360 - diff);
}

function makeTemplateMatcher(keys, options) {
  const keyHsv = keys.map((key) => ({ rgb: key, hsv: rgbToHsv(key) }));
  return function matchesTemplateBackground(pixel) {
    if (pixel.a <= 2) return true;
    for (const key of keyHsv) {
      if (channelDistance(pixel, key.rgb) <= options.distanceThreshold) return true;
      const hsv = rgbToHsv(pixel);
      if (
        hsv.s >= options.minSaturation &&
        hsv.v >= options.minValue &&
        hueDistance(hsv.h, key.hsv.h) <= options.hueThreshold
      ) {
        return true;
      }
    }
    return false;
  };
}

function removeGuideLines(source, marked, keys, options) {
  const matcher = makeTemplateMatcher(keys, {
    distanceThreshold: options.distanceThreshold,
    hueThreshold: options.lineHueThreshold,
    minSaturation: options.minSaturation,
    minValue: options.minValue,
  });
  let removed = 0;
  function removeRun(indexes) {
    if (indexes.length < options.lineMinRun) return;
    for (const index of indexes) {
      if (!marked[index]) {
        marked[index] = 1;
        removed += 1;
      }
    }
  }

  for (let y = 0; y < source.height; y += 1) {
    let run = [];
    for (let x = 0; x <= source.width; x += 1) {
      const index = y * source.width + x;
      const isCandidate =
        x < source.width && !marked[index] && matcher(getPixel(source, index));
      if (isCandidate) {
        run.push(index);
      } else if (run.length > 0) {
        removeRun(run);
        run = [];
      }
    }
  }

  for (let x = 0; x < source.width; x += 1) {
    let run = [];
    for (let y = 0; y <= source.height; y += 1) {
      const index = y * source.width + x;
      const isCandidate =
        y < source.height && !marked[index] && matcher(getPixel(source, index));
      if (isCandidate) {
        run.push(index);
      } else if (run.length > 0) {
        removeRun(run);
        run = [];
      }
    }
  }
  return removed;
}

function getPixel(png, index) {
  const offset = index * 4;
  return {
    r: png.data[offset],
    g: png.data[offset + 1],
    b: png.data[offset + 2],
    a: png.data[offset + 3],
  };
}

function setTransparent(png, index) {
  const offset = index * 4;
  png.data[offset] = 0;
  png.data[offset + 1] = 0;
  png.data[offset + 2] = 0;
  png.data[offset + 3] = 0;
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

function renderOverBackground(source, bg) {
  const out = new PNG({ width: source.width, height: source.height });
  for (let y = 0; y < source.height; y += 1) {
    for (let x = 0; x < source.width; x += 1) {
      const index = (source.width * y + x) * 4;
      const mixed = compositeOver(
        {
          r: source.data[index],
          g: source.data[index + 1],
          b: source.data[index + 2],
          a: source.data[index + 3],
        },
        bg
      );
      out.data[index] = mixed.r;
      out.data[index + 1] = mixed.g;
      out.data[index + 2] = mixed.b;
      out.data[index + 3] = 255;
    }
  }
  return out;
}

function renderContactSheet(source, colors) {
  const out = new PNG({ width: source.width * colors.length, height: source.height });
  for (let i = 0; i < colors.length; i += 1) {
    const rendered = renderOverBackground(source, colors[i]);
    for (let y = 0; y < source.height; y += 1) {
      for (let x = 0; x < source.width; x += 1) {
        const src = (source.width * y + x) * 4;
        const dst = (out.width * y + (i * source.width + x)) * 4;
        out.data[dst] = rendered.data[src];
        out.data[dst + 1] = rendered.data[src + 1];
        out.data[dst + 2] = rendered.data[src + 2];
        out.data[dst + 3] = 255;
      }
    }
  }
  return out;
}

function visibleBounds(png) {
  let minX = png.width;
  let minY = png.height;
  let maxX = -1;
  let maxY = -1;
  let visible = 0;
  for (let y = 0; y < png.height; y += 1) {
    for (let x = 0; x < png.width; x += 1) {
      const alpha = png.data[(png.width * y + x) * 4 + 3];
      if (alpha <= 2) continue;
      visible += 1;
      minX = Math.min(minX, x);
      minY = Math.min(minY, y);
      maxX = Math.max(maxX, x);
      maxY = Math.max(maxY, y);
    }
  }
  if (maxX < minX || maxY < minY) {
    return { x: 0, y: 0, width: 0, height: 0, visible };
  }
  return { x: minX, y: minY, width: maxX - minX + 1, height: maxY - minY + 1, visible };
}

function keepLargestVisibleComponent(png) {
  const total = png.width * png.height;
  const seen = new Uint8Array(total);
  const components = [];
  for (let start = 0; start < total; start += 1) {
    if (seen[start]) continue;
    if (png.data[start * 4 + 3] <= 2) {
      seen[start] = 1;
      continue;
    }
    const pixels = [start];
    const queue = [start];
    seen[start] = 1;
    for (let cursor = 0; cursor < queue.length; cursor += 1) {
      const index = queue[cursor];
      const x = index % png.width;
      const y = Math.floor(index / png.width);
      const neighbors = [
        { index: index - 1, x: x - 1, y },
        { index: index + 1, x: x + 1, y },
        { index: index - png.width, x, y: y - 1 },
        { index: index + png.width, x, y: y + 1 },
      ];
      for (const next of neighbors) {
        if (
          next.x < 0 ||
          next.y < 0 ||
          next.x >= png.width ||
          next.y >= png.height ||
          seen[next.index]
        ) {
          continue;
        }
        if (png.data[next.index * 4 + 3] <= 2) {
          seen[next.index] = 1;
          continue;
        }
        seen[next.index] = 1;
        pixels.push(next.index);
        queue.push(next.index);
      }
    }
    components.push(pixels);
  }

  components.sort((a, b) => b.length - a.length);
  const keep = new Set(components[0] ?? []);
  let removed = 0;
  for (let i = 1; i < components.length; i += 1) {
    for (const index of components[i]) {
      if (keep.has(index)) continue;
      setTransparent(png, index);
      removed += 1;
    }
  }
  return {
    componentCount: components.length,
    largestComponentPixels: components[0]?.length ?? 0,
    removedPixels: removed,
  };
}

const args = parseArgs(process.argv.slice(2));
const inputFile = args.input;
const outFile = args.out;
if (typeof inputFile !== "string" || typeof outFile !== "string") usage();

const keys = String(args.keys ?? "#ff0000,#ff00ff")
  .split(",")
  .map((value) => parseColor(value.trim()));
const matcher = makeTemplateMatcher(keys, {
  distanceThreshold: readNumberArg(args, "distance-threshold", 90, 0, 255),
  hueThreshold: readNumberArg(args, "hue-threshold", 18, 0, 180),
  minSaturation: readNumberArg(args, "min-saturation", 0.55, 0, 1),
  minValue: readNumberArg(args, "min-value", 0.45, 0, 1),
});
const source = readPng(inputFile);
const out = PNG.sync.read(PNG.sync.write(source));
const total = source.width * source.height;
const marked = new Uint8Array(total);
const queue = [];

function enqueue(x, y) {
  if (x < 0 || y < 0 || x >= source.width || y >= source.height) return;
  const index = y * source.width + x;
  if (marked[index]) return;
  if (!matcher(getPixel(source, index))) return;
  marked[index] = 1;
  queue.push(index);
}

for (let x = 0; x < source.width; x += 1) {
  enqueue(x, 0);
  enqueue(x, source.height - 1);
}
for (let y = 0; y < source.height; y += 1) {
  enqueue(0, y);
  enqueue(source.width - 1, y);
}

for (let cursor = 0; cursor < queue.length; cursor += 1) {
  const index = queue[cursor];
  const x = index % source.width;
  const y = Math.floor(index / source.width);
  enqueue(x - 1, y);
  enqueue(x + 1, y);
  enqueue(x, y - 1);
  enqueue(x, y + 1);
}

const guideLineRemoved = args["remove-guide-lines"]
  ? removeGuideLines(source, marked, keys, {
      distanceThreshold: readNumberArg(args, "distance-threshold", 90, 0, 255),
      lineHueThreshold: readNumberArg(args, "line-hue-threshold", 45, 0, 180),
      minSaturation: readNumberArg(args, "min-saturation", 0.55, 0, 1),
      minValue: readNumberArg(args, "min-value", 0.45, 0, 1),
      lineMinRun: readNumberArg(args, "line-min-run", 256, 1, Math.max(source.width, source.height)),
    })
  : 0;

for (let i = 0; i < marked.length; i += 1) {
  if (marked[i]) setTransparent(out, i);
}

const componentCleanup = args["keep-largest-component"]
  ? keepLargestVisibleComponent(out)
  : { componentCount: undefined, largestComponentPixels: undefined, removedPixels: 0 };

writePng(outFile, out);

if (typeof args["preview-out"] === "string") {
  const previewBg = parseColor(args["preview-bg"] ?? "#ff00ff");
  writePng(args["preview-out"], renderOverBackground(out, previewBg));
}

if (typeof args["contact-sheet-out"] === "string") {
  const colors = String(args["contact-sheet-colors"] ?? "red,purple,cyan,yellow,black,white")
    .split(",")
    .map((value) => parseColor(value.trim()));
  writePng(args["contact-sheet-out"], renderContactSheet(out, colors));
}

const bounds = visibleBounds(out);
const report = {
  input: inputFile,
  out: outFile,
  width: source.width,
  height: source.height,
  keys: keys.map(colorToHex),
  removedPixels: queue.length + guideLineRemoved + componentCleanup.removedPixels,
  removedRatio: (queue.length + guideLineRemoved + componentCleanup.removedPixels) / total,
  guideLineRemovedPixels: guideLineRemoved,
  componentCleanup: {
    enabled: Boolean(args["keep-largest-component"]),
    componentCount: componentCleanup.componentCount,
    largestComponentPixels: componentCleanup.largestComponentPixels,
    removedPixels: componentCleanup.removedPixels,
  },
  visiblePixels: bounds.visible,
  bounds: { x: bounds.x, y: bounds.y, width: bounds.width, height: bounds.height },
  thresholds: {
    distanceThreshold: readNumberArg(args, "distance-threshold", 90, 0, 255),
    hueThreshold: readNumberArg(args, "hue-threshold", 18, 0, 180),
    minSaturation: readNumberArg(args, "min-saturation", 0.55, 0, 1),
    minValue: readNumberArg(args, "min-value", 0.45, 0, 1),
    removeGuideLines: Boolean(args["remove-guide-lines"]),
    lineHueThreshold: readNumberArg(args, "line-hue-threshold", 45, 0, 180),
    lineMinRun: readNumberArg(args, "line-min-run", 256, 1, Math.max(source.width, source.height)),
  },
};
if (typeof args.report === "string") {
  fs.mkdirSync(path.dirname(args.report), { recursive: true });
  fs.writeFileSync(args.report, `${JSON.stringify(report, null, 2)}\n`);
} else {
  process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
}
