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
  [--background-threshold 40] [--same-threshold 8] [--opaque-distance-threshold 96] \\
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

function averageOpaque(first, second) {
  return {
    r: Math.round((first.r + second.r) / 2),
    g: Math.round((first.g + second.g) / 2),
    b: Math.round((first.b + second.b) / 2),
    a: 255,
  };
}

function baseOpaque(first) {
  return { r: first.r, g: first.g, b: first.b, a: 255 };
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

function isMatteLikeColor(color) {
  const { r, g, b } = color;
  const dominant = Math.max(r, g, b);
  const weakest = Math.min(r, g, b);
  const chroma = dominant - weakest;
  const brightGreenMatte = g >= 220 && g - Math.max(r, b) >= 65 && Math.max(r, b) >= 70;
  const brightRedMatte = r >= 220 && r - Math.max(g, b) >= 65;
  const brightBlueMatte = b >= 220 && b - Math.max(r, g) >= 65;
  const brightTwoChannelMatte =
    dominant >= 220 &&
    chroma >= 65 &&
    ((r >= 220 && g >= 220) || (r >= 220 && b >= 220) || (g >= 220 && b >= 220));
  return brightGreenMatte || brightRedMatte || brightBlueMatte || brightTwoChannelMatte;
}

function detectBorderMatteWash(source) {
  const border = Math.max(8, Math.floor(Math.min(source.width, source.height) * 0.18));
  let sampled = 0;
  let transparent = 0;
  let matteLike = 0;
  for (let y = 0; y < source.height; y += 1) {
    for (let x = 0; x < source.width; x += 1) {
      const inBorder =
        x < border || y < border || x >= source.width - border || y >= source.height - border;
      if (!inBorder) continue;
      sampled += 1;
      const index = (source.width * y + x) * 4;
      const alpha = source.data[index + 3];
      if (alpha < 32) {
        transparent += 1;
        continue;
      }
      if (
        isMatteLikeColor({
          r: source.data[index],
          g: source.data[index + 1],
          b: source.data[index + 2],
        })
      ) {
        matteLike += 1;
      }
    }
  }
  const transparentRatio = sampled ? transparent / sampled : 0;
  const matteLikeRatio = sampled ? matteLike / sampled : 0;
  return {
    sampled,
    transparent,
    matteLike,
    transparentRatio,
    matteLikeRatio,
    rejected: sampled > 0 && transparentRatio <= 0.18 && matteLikeRatio > 0.58,
  };
}

function looksLikeBakedCheckerboardPreview(source) {
  const { data, width, height } = source;
  if (width < 24 || height < 24) return false;

  const border = Math.max(8, Math.floor(Math.min(width, height) * 0.16));
  let sampled = 0;
  let transparent = 0;
  let opaqueGray = 0;
  let lowGray = 0;
  let highGray = 0;

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const inBorder = x < border || y < border || x >= width - border || y >= height - border;
      if (!inBorder) continue;
      sampled += 1;
      const offset = (y * width + x) * 4;
      const red = data[offset];
      const green = data[offset + 1];
      const blue = data[offset + 2];
      const alpha = data[offset + 3];
      if (alpha < 32) {
        transparent += 1;
        continue;
      }
      const brightness = (red + green + blue) / 3;
      const grayish = Math.max(Math.abs(red - green), Math.abs(red - blue), Math.abs(green - blue)) <= 10;
      if (alpha > 240 && grayish && brightness >= 70 && brightness <= 210) {
        opaqueGray += 1;
        if (brightness < 125) {
          lowGray += 1;
        } else if (brightness > 145) {
          highGray += 1;
        }
      }
    }
  }

  if (sampled === 0 || transparent / sampled > 0.18) return false;
  return opaqueGray / sampled > 0.58 && lowGray / sampled > 0.08 && highGray / sampled > 0.18;
}

function looksLikeBakedSolidMattePreview(source) {
  const { data, width, height } = source;
  if (width < 24 || height < 24) return false;

  const border = Math.max(8, Math.floor(Math.min(width, height) * 0.18));
  let sampled = 0;
  let transparent = 0;
  let matteLike = 0;

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const inBorder = x < border || y < border || x >= width - border || y >= height - border;
      if (!inBorder) continue;
      sampled += 1;
      const offset = (y * width + x) * 4;
      const alpha = data[offset + 3];
      if (alpha < 32) {
        transparent += 1;
        continue;
      }
      if (isMatteLikeColor({ r: data[offset], g: data[offset + 1], b: data[offset + 2] })) {
        matteLike += 1;
      }
    }
  }

  if (sampled === 0 || transparent / sampled > 0.18) return false;
  return matteLike / sampled > 0.58;
}

function looksLikeBakedNeutralSolidMattePreview(source) {
  const { data, width, height } = source;
  if (width < 24 || height < 24) return false;

  const border = Math.max(8, Math.floor(Math.min(width, height) * 0.18));
  let sampled = 0;
  let transparent = 0;
  let neutralMatteLike = 0;

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const inBorder = x < border || y < border || x >= width - border || y >= height - border;
      if (!inBorder) continue;
      sampled += 1;
      const offset = (y * width + x) * 4;
      const red = data[offset];
      const green = data[offset + 1];
      const blue = data[offset + 2];
      const alpha = data[offset + 3];
      if (alpha < 32) {
        transparent += 1;
        continue;
      }
      const brightness = (red + green + blue) / 3;
      const grayish = Math.max(Math.abs(red - green), Math.abs(red - blue), Math.abs(green - blue)) <= 12;
      if (alpha > 240 && grayish && (brightness >= 235 || brightness <= 20)) {
        neutralMatteLike += 1;
      }
    }
  }

  if (sampled === 0 || transparent / sampled > 0.18) return false;
  return neutralMatteLike / sampled > 0.58;
}

function looksLikeResidualMatteGridArtifact(source) {
  const { data, width, height } = source;
  if (width < 48 || height < 48) return false;

  const rowCounts = new Uint32Array(height);
  const columnCounts = new Uint32Array(width);
  let matteLike = 0;

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const offset = (y * width + x) * 4;
      const red = data[offset];
      const green = data[offset + 1];
      const blue = data[offset + 2];
      const alpha = data[offset + 3];
      if (alpha < 24 || alpha > 190) continue;

      const greenMatte = green >= 35 && green - Math.max(red, blue) >= 25 && red <= 110 && blue <= 110;
      const redMatte = red >= 35 && red - Math.max(green, blue) >= 25 && green <= 120 && blue <= 120;
      const blueMatte = blue >= 35 && blue - Math.max(red, green) >= 25 && red <= 120 && green <= 120;
      const purpleMatte = red >= 35 && blue >= 35 && Math.min(red, blue) - green >= 25 && green <= 120;
      if (!greenMatte && !redMatte && !blueMatte && !purpleMatte) continue;

      matteLike += 1;
      rowCounts[y] += 1;
      columnCounts[x] += 1;
    }
  }

  const matteRatio = matteLike / (width * height);
  if (matteRatio < 0.0015) return false;

  let rowsWithLines = 0;
  for (const count of rowCounts) {
    if (count / width >= 0.12) rowsWithLines += 1;
  }

  let columnsWithLines = 0;
  for (const count of columnCounts) {
    if (count / height >= 0.12) columnsWithLines += 1;
  }

  return rowsWithLines + columnsWithLines >= 3 && (rowsWithLines >= 2 || columnsWithLines >= 2);
}

function looksLikeResidualTransparentGridLineArtifact(source) {
  const { data, width, height } = source;
  if (width < 48 || height < 48) return false;

  const rowVisibleCounts = new Uint32Array(height);
  const rowSemiCounts = new Uint32Array(height);
  const columnVisibleCounts = new Uint32Array(width);
  const columnSemiCounts = new Uint32Array(width);

  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const offset = (y * width + x) * 4;
      const alpha = data[offset + 3];
      if (alpha <= 0) continue;
      rowVisibleCounts[y] += 1;
      columnVisibleCounts[x] += 1;
      if (alpha < 255) {
        rowSemiCounts[y] += 1;
        columnSemiCounts[x] += 1;
      }
    }
  }

  let rowsWithLines = 0;
  for (let row = 0; row < height; row += 1) {
    const visibleRatio = rowVisibleCounts[row] / width;
    const semiRatio = rowSemiCounts[row] / width;
    if (visibleRatio >= 0.94 && semiRatio >= 0.72) rowsWithLines += 1;
  }

  let columnsWithLines = 0;
  for (let column = 0; column < width; column += 1) {
    const visibleRatio = columnVisibleCounts[column] / height;
    const semiRatio = columnSemiCounts[column] / height;
    if (visibleRatio >= 0.94 && semiRatio >= 0.72) columnsWithLines += 1;
  }

  return rowsWithLines + columnsWithLines >= 3 && (rowsWithLines >= 2 || columnsWithLines >= 2);
}

function isResidualMatteArtifactPixel(red, green, blue, alpha) {
  if (alpha < 24 || alpha > 190) return false;
  const greenMatte = green >= 35 && green - Math.max(red, blue) >= 25 && red <= 110 && blue <= 110;
  const redMatte = red >= 35 && red - Math.max(green, blue) >= 25 && green <= 120 && blue <= 120;
  const blueMatte = blue >= 35 && blue - Math.max(red, green) >= 25 && red <= 120 && green <= 120;
  const purpleMatte = red >= 35 && blue >= 35 && Math.min(red, blue) - green >= 25 && green <= 120;
  return greenMatte || redMatte || blueMatte || purpleMatte;
}

function clearResidualMatteArtifactPixels(source) {
  let cleared = 0;
  for (let y = 0; y < source.height; y += 1) {
    for (let x = 0; x < source.width; x += 1) {
      const index = (source.width * y + x) * 4;
      if (!isResidualMatteArtifactPixel(
        source.data[index],
        source.data[index + 1],
        source.data[index + 2],
        source.data[index + 3]
      )) {
        continue;
      }
      source.data[index] = 0;
      source.data[index + 1] = 0;
      source.data[index + 2] = 0;
      source.data[index + 3] = 0;
      cleared += 1;
    }
  }
  return cleared;
}

function isNearAnyColor(color, colors, threshold) {
  return colors.some((candidate) => dist(color, candidate) <= threshold);
}

function clearConnectedBorderMattePixels(source, matteColors, threshold) {
  const { data, width, height } = source;
  const visited = new Uint8Array(width * height);
  const stack = [];
  const enqueue = (x, y) => {
    if (x < 0 || y < 0 || x >= width || y >= height) return;
    const pixel = y * width + x;
    if (visited[pixel]) return;
    const index = pixel * 4;
    const alpha = data[index + 3];
    if (alpha <= 16) return;
    if (
      !isNearAnyColor(
        { r: data[index], g: data[index + 1], b: data[index + 2] },
        matteColors,
        threshold
      )
    ) {
      return;
    }
    visited[pixel] = 1;
    stack.push(pixel);
  };

  for (let x = 0; x < width; x += 1) {
    enqueue(x, 0);
    enqueue(x, height - 1);
  }
  for (let y = 1; y < height - 1; y += 1) {
    enqueue(0, y);
    enqueue(width - 1, y);
  }

  let cleared = 0;
  while (stack.length > 0) {
    const pixel = stack.pop();
    const x = pixel % width;
    const y = Math.floor(pixel / width);
    const index = pixel * 4;
    data[index] = 0;
    data[index + 1] = 0;
    data[index + 2] = 0;
    data[index + 3] = 0;
    cleared += 1;
    enqueue(x + 1, y);
    enqueue(x - 1, y);
    enqueue(x, y + 1);
    enqueue(x, y - 1);
  }
  return cleared;
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
const opaqueDistanceThreshold = readNumberArg(
  args["opaque-distance-threshold"],
  Math.max(bgThreshold * 2, 96),
  "opaque-distance-threshold",
  0,
  441
);
const residueThreshold = readNumberArg(
  args["residue-threshold"],
  bgThreshold,
  "residue-threshold",
  0,
  441
);
const maxPairDriftRatio = readNumberArg(
  args["max-pair-drift-ratio"],
  0.25,
  "max-pair-drift-ratio",
  0,
  1
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
let opaqueDrift = 0;
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
      pixel = averageOpaque(first, second);
      opaque += 1;
    } else if (
      firstDistance >= opaqueDistanceThreshold &&
      secondDistance >= opaqueDistanceThreshold
    ) {
      pixel = baseOpaque(first);
      opaqueDrift += 1;
      opaque += 1;
    } else {
      const alpha = estimateAlpha(first, second, firstBg, secondBg);
      if (alpha * 255 <= alphaFloor) {
        pixel = { r: 0, g: 0, b: 0, a: 0 };
        transparent += 1;
      } else if (alpha >= 0.985) {
        pixel = averageOpaque(first, second);
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

const connectedBorderMattePixelsCleared = clearConnectedBorderMattePixels(
  out,
  [firstBg, secondBg],
  residueThreshold
);
const residualMatteArtifactPixelsCleared = clearResidualMatteArtifactPixels(out);

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
const borderMatteWash = detectBorderMatteWash(out);
const rejectedPairDrift = pairDriftRatio > maxPairDriftRatio;
const previewBackground = {
  checkerboard: looksLikeBakedCheckerboardPreview(out),
  solidMatte: looksLikeBakedSolidMattePreview(out),
  neutralSolidMatte: looksLikeBakedNeutralSolidMattePreview(out),
  residualMatteGrid: looksLikeResidualMatteGridArtifact(out),
  residualTransparentGridLines: looksLikeResidualTransparentGridLineArtifact(out),
};
const rejectedPreviewBackground = Object.values(previewBackground).some(Boolean);
if (pairDriftRatio > 0.05) {
  warnings.push(
    "Matte pair drift detected. This is common with AI-generated matte pairs and is not a failure by itself; inspect visual previews."
  );
}
if (rejectedPairDrift) {
  warnings.push(
    "Rejected: the matte pair changed too much of the asset. Regenerate the second matte with strict change-background-only instructions, or regenerate both mattes with a simpler opaque sprite prompt."
  );
}
if (baseResidueRatio > 0.01 || swapResidueRatio > 0.01) {
  warnings.push(
    "Potential matte-color residue detected in visible pixels. Inspect the contact sheet for halos, holes, or background blocks."
  );
}
if (borderMatteWash.rejected) {
  warnings.push(
    "Rejected: the output border still contains a large matte-color wash. Regenerate or retry extraction before accepting this runtime asset."
  );
}
if (rejectedPreviewBackground) {
  warnings.push(
    "Rejected: the output still looks like a baked checkerboard, matte, preview, or grid-background image. Regenerate or retry extraction before accepting this runtime asset."
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
    opaqueDriftPixels: opaqueDrift,
    connectedBorderMattePixelsCleared,
    residualMatteArtifactPixelsCleared,
    potentialMatteResidue: {
      baseBgPixels: potentialBaseResidue,
      baseBgRatio: baseResidueRatio,
      swapBgPixels: potentialSwapResidue,
      swapBgRatio: swapResidueRatio,
      threshold: residueThreshold,
    },
    borderMatteWash,
    previewBackground,
    warnings,
    acceptance: {
      automaticResult: rejectedPairDrift
        ? "rejected-pair-drift"
        : borderMatteWash.rejected || rejectedPreviewBackground
          ? "rejected-preview-background"
          : warnings.length
            ? "visual-review-required"
            : "no-obvious-script-detected-residue",
      rule: "Do not reject only because matte/semiTransparent counts are high. Reject obvious matte-background washes; otherwise accept or retry based on visual contact-sheet inspection.",
    },
  },
  colors: { firstBg, secondBg, previewBg },
  contactSheet: contactSheetColors
    ? {
        out: typeof args["contact-sheet-out"] === "string" ? args["contact-sheet-out"] : undefined,
        colors: contactSheetColors.map(colorToHex),
      }
    : undefined,
  thresholds: {
    bgThreshold,
    sameThreshold,
    alphaFloor,
    opaqueDistanceThreshold,
    residueThreshold,
    maxPairDriftRatio,
  },
};

if (typeof args.report === "string") {
  fs.mkdirSync(path.dirname(args.report), { recursive: true });
  fs.writeFileSync(args.report, `${JSON.stringify(report, null, 2)}\n`);
} else {
  process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
}

if (rejectedPairDrift || borderMatteWash.rejected || rejectedPreviewBackground) {
  try {
    fs.unlinkSync(outFile);
  } catch {
    // The non-zero exit is the source of truth; missing output cleanup is non-fatal.
  }
  console.error(
    "extract-alpha-background-swap rejected output: matte pair drift, baked checkerboard, matte, preview, grid, or matte-color wash remains."
  );
  process.exitCode = 2;
}
