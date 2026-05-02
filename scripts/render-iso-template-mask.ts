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
node scripts/render-iso-template-mask.ts \\
  --out tmp/factory-template.png --size 1024 \\
  --tile-width 280 --tile-height 140 \\
  --footprint-width 2 --footprint-height 2 \\
  --origin-x 512 --origin-y 720 [--report report.json]

Creates a 3-color template mask:
red = locked background, purple = editable vertical body column, green = floor footprint.
Current v1 asset extraction only supports square footprints.
`);
}

function readNumberArg(args, name, fallback, min, max) {
  const parsed = args[name] === undefined ? fallback : Number(args[name]);
  if (!Number.isFinite(parsed) || parsed < min || parsed > max) {
    throw new Error(`Invalid --${name}: expected a number from ${min} to ${max}`);
  }
  return parsed;
}

function setPixel(png, x, y, color) {
  if (x < 0 || y < 0 || x >= png.width || y >= png.height) return;
  const index = (png.width * y + x) * 4;
  png.data[index] = color.r;
  png.data[index + 1] = color.g;
  png.data[index + 2] = color.b;
  png.data[index + 3] = color.a;
}

function isoPoint(originX, originY, tileWidth, tileHeight, gridX, gridY, footprintWidth, footprintHeight) {
  const centeredX = gridX - footprintWidth / 2;
  const centeredY = gridY - footprintHeight / 2;
  return {
    x: originX + (centeredX - centeredY) * (tileWidth / 2),
    y: originY + (centeredX + centeredY) * (tileHeight / 2),
  };
}

function pointInPolygon(x, y, polygon) {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i, i += 1) {
    const xi = polygon[i].x;
    const yi = polygon[i].y;
    const xj = polygon[j].x;
    const yj = polygon[j].y;
    const intersects = yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi;
    if (intersects) inside = !inside;
  }
  return inside;
}

function floorColumnLowerEnvelope(width, height, floor) {
  const lower = new Array(width).fill(-1);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      if (pointInPolygon(x + 0.5, y + 0.5, floor)) {
        lower[x] = Math.max(lower[x], y);
      }
    }
  }
  return lower;
}

const args = parseArgs(process.argv.slice(2));
const outFile = args.out;
if (typeof outFile !== "string") usage();

const size = readNumberArg(args, "size", 1024, 128, 8192);
const tileWidth = readNumberArg(args, "tile-width", 280, 1, 4096);
const tileHeight = readNumberArg(args, "tile-height", tileWidth / 2, 1, 4096);
if (Math.abs(tileWidth / tileHeight - 2) > 0.001) {
  throw new Error("--tile-width must be exactly twice --tile-height for classic 2:1 iso");
}
const footprintWidth = readNumberArg(args, "footprint-width", 2, 1, 4);
const footprintHeight = readNumberArg(args, "footprint-height", 2, 1, 4);
if (!Number.isInteger(footprintWidth) || !Number.isInteger(footprintHeight)) {
  throw new Error("--footprint-width and --footprint-height must be integers from 1 to 4");
}
if (footprintWidth !== footprintHeight) {
  throw new Error(
    "Rectangular footprints are not supported by the v1 iso extraction workflow. Use a square footprint such as 1x1, 2x2, 3x3, or 4x4."
  );
}
const originX = readNumberArg(args, "origin-x", size / 2, -4096, size + 4096);
const originY = readNumberArg(args, "origin-y", size * 0.7, -4096, size + 4096);

const red = { r: 255, g: 0, b: 0, a: 255 };
const green = { r: 0, g: 255, b: 0, a: 255 };
const purple = { r: 255, g: 0, b: 255, a: 255 };
const png = new PNG({ width: size, height: size });
for (let i = 0; i < png.data.length; i += 4) {
  png.data[i] = red.r;
  png.data[i + 1] = red.g;
  png.data[i + 2] = red.b;
  png.data[i + 3] = red.a;
}

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
const floor = [top, right, bottom, left];
const minX = Math.floor(Math.min(...floor.map((point) => point.x)));
const maxX = Math.ceil(Math.max(...floor.map((point) => point.x)));
const minY = Math.floor(Math.min(...floor.map((point) => point.y)));
const maxY = Math.ceil(Math.max(...floor.map((point) => point.y)));
const columnLower = floorColumnLowerEnvelope(size, size, floor);
let touchableMinX = size;
let touchableMaxX = -1;
let touchableMaxY = -1;

for (let x = Math.max(0, minX); x <= Math.min(size - 1, maxX); x += 1) {
  const lowerY = columnLower[x];
  if (lowerY < 0) continue;
  touchableMinX = Math.min(touchableMinX, x);
  touchableMaxX = Math.max(touchableMaxX, x);
  touchableMaxY = Math.max(touchableMaxY, lowerY);
  for (let y = 0; y <= lowerY; y += 1) {
    setPixel(png, x, y, purple);
  }
}

for (let y = minY; y <= maxY; y += 1) {
  for (let x = minX; x <= maxX; x += 1) {
    if (pointInPolygon(x + 0.5, y + 0.5, floor)) setPixel(png, x, y, green);
  }
}

fs.mkdirSync(path.dirname(outFile), { recursive: true });
fs.writeFileSync(outFile, PNG.sync.write(png));

const report = {
  out: outFile,
  size,
  projection: "isometric-2:1",
  tile: { width: tileWidth, height: tileHeight },
  footprint: { width: footprintWidth, height: footprintHeight },
  origin: { x: originX, y: originY },
  floor: { top, right, bottom, left },
  floorBounds: { x: minX, y: minY, width: maxX - minX + 1, height: maxY - minY + 1 },
  touchableColumn: {
    mode: "floor-column-lower-envelope",
    x: touchableMinX,
    y: 0,
    width: touchableMaxX - touchableMinX + 1,
    height: touchableMaxY + 1,
    note: "Purple is filled independently per x-column down to the actual floor footprint, then green floor is drawn over it.",
  },
  colors: { locked: "#ff0000", body: "#ff00ff", floor: "#00ff00" },
};
if (typeof args.report === "string") {
  fs.mkdirSync(path.dirname(args.report), { recursive: true });
  fs.writeFileSync(args.report, `${JSON.stringify(report, null, 2)}\n`);
} else {
  process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
}
