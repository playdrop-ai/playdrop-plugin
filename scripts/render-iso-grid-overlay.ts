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
node scripts/render-iso-grid-overlay.ts \\
  --image assets/iso/building.png --out tmp/building-iso-overlay.png \\
  --tile-width 128 --tile-height 64 --footprint-width 2 --footprint-height 2 \\
  --origin-x 512 --origin-y 720 [--background '#ff00ff'] [--report report.json]

Only classic 2:1 isometric grids are supported.
Current v1 asset extraction only supports square footprints.
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
  if (typeof value !== "string") usage();
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

function compositeOver(pixel, bg) {
  const alpha = pixel.a / 255;
  return {
    r: Math.round(pixel.r * alpha + bg.r * (1 - alpha)),
    g: Math.round(pixel.g * alpha + bg.g * (1 - alpha)),
    b: Math.round(pixel.b * alpha + bg.b * (1 - alpha)),
    a: 255,
  };
}

function blendOver(data, width, height, x, y, color) {
  const px = Math.round(x);
  const py = Math.round(y);
  if (px < 0 || py < 0 || px >= width || py >= height) return;
  const index = (width * py + px) * 4;
  const alpha = color.a / 255;
  data[index] = Math.round(color.r * alpha + data[index] * (1 - alpha));
  data[index + 1] = Math.round(color.g * alpha + data[index + 1] * (1 - alpha));
  data[index + 2] = Math.round(color.b * alpha + data[index + 2] * (1 - alpha));
  data[index + 3] = 255;
}

function drawLine(png, x0, y0, x1, y1, color, width = 2) {
  const dx = x1 - x0;
  const dy = y1 - y0;
  const steps = Math.max(Math.abs(dx), Math.abs(dy), 1);
  for (let i = 0; i <= steps; i += 1) {
    const t = i / steps;
    const x = x0 + dx * t;
    const y = y0 + dy * t;
    const radius = Math.floor(width / 2);
    for (let oy = -radius; oy <= radius; oy += 1) {
      for (let ox = -radius; ox <= radius; ox += 1) {
        blendOver(png.data, png.width, png.height, x + ox, y + oy, color);
      }
    }
  }
}

function drawCross(png, x, y, color) {
  drawLine(png, x - 10, y, x + 10, y, color, 3);
  drawLine(png, x, y - 10, x, y + 10, color, 3);
}

function isoPoint(originX, originY, tileWidth, tileHeight, gridX, gridY, footprintWidth, footprintHeight) {
  const centeredX = gridX - footprintWidth / 2;
  const centeredY = gridY - footprintHeight / 2;
  return {
    x: originX + (centeredX - centeredY) * (tileWidth / 2),
    y: originY + (centeredX + centeredY) * (tileHeight / 2),
  };
}

function visibleBounds(png) {
  let minX = png.width;
  let minY = png.height;
  let maxX = -1;
  let maxY = -1;
  for (let y = 0; y < png.height; y += 1) {
    for (let x = 0; x < png.width; x += 1) {
      const alpha = png.data[(png.width * y + x) * 4 + 3];
      if (alpha <= 2) continue;
      minX = Math.min(minX, x);
      minY = Math.min(minY, y);
      maxX = Math.max(maxX, x);
      maxY = Math.max(maxY, y);
    }
  }
  if (maxX < minX || maxY < minY) return { x: 0, y: 0, width: 0, height: 0 };
  return { x: minX, y: minY, width: maxX - minX + 1, height: maxY - minY + 1 };
}

const args = parseArgs(process.argv.slice(2));
const imageFile = args.image;
const outFile = args.out;
if (typeof imageFile !== "string" || typeof outFile !== "string") usage();

const tileWidth = readNumberArg(args, "tile-width", 128, 1, 4096);
const tileHeight = readNumberArg(args, "tile-height", tileWidth / 2, 1, 4096);
if (Math.abs(tileWidth / tileHeight - 2) > 0.001) {
  throw new Error("--tile-width must be exactly twice --tile-height for classic 2:1 iso");
}
const fallbackFootprint = readNumberArg(args, "footprint", 1, 1, 4);
const footprintWidth = readNumberArg(args, "footprint-width", fallbackFootprint, 1, 4);
const footprintHeight = readNumberArg(args, "footprint-height", fallbackFootprint, 1, 4);
if (!Number.isInteger(footprintWidth) || !Number.isInteger(footprintHeight)) {
  throw new Error("--footprint-width and --footprint-height must be integers from 1 to 4");
}
if (footprintWidth !== footprintHeight) {
  throw new Error(
    "Rectangular footprints are not supported by the v1 iso extraction workflow. Use a square footprint such as 1x1, 2x2, 3x3, or 4x4."
  );
}

const source = readPng(imageFile);
const background = parseColor(args.background ?? "#ff00ff");
const originX = readNumberArg(args, "origin-x", source.width / 2, -4096, source.width + 4096);
const originY = readNumberArg(args, "origin-y", source.height / 2, -4096, source.height + 4096);
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
      background
    );
    out.data[index] = mixed.r;
    out.data[index + 1] = mixed.g;
    out.data[index + 2] = mixed.b;
    out.data[index + 3] = 255;
  }
}

const line = { r: 0, g: 255, b: 255, a: 210 };
const major = { r: 255, g: 255, b: 0, a: 240 };
const originColor = { r: 255, g: 0, b: 0, a: 255 };

for (let i = 0; i <= footprintWidth; i += 1) {
  const a = isoPoint(originX, originY, tileWidth, tileHeight, i, 0, footprintWidth, footprintHeight);
  const b = isoPoint(
    originX,
    originY,
    tileWidth,
    tileHeight,
    i,
    footprintHeight,
    footprintWidth,
    footprintHeight
  );
  drawLine(out, a.x, a.y, b.x, b.y, i === 0 || i === footprintWidth ? major : line, 2);
}
for (let i = 0; i <= footprintHeight; i += 1) {
  const c = isoPoint(originX, originY, tileWidth, tileHeight, 0, i, footprintWidth, footprintHeight);
  const d = isoPoint(
    originX,
    originY,
    tileWidth,
    tileHeight,
    footprintWidth,
    i,
    footprintWidth,
    footprintHeight
  );
  drawLine(out, c.x, c.y, d.x, d.y, i === 0 || i === footprintHeight ? major : line, 2);
}
drawCross(out, originX, originY, originColor);

const top = isoPoint(originX, originY, tileWidth, tileHeight, 0, 0, footprintWidth, footprintHeight);
const right = isoPoint(
  originX,
  originY,
  tileWidth,
  tileHeight,
  footprintWidth,
  0,
  footprintWidth,
  footprintHeight
);
const bottom = isoPoint(
  originX,
  originY,
  tileWidth,
  tileHeight,
  footprintWidth,
  footprintHeight,
  footprintWidth,
  footprintHeight
);
const left = isoPoint(
  originX,
  originY,
  tileWidth,
  tileHeight,
  0,
  footprintHeight,
  footprintWidth,
  footprintHeight
);
const bounds = visibleBounds(source);
const report = {
  image: imageFile,
  width: source.width,
  height: source.height,
  projection: "isometric-2:1",
  tile: { width: tileWidth, height: tileHeight },
  footprint: { width: footprintWidth, height: footprintHeight },
  origin: { x: originX, y: originY },
  anchor: { x: originX / source.width, y: originY / source.height },
  sortPoint: { x: bottom.x / source.width, y: bottom.y / source.height },
  corners: { top, right, bottom, left },
  bounds,
};

writePng(outFile, out);
if (typeof args.report === "string") {
  fs.mkdirSync(path.dirname(args.report), { recursive: true });
  fs.writeFileSync(args.report, `${JSON.stringify(report, null, 2)}\n`);
} else {
  process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
}
